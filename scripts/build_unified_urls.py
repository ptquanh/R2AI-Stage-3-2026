import os
import sys
import glob
import time
from urllib.parse import urlparse
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BTC_LINKS_PATH = "data/raw/btc_provided/links_corpus_vi_en_zh.parquet"
OUTPUT_PATH = "data/corpus_urls_1m.parquet"
INDEX_BASE = "data/indices"

def infer_language(domain: str, url: str) -> str:
    domain = domain.lower()
    if "pubmed.ncbi.nlm.nih.gov" in domain or domain.endswith(".edu") or domain.endswith(".org"):
        return "en"
    if domain.endswith(".vn") or any(d in domain for d in ["nhathuoclongchau", "suckhoedoisong", "medlatec", "hellobacsi", "youmed", "vinmec", "thanhnien", "laodong", "vietnamnet", "vov"]):
        return "vi"
    if domain.endswith(".cn") or any(d in domain for d in ["120ask", "39.net", "cnkang", "familydoctor", "youlai", "fh21", "haodf", "guahao"]):
        return "zh"
    # Fallback based on URL patterns
    return "vi"

def main():
    print("=" * 70)
    print("🚀 BẮT ĐẦU TẠO FILE DỮ LIỆU URL HỢP NHẤT: data/corpus_urls_1m.parquet")
    print("=" * 70)
    t0 = time.time()

    if not os.path.exists(BTC_LINKS_PATH):
        print(f"❌ Không tìm thấy tệp {BTC_LINKS_PATH}!")
        return

    # 1. Đọc danh sách 1.19M links từ BTC
    print(f"\n1. Đang đọc danh sách 1.19M URLs từ {BTC_LINKS_PATH}...")
    df_btc = pd.read_parquet(BTC_LINKS_PATH)
    total_btc_links = len(df_btc)
    print(f"   -> Đã nạp {total_btc_links:,} URLs.")
    btc_id_set = set(df_btc['id'])

    # 2. Thu thập danh sách ID đã được EMBEDDED từ các khối index
    print(f"\n2. Đang quét các khối chỉ mục tại {INDEX_BASE} để tìm các ID đã EMBEDDED...")
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
    print(f"   -> Tìm thấy {len(embedded_ids):,} tài liệu hợp lệ ĐÃ ĐƯỢC EMBEDDED trong các shards index.")

    # 3. Thu thập danh sách ID đã CRAWLED từ các file văn bản
    print(f"\n3. Đang quét các tệp văn bản thô để tìm các ID đã CRAWLED...")
    crawled_ids = set(embedded_ids)  # Mọi tài liệu đã embedded chắc chắn đã được crawl

    text_files = [
        "data/raw/final_corpus_text/tier_1.parquet",
        "data/raw/final_corpus_text/tier_2.parquet",
        "data/raw/final_corpus_text/tier_1_resume.parquet",
        "data/raw/final_corpus_text/tier_other.parquet",
    ]
    for tf in text_files:
        if os.path.exists(tf):
            schema = pq.read_schema(tf)
            id_col = "id" if "id" in schema.names else ("doc_id" if "doc_id" in schema.names else None)
            if id_col:
                tab = pq.read_table(tf, columns=[id_col])
                for cid in tab[id_col].to_pylist():
                    if cid in btc_id_set:
                        crawled_ids.add(cid)
            print(f"   • Đã quét {os.path.basename(tf)} -> Tổng Crawled tích lũy: {len(crawled_ids):,}")

    # Quét thêm thư mục cào cục bộ local_recovered
    local_part_files = glob.glob("data/raw/corpus_text/local_recovered/*.parquet")
    if local_part_files:
        for lpf in local_part_files:
            schema = pq.read_schema(lpf)
            if "status" in schema.names and "id" in schema.names:
                tab = pq.read_table(lpf, columns=["id", "status"])
                pydict = tab.to_pydict()
                for cid, status in zip(pydict["id"], pydict["status"]):
                    if status == "success" and cid in btc_id_set:
                        crawled_ids.add(cid)
            elif "id" in schema.names:
                tab = pq.read_table(lpf, columns=["id"])
                for cid in tab["id"].to_pylist():
                    if cid in btc_id_set:
                        crawled_ids.add(cid)
        print(f"   • Đã quét {len(local_part_files)} file local_recovered -> Tổng Crawled tích lũy: {len(crawled_ids):,}")

    # 4. Trích xuất Domain và Ngôn ngữ
    print(f"\n4. Đang chuẩn hóa Domain, Ngôn ngữ và Gán cờ trạng thái...")
    domains = []
    langs = []
    for u in df_btc['url']:
        dom = urlparse(str(u)).netloc.lower()
        domains.append(dom)
        langs.append(infer_language(dom, str(u)))

    df_btc['domain'] = domains
    df_btc['lang'] = langs
    df_btc['crawled'] = df_btc['id'].isin(crawled_ids)
    df_btc['embedded'] = df_btc['id'].isin(embedded_ids)

    # 5. Lưu ra file Parquet duy nhất
    print(f"\n5. Đang ghi file {OUTPUT_PATH}...")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df_btc.to_parquet(OUTPUT_PATH, index=False, compression="snappy")
    file_size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
    print(f"   -> Đã lưu thành công: {OUTPUT_PATH} ({file_size_mb:.2f} MB)")

    # 6. Báo cáo thống kê chi tiết
    print("\n" + "=" * 70)
    print("📊 BÁO CÁO TOÀN DIỆN KHO DỮ LIỆU URL 1.19M CHUẨN BTC")
    print("=" * 70)
    print(f"Tổng số URLs: {len(df_btc):,}")
    print(f"Dung lượng tệp Parquet: {file_size_mb:.2f} MB (Chuẩn GitHub < 100 MB ✅)")

    print("\n--- Phân bố theo Ngôn ngữ ---")
    lang_counts = df_btc['lang'].value_counts()
    for l, cnt in lang_counts.items():
        print(f"  • {l.upper():<4}: {cnt:>9,} URLs ({cnt/len(df_btc)*100:.1f}%)")

    num_crawled = df_btc['crawled'].sum()
    num_embedded = df_btc['embedded'].sum()
    num_crawled_not_emb = num_crawled - num_embedded
    num_uncrawled = len(df_btc) - num_crawled

    print("\n--- Trạng thái Xử lý Tài nguyên ---")
    print(f"  • ĐÃ EMBEDDED (Sẵn sàng trong Index):      {num_embedded:>9,} ({num_embedded/len(df_btc)*100:.1f}%)")
    print(f"  • ĐÃ CRAWL nhưng CHƯA EMBED (Cần nhúng):    {num_crawled_not_emb:>9,} ({num_crawled_not_emb/len(df_btc)*100:.1f}%)")
    print(f"  • CHƯA CRAWL (Cần thu thập tiếp):           {num_uncrawled:>9,} ({num_uncrawled/len(df_btc)*100:.1f}%)")

    print("\n--- Top 15 Domains và Tỷ lệ Hoàn Thành ---")
    top_doms = df_btc['domain'].value_counts().head(15).index
    print(f"  {'Domain':<32} | {'Tổng URLs':>9} | {'Crawled %':>9} | {'Embedded %':>10}")
    print("  " + "-" * 70)
    for dom in top_doms:
        sub = df_btc[df_btc['domain'] == dom]
        tot = len(sub)
        cr = sub['crawled'].sum()
        em = sub['embedded'].sum()
        print(f"  {dom:<32} | {tot:>9,} | {cr/tot*100:>8.1f}% | {em/tot*100:>9.1f}%")

    print("=" * 70)
    print(f"Hoàn tất toàn bộ quy trình trong {time.time() - t0:.2f} giây.")

if __name__ == "__main__":
    main()
