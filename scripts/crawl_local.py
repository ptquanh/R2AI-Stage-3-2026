import os
import sys
import glob
import time
import random
import asyncio
import unicodedata
import argparse
import urllib.request
import collections
import zipfile
from urllib.parse import urlparse
import pandas as pd
import trafilatura
from tqdm.asyncio import tqdm

# Fix urllib3 crash if .env has malformed HTTP_PROXY
if "HTTP_PROXY" in os.environ:
    del os.environ["HTTP_PROXY"]
if "HTTPS_PROXY" in os.environ:
    del os.environ["HTTPS_PROXY"]

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

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
        if b in u:
            return f"Blacklist: {b}"
    return None

def check_layer_2(text: str):
    t = unicodedata.normalize("NFC", text.lower())
    for kw in MEDICAL_KEYWORDS:
        if unicodedata.normalize("NFC", kw) in t:
            return None
    return "No medical keyword"

# ======================================================================
# 2. DOMAIN CIRCUIT BREAKER (AUTO-SKIP DOMAINS FAILING THRESHOLD)
# ======================================================================
class DomainTracker:
    def __init__(self, failure_threshold: int = 15):
        import threading
        self.threshold = failure_threshold
        self.lock = threading.Lock()
        # stats: domain -> {'fail': int, 'success': int, 'skipped': bool}
        self.stats = collections.defaultdict(lambda: {'fail': 0, 'success': 0, 'skipped': False})

    def get_domain(self, url: str) -> str:
        try:
            return urlparse(url).netloc.lower()
        except Exception:
            return ""

    def should_skip(self, domain: str) -> bool:
        if not domain:
            return False
        with self.lock:
            return self.stats[domain]['skipped']

    def record_success(self, domain: str):
        if not domain:
            return
        with self.lock:
            self.stats[domain]['success'] += 1
            self.stats[domain]['fail'] = 0

    def record_failure(self, domain: str):
        if not domain:
            return
        with self.lock:
            data = self.stats[domain]
            if data['skipped']:
                return
            data['fail'] += 1
            if data['success'] == 0 and data['fail'] >= self.threshold:
                data['skipped'] = True
                print(f"\n🚫 [Domain Circuit Breaker] Domain '{domain}' đã thất bại {data['fail']} lần (0 success) -> TỰ ĐỘNG SKIP TOÀN BỘ URL CÒN LẠI!")

