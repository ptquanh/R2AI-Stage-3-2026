import os
import sys
import glob
import shutil
from urllib.parse import urlparse
import time
import pandas as pd
import pyarrow.parquet as pq

sys.stdout.reconfigure(encoding='utf-8')

def safe_to_parquet(df, path):
    tmp_path = path + ".tmp"
    df.to_parquet(tmp_path, index=False, engine='pyarrow')
    meta = pq.read_metadata(tmp_path)
    assert meta.num_rows == len(df), f"Lỗi: Số dòng {meta.num_rows} không khớp với {len(df)}!"
    os.replace(tmp_path, path)

def main():
    print("=" * 70)
    print("🚀 BẮT ĐẦU QUY TRÌNH KHÔI PHỤC URL BỊ GÁN NHẦM DROPPED DO LỖI MẠNG / CLOUDFLARE")
    print("=" * 70)

    dropped_path = 'data/raw/final_corpus_text/dropped_safe_offtopic_urls.parquet'
    bak_path = dropped_path + ".bak"
    if not os.path.exists(dropped_path) and not os.path.exists(bak_path):
        print(f"❌ Không tìm thấy file {dropped_path} hoặc backup")
        return

    # Ưu tiên đọc file backup nếu có (chứa toàn bộ 287k rows gốc)
    if os.path.exists(bak_path):
        df_dropped = pd.read_parquet(bak_path)
        print(f"📂 Đang nạp dữ liệu từ backup: {bak_path}")
    else:
        shutil.copy2(dropped_path, bak_path)
        df_dropped = pd.read_parquet(dropped_path)

    init_dropped_count = len(df_dropped)
    print(f"\n1. Tổng số URL trong file dropped/backup: {init_dropped_count:,}")

    # Chuẩn hóa kiểu dữ liệu sang chuỗi để tránh lỗi ArrowTypeError
    df_dropped['id'] = df_dropped['id'].astype(str)
    df_dropped['url'] = df_dropped['url'].astype(str)

    # Nhận diện các lý do là lỗi mạng / Cloudflare / 429 / Domain Skipped
    is_false_drop = df_dropped['reason'].str.contains(
        r'Domain Skipped|too many requests|rate limit|owner of this website|turnstile|cf-browser',
        case=False,
        na=False
    )

    df_to_restore = df_dropped[is_false_drop].copy()
    df_real_dropped = df_dropped[~is_false_drop].copy()

    print(f"   - Số URL thực sự là OFFTOPIC (giữ lại trong file dropped): {len(df_real_dropped):,}")
    print(f"   - Số URL bị chặn mạng/Cloudflare/429 (cần KHÔI PHỤC): {len(df_to_restore):,}")

    # 1. Cập nhật lại dropped_safe_offtopic_urls.parquet với chỉ các bài offtopic thật
    safe_to_parquet(df_real_dropped, dropped_path)
    print(f"✅ Đã dọn sạch {dropped_path}: Giữ lại chuẩn xác {len(df_real_dropped):,} URLs offtopic.")

    # 2. Đọc tất cả các ID và URL đã có trong các file Tier để loại trừ tuyệt đối trùng lặp
    print("\n2. Đang quét các file Tier để đảm bảo không trùng lặp...")
    tier_files = [
        'data/raw/final_corpus_text/tier_1.parquet',
        'data/raw/final_corpus_text/tier_1_resume.parquet',
        'data/raw/final_corpus_text/tier_2.parquet',
        'data/raw/final_corpus_text/tier_other.parquet'
    ]
    already_success_ids = set()
    already_success_urls = set()
    for tf in tier_files:
        if os.path.exists(tf):
            df_t = pd.read_parquet(tf, columns=['id', 'url'])
            already_success_ids.update(df_t['id'].astype(str).tolist())
            already_success_urls.update(df_t['url'].astype(str).tolist())

    print(f"   - Tổng số URLs đã cào thành công trong các Tier: {len(already_success_urls):,}")

    # Loại bỏ các URL đã thành công
    df_to_restore = df_to_restore[
        ~df_to_restore['id'].isin(already_success_ids) &
        ~df_to_restore['url'].isin(already_success_urls)
    ].drop_duplicates(subset=['id']).drop_duplicates(subset=['url']).copy()

    print(f"   - Số URLs thực sự cần khôi phục sau khi đối chiếu Tier: {len(df_to_restore):,}")

    # 3. Phân chia URLs khôi phục theo Domain (Selenium vs Fast)
    SELENIUM_KEYWORDS = [
        'zysjonline.com', 'bingli.iiyi.com', 'article.iiyi.com',
        'beta.pharmacity.io', 'msdmanuals.cn', 'youmed.vn',
        '120ask.com', 'familydoctor.com.cn', 'qihuangzhishu.com', 'fitness.39.net'
    ]

    def is_selenium_url(u):
        u_str = str(u).lower()
        for kw in SELENIUM_KEYWORDS:
            if kw in u_str:
                return True
        return False

    restore_sel_mask = df_to_restore['url'].apply(is_selenium_url)
    df_restore_sel = df_to_restore[restore_sel_mask][['id', 'url']].copy()
    df_restore_fast = df_to_restore[~restore_sel_mask][['id', 'url']].copy()

    print(f"\n3. Phân chia URLs khôi phục:")
    print(f"   - Khôi phục về Selenium queue: {len(df_restore_sel):,} URLs")
    print(f"   - Khôi phục về Fast queue:     {len(df_restore_fast):,} URLs")

    # 4. Khôi phục vào remaining_urls.parquet (Tổng)
    rem_path = 'data/raw/final_corpus_text/remaining_urls.parquet'
    if os.path.exists(rem_path):
        if not os.path.exists(rem_path + ".bak"):
            shutil.copy2(rem_path, rem_path + ".bak")
        df_rem = pd.read_parquet(rem_path)
        df_rem['id'] = df_rem['id'].astype(str)
        df_rem['url'] = df_rem['url'].astype(str)
        existing_rem_ids = set(df_rem['id'].tolist())
        items_add_rem = df_to_restore[['id', 'url']][~df_to_restore['id'].isin(existing_rem_ids)].copy()
        items_add_rem['id'] = items_add_rem['id'].astype(str)
        items_add_rem['url'] = items_add_rem['url'].astype(str)
        
        df_rem_updated = pd.concat([df_rem, items_add_rem], ignore_index=True)
        safe_to_parquet(df_rem_updated, rem_path)
        print(f"✅ {rem_path}: Đã thêm {len(items_add_rem):,} URLs (Tổng hiện tại: {len(df_rem_updated):,})")

    # 5. Khôi phục vào remaining_urls_selenium.parquet
    rem_sel_path = 'data/raw/final_corpus_text/remaining_urls_selenium.parquet'
    if os.path.exists(rem_sel_path):
        if not os.path.exists(rem_sel_path + ".bak"):
            shutil.copy2(rem_sel_path, rem_sel_path + ".bak")
        df_rem_sel = pd.read_parquet(rem_sel_path)
        df_rem_sel['id'] = df_rem_sel['id'].astype(str)
        df_rem_sel['url'] = df_rem_sel['url'].astype(str)
        existing_sel_ids = set(df_rem_sel['id'].tolist())
        items_add_sel = df_restore_sel[~df_restore_sel['id'].isin(existing_sel_ids)].copy()
        items_add_sel['id'] = items_add_sel['id'].astype(str)
        items_add_sel['url'] = items_add_sel['url'].astype(str)

        df_rem_sel_updated = pd.concat([df_rem_sel, items_add_sel], ignore_index=True)
        safe_to_parquet(df_rem_sel_updated, rem_sel_path)
        print(f"✅ {rem_sel_path}: Đã thêm {len(items_add_sel):,} URLs (Tổng hiện tại: {len(df_rem_sel_updated):,})")

    # 6. Khôi phục vào remaining_urls_fast.parquet
    rem_fast_path = 'data/raw/final_corpus_text/remaining_urls_fast.parquet'
    if os.path.exists(rem_fast_path):
        if not os.path.exists(rem_fast_path + ".bak"):
            shutil.copy2(rem_fast_path, rem_fast_path + ".bak")
        df_rem_fast = pd.read_parquet(rem_fast_path)
        df_rem_fast['id'] = df_rem_fast['id'].astype(str)
        df_rem_fast['url'] = df_rem_fast['url'].astype(str)
        existing_fast_ids = set(df_rem_fast['id'].tolist())
        items_add_fast = df_restore_fast[~df_restore_fast['id'].isin(existing_fast_ids)].copy()
        items_add_fast['id'] = items_add_fast['id'].astype(str)
        items_add_fast['url'] = items_add_fast['url'].astype(str)

        df_rem_fast_updated = pd.concat([df_rem_fast, items_add_fast], ignore_index=True)
        safe_to_parquet(df_rem_fast_updated, rem_fast_path)
        print(f"✅ {rem_fast_path}: Đã thêm {len(items_add_fast):,} URLs (Tổng hiện tại: {len(df_rem_fast_updated):,})")

    # 7. Dọn dẹp các bản ghi dropped bị nhầm trong data/raw/corpus_text/local_recovered
    print("\n4. Dọn dẹp thư mục local_recovered để crawler không bỏ qua các URL khôi phục...")
    rec_files = sorted(glob.glob('data/raw/corpus_text/local_recovered/*.parquet'))
    cleaned_files = 0
    deleted_empty_files = 0
    skipped_locked = 0
    
    # Tập hợp các ID cần xóa khỏi local_recovered (để crawler cào lại)
    ids_to_unmark = set(df_to_restore['id'].tolist())

    for rf in rec_files:
        try:
            # Bỏ qua file vừa được tạo trong vòng 30 giây gần đây để tránh xung đột với crawler đang chạy
            if os.path.getmtime(rf) > time.time() - 30:
                continue
            df_part = pd.read_parquet(rf)
            df_part['id_str'] = df_part['id'].astype(str)
            # Kiểm tra xem có ID nào nằm trong nhóm cần khôi phục không
            has_false_drops = df_part['id_str'].isin(ids_to_unmark).any()
            if has_false_drops:
                # Giữ lại các dòng success hoặc real dropped, loại bỏ các dòng false dropped
                df_clean = df_part[~df_part['id_str'].isin(ids_to_unmark)].drop(columns=['id_str']).copy()
                if len(df_clean) == 0:
                    os.remove(rf)
                    deleted_empty_files += 1
                else:
                    df_clean.to_parquet(rf, index=False)
                    cleaned_files += 1
        except Exception as e:
            skipped_locked += 1

    print(f"✅ Đã dọn dẹp {cleaned_files} files part và xóa {deleted_empty_files} files rỗng trong local_recovered (bỏ qua {skipped_locked} files đang bận).")

    print("\n" + "=" * 70)
    print("🎉 HOÀN TẤT KHÔI PHỤC TOÀN BỘ URL!")
    print("=" * 70)

if __name__ == "__main__":
    main()
