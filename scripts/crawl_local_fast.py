import os
import sys
import glob
import time
import random
import asyncio
import unicodedata
import argparse
import collections
import itertools
import threading
import re
import json
from urllib.parse import urlparse
import pandas as pd
import trafilatura
from tqdm.asyncio import tqdm
from curl_cffi import requests
import concurrent.futures

sys.stdout.reconfigure(encoding='utf-8')

# ======================================================================
# 1. BỘ LỌC NỘI DUNG (URL BLACKLIST & MEDICAL KEYWORDS)
# ======================================================================
URL_BLACKLIST = [
    "/rao-vat/", "/san-pham/", "/gio-hang/", "/mua-ban/", "/cart/",
    "/checkout/", "/shop/", "/store/", "shopee", "lazada", "tiki"
]

MEDICAL_KEYWORDS = [
    "bác sĩ", "bệnh", "triệu chứng", "điều trị", "thuốc", "sức khỏe", "ung thư", "viêm", "đau", "chẩn đoán", "huyết áp", "phẫu thuật",
    "khám", "y tế", "bệnh nhân", "phòng khám", "dược", "tim mạch", "tiểu đường", "dinh dưỡng", "xét nghiệm", "nhi khoa", "sản khoa",
    "thần kinh", "cơ xương khớp", "hô hấp", "tiêu hóa", "đông y", "nam dược", "thảo dược", "vắc-xin", "vaccine", "chữa trị",
    "phòng ngừa", "cấp cứu", "lâm sàng", "cơ địa", "miễn dịch", "nhiễm trùng", "virus", "vi khuẩn", "hội chứng", "mãn tính", "cấp tính",
    "医院", "医生", "治疗", "疾病", "症状", "药", "患者", "健康", "诊断", "手术", "科",
    "doctor", "disease", "symptom", "treatment", "medicine", "health", "cancer", "pain", "diagnosis", "blood pressure", "surgery", "clinic",
    "medical", "patient", "hospital", "pharmacy", "syndrome", "infection", "therapy"
]

def check_layer_1(url: str):
    u = url.lower()
    for b in URL_BLACKLIST:
        if b in u: return f"Blacklist: {b}"
    return None

def check_layer_2(text: str):
    t = unicodedata.normalize("NFC", text.lower())
    for kw in MEDICAL_KEYWORDS:
        if unicodedata.normalize("NFC", kw) in t:
            return None
    return "No medical keyword"

# ======================================================================
# 2. PROXY POOL (XOAY VÒNG ROUND-ROBIN 1 HOẶC 2 PROXY)
# ======================================================================
class FastProxyPool:
    def __init__(self, proxy_list):
        self.proxies = [p for p in proxy_list if p]
        self._cycle = itertools.cycle(self.proxies) if self.proxies else None
        self._lock = threading.Lock()

    def get_proxy(self):
        if not self._cycle:
            return None
        with self._lock:
            return next(self._cycle)

    def __len__(self):
        return len(self.proxies)

# ======================================================================
# 3. DOMAIN CIRCUIT BREAKER (AUTO-SKIP DOMAINS CHẾT / BLOCK CỨNG)
# ======================================================================
class DomainTracker:
    def __init__(self, failure_threshold: int = 15):
        self.threshold = failure_threshold
        self.lock = threading.Lock()
        self.stats = collections.defaultdict(lambda: {'fail': 0, 'consecutive_fails': 0, 'success': 0, 'skipped': False})

    def get_domain(self, url: str) -> str:
        try:
            return urlparse(url).netloc.lower()
        except Exception:
            return ""

    def should_skip(self, domain: str) -> bool:
        if not domain or self.threshold <= 0:
            return False
        with self.lock:
            return self.stats[domain]['skipped']

    def record_success(self, domain: str):
        if not domain:
            return
        with self.lock:
            self.stats[domain]['success'] += 1
            self.stats[domain]['consecutive_fails'] = 0

    def record_failure(self, domain: str):
        if not domain or self.threshold <= 0:
            return
        with self.lock:
            data = self.stats[domain]
            if data['skipped']:
                return
            data['fail'] += 1
            data['consecutive_fails'] += 1
            if data['consecutive_fails'] >= self.threshold:
                data['skipped'] = True
                print(f"\n🚫 [Domain Circuit Breaker] Domain '{domain}' đã thất bại {data['consecutive_fails']} lần liên tiếp -> TỰ ĐỘNG SKIP TOÀN BỘ URL CÒN LẠI!")