# ======================================================================
# 3. PROXY MANAGER (XOAY IP, AUTO-FETCH PROXY & PRUNING)
# ======================================================================
class ProxyManager:
    def __init__(self, single_proxy=None, proxy_file=None, auto_fetch=False):
        import threading
        self.proxies = []
        self.fail_counts = collections.defaultdict(int)
        self.auto_fetch = auto_fetch
        self.lock = threading.Lock()
        
        # Load blacklist để ghi nhớ proxy hỏng qua các lần chạy
        self.blacklist_file = "data/raw/corpus_text/bad_proxies.txt"
        self.blacklisted_proxies = set()
        if os.path.exists(self.blacklist_file):
            with open(self.blacklist_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        self.blacklisted_proxies.add(line.strip())
                        self.fail_counts[line.strip()] = 5
            print(f"🚫 [Proxy Pool] Đã nạp {len(self.blacklisted_proxies)} proxy từ blacklist (bỏ qua không thử lại).")

        # Load whitelist proxy tốt
        self.goodlist_file = "data/raw/corpus_text/good_proxies.txt"
        self.good_proxies = set()
        if os.path.exists(self.goodlist_file):
            with open(self.goodlist_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip() and line.strip() not in self.blacklisted_proxies:
                        self.good_proxies.add(line.strip())
                        self.proxies.append(line.strip())
            print(f"💎 [Proxy Pool] Đã nạp {len(self.good_proxies)} proxy VIP (sẽ ưu tiên sử dụng).")

        self.custom_proxy = single_proxy

        if single_proxy:
            self.proxies.append(single_proxy)
            self.good_proxies.add(single_proxy)
            print(f"🌐 [Proxy] Đã cấu hình Custom Proxy: {single_proxy} (Cấp Miễn Tử Kim Bài)")

        if proxy_file and os.path.exists(proxy_file):
            with open(proxy_file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                for l in lines:
                    p = l if l.startswith("http") or l.startswith("socks") else f"http://{l}"
                    if p not in self.blacklisted_proxies:
                        self.proxies.append(p)
            print(f"🌐 [Proxy] Đã nạp {len(self.proxies)} proxies khả dụng từ file {proxy_file}")

        if self.auto_fetch:
            print("🔍 [Proxy] Đang tự động quét danh sách proxy miễn phí từ GitHub/ProxyScrape...")
            fetched = self._fetch_public_proxies()
            for p in fetched:
                if p not in self.blacklisted_proxies:
                    self.proxies.append(p)
            print(f"🌐 [Proxy] Đã nạp thêm {len(self.proxies)} proxy miễn phí vào pool (đã lọc blacklist)!")

        # Loại bỏ trùng lặp
        self.proxies = list(dict.fromkeys(self.proxies))
        if self.proxies:
            print(f"✅ [Proxy Pool] Sẵn sàng với {len(self.proxies)} IP/Proxies.")
        else:
            print("ℹ️ [Proxy Pool] Không cấu hình proxy -> Sử dụng kết nối mạng trực tiếp (Direct IP).")
            
        self.proxy_last_used = {}
        self.MIN_PROXY_COOLDOWN = 3.0 # Giãn cách 3 giây cho mỗi proxy

    def _fetch_public_proxies(self):
        import json
        pool = []
        
        # 1. Các nguồn Proxy VN (Đã lọc)
        txt_urls = [
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=VN&ssl=all&anonymity=all",
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/country/VN/http.txt",
            "https://raw.githubusercontent.com/vakhov/free-proxy-list/master/proxies/country/VN.txt",
            "https://raw.githubusercontent.com/Bardiafa/Proxy-Leecher/main/proxies/countries/VN/http.txt",
            "https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/country/VN/http.txt"
        ]
        for u in txt_urls:
            try:
                req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as res:
                    lines = res.read().decode('utf-8', errors='ignore').strip().split('\n')
                    for line in lines:
                        p = line.strip()
                        if ':' in p:
                            pool.append(f"http://{p}")
            except Exception:
                pass
                
        # 2. API Trả về JSON (GeoNode VN)
        try:
            req = urllib.request.Request("https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&country=VN&protocols=http%2Chttps", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as res:
                data = json.loads(res.read().decode('utf-8'))
                for item in data.get('data', []):
                    ip = item.get('ip')
                    port = item.get('port')
                    if ip and port:
                        pool.append(f"http://{ip}:{port}")
        except Exception:
            pass
            
        # 3. Nguồn tổng hợp cần lọc thủ công (SPYS.ME)
        try:
            req = urllib.request.Request("https://spys.me/proxy.txt", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as res:
                lines = res.read().decode('utf-8', errors='ignore').strip().split('\n')
                for line in lines:
                    if ' VN-' in line: # Chỉ lấy dòng có mã quốc gia là VN
                        p = line.split(' ')[0]
                        pool.append(f"http://{p}")
        except Exception:
            pass
            
        random.shuffle(pool)
        return pool[:1000]

    def get_proxy(self):
        import time
        with self.lock:
            if self.auto_fetch and len(self.proxies) < 5:
                # Nạp lại proxy nếu cạn kiệt
                fetched = self._fetch_public_proxies()
                added = 0
                for p in fetched:
                    if p not in self.proxies and p not in self.blacklisted_proxies and self.fail_counts[p] < 1:
                        self.proxies.append(p)
                        added += 1
                
                # Nếu tất cả các proxy trên mạng đều đã bị đánh dấu hỏng, reset
                if added == 0 and fetched:
                    print("\n🔄 [Proxy Pool] Toàn bộ proxy mạng đã chạm giới hạn lỗi. Tiến hành reset lịch sử lỗi để tái sử dụng...")
                    self.fail_counts.clear()
                    self.blacklisted_proxies.clear() # Cho các proxy hỏng một cơ hội nữa
                    for p in fetched:
                        if p not in self.proxies:
                            self.proxies.append(p)
                            added += 1

                if added > 0:
                    print(f"\n🔄 [Proxy Pool] Tự động nạp thêm {added} proxy (Tổng: {len(self.proxies)})")
        
            if not self.proxies:
                return None
                
            now = time.time()
            # Lọc các proxy VIP đang "rảnh" (đã nghỉ ít nhất 3 giây)
            ready_good_proxies = [
                p for p in self.good_proxies 
                if now - self.proxy_last_used.get(p, 0) >= self.MIN_PROXY_COOLDOWN
            ]
                
            # Ưu tiên proxy tốt 80% thời gian nếu có
            if ready_good_proxies and random.random() < 0.8:
                chosen = random.choice(ready_good_proxies)
                self.proxy_last_used[chosen] = now
                return chosen
                
            # Lọc các proxy thường đang "rảnh"
            ready_pool = [
                p for p in self.proxies
                if now - self.proxy_last_used.get(p, 0) >= self.MIN_PROXY_COOLDOWN
            ]
            
            if ready_pool:
                chosen = random.choice(ready_pool)
            else:
                chosen = random.choice(self.proxies)
                
            self.proxy_last_used[chosen] = now
            return chosen

    def report_success(self, proxy):
        if not proxy or "127.0.0.1" in proxy or "localhost" in proxy:
            return
        with self.lock:
            if proxy not in self.good_proxies and proxy not in self.blacklisted_proxies:
                self.good_proxies.add(proxy)
                print(f"\n💎 [Proxy Pool] Phát hiện VIP Proxy: {proxy}")
                try:
                    with open(self.goodlist_file, "a", encoding="utf-8") as f:
                        f.write(proxy + "\n")
                except Exception:
                    pass

    def report_failure(self, proxy):
        if not proxy or "127.0.0.1" in proxy or "localhost" in proxy:
            return
        # MIỄN TỬ KIM BÀI CHO ROTATING PROXY MUA BẰNG TIỀN
        if hasattr(self, 'custom_proxy') and proxy == self.custom_proxy:
            return

        with self.lock:
            self.fail_counts[proxy] += 1
            if self.fail_counts[proxy] >= 1:
                if proxy in self.proxies:
                    self.proxies.remove(proxy)
                if proxy in self.good_proxies:
                    self.good_proxies.remove(proxy)
                
                if proxy not in self.blacklisted_proxies:
                    self.blacklisted_proxies.add(proxy)
                    try:
                        with open(self.blacklist_file, "a", encoding="utf-8") as f:
                            f.write(proxy + "\n")
                    except Exception:
                        pass

# ======================================================================
# 3. ADAPTIVE DOMAIN RATE-LIMITER (COOLDOWN CHỐNG 429 TRÊN IP NHÀ)
# ======================================================================
domain_consecutive_429 = collections.defaultdict(int)
domain_cooldown_lock = asyncio.Lock()

async def handle_rate_limit_cooldown(domain: str, has_proxies: bool):
    """
    Nếu không dùng proxy và bị dính 429 liên tục trên IP nhà,
    tạm dừng toàn bộ các luồng trong 20-30 giây để Cloudflare nhả IP.
    """
    if has_proxies:
        return

    domain_consecutive_429[domain] += 1
    if domain_consecutive_429[domain] >= 4:
        async with domain_cooldown_lock:
            if domain_consecutive_429[domain] >= 4:
                cooldown = 25
                print(f"\n⚠️ [RATE LIMIT ALERT] Domain '{domain}' trả về 429/403 liên tiếp!")
                print(f"⏳ Tạm dừng (cooldown) {cooldown}s để IP hồi phục trước khi tiếp tục...")
                await asyncio.sleep(cooldown)
                domain_consecutive_429[domain] = 0
                print(f"🚀 Hết thời gian cooldown cho '{domain}', tiếp tục cào!\n")

# ======================================================================
# 4. SELENIUM THREAD WORKER
# ======================================================================
import threading
thread_local = threading.local()
all_workers = []
worker_lock = threading.Lock()
driver_init_lock = threading.Lock()
driver_path_lock = threading.Lock()
CACHED_DRIVER_PATH = None

def clean_wdm_locks():
    """Xóa các file lock của webdriver-manager còn sót lại sau khi process bị crash/Ctrl+C"""
    try:
        import glob
        for lock_f in glob.glob(os.path.expanduser('~/.wdm/.wdm-lock*')):
            try:
                os.remove(lock_f)
            except Exception:
                pass
    except Exception:
        pass

def get_chromedriver_path():
    """Lấy đường dẫn chromedriver một lần duy nhất và cache lại, tránh lock timeout giữa các thread"""
    global CACHED_DRIVER_PATH
    if CACHED_DRIVER_PATH is None:
        with driver_path_lock:
            if CACHED_DRIVER_PATH is None:
                clean_wdm_locks()
                try:
                    CACHED_DRIVER_PATH = ChromeDriverManager().install()
                except Exception:
                    clean_wdm_locks()
                    CACHED_DRIVER_PATH = ChromeDriverManager().install()
    return CACHED_DRIVER_PATH

def create_proxy_auth_extension(proxy_host, proxy_port, proxy_user, proxy_pass, plugin_path='proxy_auth_plugin.zip'):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """
    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
              },
              bypassList: ["localhost"]
            }
          };
    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }
    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (proxy_host, proxy_port, proxy_user, proxy_pass)
    
    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    return plugin_path

def create_driver(proxy=None):
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--blink-settings=imagesEnabled=false")
    opts.add_argument("--ignore-certificate-errors")
    opts.add_argument("--ignore-ssl-errors")
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Stealth
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    
    if proxy:
        parsed = urlparse(proxy if proxy.startswith('http') else f"http://{proxy}")
        if parsed.username and parsed.password:
            # Dùng Chrome Extension để authen proxy
            import threading
            plugin_dir = "data/proxy_credentials"
            os.makedirs(plugin_dir, exist_ok=True)
            plugin_path = os.path.join(plugin_dir, f"proxy_auth_plugin_{threading.get_ident()}.zip")
            create_proxy_auth_extension(parsed.hostname, parsed.port, parsed.username, parsed.password, plugin_path)
            opts.add_extension(plugin_path)
        else:
            # Proxy không có user:pass
            proxy_ip_port = proxy.replace("http://", "").replace("https://", "")
            opts.add_argument(f"--proxy-server={proxy_ip_port}")
            
    prefs = {"profile.managed_default_content_settings.images": 2, "profile.default_content_setting_values.notifications": 2}
    opts.add_experimental_option("prefs", prefs)

    # Disable webdriver logging
    import logging
    logging.getLogger('WDM').setLevel(logging.WARNING)

    # Clear environment variables again right before initializing the driver just to be completely safe
    for k in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"]:
        if k in os.environ:
            del os.environ[k]

    driver_path = get_chromedriver_path()
    svc = Service(driver_path)

    driver = webdriver.Chrome(service=svc, options=opts)
    driver.set_page_load_timeout(30)
    return driver

class SeleniumWorker:
    def __init__(self, proxy_mgr):
        self.proxy_mgr = proxy_mgr
        self.driver = None
        self.current_proxy = None

    def init_driver(self):
        self.close()
        self.current_proxy = self.proxy_mgr.get_proxy()
        print(f"🌐 [Worker] Khởi tạo trình duyệt với Proxy: {self.current_proxy}")
        with driver_init_lock:
            self.driver = create_driver(self.current_proxy)
            import time
            time.sleep(1.0) # Giảm tải CPU khi mở nhiều tab cùng lúc

    def close(self):
        if self.driver:
            try: self.driver.quit()
            except: pass
            self.driver = None

def get_thread_worker(proxy_mgr):
    if not hasattr(thread_local, "worker"):
        w = SeleniumWorker(proxy_mgr)
        thread_local.worker = w
        with worker_lock:
            all_workers.append(w)
    return thread_local.worker

def fetch_one_sync(row: dict, proxy_mgr: ProxyManager, max_retries: int, domain_tracker: DomainTracker):
    url = row['url']
    row_id = row['id']
    res = {'id': row_id, 'url': url, 'text': None, 'status': None, 'reason': '', 'dropped_at_layer': None}

    domain = domain_tracker.get_domain(url)
    if domain_tracker.should_skip(domain):
        res['status'] = 'error'
        res['reason'] = f"Domain Blocked/Skipped ({domain})"
        return res

    # Tầng 1: Lọc blacklist URL
    l1 = check_layer_1(url)
    if l1:
        res['status'] = 'dropped'
        res['dropped_at_layer'] = 1
        res['reason'] = l1
        return res

    worker = get_thread_worker(proxy_mgr)
    
    for attempt in range(max_retries + 1):
        if worker.driver is None:
            worker.init_driver()
            
        try:
            worker.driver.get(url)
            time.sleep(1.0)
            html = worker.driver.page_source
            
            # Kiểm tra Cloudflare và chờ giải challenge nếu gặp
            if "cf-browser-verification" in html or "Just a moment..." in html or "Attention Required!" in html:
                time.sleep(3.5)
                html = worker.driver.page_source

            if "cf-browser-verification" in html or "Just a moment..." in html or "Attention Required!" in html or ("Access denied" in html and "Cloudflare" in html):
                res['reason'] = "Cloudflare Block/Challenge"
                proxy_mgr.report_failure(worker.current_proxy)
                if len(proxy_mgr.proxies) > 1:
                    worker.close()
                time.sleep(2.0)
                continue
                
            if "This site can’t be reached" in html or "ERR_PROXY_CONNECTION_FAILED" in html or "ERR_TUNNEL_CONNECTION_FAILED" in html or "ERR_CONNECTION_TIMED_OUT" in html or "ERR_TIMED_OUT" in html or "Your connection is not private" in html:
                res['reason'] = "Proxy Connection Failed"
                proxy_mgr.report_failure(worker.current_proxy)
                if len(proxy_mgr.proxies) > 1:
                    worker.close()
                time.sleep(2.0)
                continue

            # Nhận diện lỗi HTTP từ máy chủ
            if "<title>403 Forbidden</title>" in html or "<h1>403 Forbidden</h1>" in html or "403 Forbidden<" in html:
                res['reason'] = "HTTP 403 Forbidden (Nginx/Server Block)"
                break

            if "<title>404 Not Found</title>" in html or "<h1>404 Not Found</h1>" in html or "404 Not Found<" in html:
                res['reason'] = "HTTP 404 Not Found"
                res['status'] = 'dropped'
                res['dropped_at_layer'] = 1
                break
                
            text = trafilatura.extract(html, include_links=False, include_images=False)
            if not text or len(text.strip()) < 200:
                # Đợi thêm 2s phòng trường hợp trang SPA / dynamic JS render chậm
                time.sleep(2.0)
                html = worker.driver.page_source
                text = trafilatura.extract(html, include_links=False, include_images=False)

            if text and len(text.strip()) > 200:
                lower_text = text.lower()
                if "too many requests" in lower_text or "rate limit" in lower_text:
                    res['reason'] = "429 Too Many Requests"
                    proxy_mgr.report_failure(worker.current_proxy)
                    time.sleep(2.0)
                    continue

                if "owner of this website" in lower_text or "cf-browser-verification" in lower_text or "just a moment..." in lower_text or "attention required" in lower_text:
                    res['reason'] = "Cloudflare Block/Challenge"
                    proxy_mgr.report_failure(worker.current_proxy)
                    if len(proxy_mgr.proxies) > 1:
                        worker.close()
                    time.sleep(2.0)
                    continue

                l2 = check_layer_2(text)
                if l2:
                    res['status'] = 'dropped'
                    res['dropped_at_layer'] = 2
                    res['reason'] = f"{l2} (Text snippet: {text[:30]}...)"
                else:
                    res['text'] = text
                    res['status'] = 'success'
                    res['reason'] = 'Success'
                    proxy_mgr.report_success(worker.current_proxy)
                break # Thành công hoặc xác định chính xác là rác -> thoát vòng lặp
            else:
                res['reason'] = 'Empty text or Cloudflare Turnstile'
                proxy_mgr.report_failure(worker.current_proxy)
                if len(proxy_mgr.proxies) > 1:
                    worker.close()
                time.sleep(1.5)
                continue # Text trống (do block), thử retry
                
        except Exception as e:
            res['reason'] = type(e).__name__
            proxy_mgr.report_failure(worker.current_proxy)
            worker.close() # Browser lỗi thực sự -> đóng để tạo lại
            time.sleep(2.0)
            continue

    # Nếu hết lượt retry mà vẫn chưa success/dropped
    if res['status'] is None:
        res['status'] = 'error'

    # Ghi nhận kết quả vào DomainTracker
    if res['status'] == 'success' or (res['status'] == 'dropped' and res['dropped_at_layer'] == 2):
        domain_tracker.record_success(domain)
    elif res['status'] == 'error' or (res['status'] == 'dropped' and '404' in res['reason']):
        domain_tracker.record_failure(domain)

    if res['status'] != 'success':
        print(f"\n[Debug] URL: {url} | Status: {res['status']} | Reason: {res['reason']}")

    return res

async def crawl_batch(df_batch: pd.DataFrame, sem: asyncio.Semaphore, delay: float, proxy_mgr: ProxyManager, max_retries: int, pbar, executor, domain_tracker: DomainTracker):
    loop = asyncio.get_running_loop()
    
    async def process_row(row):
        async with sem:
            domain = domain_tracker.get_domain(row['url'])
            if not domain_tracker.should_skip(domain) and delay > 0:
                await asyncio.sleep(random.uniform(delay * 0.7, delay * 1.3))
            return await loop.run_in_executor(executor, fetch_one_sync, row, proxy_mgr, max_retries, domain_tracker)

    tasks = [process_row(row) for _, row in df_batch.iterrows()]
    
    results = []
    success_count = 0
    for fut in asyncio.as_completed(tasks):
        r = await fut
        results.append(r)
        if r['status'] == 'success':
            success_count += 1
        pbar.update(1)
        pbar.set_postfix({
            'success': success_count,
            'status': r['status'] if r['status'] else r['reason']
        })
        
    return results

def get_already_crawled_ids(output_dir: str):
    """
    Chỉ coi là đã cào nếu status == 'success'.
    Bất kỳ URL nào bị 429/timeout trước đó sẽ KHÔNG bị bỏ qua và được cào lại.
    """
    files = glob.glob(os.path.join(output_dir, "*.parquet"))
    crawled_ids = set()
    for f in files:
        try:
            df = pd.read_parquet(f, columns=['id', 'status'])
            succ_df = df[df['status'].isin(['success', 'dropped'])]
            crawled_ids.update(succ_df['id'].tolist())
        except Exception:
            pass
    return crawled_ids

# ======================================================================
# 5. MAIN ASYNC ORCHESTRATOR
# ======================================================================
async def main_async(args):
    print("=" * 70)
    print("🚀 LOCAL HIGH-RESILIENCE STEALTH CRAWLER (V2.0 - PARITY WITH KAGGLE)")
    print("=" * 70)
    print(f"📌 Input file:     {args.input}")
    print(f"📌 Output dir:     {args.output_dir}")
    print(f"📌 Target domain:  {args.domain if args.domain else 'ALL DOMAINS'}")
    print(f"📌 Concurrency:    {args.concurrency}")
    print(f"📌 Delay jitter:   {args.delay}s")
    print(f"📌 Max Retries:    {args.max_retries}")
    print(f"📌 Domain fail limit: {args.domain_fail_limit} (Auto-skip dead domains)")
    print(f"📌 Batch size:     {args.batch_size}")
    if args.limit:
        print(f"📌 Limit URLs:     {args.limit:,}")
    print("=" * 70)

    proxy_mgr = ProxyManager(
        single_proxy=args.proxy,
        proxy_file=args.proxy_file,
        auto_fetch=args.auto_proxy
    )
    domain_tracker = DomainTracker(failure_threshold=args.domain_fail_limit)

    os.makedirs(args.output_dir, exist_ok=True)
    clean_wdm_locks()
    get_chromedriver_path()

    print("\n1. Đang đọc danh sách URL cần cào...")
    df_rem = pd.read_parquet(args.input)
    print(f"   - Tổng URLs trong remaining_urls: {len(df_rem):,}")

    if args.domain:
        is_target = df_rem['url'].str.contains(args.domain, case=False, na=False)
        df_target = pd.concat([df_rem[is_target], df_rem[~is_target]])
        print(f"   - [OVERNIGHT MODE] Ưu tiên {is_target.sum():,} URLs thuộc '{args.domain}' lên đầu.")
        print(f"   - Sau khi cào xong sẽ tự động tiếp tục cào {(~is_target).sum():,} URLs của các trang khác.")
    else:
        df_target = df_rem.copy()

    # Kiểm tra các ID đã cào thành công trước đó
    crawled_ids = get_already_crawled_ids(args.output_dir)
    if crawled_ids:
        print(f"   - Đã có {len(crawled_ids):,} IDs cào thành công trước đó. Tự động bỏ qua.")
        df_target = df_target[~df_target['id'].isin(crawled_ids)].copy()
        print(f"   - Còn lại cần cào: {len(df_target):,} URLs")

    if args.limit and args.limit > 0 and len(df_target) > args.limit:
        df_target = df_target.head(args.limit).copy()
        print(f"   - Áp dụng giới hạn lượt này: {len(df_target):,} URLs")
    elif args.limit == 0:
        print(f"   - Không giới hạn số lượng. Sẽ cào toàn bộ {len(df_target):,} URLs!")

    if len(df_target) == 0:
        print("🎉 Không còn URL nào cần cào. Hoàn tất!")
        return

    import concurrent.futures
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency)
    sem = asyncio.Semaphore(args.concurrency)
    num_batches = (len(df_target) // args.batch_size) + (1 if len(df_target) % args.batch_size > 0 else 0)

    # Đếm số thứ tự file part hiện có
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

            batch_results = await crawl_batch(batch_df, sem, args.delay, proxy_mgr, args.max_retries, pbar, executor, domain_tracker)

            df_res = pd.DataFrame(batch_results)
            df_valid = df_res[df_res['status'].isin(['success', 'dropped'])]
            succ = (df_res['status'] == 'success').sum()

            # Chỉ lưu file nếu có ít nhất 1 bài thành công hoặc dropped
            if len(df_valid) > 0:
                df_valid.to_parquet(out_file, index=False)
            else:
                print(f"\n⚠️ [Batch {part_no:04d}] Không có URL nào hợp lệ (Toàn bộ 429/Error). Không lưu file này để cào lại sau.")

            total_success += succ
            total_processed += len(df_res)

    print("\n" + "=" * 70)
    print("🎉 HOÀN THÀNH PHIÊN CÀO LOCAL!")
    print(f"   - Tổng URL đã xử lý: {total_processed:,}")
    print(f"   - Thành công (success): {total_success:,} ({total_success/total_processed*100:.1f}%)" if total_processed > 0 else "")
    print(f"   - Dữ liệu lưu tại: {args.output_dir}")
    print("=" * 70)

    # Dọn dẹp Selenium workers
    for w in all_workers:
        try:
            w.close()
        except Exception:
            pass

def main():
    parser = argparse.ArgumentParser(description="Local Stealth Crawler v3 (Selenium Parity)")
    parser.add_argument("--input", default="data/raw/final_corpus_text/remaining_urls.parquet", help="Path to input parquet")
    parser.add_argument("--output-dir", default="data/raw/corpus_text/local_recovered", help="Directory to save crawled batches")
    parser.add_argument("--domain", default="nhathuoclongchau.com.vn", help="Target domain filter (default: nhathuoclongchau.com.vn)")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of URLs to crawl (default: 0 = No limit)")
    parser.add_argument("--concurrency", type=int, default=2, help="Concurrent async workers (default: 2)")
    parser.add_argument("--delay", type=float, default=0.25, help="Polite delay jitter between requests in seconds (default: 0.25)")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size per saved parquet file (default: 100)")
    parser.add_argument("--max-retries", type=int, default=2, help="Max retry attempts per URL on 429/timeout (default: 2)")
    parser.add_argument("--domain-fail-limit", type=int, default=15, help="Auto-skip domain after N failures if 0 success (default: 15)")
    parser.add_argument("--proxy", default=None, help="Single custom proxy (e.g. 'http://user:pass@host:port' or 'socks5://127.0.0.1:1080')")
    parser.add_argument("--proxy-file", default=None, help="Path to text file containing proxies (1 per line)")
    parser.add_argument("--auto-proxy", action="store_true", help="Automatically fetch free public proxies from ProxyScrape")

    args = parser.parse_args()
    
    # Lấy proxy từ cấu hình .env nếu không truyền từ CLI
    if not args.proxy:
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        try:
            from src.config import settings
            if hasattr(settings, "PROXY_240S") and settings.PROXY_240S:
                args.proxy = settings.PROXY_240S
        except ImportError:
            pass


    asyncio.run(main_async(args))

if __name__ == "__main__":
    main()
