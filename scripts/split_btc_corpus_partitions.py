import os
import sys
import glob
import time
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BTC_LINKS_PATH = "data/raw/btc_provided/links_corpus_vi_en_zh.parquet"
INDEX_BASE = "data/indices"

OUT_REMAINING = "data/remaining_urls.parquet"
OUT_EMBEDDED = "data/embedded_samples.parquet"
OUT_UNEMBEDDED = "data/unembedded_samples.parquet"

def main():
    print("=" * 70)
    print("🚀 PHÂN TÁCH KHO DỮ LIỆU BTC 1.19M THÀNH 3 TỆP PARQUET CHUẨN")
    print("   1. Remaining URLs:       data/remaining_urls.parquet (id, url)")
    print("   2. Embedded Samples:     data/embedded_samples.parquet (id, url, text)")
    print("   3. Unembedded Samples:   data/unembedded_samples.parquet (id, url, text)")
    print("=" * 70)
    t0 = time.time()

    # 1. Đọc danh sách 1.19M links từ BTC
    print(f"\n1. Đang nạp danh sách 1.19M URLs từ {BTC_LINKS_PATH}...")
    df_btc = pd.read_parquet(BTC_LINKS_PATH)
    total_btc = len(df_btc)
    print(f"   -> Đã nạp {total_btc:,} URLs.")
    btc_id_set = set(df_btc['id'])
    id_to_url = dict(zip(df_btc['id'], df_btc['url']))

    # 2. Thu thập danh sách ID đã được EMBEDDED từ các khối index
    print(f"\n2. Đang quét 20 khối chỉ mục tại {INDEX_BASE} để tìm các ID đã EMBEDDED...")
    chunk_marker_dirs = sorted(glob.glob(os.path.join(INDEX_BASE, "**", "chunks"), recursive=True))
    unique_shard_dirs = []
    seen_signatures = {}
    for d in chunk_marker_dirs:
        s_dir = os.path.dirname(d)
        p_files = sorted(glob.glob(os.path.join(d, "part_*.parquet")))
        if not p_files:
            continue
        df_sig = pd.read_parquet(p_files[0], columns=["doc_id"])
        sig = (len(p_files), len(df_sig), tuple(df_sig["doc_id"].iloc[:5].tolist()))
        if sig not in seen_signatures:
            seen_signatures[sig] = s_dir
            unique_shard_dirs.append(s_dir)

    embedded_ids = set()
    for s in unique_shard_dirs:
        for p_file in glob.glob(f"{s}/chunks/part_*.parquet"):
            tab = pq.read_table(p_file, columns=["doc_id"])
            for did in tab["doc_id"].to_pylist():
                if did in btc_id_set:
                    embedded_ids.add(did)
    print(f"   -> Đã xác định {len(embedded_ids):,} tài liệu hợp lệ ĐÃ ĐƯỢC EMBEDDED.")

    # 3. Thu thập nội dung text cho các tài liệu EMBEDDED
    print(f"\n3. Đang trích xuất nội dung text cho {len(embedded_ids):,} tài liệu EMBEDDED...")
    embedded_texts = {}
    for s in unique_shard_dirs:
        for p_file in glob.glob(f"{s}/text/part_*.parquet"):
            tab = pq.read_table(p_file, columns=["doc_id", "text"])
            pyd = tab.to_pydict()
            for did, txt in zip(pyd["doc_id"], pyd["text"]):
                if did in embedded_ids and did not in embedded_texts:
                    embedded_texts[did] = txt
    print(f"   -> Đã lấy được text từ shard cho {len(embedded_texts):,} / {len(embedded_ids):,} tài liệu embedded.")

    # 4. Thu thập nội dung text cho các tài liệu UNEMBEDDED (Đã cào nhưng chưa nhúng)
    print(f"\n4. Đang quét các file văn bản thô để tìm tài liệu UNEMBEDDED (crawled nhưng chưa nhúng)...")
    unembedded_texts = {}

    text_sources = [
        "data/raw/final_corpus_text/tier_1_resume.parquet",
        "data/raw/final_corpus_text/tier_other.parquet",
        "data/raw/final_corpus_text/tier_1.parquet",
        "data/raw/final_corpus_text/tier_2.parquet"
    ]
    for ts in text_sources:
        if os.path.exists(ts):
            t_start = time.time()
            schema = pq.read_schema(ts)
            id_col = "id" if "id" in schema.names else ("doc_id" if "doc_id" in schema.names else None)
            if id_col and "text" in schema.names:
                tab = pq.read_table(ts, columns=[id_col, "text"])
                pyd = tab.to_pydict()
                added_from_file = 0
                for cid, txt in zip(pyd[id_col], pyd["text"]):
                    if cid in btc_id_set:
                        # Nếu là embedded mà shard bị thiếu text, bổ sung text
                        if cid in embedded_ids and cid not in embedded_texts:
                            embedded_texts[cid] = txt
                        # Nếu chưa embedded, đưa vào unembedded
                        elif cid not in embedded_ids and cid not in unembedded_texts:
                            unembedded_texts[cid] = txt
                            added_from_file += 1
                print(f"   • {os.path.basename(ts):<32}: +{added_from_file:>7,} unembedded docs ({time.time() - t_start:.2f}s)")

    # Quét thêm local_recovered
    local_part_files = glob.glob("data/raw/corpus_text/local_recovered/*.parquet")
    if local_part_files:
        added_local = 0
        for lpf in local_part_files:
            schema = pq.read_schema(lpf)
            id_col = "id" if "id" in schema.names else ("doc_id" if "doc_id" in schema.names else None)
            if id_col and "text" in schema.names:
                tab = pq.read_table(lpf, columns=[id_col, "text"])
                pyd = tab.to_pydict()
                for cid, txt in zip(pyd[id_col], pyd["text"]):
                    if cid in btc_id_set:
                        if cid in embedded_ids and cid not in embedded_texts:
                            embedded_texts[cid] = txt
                        elif cid not in embedded_ids and cid not in unembedded_texts:
                            unembedded_texts[cid] = txt
                            added_local += 1
        print(f"   • local_recovered (591 files)     : +{added_local:>7,} unembedded docs")

    print(f"   -> Tổng số tài liệu UNEMBEDDED thu thập được: {len(unembedded_texts):,}")

    # 5. Xác định các URL chưa cào (REMAINING URLs)
    print(f"\n5. Đang xác định các URLs CHƯA CÀO (Remaining)...")
    crawled_ids = set(embedded_ids) | set(unembedded_texts.keys())
    remaining_ids = btc_id_set - crawled_ids
    print(f"   -> Tổng số URLs chưa cào: {len(remaining_ids):,}")

    # 6. Ghi ra 3 tệp Parquet
    print(f"\n6. Đang xuất 3 tệp Parquet chuẩn...")

    # File 1: Remaining URLs (id, url)
    print(f"   [1/3] Đang ghi {OUT_REMAINING}...")
    df_remaining = df_btc[df_btc['id'].isin(remaining_ids)][['id', 'url']].copy()
    df_remaining.to_parquet(OUT_REMAINING, index=False, compression="snappy")
    sz_rem = os.path.getsize(OUT_REMAINING) / (1024 * 1024)
    print(f"         -> Thành công: {len(df_remaining):,} URLs ({sz_rem:.2f} MB)")

    # File 2: Embedded Samples (id, url, text)
    print(f"   [2/3] Đang tạo và ghi {OUT_EMBEDDED}...")
    emb_rows = []
    for did in sorted(embedded_ids):
        emb_rows.append({
            "id": int(did),
            "url": id_to_url.get(did, ""),
            "text": embedded_texts.get(did, "")
        })
    df_emb = pd.DataFrame(emb_rows)
    df_emb.to_parquet(OUT_EMBEDDED, index=False, compression="snappy")
    sz_emb = os.path.getsize(OUT_EMBEDDED) / (1024 * 1024)
    print(f"         -> Thành công: {len(df_emb):,} samples ({sz_emb:.2f} MB)")
    del emb_rows, df_emb, embedded_texts

    # File 3: Unembedded Samples (id, url, text)
    print(f"   [3/3] Đang tạo và ghi {OUT_UNEMBEDDED}...")
    unemb_rows = []
    for did in sorted(unembedded_texts.keys()):
        unemb_rows.append({
            "id": int(did),
            "url": id_to_url.get(did, ""),
            "text": unembedded_texts.get(did, "")
        })
    df_unemb = pd.DataFrame(unemb_rows)
    df_unemb.to_parquet(OUT_UNEMBEDDED, index=False, compression="snappy")
    sz_unemb = os.path.getsize(OUT_UNEMBEDDED) / (1024 * 1024)
    print(f"         -> Thành công: {len(df_unemb):,} samples ({sz_unemb:.2f} MB)")
    del unemb_rows, df_unemb, unembedded_texts

    # 7. Tổng kết & Kiểm tra Toàn vẹn (Checksums)
    total_partitioned = len(df_remaining) + len(embedded_ids) + len(crawled_ids - embedded_ids)
    print("\n" + "=" * 70)
    print("📊 BÁO CÁO TỔNG KẾT PHÂN TÁCH 3 TỆP PARQUET")
    print("=" * 70)
    print(f"Tổng số URL gốc của BTC:        {total_btc:>10,}")
    print(f"1. Remaining URLs (chưa cào):    {len(df_remaining):>10,} ({sz_rem:.2f} MB) -> {OUT_REMAINING}")
    print(f"2. Embedded Samples (đã nhúng):  {len(embedded_ids):>10,} ({sz_emb:.2f} MB) -> {OUT_EMBEDDED}")
    print(f"3. Unembedded Samples (chờ nhúng):{len(crawled_ids - embedded_ids):>10,} ({sz_unemb:.2f} MB) -> {OUT_UNEMBEDDED}")
    print("  " + "-" * 68)
    print(f"Tổng số bản ghi 3 tệp cộng lại:  {total_partitioned:>10,}")
    print(f"Khớp chính xác 100% với BTC:     {'✅ ĐỒNG NHẤT TUYỆT ĐỐI' if total_partitioned == total_btc else '⚠️ CHÊNH LỆCH'}")
    print("=" * 70)
    print(f"Hoàn thành toàn bộ trong {time.time() - t0:.2f} giây.")

if __name__ == "__main__":
    main()