def decode_html_bytes(content: bytes, domain: str, default_text: str = "") -> str:
    if any(d in domain for d in ['cnkang.com', 'wujue.com', 'zydcd.com', 'a-hospital.com']):
        try:
            cand = content.decode('gb18030')
            if cand.count('\ufffd') < 5:
                return cand
        except Exception:
            pass

    try:
        cand = content.decode('utf-8')
        if cand.count('\ufffd') < 5:
            return cand
    except Exception:
        pass

    try:
        cand_gb = content.decode('gb18030', errors='ignore')
        return cand_gb
    except Exception:
        pass

    return default_text

# ======================================================================
# 4. WORKER CRAWL MỘT URL
# ======================================================================
def fetch_one_sync(row: dict, proxy_pool: FastProxyPool, max_retries: int, domain_tracker: DomainTracker):
    url = row['url']
    row_id = row['id']
    res = {'id': row_id, 'url': url, 'text': None, 'status': None, 'reason': '', 'dropped_at_layer': None}

    domain = domain_tracker.get_domain(url)
    if domain_tracker.should_skip(domain):
        # Đánh dấu error để KHÔNG ghi vào file parquet và không mất URL
        res['status'] = 'error'
        res['reason'] = f"Domain Blocked/Skipped ({domain})"
        return res

    l1 = check_layer_1(url)
    if l1:
        res['status'] = 'dropped'
        res['dropped_at_layer'] = 1
        res['reason'] = l1
        return res

    # 0. Xử lý chuyên biệt cho pubmed.ncbi.nlm.nih.gov qua Europe PMC Open API
    if "pubmed.ncbi.nlm.nih.gov" in domain or "pubmed.ncbi.nlm.nih.gov" in url:
        m = re.search(r'/(\d+)/?', url)
        if m:
            pmid = m.group(1)
            api_url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:{pmid}%20SRC:MED&format=json&resultType=core"
            try:
                api_req = requests.get(api_url, timeout=12)
                if api_req.status_code == 200:
                    data = api_req.json()
                    items = data.get('resultList', {}).get('result', [])
                    if items:
                        title = items[0].get('title', '')
                        abstract = items[0].get('abstractText', '')
                        full_text = f"{title}\n\n{abstract}".strip() if abstract else (title.strip() if title else "")
                        if full_text and len(full_text) > 40:
                            res['text'] = full_text
                            res['status'] = 'success'
                            res['reason'] = 'Success (PubMed Europe PMC)'
                            domain_tracker.record_success(domain)
                            return res
                        else:
                            res['status'] = 'dropped'
                            res['dropped_at_layer'] = 2
                            res['reason'] = "No abstract in PubMed article"
                            return res
                    else:
                        res['status'] = 'dropped'
                        res['dropped_at_layer'] = 1
                        res['reason'] = "PMID not found in Europe PMC"
                        return res
            except Exception as e:
                res['status'] = 'error'
                res['reason'] = f"Europe PMC error: {str(e)[:40]}"
                domain_tracker.record_failure(domain)
                return res

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
            
    for attempt in range(max_retries + 1):
        proxy_url = proxy_pool.get_proxy()
        proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None

        try:
            req = requests.get(url, proxies=proxies, headers=headers, timeout=15, impersonate="chrome120")
            html = decode_html_bytes(req.content, domain, req.text)
            
            # 1. Kiểm tra mã lỗi 404 Not Found (Trang đã bị xóa vĩnh viễn)
            if req.status_code == 404 or "<title>404 Not Found</title>" in html:
                res['status'] = 'dropped'
                res['dropped_at_layer'] = 1
                res['reason'] = "HTTP 404 Not Found"
                break

            # 2. Kiểm tra mã lỗi 429 Too Many Requests / Rate Limited
            if req.status_code == 429 or "too many requests" in html.lower() or "rate limit" in html.lower():
                res['reason'] = "429 Too Many Requests"
                if attempt < max_retries:
                    time.sleep(2.0)
                    continue
                else:
                    break

            # 3. Kiểm tra mã lỗi 403 Forbidden do Nginx/Server
            if req.status_code == 403 and "nginx" in html.lower() and "forbidden" in html.lower():
                res['reason'] = "HTTP 403 Forbidden (Nginx Block)"
                break

            # 4. Kiểm tra dấu hiệu Cloudflare / Anti-bot Block / Turnstile / Captcha
            is_cf = (
                "cf-browser-verification" in html or 
                "Just a moment..." in html or 
                "Attention Required!" in html or 
                "owner of this website" in html.lower() or
                "turnstile" in html.lower() or
                "滑动拼图" in html or
                "拼图验证" in html or
                "人机验证" in html or
                (req.status_code in [403, 503] and ("cloudflare" in html.lower() or "turnstile" in html.lower() or "waf" in html.lower()))
            )
            
            if is_cf:
                res['reason'] = "Anti-bot / Captcha Block"
                if len(proxy_pool) > 1 and attempt < max_retries:
                    time.sleep(1.0)
                    continue
                else:
                    break
                
            text = trafilatura.extract(html, include_links=False, include_images=False)
            if text and len(text.strip()) > 80:
                lower_text = text.lower()

                # Kiểm tra thông báo lỗi hệ thống ẩn bên trong nội dung văn bản
                if "too many requests" in lower_text or "rate limit" in lower_text:
                    res['reason'] = "429 Too Many Requests"
                    if attempt < max_retries:
                        time.sleep(2.0)
                        continue
                    else:
                        break

                if "owner of this website" in lower_text or "cf-browser-verification" in lower_text or "just a moment..." in lower_text or "attention required" in lower_text:
                    res['reason'] = "Cloudflare Block/Challenge"
                    if attempt < max_retries:
                        time.sleep(15.5 if len(proxy_pool) == 1 else 1.0)
                        continue
                    else:
                        break

                if "403 forbidden" in lower_text or "access denied" in lower_text:
                    res['reason'] = "HTTP 403 Forbidden"
                    break

                # Văn bản thực sự -> Kiểm tra từ khóa y tế (Layer 2)
                l2 = check_layer_2(text)
                if l2:
                    res['status'] = 'dropped'
                    res['dropped_at_layer'] = 2
                    res['reason'] = f"{l2} (Text snippet: {text[:30]}...)"
                else:
                    res['text'] = text
                    res['status'] = 'success'
                    res['reason'] = 'Success'
                break
            else:
                # Text rỗng hoặc quá ngắn (<80 ký tự)
                is_turnstile = "turnstile" in html.lower() or "challenge" in html.lower()
                if is_turnstile:
                    res['reason'] = "Cloudflare Turnstile"
                    if attempt < max_retries:
                        if len(proxy_pool) == 1:
                            time.sleep(15.5)
                        else:
                            time.sleep(1.0)
                        continue
                    else:
                        break
                else:
                    res['reason'] = 'Empty text'
                    if attempt < max_retries:
                        time.sleep(1.5)
                        continue
                    else:
                        break
        except Exception as e:
            res['reason'] = type(e).__name__
            # Fallback: nếu proxy lỗi kết nối, thử lại trực tiếp (direct) không qua proxy
            if proxies:
                try:
                    req_direct = requests.get(url, headers=headers, timeout=12, impersonate="chrome120")
                    if req_direct.status_code == 200:
                        html_d = decode_html_bytes(req_direct.content, domain, req_direct.text)
                        text_d = trafilatura.extract(html_d, include_links=False, include_images=False)
                        if text_d and len(text_d.strip()) > 80:
                            l2_d = check_layer_2(text_d)
                            if not l2_d:
                                res['text'] = text_d
                                res['status'] = 'success'
                                res['reason'] = 'Success (Direct Fallback)'
                                break
                except:
                    pass
            if attempt < max_retries:
                time.sleep(1.5)
                continue
            else:
                break

    # Nếu hết lượt retry mà vẫn chưa success/dropped -> gán status = 'error'
    if res['status'] is None:
        res['status'] = 'error'

    # Ghi nhận domain stats
    if res['status'] == 'success' or (res['status'] == 'dropped' and res['dropped_at_layer'] == 2):
        domain_tracker.record_success(domain)
    elif res['status'] == 'error' or (res['status'] == 'dropped' and '404' in res['reason']):
        domain_tracker.record_failure(domain)

    if res['status'] != 'success':
        print(f"\n[Debug] URL: {url} | Status: {res['status']} | Reason: {res['reason']}")

    return res

