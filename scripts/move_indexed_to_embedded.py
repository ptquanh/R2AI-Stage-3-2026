"""
Move all indexed samples from data/unembedded_samples.parquet to data/embedded_samples.parquet.
Ensures:
1. Exact match between embedded_samples.parquet and indexed documents (962,326 docs).
2. Clean removal of indexed samples from unembedded_samples.parquet (198,138 remaining).
3. Zero duplication in both files.
4. Automatic backup before modifications.
"""

import os
import sys
import time
import shutil
import pandas as pd
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE = Path("d:/CODE PLAYGROUND/Projects/Competitions/R2AI-Stage-3-2026")
INDEX_META_PATH = BASE / "data" / "indices" / "new_dataset" / "index" / "chunks_metadata.parquet"
EMB_SAMPLES_PATH = BASE / "data" / "embedded_samples.parquet"
UNEMB_SAMPLES_PATH = BASE / "data" / "unembedded_samples.parquet"


def main():
    print("=" * 80)
    print("🚀 DI CHUYỂN CÁC MẪU ĐÃ CÓ TRONG INDEX TỪ UNEMBEDDED SANG EMBEDDED")
    print("=" * 80)
    t0 = time.time()

    # 1. Đọc danh sách doc_id đã có trong index
    print(f"[1/4] Đang đọc danh sách doc_id từ index: {INDEX_META_PATH}...")
    df_meta = pd.read_parquet(INDEX_META_PATH, columns=["doc_id"])
    indexed_ids = set(df_meta["doc_id"].unique())
    print(f"  ✅ Tìm thấy {len(indexed_ids):,} doc_ids trong index.")

    # 2. Đọc unembedded_samples.parquet
    print(f"\n[2/4] Đang phân loại mẫu trong {UNEMB_SAMPLES_PATH}...")
    df_unemb = pd.read_parquet(UNEMB_SAMPLES_PATH)
    initial_unemb_count = len(df_unemb)
    print(f"  - Tổng số mẫu unembedded hiện tại: {initial_unemb_count:,}")

    # Lọc các mẫu đã có trong index vs chưa có trong index
    mask_in_index = df_unemb["id"].isin(indexed_ids)
    df_to_move = df_unemb[mask_in_index].copy()
    df_unemb_remaining = df_unemb[~mask_in_index].copy()

    n_to_move = len(df_to_move)
    n_remaining = len(df_unemb_remaining)
    print(f"  - Mẫu ĐÃ CÓ trong index (cần chuyển sang embedded): {n_to_move:,}")
    print(f"  - Mẫu CHƯA CÓ trong index (giữ lại ở unembedded):    {n_remaining:,}")

    # Backup unembedded_samples.parquet
    backup_unemb = UNEMB_SAMPLES_PATH.with_suffix(".parquet.bak")
    shutil.copy2(UNEMB_SAMPLES_PATH, backup_unemb)
    print(f"  - Đã backup unembedded vào: {backup_unemb.name}")

    # 3. Đọc và cập nhật embedded_samples.parquet
    print(f"\n[3/4] Đang cập nhật {EMB_SAMPLES_PATH}...")
    df_emb = pd.read_parquet(EMB_SAMPLES_PATH)
    initial_emb_count = len(df_emb)
    print(f"  - Số mẫu embedded hiện tại: {initial_emb_count:,}")

    # Backup embedded_samples.parquet
    backup_emb = EMB_SAMPLES_PATH.with_suffix(".parquet.bak")
    shutil.copy2(EMB_SAMPLES_PATH, backup_emb)
    print(f"  - Đã backup embedded vào: {backup_emb.name}")

    # Nối và khử trùng lặp
    df_emb_new = pd.concat([df_emb, df_to_move], ignore_index=True)
    df_emb_new = df_emb_new.drop_duplicates(subset=["id"])
    df_emb_new.to_parquet(EMB_SAMPLES_PATH, index=False, compression="snappy")
    final_emb_count = len(df_emb_new)
    print(f"  ✅ Đã lưu {EMB_SAMPLES_PATH}: {initial_emb_count:,} -> {final_emb_count:,} (+{final_emb_count - initial_emb_count:,} mẫu)")

    # Lưu lại unembedded_samples.parquet đã loại bỏ các mẫu đã chuyển
    df_unemb_remaining = df_unemb_remaining.drop_duplicates(subset=["id"])
    df_unemb_remaining.to_parquet(UNEMB_SAMPLES_PATH, index=False, compression="snappy")
    final_unemb_count = len(df_unemb_remaining)
    print(f"  ✅ Đã lưu {UNEMB_SAMPLES_PATH}: {initial_unemb_count:,} -> {final_unemb_count:,} (-{n_to_move:,} mẫu)")

    # 4. Kiểm tra tính toàn vẹn (Integrity Assertions)
    print("\n[4/4] Kiểm tra toàn vẹn...")
    assert final_emb_count == initial_emb_count + n_to_move, "Lỗi số lượng embedded_samples không khớp!"
    assert final_unemb_count == initial_unemb_count - n_to_move, "Lỗi số lượng unembedded_samples không khớp!"
    assert len(set(df_emb_new["id"]).intersection(set(df_unemb_remaining["id"]))) == 0, "Trùng lặp ID giữa embedded và unembedded!"
    assert set(df_emb_new["id"]) == indexed_ids, "Danh sách ID trong embedded_samples không khớp 100% với index!"
    print("  ✅ Tất cả kiểm tra toàn vẹn đã ĐẠT 100%!")

    print("\n" + "=" * 80)
    print(f"🎉 HOÀN TẤT DI CHUYỂN TRONG {time.time() - t0:.2f}s!")
    print(f" • embedded_samples.parquet:   {final_emb_count:,} mẫu (Khớp 100% với {len(indexed_ids):,} docs trong index)")
    print(f" • unembedded_samples.parquet: {final_unemb_count:,} mẫu (Thực sự chưa nhúng)")
    print("=" * 80)


if __name__ == "__main__":
    main()
