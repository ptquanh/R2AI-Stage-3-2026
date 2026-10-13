import os
import sys
import glob
import shutil
from urllib.parse import urlparse
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
    print("🚀 BẮT ĐẦU QUY TRÌNH PHÂN CHIA VÀ CẬP NHẬT URL RECOVERED")
    print("=" * 70)

    import argparse
    parser = argparse.ArgumentParser(description="Append recovered URLs into tier files")
    parser.add_argument("--dirs", nargs="+", default=["data/raw/corpus_text/local_recovered"], help="Input directories containing recovered parquets")
    parser.add_argument("--no-clean", action="store_true", help="Do not delete local_recovered parquet files after processing")
    args = parser.parse_args()

    # 1. Tìm tất cả các file trong local_recovered
    all_recovered_files = []
    for d in args.dirs:
        found = sorted(glob.glob(os.path.join(d, "*.parquet")))
        all_recovered_files.extend(found)
        print(f"   - {d}: {len(found)} files")

    if not all_recovered_files:
        print("⚠️ Không tìm thấy file parquet nào trong thư mục recovered. Thoát.")
        return

    recovered_dfs_succ = []
    recovered_dfs_drop = []
    for f in all_recovered_files:
        try:
            df = pd.read_parquet(f)
        except Exception as e:
            print(f"   ⚠️ Lỗi đọc file {f}: {e}")
            continue

        if 'status' not in df.columns:
            continue

        succ = df[df['status'] == 'success'].copy()
        if len(succ) > 0:
            recovered_dfs_succ.append(succ[['id', 'url', 'text']])
            
        drop = df[df['status'] == 'dropped'].copy()
        if len(drop) > 0:
            if 'reason' not in drop.columns:
                drop['reason'] = 'offtopic'
            recovered_dfs_drop.append(drop[['id', 'url', 'reason']])

    succ_all = pd.concat(recovered_dfs_succ, ignore_index=True) if recovered_dfs_succ else pd.DataFrame(columns=['id', 'url', 'text'])
    drop_all = pd.concat(recovered_dfs_drop, ignore_index=True) if recovered_dfs_drop else pd.DataFrame(columns=['id', 'url', 'reason'])
    
    print(f"\n2. Tổng số URL success thu được: {len(succ_all)}")
    print(f"   Tổng số URL dropped (rác) thu được: {len(drop_all)}")
    
    # Ép kiểu chuẩn và khử trùng lặp nội bộ
    if len(succ_all) > 0:
        succ_all['id'] = succ_all['id'].astype('int64')
        succ_all['url'] = succ_all['url'].astype('string')
        succ_all['text'] = succ_all['text'].astype('string')
        init_succ = len(succ_all)
        succ_all = succ_all.drop_duplicates(subset=['id']).drop_duplicates(subset=['url']).copy()
        print(f"   - Sau khử trùng lặp nội bộ success: {len(succ_all)} URLs (đã loại {init_succ - len(succ_all)})")
        
    if len(drop_all) > 0:
        # dropped_safe_offtopic_urls lưu id dạng str
        drop_all['id'] = drop_all['id'].astype(str)
        drop_all['url'] = drop_all['url'].astype(str)
        drop_all['reason'] = drop_all['reason'].astype(str)
        init_drop = len(drop_all)
        drop_all = drop_all.drop_duplicates(subset=['id']).drop_duplicates(subset=['url']).copy()
        print(f"   - Sau khử trùng lặp nội bộ dropped: {len(drop_all)} URLs (đã loại {init_drop - len(drop_all)})")

    # 3. Phân chia theo Domain / Host cho các URL success
    def get_tier(url_str):
        host = urlparse(str(url_str)).netloc.lower()
        tier1_hosts = [
            'tiemchunglongchau.com.vn', 'youmed.vn', 'ask.39.net', '120ask.com',
            'suckhoedoisong.vn', 'suckhoecongdongonline.vn', 'jb39.com',
            'vinmec.com', 'medlatec.vn', 'hellobacsi.com', 'nhathuoclongchau.com.vn',
            'youlai.cn', 'tamanhhospital.vn', 'thaythuocvietnam.vn', 'bachmai.gov.vn',
            'benhviennhitrunguong.gov.vn', 'benhvienvietduc.org', 'pharmacity.vn'
        ]
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

    # Đọc nhanh ID và URL của tier_1 để tránh trùng lặp vào bất kỳ tier nào
    t1_ids = set()
    t1_urls = set()
    t1_path = 'data/raw/final_corpus_text/tier_1.parquet'
    if os.path.exists(t1_path):
        t1_df = pd.read_parquet(t1_path, columns=['id', 'url'])
        t1_ids = set(t1_df['id'].tolist())
        t1_urls = set(t1_df['url'].tolist())

    # 4. Cập nhật từng file Tier cho URL success
    if len(succ_all) > 0:
        succ_all['target_tier'] = succ_all['url'].apply(get_tier)
        print("\n3. Phân bố các URL success theo tier:")
        print(succ_all['target_tier'].value_counts().to_string())

        tier_files = {
            'tier_1_resume': 'data/raw/final_corpus_text/tier_1_resume.parquet',
            'tier_2': 'data/raw/final_corpus_text/tier_2.parquet',
            'tier_other': 'data/raw/final_corpus_text/tier_other.parquet',
        }

        print("\n4. Tiến hành bổ sung vào các file Tier (an toàn không ghi đè):")
        for t_name, t_path in tier_files.items():
            candidates = succ_all[succ_all['target_tier'] == t_name][['id', 'url', 'text']].copy()
            if len(candidates) == 0:
                print(f"   >>> Bỏ qua {t_name} ({t_path}): Không có URL nào thuộc tier này.")
                continue

            bak_path = t_path + ".bak"
            if os.path.exists(t_path):
                shutil.copy2(t_path, bak_path)
                df_target = pd.read_parquet(t_path)
            else:
                df_target = pd.DataFrame(columns=['id', 'url', 'text'])

            existing_ids = set(df_target['id'].tolist())
            existing_urls = set(df_target['url'].tolist())

            # Luôn kiểm tra chống trùng với tier_1
            existing_ids.update(t1_ids)
            existing_urls.update(t1_urls)

            items_to_add = candidates[
                ~candidates['id'].isin(existing_ids) &
                ~candidates['url'].isin(existing_urls)
            ].copy()

            num_new = len(items_to_add)
            if num_new > 0:
                updated_df = pd.concat([df_target, items_to_add], ignore_index=True)
                # Đảm bảo dtypes
                updated_df['id'] = updated_df['id'].astype('int64')
                updated_df['url'] = updated_df['url'].astype('string')
                updated_df['text'] = updated_df['text'].astype('string')
                safe_to_parquet(updated_df, t_path)
                print(f"   >>> Xử lý {t_name} ({t_path}): Đã thêm {num_new} URLs mới (tổng {len(updated_df)})")
            else:
                print(f"   >>> Xử lý {t_name} ({t_path}): Tất cả {len(candidates)} ứng viên đã tồn tại trước đó.")

    # 4b. Xử lý dropped URLs
    if len(drop_all) > 0:
        print("\n4b. Xử lý các URL dropped (lưu vào dropped_safe_offtopic_urls.parquet)...")
        drop_path = 'data/raw/final_corpus_text/dropped_safe_offtopic_urls.parquet'
        if os.path.exists(drop_path):
            shutil.copy2(drop_path, drop_path + ".bak")
            df_existing_drop = pd.read_parquet(drop_path)
            df_existing_drop['id'] = df_existing_drop['id'].astype(str)
            df_existing_drop['url'] = df_existing_drop['url'].astype(str)
            if 'reason' not in df_existing_drop.columns:
                df_existing_drop['reason'] = 'offtopic'
            df_existing_drop['reason'] = df_existing_drop['reason'].astype(str)
            
            existing_drop_ids = set(df_existing_drop['id'].tolist())
            existing_drop_urls = set(df_existing_drop['url'].tolist())
            
            drop_to_add = drop_all[
                ~drop_all['id'].isin(existing_drop_ids) &
                ~drop_all['url'].isin(existing_drop_urls)
            ].copy()
            
            if len(drop_to_add) > 0:
                df_updated_drop = pd.concat([df_existing_drop, drop_to_add], ignore_index=True)
                df_updated_drop['id'] = df_updated_drop['id'].astype(str)
                df_updated_drop['url'] = df_updated_drop['url'].astype(str)
                df_updated_drop['reason'] = df_updated_drop['reason'].astype(str)
                safe_to_parquet(df_updated_drop, drop_path)
                print(f"   - Đã thêm {len(drop_to_add)} URLs vào file dropped (tổng {len(df_updated_drop)})")
            else:
                print(f"   - Tất cả {len(drop_all)} URLs dropped đã tồn tại trong file dropped.")
        else:
            safe_to_parquet(drop_all, drop_path)
            print(f"   - Đã tạo mới file dropped với {len(drop_all)} URLs")

    # 5. Xóa các URL đó trong remaining_urls files
    print("\n5. Đang xóa các URL đã xử lý (success + dropped) khỏi các file remaining_urls...")
    rem_files = [
        'data/raw/final_corpus_text/remaining_urls.parquet',
        'data/raw/final_corpus_text/remaining_urls_fast.parquet',
        'data/raw/final_corpus_text/remaining_urls_selenium.parquet'
    ]
    
    # Tập hợp tất cả các URL và ID cần loại bỏ (cả success lẫn dropped và tier_1)
    urls_to_remove = set()
    ids_to_remove = set()
    if len(succ_all) > 0:
        urls_to_remove.update(succ_all['url'].astype(str).tolist())
        ids_to_remove.update(succ_all['id'].astype(str).tolist())
    if len(drop_all) > 0:
        urls_to_remove.update(drop_all['url'].astype(str).tolist())
        ids_to_remove.update(drop_all['id'].astype(str).tolist())

    # Thêm cả các URL/ID đã có trong tier_1 để dọn sạch hàng đợi triệt để
    urls_to_remove.update(str(u) for u in t1_urls)
    ids_to_remove.update(str(i) for i in t1_ids)

    print(f"   - Tổng số URLs trong danh sách loại trừ: {len(urls_to_remove)} (từ {len(ids_to_remove)} IDs)")

    for rem_path in rem_files:
        if os.path.exists(rem_path):
            shutil.copy2(rem_path, rem_path + ".bak")
            df_rem = pd.read_parquet(rem_path)
            rem_init_len = len(df_rem)
            
            rem_urls = df_rem['url'].astype(str)
            rem_ids = df_rem['id'].astype(str)
            
            mask_keep = (~rem_urls.isin(urls_to_remove)) & (~rem_ids.isin(ids_to_remove))
            df_rem_filtered = df_rem[mask_keep].copy()
            
            rem_final_len = len(df_rem_filtered)
            num_deleted = rem_init_len - rem_final_len
            
            if num_deleted > 0:
                safe_to_parquet(df_rem_filtered, rem_path)
                print(f"   - {rem_path}: Đã xóa {num_deleted} URLs (từ {rem_init_len} -> còn {rem_final_len})")
            else:
                print(f"   - {rem_path}: Không có URL nào cần xóa (giữ nguyên {rem_init_len}).")

    # 6. Dọn dẹp thư mục local_recovered
    if not args.no_clean:
        print("\n6. Dọn dẹp các file recovered đã xử lý trong local_recovered...")
        deleted_count = 0
        for f in all_recovered_files:
            try:
                os.remove(f)
                deleted_count += 1
            except Exception as e:
                print(f"   ⚠️ Lỗi xóa file {f}: {e}")
        print(f"   - Đã xóa thành công {deleted_count}/{len(all_recovered_files)} files trong local_recovered.")
    else:
        print("\n6. Bỏ qua bước xóa file local_recovered (--no-clean được bật).")

    print("\n" + "=" * 70)
    print("🎉 HOÀN TẤT TOÀN BỘ QUY TRÌNH!")
    print(f"   - Đã xử lý: {len(succ_all)} URLs success và {len(drop_all)} URLs dropped.")
    print("=" * 70)

if __name__ == "__main__":
    main()