# ======================================================================
# 5. ASYNC BATCH RUNNER
# ======================================================================
async def crawl_batch(df_batch, sem, delay, proxy_pool, max_retries, pbar, executor, domain_tracker):
    loop = asyncio.get_running_loop()
    async def process_row(row):
        async with sem:
            domain = domain_tracker.get_domain(row['url'])
            if not domain_tracker.should_skip(domain) and delay > 0:
                await asyncio.sleep(random.uniform(delay * 0.7, delay * 1.3))
            return await loop.run_in_executor(executor, fetch_one_sync, row, proxy_pool, max_retries, domain_tracker)
    tasks = [process_row(row) for _, row in df_batch.iterrows()]
    results = []
    success_count = 0
    for fut in asyncio.as_completed(tasks):
        r = await fut
        results.append(r)
        if r['status'] == 'success':
            success_count += 1
        pbar.update(1)
        pbar.set_postfix({'success': success_count, 'status': r['status'] if r['status'] else r['reason']})
    return results

def get_already_crawled_ids(output_dir):
    files = glob.glob(os.path.join(output_dir, "*.parquet"))
    crawled_ids = set()
    for f in files:
        try:
            df = pd.read_parquet(f, columns=['id', 'status'])
            crawled_ids.update(df[df['status'].isin(['success', 'dropped'])]['id'].tolist())
        except: pass
    return crawled_ids

