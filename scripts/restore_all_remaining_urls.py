"""
Khôi phục toàn bộ các URL còn lại của BTC (92,304 URLs) vào data/remaining_urls.parquet.
Nguyên tắc:
1. Mốc chuẩn: data/raw/btc_provided/links_corpus_vi_en_zh.parquet (1,220,598 URLs).
2. Loại trừ tất cả các ID đã có trong:
   - data/embedded_samples.parquet (1,156,349 docs)
   - data/unembedded_samples.parquet (16,931 docs)
3. Tập hợp còn lại chính xác là 92,304 URLs (bao gồm 14,591 URLs hiện có + 77,713 URLs bị sót).
4. Sao lưu an toàn data/remaining_urls.parquet.bak trước khi ghi.
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

BTC_LINKS_PATH = DATA_DIR / "raw" / "btc_provided" / "links_corpus_vi_en_zh.parquet"
EMB_PATH = DATA_DIR / "embedded_samples.parquet"
UNEMB_PATH = DATA_DIR / "unembedded_samples.parquet"
REM_PATH = DATA_DIR / "remaining_urls.parquet"


def main():
    print("=" * 80)
    print("🚀 KHÔI PHỤC TOÀN DIỆN DATA/REMAINING_URLS.PARQUET (CHUẨN 92,304 URLs)")
    print("=" * 80)

    # 1. Đọc BTC links
    print(f"\n[1/4] Đọc mốc chuẩn BTC: {BTC_LINKS_PATH}...")
    df_btc = pd.read_parquet(BTC_LINKS_PATH)
    total_btc = len(df_btc)
    print(f"  • Tổng URLs trong BTC: {total_btc:,}")
    assert total_btc == 1220598, f"Số lượng BTC links không khớp: {total_btc}"

    # 2. Đọc các ID đã cào
    print(f"\n[2/4] Đọc danh sách đã cào từ embedded và unembedded...")
    df_emb = pd.read_parquet(EMB_PATH, columns=["id"])
    df_unemb = pd.read_parquet(UNEMB_PATH, columns=["id"])

    emb_ids = set(df_emb["id"])
    unemb_ids = set(df_unemb["id"])
    crawled_ids = emb_ids.union(unemb_ids)
    print(f"  • Đã cào trong embedded_samples:   {len(emb_ids):,}")
    print(f"  • Đã cào trong unembedded_samples: {len(unemb_ids):,}")
    print(f"  • Tổng số ID đã cào (không trùng): {len(crawled_ids):,}")

    # 3. Lọc các URL chưa cào
    print(f"\n[3/4] Trích xuất toàn bộ URLs chưa cào từ mốc chuẩn BTC...")
    df_remaining_new = df_btc[~df_btc["id"].isin(crawled_ids)][["id", "url"]].copy()
    # Sắp xếp theo ID tăng dần
    df_remaining_new.sort_values(by="id", inplace=True)
    df_remaining_new.reset_index(drop=True, inplace=True)

    n_remaining = len(df_remaining_new)
    print(f"  • Số URLs còn lại thực tế cần cào: {n_remaining:,}")
    assert n_remaining == 92304, f"Số lượng URLs còn lại {n_remaining} != 92,304!"

    # Kiểm tra giao thoa với remaining_urls hiện tại
    if REM_PATH.exists():
        df_rem_curr = pd.read_parquet(REM_PATH)
        n_curr = len(df_rem_curr)
        curr_ids = set(df_rem_curr["id"])
        print(f"  • remaining_urls.parquet hiện tại: {n_curr:,} URLs")
        diff_ids = set(df_remaining_new["id"]) - curr_ids
        print(f"  • Bổ sung thêm các URLs bị sót: +{len(diff_ids):,} URLs")
        assert len(diff_ids) == 77713, f"Số URL sót {len(diff_ids)} != 77,713!"

    # 4. Sao lưu và ghi file
    print(f"\n[4/4] Sao lưu và ghi tệp mới...")
    if REM_PATH.exists():
        bak_file = DATA_DIR / "remaining_urls.parquet.bak_pre_restore"
        shutil.copy2(REM_PATH, bak_file)
        print(f"  ✓ Đã sao lưu bản cũ vào: {bak_file}")

    # Ghi tệp Parquet chuẩn
    tmp_path = REM_PATH.with_suffix(".tmp")
    df_remaining_new.to_parquet(tmp_path, index=False, compression="snappy")
    if os.path.exists(REM_PATH):
        os.remove(REM_PATH)
    os.rename(tmp_path, REM_PATH)

    sz_mb = os.path.getsize(REM_PATH) / (1024 * 1024)
    print(f"  💾 Đã lưu thành công: {REM_PATH} ({n_remaining:,} URLs, {sz_mb:.2f} MB)")

    # Kiểm tra xác thực cuối cùng
    df_verify = pd.read_parquet(REM_PATH)
    v_ids = set(df_verify["id"])
    overlap_emb = v_ids.intersection(emb_ids)
    overlap_unemb = v_ids.intersection(unemb_ids)
    assert len(overlap_emb) == 0, f"Lỗi: Trùng lặp {len(overlap_emb)} ID với embedded_samples!"
    assert len(overlap_unemb) == 0, f"Lỗi: Trùng lặp {len(overlap_unemb)} ID với unembedded_samples!"
    assert len(df_verify) == 92304, f"Lỗi số dòng: {len(df_verify)} != 92,304!"
    assert df_verify["id"].nunique() == 92304, "Lỗi ID không duy nhất!"

    print("\n" + "=" * 80)
    print(f"🎉 KHÔI PHỤC THÀNH CÔNG TOÀN BỘ 92,304 URLs!")
    print(f" • Schema: {df_verify.columns.tolist()}")
    print(f" • Tổng số URLs cần cào: {len(df_verify):,}")
    print(f" • Trùng lặp với embedded: 0")
    print(f" • Trùng lặp với unembedded: 0")
    print("=" * 80)


if __name__ == "__main__":
    main()
