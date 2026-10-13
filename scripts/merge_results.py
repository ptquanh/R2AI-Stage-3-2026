import os
import sys
import glob
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("1. Đọc dữ liệu đã cào được từ local_recovered...")
    rec_files = glob.glob("data/raw/corpus_text/local_recovered/*.parquet")
    if not rec_files:
        print("Không có file nào trong local_recovered.")
        return
        
    df_rec = pd.concat([pd.read_parquet(f) for f in rec_files], ignore_index=True)
    df_rec['id'] = df_rec['id'].astype(str)
    df_rec = df_rec.drop_duplicates(subset=['id'], keep='last')
    
    df_succ = df_rec[df_rec['status'] == 'success']
    df_drop = df_rec[df_rec['status'] == 'dropped']
    
    print(f"Tổng hợp: {len(df_succ):,} bài thành công, {len(df_drop):,} bài rác (dropped).")
    
    # Lấy set id đã xử lý để xóa khỏi remaining
    processed_ids = set(df_rec['id'].tolist())
    
    print("\n2. Cập nhật các file tier...")
    tier_files = [
        "data/raw/final_corpus_text/tier_1_resume.parquet",
        "data/raw/final_corpus_text/tier_2.parquet",
        "data/raw/final_corpus_text/tier_other.parquet"
    ]
    
    for tf in tier_files:
        if os.path.exists(tf):
            df_tier = pd.read_parquet(tf)
            df_tier['id'] = df_tier['id'].astype(str)
            # Tạo dictionary mapping id -> text
            succ_mapping = dict(zip(df_succ['id'], df_succ['text']))
            
            # Đếm xem có bao nhiêu id thuộc tier này
            matched_ids = set(df_tier['id']).intersection(set(df_succ['id']))
            if matched_ids:
                print(f"  - {tf}: Tìm thấy {len(matched_ids):,} bài. Đang cập nhật text...")
                # Update text cho những dòng match
                # Hàm map sẽ trả về NaN nếu không có trong succ_mapping, nên ta dùng fillna để giữ lại text cũ (nếu có)
                df_tier['text'] = df_tier['id'].map(succ_mapping).fillna(df_tier['text'])
                
                # Lưu lại
                df_tier.to_parquet(tf, index=False)
            else:
                print(f"  - {tf}: Không có bài mới nào thuộc tier này.")
                
    print("\n3. Lưu các bài rác vào dropped_safe_offtopic_urls.parquet...")
    drop_file = "data/raw/final_corpus_text/dropped_safe_offtopic_urls.parquet"
    if len(df_drop) > 0:
        if os.path.exists(drop_file):
            df_old_drop = pd.read_parquet(drop_file)
            df_old_drop['id'] = df_old_drop['id'].astype(str)
            df_new_drop = pd.concat([df_old_drop, df_drop[['id', 'url', 'reason']]], ignore_index=True).drop_duplicates(subset=['id'])
            df_new_drop.to_parquet(drop_file, index=False)
        else:
            df_drop[['id', 'url', 'reason']].to_parquet(drop_file, index=False)
        print(f"Đã lưu {len(df_drop):,} bài rác.")

    print("\n4. Xóa các URL đã cào khỏi danh sách remaining...")
    rem_files = [
        "data/raw/final_corpus_text/remaining_urls.parquet",
        "data/raw/final_corpus_text/remaining_urls_fast.parquet",
        "data/raw/final_corpus_text/remaining_urls_selenium.parquet"
    ]
    
    for rf in rem_files:
        if os.path.exists(rf):
            df_rem = pd.read_parquet(rf)
            df_rem['id'] = df_rem['id'].astype(str)
            old_len = len(df_rem)
            df_rem = df_rem[~df_rem['id'].isin(processed_ids)]
            new_len = len(df_rem)
            if old_len != new_len:
                df_rem.to_parquet(rf, index=False)
                print(f"  - {rf}: Đã xóa {old_len - new_len:,} URLs (Còn lại {new_len:,})")
            
    print("\n🎉 HOÀN TẤT GOM DỮ LIỆU!")
    print("Gợi ý: Bây giờ bạn có thể xóa toàn bộ file trong local_recovered để dọn dẹp không gian.")

if __name__ == "__main__":
    main()
