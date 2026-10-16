"""
Đồng bộ hóa dữ liệu:
Chuyển các sample đã embedded trong index từ data/unembedded_samples.parquet
sang data/embedded_samples.parquet (tránh trùng lặp), và xóa trong data/remaining_urls.parquet.
"""

import os
import sys
import shutil
import pandas as pd
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(r"d:\CODE PLAYGROUND\Projects\Competitions\R2AI-Stage-3-2026")
DATA_DIR = BASE / "data"

UNEMB_PATH = DATA_DIR / "unembedded_samples.parquet"
EMB_PATH = DATA_DIR / "embedded_samples.parquet"
REM_PATH = DATA_DIR / "remaining_urls.parquet"
INDEX_META_PATH = DATA_DIR / "indices" / "new_dataset" / "index" / "chunks_metadata.parquet"


def main():
    print("=" * 80)
    print("🔄 BẮT ĐẦU ĐỒNG BỘ CÁC SAMPLE ĐÃ EMBEDDED SANG EMBEDDED_SAMPLES.PARQUET")
    print("=" * 80)

    # 1. Đọc doc_ids đã indexed
    print(f"\n[1/5] Đọc danh sách doc_id đã có trong index: {INDEX_META_PATH}...")
    df_meta = pd.read_parquet(INDEX_META_PATH, columns=["doc_id"])
    indexed_doc_ids = set(df_meta["doc_id"].unique())
    print(f"  • Tổng doc_ids trong index: {len(indexed_doc_ids):,}")

    # 2. Đọc unembedded_samples.parquet
    print(f"\n[2/5] Đọc dữ liệu unembedded: {UNEMB_PATH}...")
    df_unemb = pd.read_parquet(UNEMB_PATH)
    total_unemb_before = len(df_unemb)
    print(f"  • unembedded_samples trước khi lọc: {total_unemb_before:,} rows")

    mask_embedded = df_unemb["id"].isin(indexed_doc_ids)
    df_to_move = df_unemb[mask_embedded].copy()
    df_unemb_remaining = df_unemb[~mask_embedded].copy()

    n_to_move = len(df_to_move)
    n_remaining = len(df_unemb_remaining)
    print(f"  • Số sample đã embedded cần chuyển đi: {n_to_move:,}")
    print(f"  • Số sample chưa embedded còn giữ lại: {n_remaining:,}")
    assert n_to_move + n_remaining == total_unemb_before, "Tổng số dòng không khớp sau khi phân tách!"

    # 3. Đọc và gộp vào embedded_samples.parquet
    print(f"\n[3/5] Gộp vào dữ liệu embedded: {EMB_PATH}...")
    if EMB_PATH.exists():
        df_emb = pd.read_parquet(EMB_PATH)
        n_emb_before = len(df_emb)
        print(f"  • embedded_samples hiện tại: {n_emb_before:,} rows")
        df_emb_combined = pd.concat([df_emb, df_to_move], ignore_index=True)
    else:
        n_emb_before = 0
        df_emb_combined = df_to_move

    # Tránh trùng lặp dữ liệu (Deduplicate)
    df_emb_final = df_emb_combined.drop_duplicates(subset=["id"]).copy()
    n_emb_final = len(df_emb_final)
    print(f"  • embedded_samples sau khi gộp và khử trùng lặp: {n_emb_final:,} rows (+{n_emb_final - n_emb_before:,} mới)")

    # 4. Kiểm tra và loại bỏ các ID đã embedded khỏi remaining_urls.parquet
    print(f"\n[4/5] Cập nhật remaining_urls: {REM_PATH}...")
    if REM_PATH.exists():
        df_rem = pd.read_parquet(REM_PATH)
        n_rem_before = len(df_rem)
        id_col = "id" if "id" in df_rem.columns else df_rem.columns[0]
        # Xóa các ID đã embedded
        df_rem_final = df_rem[~df_rem[id_col].isin(df_to_move["id"])].copy()
        # Đảm bảo cũng không trùng với bất kỳ ID nào trong embedded_samples
        df_rem_final = df_rem_final[~df_rem_final[id_col].isin(df_emb_final["id"])].copy()
        n_rem_final = len(df_rem_final)
        print(f"  • remaining_urls trước: {n_rem_before:,} rows | sau: {n_rem_final:,} rows (đã loại bỏ {n_rem_before - n_rem_final:,})")
    else:
        df_rem_final = None
        n_rem_before = n_rem_final = 0
        print("  • Không tìm thấy remaining_urls.parquet!")

    # 5. Sao lưu và ghi đè an toàn
    print(f"\n[5/5] Tiến hành sao lưu .bak và lưu dữ liệu mới...")
    # Tạo backup
    shutil.copy2(UNEMB_PATH, DATA_DIR / "unembedded_samples.parquet.bak")
    if EMB_PATH.exists():
        shutil.copy2(EMB_PATH, DATA_DIR / "embedded_samples.parquet.bak")
    if REM_PATH.exists():
        shutil.copy2(REM_PATH, DATA_DIR / "remaining_urls.parquet.bak")
    print("  ✓ Đã tạo các tệp .bak an toàn.")

    # Ghi tệp
    df_unemb_remaining.to_parquet(UNEMB_PATH, index=False, compression="snappy")
    print(f"  💾 Đã lưu {UNEMB_PATH}: {len(df_unemb_remaining):,} rows")

    df_emb_final.to_parquet(EMB_PATH, index=False, compression="snappy")
    print(f"  💾 Đã lưu {EMB_PATH}: {len(df_emb_final):,} rows")

    if df_rem_final is not None:
        df_rem_final.to_parquet(REM_PATH, index=False, compression="snappy")
        print(f"  💾 Đã lưu {REM_PATH}: {len(df_rem_final):,} rows")

    # Xác thực tính toàn vẹn
    print("\n🔍 KIỂM TRA TÍNH TOÀN VẸN CUỐI CÙNG:")
    v_unemb = pd.read_parquet(UNEMB_PATH)
    v_emb = pd.read_parquet(EMB_PATH)
    set_unemb = set(v_unemb["id"])
    set_emb = set(v_emb["id"])
    overlap = set_unemb.intersection(set_emb)
    print(f"  • Trùng lặp giữa embedded_samples và unembedded_samples: {len(overlap)} (Phải bằng 0)")
    assert len(overlap) == 0, f"Phát hiện {len(overlap)} ID bị trùng giữa 2 tệp!"

    if REM_PATH.exists():
        v_rem = pd.read_parquet(REM_PATH)
        rem_overlap = set(v_rem["id"]).intersection(set_emb)
        print(f"  • Trùng lặp giữa remaining_urls và embedded_samples: {len(rem_overlap)} (Phải bằng 0)")
        assert len(rem_overlap) == 0, f"Phát hiện {len(rem_overlap)} ID bị trùng giữa remaining_urls và embedded!"

    print("\n" + "=" * 80)
    print("🎉 ĐỒNG BỘ THÀNH CÔNG VÀ CHÍNH XÁC 100%!")
    print(f" • embedded_samples:   {len(v_emb):,} tài liệu")
    print(f" • unembedded_samples: {len(v_unemb):,} tài liệu chưa embedded")
    if REM_PATH.exists():
        print(f" • remaining_urls:     {len(v_rem):,} urls còn lại chưa cào")
    print("=" * 80)


if __name__ == "__main__":
    main()