# ======================================================================
# 6. MAIN CONTROLLER
# ======================================================================
async def main_async(args, proxy_pool, domain_tracker):
    print("=" * 70)
    print("🚀 FAST REQUESTS CRAWLER (ROTATING PROXY POOL)")
    print("=" * 70)
    print(f"📌 Input file:     {args.input}")
    print(f"📌 Output dir:     {args.output_dir}")
    print(f"📌 Proxy Mode:     {args.proxy_mode.upper()} ({len(proxy_pool)} proxy active)")
    for i, p in enumerate(proxy_pool.proxies, 1):
        print(f"   [{i}] {p.split('@')[-1]}")
    print(f"📌 Concurrency:    {args.concurrency}")
    print(f"📌 Delay jitter:   {args.delay}s")
    print(f"📌 Max Retries:    {args.max_retries}")
    print(f"📌 Domain Limit:   {args.domain_fail_limit}")
    print(f"📌 Batch size:     {args.batch_size}")
    if args.limit:
        print(f"📌 Limit URLs:     {args.limit:,}")
    print("=" * 70)
    
    os.makedirs(args.output_dir, exist_ok=True)
    df_rem = pd.read_parquet(args.input)
    print(f"\n1. Đang đọc danh sách URL cần cào...")
    print(f"   - Tổng URLs trong input: {len(df_rem):,}")
    if "crawled" in df_rem.columns:
        already_c = df_rem["crawled"].sum()
        df_rem = df_rem[~df_rem["crawled"]].copy()
        print(f"   - Tự động bỏ qua {already_c:,} URLs đã có trạng thái crawled=True. Còn lại: {len(df_rem):,} URLs cần cào.")

    if args.domain:
        is_target = df_rem['url'].str.contains(args.domain, case=False, na=False)
        df_target = pd.concat([df_rem[is_target], df_rem[~is_target]])
        print(f"   - Ưu tiên domain: {args.domain} ({is_target.sum():,} URLs)")
    else:
        df_target = df_rem.copy()

    crawled_ids = get_already_crawled_ids(args.output_dir)
    if crawled_ids:
        df_target = df_target[~df_target['id'].isin(crawled_ids)].copy()
        print(f"   - Bỏ qua {len(crawled_ids):,} IDs đã cào. Còn lại: {len(df_target):,} URLs")

    if args.limit and args.limit > 0 and len(df_target) > args.limit:
        df_target = df_target.head(args.limit).copy()
        print(f"   - Giới hạn lượt này: {len(df_target):,} URLs")

    if len(df_target) == 0:
        print("🎉 Không còn URL nào cần cào. Hoàn tất!")
        return

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency)
    sem = asyncio.Semaphore(args.concurrency)
    num_batches = (len(df_target) // args.batch_size) + (1 if len(df_target) % args.batch_size > 0 else 0)

    existing_parts = [
        int(os.path.basename(f).replace("local_part_", "").replace(".parquet", ""))
        for f in glob.glob(os.path.join(args.output_dir, "local_part_*.parquet"))
        if os.path.basename(f).replace("local_part_", "").replace(".parquet", "").isdigit()
    ]
    start_part = max(existing_parts) + 1 if existing_parts else 0

    total_success = 0
    total_processed = 0
    print(f"\n2. Bắt đầu cào ({num_batches} batches, từ part {start_part:04d})...")

    with tqdm(total=len(df_target), desc="Crawling", unit="URL") as pbar:
        for b_idx in range(num_batches):
            part_no = start_part + b_idx
            out_file = os.path.join(args.output_dir, f"local_part_{part_no:04d}.parquet")
            s = b_idx * args.batch_size
            e = min(s + args.batch_size, len(df_target))
            batch_df = df_target.iloc[s:e]
            
            batch_results = await crawl_batch(batch_df, sem, args.delay, proxy_pool, args.max_retries, pbar, executor, domain_tracker)
            df_res = pd.DataFrame(batch_results)
            
            # Chỉ lưu những URL thành công hoặc được phân loại là rác (dropped)
            df_valid = df_res[df_res['status'].isin(['success', 'dropped'])]
            succ = (df_res['status'] == 'success').sum()

            if len(df_valid) > 0: 
                df_valid.to_parquet(out_file, index=False)
                
            total_success += succ
            total_processed += len(df_res)
            
    executor.shutdown(wait=False)

    print("\n" + "=" * 70)
    print("🎉 HOÀN THÀNH PHIÊN CÀO FAST!")
    print(f"   - Tổng URL đã xử lý: {total_processed:,}")
    print(f"   - Thành công: {total_success:,} ({total_success/total_processed*100:.1f}%)" if total_processed > 0 else "")
    print(f"   - Dữ liệu lưu tại: {args.output_dir}")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description="Fast Asynchronous Requests Crawler (Multi-Proxy Rotation)")
    parser.add_argument("--input", default="data/remaining_urls.parquet")
    parser.add_argument("--output-dir", default="data/raw/corpus_text/local_recovered")
    parser.add_argument("--domain", default=None)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--concurrency", type=int, default=40)
    parser.add_argument("--delay", type=float, default=0.0)
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--proxy-mode", choices=["both", "15s", "240s", "none"], default="none",
                        help="Chế độ proxy: 'both' (xoay vòng cả 2 proxy), '15s' (chỉ proxy 15s), '240s' (chỉ proxy 240s), 'none' (Direct IP)")
    parser.add_argument("--proxy", default=None, help="Chỉ định custom proxy URL (ghi đè --proxy-mode)")
    parser.add_argument("--proxy-file", default=None, help="Đọc danh sách proxy từ file txt (1 proxy / dòng)")
    parser.add_argument("--domain-fail-limit", type=int, default=15, help="Tự động skip domain sau N lần fail liên tiếp (default: 15)")
    args = parser.parse_args()

    # Xử lý danh sách Proxy
    proxy_list = []
    if args.proxy_file and os.path.exists(args.proxy_file):
        with open(args.proxy_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = [l.strip() for l in f if l.strip()]
        proxy_list = list(dict.fromkeys(lines))
        print(f"🌐 [Proxy] Đã nạp {len(proxy_list)} proxy từ {args.proxy_file}")
    elif args.proxy:
        proxy_list = [args.proxy]
        print(f"🌐 [Proxy] Sử dụng Custom Proxy chỉ định: {args.proxy.split('@')[-1]}")
    elif args.proxy_mode == "none":
        print("🌐 [Proxy] Chế độ DIRECT IP (Không dùng Proxy)")
    else:
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        try:
            from src.config import settings
            p15 = getattr(settings, "PROXY_15S", None)
            p240 = getattr(settings, "PROXY_240S", None)

            if args.proxy_mode == "both":
                if p15: proxy_list.append(p15)
                if p240: proxy_list.append(p240)
            elif args.proxy_mode == "15s":
                if p15: proxy_list.append(p15)
            elif args.proxy_mode == "240s":
                if p240: proxy_list.append(p240)
        except Exception as e:
            print(f"⚠️ Không thể đọc proxy từ settings: {e}")

    proxy_pool = FastProxyPool(proxy_list)
    domain_tracker = DomainTracker(failure_threshold=args.domain_fail_limit)

    asyncio.run(main_async(args, proxy_pool, domain_tracker))

if __name__ == "__main__":
    main()
