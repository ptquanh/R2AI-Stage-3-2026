"""
Synchronize successfully crawled items from local_recovered:
1. Load all parts from data/raw/corpus_text/local_recovered where status == 'success'
2. Append to data/unembedded_samples.parquet
3. Remove successful IDs from data/remaining_urls.parquet
4. Validate row counts and integrity
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
RECOV_DIR = BASE / "data" / "raw" / "corpus_text" / "local_recovered"
UNEMBEDDED_PATH = BASE / "data" / "unembedded_samples.parquet"
REMAINING_PATH = BASE / "data" / "remaining_urls.parquet"


def main():
    print("=" * 75)
    print("🚀 ĐỒNG BỘ DỮ LIỆU CÀO THÀNH CÔNG VÀO UNEMBEDDED & REMAINING URLS")
    print("=" * 75)
    t0 = time.time()

    # 1. Đọc tất cả các parts từ local_recovered
    parquet_files = sorted(list(RECOV_DIR.glob("*.parquet")))
    print(f"[1/4] Đang nạp {len(parquet_files)} parquet files từ {RECOV_DIR}...")
    dfs = []
    for f in parquet_files:
        try:
            df_part = pd.read_parquet(f)
            # Chỉ lấy các dòng status == 'success' và text không rỗng
            valid_mask = (df_part["status"] == "success") & df_part["text"].notna() & (df_part["text"].str.strip() != "")
            dfs.append(df_part[valid_mask][["id", "url", "text"]])
        except Exception as e:
            print(f"  ⚠️ Lỗi khi đọc file {f.name}: {e}")

    df_recovered = pd.concat(dfs, ignore_index=True)
    df_recovered = df_recovered.drop_duplicates(subset=["id"])
    success_ids = set(df_recovered["id"])
    n_recovered = len(df_recovered)
    print(f"  ✅ Đã trích xuất {n_recovered:,} bản ghi cào thành công hợp lệ (Unique IDs: {len(success_ids):,})")

    # 2. Đọc và cập nhật unembedded_samples.parquet
    print(f"\n[2/4] Đang cập nhật {UNEMBEDDED_PATH}...")
    df_unembedded_old = pd.read_parquet(UNEMBEDDED_PATH)
    old_unemb_count = len(df_unembedded_old)
    print(f"  - Số dòng hiện tại: {old_unemb_count:,}")

    # Tạo bản sao backup an toàn
    backup_unemb = UNEMBEDDED_PATH.with_suffix(".parquet.bak")
    shutil.copy2(UNEMBEDDED_PATH, backup_unemb)
    print(f"  - Đã backup vào: {backup_unemb.name}")

    # Nối dữ liệu mới vào cuối
    df_unembedded_new = pd.concat([df_unembedded_old, df_recovered], ignore_index=True)
    df_unembedded_new = df_unembedded_new.drop_duplicates(subset=["id"])
    df_unembedded_new.to_parquet(UNEMBEDDED_PATH, index=False, compression="snappy")
    new_unemb_count = len(df_unembedded_new)
    print(f"  ✅ Đã lưu {UNEMBEDDED_PATH}: {old_unemb_count:,} -> {new_unemb_count:,} (+{new_unemb_count - old_unemb_count:,} dòng)")

    # 3. Đọc và cập nhật remaining_urls.parquet
    print(f"\n[3/4] Đang cập nhật {REMAINING_PATH}...")
    df_remaining_old = pd.read_parquet(REMAINING_PATH)
    old_rem_count = len(df_remaining_old)
    print(f"  - Số dòng hiện tại: {old_rem_count:,}")

    # Tạo bản sao backup an toàn
    backup_rem = REMAINING_PATH.with_suffix(".parquet.bak")
    shutil.copy2(REMAINING_PATH, backup_rem)
    print(f"  - Đã backup vào: {backup_rem.name}")

    # Loại bỏ các ID đã cào thành công
    df_remaining_new = df_remaining_old[~df_remaining_old["id"].isin(success_ids)].copy()
    df_remaining_new.to_parquet(REMAINING_PATH, index=False, compression="snappy")
    new_rem_count = len(df_remaining_new)
    removed_count = old_rem_count - new_rem_count
    print(f"  ✅ Đã lưu {REMAINING_PATH}: {old_rem_count:,} -> {new_rem_count:,} (-{removed_count:,} dòng)")

    # 4. Kiểm tra tính toàn vẹn (Integrity Assertions)
    print("\n[4/4] Kiểm tra toàn vẹn...")
    assert new_unemb_count == old_unemb_count + n_recovered, f"Mismatch unemb count: {new_unemb_count} != {old_unemb_count + n_recovered}"
    assert removed_count == n_recovered, f"Mismatch removed count: {removed_count} != {n_recovered}"
    assert len(set(df_remaining_new["id"]).intersection(set(df_unembedded_new["id"]))) == 0, "Trùng ID giữa remaining và unembedded!"
    print("  ✅ Tất cả kiểm tra toàn vẹn đã ĐẠT 100%!")

    print("\n" + "=" * 75)
    print(f"🎉 HOÀN THÀNH TẤT CẢ TRONG {time.time() - t0:.2f}s!")
    print(f" • unembedded_samples.parquet: {new_unemb_count:,} mẫu (sẵn sàng nhúng)")
    print(f" • remaining_urls.parquet: {new_rem_count:,} URLs còn lại")
    print("=" * 75)


if __name__ == "__main__":
    main()
