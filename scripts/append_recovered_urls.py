import os
import sys
import glob
import shutil
from urllib.parse import urlparse
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("=" * 70)
    print("🚀 BẮT ĐẦU QUY TRÌNH PHÂN CHIA VÀ CẬP NHẬT URL RECOVERED")
    print("=" * 70)

    # 1. Thu thập tất cả các file recovered
    dir1 = "data/raw/corpus_text/recovered_remaining_urls/corpus_text_0_to_34_10"
    dir2 = "data/raw/corpus_text/recovered_remaining_urls/corpus_text_35_to_62_10"

    files1 = sorted(glob.glob(os.path.join(dir1, "*.parquet")))
    files2 = sorted(glob.glob(os.path.join(dir2, "*.parquet")))
    all_recovered_files = files1 + files2

    print(f"\n1. Đã tìm thấy {len(all_recovered_files)} file parquet:")
    print(f"   - {dir1}: {len(files1)} files")
    print(f"   - {dir2}: {len(files2)} files")

    recovered_dfs = []
    for f in all_recovered_files:
        df = pd.read_parquet(f)
        succ = df[df['status'] == 'success']
        if len(succ) > 0:
            recovered_dfs.append(succ[['id', 'url', 'text']])

    succ_all = pd.concat(recovered_dfs, ignore_index=True)
    print(f"\n2. Tổng số URL success thu được: {len(succ_all)}")
    
    # Ép kiểu chuẩn
    succ_all['id'] = succ_all['id'].astype('int64')
    succ_all['url'] = succ_all['url'].astype('string')
    succ_all['text'] = succ_all['text'].astype('string')

    # Loại bỏ trùng lặp nội bộ nếu có
    init_count = len(succ_all)
    succ_all = succ_all.drop_duplicates(subset=['id']).drop_duplicates(subset=['url'])
    print(f"   - Sau khi kiểm tra trùng lặp nội bộ: {len(succ_all)} URLs (đã loại {init_count - len(succ_all)})")

    # 3. Phân chia theo Domain / Host
    def get_tier(url_str):
        host = urlparse(str(url_str)).netloc.lower()
        # Tier 1 hosts
        tier1_hosts = [
            'tiemchunglongchau.com.vn', 'youmed.vn', 'ask.39.net', '120ask.com',
            'suckhoedoisong.vn', 'suckhoecongdongonline.vn', 'jb39.com',
            'vinmec.com', 'medlatec.vn', 'hellobacsi.com', 'nhathuoclongchau.com.vn',
            'youlai.cn', 'tamanhhospital.vn', 'thaythuocvietnam.vn', 'bachmai.gov.vn',
            'benhviennhitrunguong.gov.vn', 'benhvienvietduc.org', 'pharmacity.vn'
        ]
        # Tier 2 hosts
        tier2_hosts = [
            'cancer.39.net', 'cnkang.com', 'a-hospital.com', 'zhongyibaodian.net',
            'zydcd.com', 'qihuangzhishu.com', 'msdmanuals.cn', 'care.39.net',
            'fk.39.net', 'nk.39.net', 'heart.39.net', 'gan.39.net', 'tnb.39.net',
            'wei.39.net', 'shen.39.net', 'ek.39.net', 'gk.39.net', 'gc.39.net',
            'pf.39.net', 'health.people.com.cn', 'sj.39.net', 'byby.39.net'
        ]
        for h in tier1_hosts:
            if h in host:
                return 'tier_1_resume'
        for h in tier2_hosts:
            if h in host:
                return 'tier_2'
        return 'tier_other'

    succ_all['target_tier'] = succ_all['url'].apply(get_tier)
    print("\n3. Phân bố các URL success theo tier:")
    print(succ_all['target_tier'].value_counts().to_string())

    tier_files = {
        'tier_1_resume': 'data/raw/final_corpus_text/tier_1_resume.parquet',
        'tier_2': 'data/raw/final_corpus_text/tier_2.parquet',
        'tier_other': 'data/raw/final_corpus_text/tier_other.parquet',
    }
    rem_path = 'data/raw/final_corpus_text/remaining_urls.parquet'

    # Tạo thư mục / file backup an toàn
    print("\n4. Đang tạo bản sao lưu an toàn (backup)...")
    for t_name, t_path in tier_files.items():
        bak_path = t_path + ".bak"
        shutil.copy2(t_path, bak_path)
        print(f"   - Sao lưu {t_path} -> {bak_path}")
    rem_bak = rem_path + ".bak"
    shutil.copy2(rem_path, rem_bak)
    print(f"   - Sao lưu {rem_path} -> {rem_bak}")

    # 4. Cập nhật từng file Tier
    print("\n5. Tiến hành bổ sung vào cuối các file Tier (không reset index):")
    all_added_urls = set()
    all_added_ids = set()

    for t_name, t_path in tier_files.items():
        df_target = pd.read_parquet(t_path)
        init_len = len(df_target)

        # Lọc các items cho tier này
        items_to_add = succ_all[succ_all['target_tier'] == t_name][['id', 'url', 'text']].copy()

        # Kiểm tra trùng lặp với data sẵn có trong target file
        existing_ids = set(df_target['id'].tolist())
        existing_urls = set(df_target['url'].tolist())

        items_to_add = items_to_add[
            ~items_to_add['id'].isin(existing_ids) &
            ~items_to_add['url'].isin(existing_urls)
        ]

        num_new = len(items_to_add)
        print(f"\n   >>> Xử lý {t_name} ({t_path}):")
        print(f"       - Số dòng hiện tại: {init_len}")
        print(f"       - Số dòng mới cần thêm: {num_new}")

        if num_new > 0:
            # Gán index tiếp nối liên tục từ init_len đến init_len + num_new - 1
            # Đảm bảo index của df_target ban đầu hoàn toàn nguyên vẹn
            items_to_add.index = range(init_len, init_len + num_new)
            
            # Nối vào cuối
            updated_df = pd.concat([df_target, items_to_add])
            
            # Kiểm tra tính toàn vẹn
            assert len(updated_df) == init_len + num_new, "Lỗi: Kích thước sau khi nối không khớp!"
            assert updated_df.index.equals(pd.RangeIndex(len(updated_df))), "Lỗi: Index không liên tục!"
            assert updated_df.iloc[:init_len]['id'].equals(df_target['id']), "Lỗi: Dữ liệu ban đầu bị thay đổi!"

            # Lưu lại file parquet
            updated_df.to_parquet(t_path, index=False, engine='pyarrow')
            print(f"       - Đã lưu thành công! Số dòng mới: {len(updated_df)}")

            all_added_urls.update(items_to_add['url'].tolist())
            all_added_ids.update(items_to_add['id'].tolist())
        else:
            print("       - Không có dòng mới cần thêm.")

    # 5. Xóa các URL đó trong remaining_urls.parquet
    print("\n6. Đang xóa các URL đã thêm khỏi remaining_urls.parquet...")
    df_rem = pd.read_parquet(rem_path)
    rem_init_len = len(df_rem)
    print(f"   - Số lượng remaining_urls ban đầu: {rem_init_len}")

    # Lọc bỏ các URL và ID đã thêm
    df_rem_filtered = df_rem[
        ~df_rem['url'].isin(all_added_urls) &
        ~df_rem['id'].astype(str).isin([str(i) for i in all_added_ids])
    ].copy()

    rem_final_len = len(df_rem_filtered)
    num_deleted = rem_init_len - rem_final_len
    print(f"   - Số lượng đã xóa: {num_deleted}")
    print(f"   - Số lượng remaining_urls còn lại: {rem_final_len}")

    # Lưu lại remaining_urls (giữ nguyên không thêm index column thừa)
    df_rem_filtered.to_parquet(rem_path, index=False, engine='pyarrow')
    print("   - Đã lưu cập nhật remaining_urls.parquet thành công!")

    print("\n" + "=" * 70)
    print("🎉 HOÀN TẤT TOÀN BỘ QUY TRÌNH!")
    print(f"   - Đã phân chia: {len(all_added_urls)} URLs thành công vào 3 file tier")
    print(f"   - Đã xóa chính xác {num_deleted} URLs khỏi remaining_urls.parquet")
    print("=" * 70)

if __name__ == "__main__":
    main()
