import os
import sys
import pandas as pd
from urllib.parse import urlparse
from curl_cffi import requests
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding='utf-8')

# Lấy proxy từ config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from src.config import settings
    CUSTOM_PROXY = getattr(settings, "PROXY_15S", None) or getattr(settings, "PROXY_240S", None)
except ImportError:

    CUSTOM_PROXY = None

def get_domain(url):
    try:
        return urlparse(url).netloc.replace("www.", "")
    except:
        return ""

def test_domain(domain, urls, proxy):
    proxies = {"http": proxy, "https": proxy} if proxy else None
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    # Thử tối đa 2 URL của domain đó
    for url in urls[:2]:
        try:
            req = requests.get(url, proxies=proxies, headers=headers, timeout=15, impersonate="chrome120")
            html = req.text
            if "cf-browser-verification" in html or "Just a moment..." in html or "Attention Required!" in html:
                return domain, "SELENIUM", "Bị chặn bởi Cloudflare Turnstile"
            elif "owner of this website" in html:
                return domain, "SELENIUM", "Bị chặn bởi Cloudflare WAF"
            elif req.status_code == 200:
                return domain, "FAST", "Thành công"
            else:
                return domain, "UNKNOWN", f"Status: {req.status_code}"
        except Exception as e:
            pass
    return domain, "UNKNOWN", "Lỗi kết nối"

def main():
    print("1. Đọc dữ liệu từ remaining_urls.parquet...")
    input_file = "data/raw/final_corpus_text/remaining_urls.parquet"
    if not os.path.exists(input_file):
        print("Không tìm thấy file!")
        return

    df = pd.read_parquet(input_file)
    df['domain'] = df['url'].apply(get_domain)
    
    domain_counts = df['domain'].value_counts()
    print(f"\nPhát hiện {len(domain_counts)} domains khác nhau.")
    
    # Lấy các domain chiếm đa số (trên 100 URL) để test cho nhanh
    top_domains = domain_counts[domain_counts > 10].index.tolist()
    print(f"Sẽ test {len(top_domains)} domains phổ biến nhất...")
    
    results = []
    
    # Test song song
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for dom in top_domains:
            sample_urls = df[df['domain'] == dom]['url'].tolist()
            futures.append(executor.submit(test_domain, dom, sample_urls, CUSTOM_PROXY))
            
        for fut in futures:
            results.append(fut.result())
            
    # Phân loại
    fast_domains = [r[0] for r in results if r[1] == "FAST"]
    selenium_domains = [r[0] for r in results if r[1] == "SELENIUM"]
    unknown_domains = [r[0] for r in results if r[1] == "UNKNOWN"]
    
    print("\n" + "="*50)
    print("📊 KẾT QUẢ PHÂN TÍCH DOMAINS")
    print("="*50)
    print(f"🚀 THÍCH HỢP CHO FAST CRAWLER ({len(fast_domains)} domains):")
    for d in fast_domains: print(f"  - {d}")
        
    print(f"\n🐢 BẮT BUỘC DÙNG SELENIUM ({len(selenium_domains)} domains):")
    for d in selenium_domains: print(f"  - {d}")
        
    print(f"\n❓ KHÔNG RÕ/LỖI ({len(unknown_domains)} domains):")
    for d in unknown_domains: print(f"  - {d}")
        
    # Tạo 2 DataFrame tách biệt
    df_fast = df[df['domain'].isin(fast_domains)]
    df_selenium = df[df['domain'].isin(selenium_domains + unknown_domains)]
    
    print("\n" + "="*50)
    print(f"💾 Phân chia dữ liệu:")
    print(f"  - Dữ liệu cho FAST: {len(df_fast):,} URLs")
    print(f"  - Dữ liệu cho SELENIUM: {len(df_selenium):,} URLs")
    
    df_fast.drop(columns=['domain']).to_parquet("data/raw/final_corpus_text/remaining_urls_fast.parquet", index=False)
    df_selenium.drop(columns=['domain']).to_parquet("data/raw/final_corpus_text/remaining_urls_selenium.parquet", index=False)
    print("\n✅ Đã xuất ra 2 file: remaining_urls_fast.parquet và remaining_urls_selenium.parquet")

if __name__ == "__main__":
    main()
