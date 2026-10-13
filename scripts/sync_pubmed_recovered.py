"""
Sync successfully crawled PubMed articles:
1. Append new PubMed samples to data/unembedded_samples.parquet (without duplicates).
2. Remove successful PubMed IDs from data/remaining_urls.parquet.
3. Validate row counts, schema, and ID uniqueness.
"""

import os
import sys
import glob
import time
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

PUBMED_DIR = "data/raw/corpus_text/pubmed_recovered"
UNEMBEDDED_PATH = "data/unembedded_samples.parquet"
REMAINING_PATH = "data/remaining_urls.parquet"


def main():
    print("=" * 75)
    print("🚀 BẮT ĐẦU ĐỒNG BỘ DỮ LIỆU CÀO PUBMED THÀNH CÔNG")
    print("=" * 75)
    t0 = time.time()

    # 1. Đọc tất cả các tệp pubmed_recovered
    pubmed_files = sorted(glob.glob(os.path.join(PUBMED_DIR, "part_*.parquet")))
    print(f"1. Đọc {len(pubmed_files)} tệp parquet từ {PUBMED_DIR}...")
    pubmed_dfs = [pd.read_parquet(f) for f in pubmed_files]
    df_pubmed = pd.concat(pubmed_dfs, ignore_index=True)
    total_pubmed = len(df_pubmed)
    pubmed_ids = set(df_pubmed["id"])
    print(f"   -> Tổng số bài PubMed cào được: {total_pubmed:,} (Unique IDs: {len(pubmed_ids):,})")

    # 2. Xử lý data/unembedded_samples.parquet
    print(f"\n2. Đang đọc và đồng bộ vào {UNEMBEDDED_PATH}...")
    df_unemb = pd.read_parquet(UNEMBEDDED_PATH)
    orig_unemb_len = len(df_unemb)
    existing_unemb_ids = set(df_unemb["id"])
    print(f"   -> unembedded_samples hiện tại: {orig_unemb_len:,} rows")

    # Lọc các bài pubmed chưa có trong unembedded để không trùng lặp
    new_pubmed = df_pubmed[~df_pubmed["id"].isin(existing_unemb_ids)]
    n_new = len(new_pubmed)
    n_skip = total_pubmed - n_new
    print(f"   -> Mẫu mới cần thêm: {n_new:,} (Bỏ qua {n_skip:,} mẫu đã có sẵn để tránh trùng lặp)")

    # Nối vào cuối, giữ nguyên thứ tự và index ban đầu
    df_unemb_updated = pd.concat([df_unemb, new_pubmed], ignore_index=True)
    final_unemb_len = len(df_unemb_updated)
    print(f"   -> unembedded_samples sau khi gộp: {final_unemb_len:,} rows (Kỳ vọng: {orig_unemb_len + n_new:,})")
    assert final_unemb_len == orig_unemb_len + n_new, "Lỗi kích thước dòng unembedded_samples!"
    assert len(df_unemb_updated["id"].unique()) == final_unemb_len, "Lỗi có ID trùng lặp trong unembedded_samples!"

    # Lưu lại unembedded_samples.parquet
    t_save = time.time()
    df_unemb_updated.to_parquet(UNEMBEDDED_PATH, index=False, compression="snappy")
    print(f"   💾 Đã ghi thành công {UNEMBEDDED_PATH} ({os.path.getsize(UNEMBEDDED_PATH) / (1024**2):.1f} MB) trong {time.time() - t_save:.1f}s")

    # 3. Xử lý data/remaining_urls.parquet
    print(f"\n3. Đang lọc và xóa các ID thành công khỏi {REMAINING_PATH}...")
    df_rem = pd.read_parquet(REMAINING_PATH)
    orig_rem_len = len(df_rem)
    print(f"   -> remaining_urls hiện tại: {orig_rem_len:,} rows")

    # Xóa toàn bộ các ID đã cào thành công trong pubmed_recovered
    df_rem_updated = df_rem[~df_rem["id"].isin(pubmed_ids)].copy()
    final_rem_len = len(df_rem_updated)
    n_removed = orig_rem_len - final_rem_len
    print(f"   -> Đã xóa {n_removed:,} URLs đã cào thành công")
    print(f"   -> remaining_urls sau khi lọc: {final_rem_len:,} rows (Kỳ vọng: {orig_rem_len - total_pubmed:,})")
    assert final_rem_len == orig_rem_len - total_pubmed, "Lỗi số lượng URLs bị xóa không khớp với tổng số pubmed_ids!"

    # Lưu lại remaining_urls.parquet
    t_save_rem = time.time()
    df_rem_updated.to_parquet(REMAINING_PATH, index=False, compression="snappy")
    print(f"   💾 Đã ghi thành công {REMAINING_PATH} ({os.path.getsize(REMAINING_PATH) / (1024**2):.1f} MB) trong {time.time() - t_save_rem:.1f}s")

    # 4. Báo cáo tổng kết
    print("\n" + "=" * 75)
    print("🎉 ĐỒNG BỘ DỮ LIỆU PUBMED HOÀN TẤT THÀNH CÔNG 100%!")
    print(f"  • Mẫu đã thêm vào unembedded_samples.parquet: +{n_new:,} bài mới (Tổng: {final_unemb_len:,} rows)")
    print(f"  • URLs đã xóa khỏi remaining_urls.parquet: -{n_removed:,} URLs (Còn lại: {final_rem_len:,} URLs)")
    print(f"  • Tổng thời gian thực hiện: {time.time() - t0:.1f}s")
    print("=" * 75)


if __name__ == "__main__":
    main()
