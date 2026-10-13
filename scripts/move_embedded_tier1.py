import glob
import os
import zipfile
import io
import shutil
import sys
import pandas as pd
import pyarrow.parquet as pq

sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("=" * 80)
    print("🚀 ĐỒNG BỘ TOÀN DIỆN: TIER 1 INDEX -> TIER 1 PARQUET & DỌN DẸP TIER 1 RESUME")
    print("=" * 80)

    t1_path = 'data/raw/final_corpus_text/tier_1.parquet'
    t1_res_path = 'data/raw/final_corpus_text/tier_1_resume.parquet'

    # 1. Đọc dữ liệu hiện tại
    print("\n1. Đọc dữ liệu hiện có trong tier_1.parquet và tier_1_resume.parquet...")
    t1_df = pd.read_parquet(t1_path)
    t1_df['id'] = t1_df['id'].astype('int64')
    t1_df['url'] = t1_df['url'].astype('string')
    t1_df['text'] = t1_df['text'].astype('string')

    t1_res_df = pd.read_parquet(t1_res_path)
    t1_res_df['id'] = t1_res_df['id'].astype('int64')
    t1_res_df['url'] = t1_res_df['url'].astype('string')
    t1_res_df['text'] = t1_res_df['text'].astype('string')

    t1_existing_ids = set(t1_df['id'].tolist())
    t1_existing_urls = set(t1_df['url'].tolist())

    print(f"   - tier_1.parquet hiện có:        {len(t1_df):,} records")
    print(f"   - tier_1_resume.parquet hiện có: {len(t1_res_df):,} records")

    # 2. Quét toàn bộ các shard trong data/indices/tier 1
    print("\n2. Quét các shard trong data/indices/tier 1 để kiểm tra độ đầy đủ...")
    shards = sorted(os.listdir('data/indices/tier 1'))

    all_indexed_ids = set()
    all_indexed_urls = set()
    shards_to_recover = []

    for s in shards:
        sp = os.path.join('data/indices/tier 1', s)
        shard_ids = set()
        
        # Bỏ qua file zip nếu đã có thư mục giải nén tương ứng
        if s.endswith('.zip'):
            folder_name = s[:-4]
            if folder_name in shards and os.path.isdir(os.path.join('data/indices/tier 1', folder_name)):
                continue

        if os.path.isdir(sp):
            docs_files = sorted(glob.glob(os.path.join(sp, '**', 'docs', '*.parquet'), recursive=True))
            for df_path in docs_files:
                try:
                    df_doc = pd.read_parquet(df_path, columns=['doc_id', 'url'])
                    shard_ids.update(df_doc['doc_id'].astype('int64').tolist())
                    all_indexed_ids.update(df_doc['doc_id'].astype('int64').tolist())
                    all_indexed_urls.update(df_doc['url'].dropna().tolist())
                except Exception as e:
                    print(f"   - Lỗi đọc {df_path}: {e}")
        elif s.endswith('.zip'):
            try:
                with zipfile.ZipFile(sp, 'r') as z:
                    for n in z.namelist():
                        if 'docs' in n and n.endswith('.parquet'):
                            df_doc = pd.read_parquet(io.BytesIO(z.read(n)), columns=['doc_id', 'url'])
                            shard_ids.update(df_doc['doc_id'].astype('int64').tolist())
                            all_indexed_ids.update(df_doc['doc_id'].astype('int64').tolist())
                            all_indexed_urls.update(df_doc['url'].dropna().tolist())
            except Exception as e:
                print(f"   - Lỗi đọc zip {sp}: {e}")

        # Kiểm tra xem shard này đã có trong t1_df chưa
        in_t1_count = len(shard_ids.intersection(t1_existing_ids))
        if in_t1_count < len(shard_ids):
            shards_to_recover.append((s, shard_ids))
            print(f"   Shard {s:<15}: có {len(shard_ids):,} docs | Đã có trong tier_1: {in_t1_count:,} -> CẦN BỔ SUNG")
        else:
            print(f"   Shard {s:<15}: có {len(shard_ids):,} docs | Đã có đầy đủ trong tier_1")

    print(f"\n📊 Tổng số IDs đã index trong tier 1:  {len(all_indexed_ids):,}")
    print(f"📊 Tổng số URLs đã index trong tier 1: {len(all_indexed_urls):,}")

    # 3. Phục hồi dữ liệu từ các shard bị thiếu vào danh sách bổ sung
    recovered_dfs = []
    print(f"\n3. Đang trích xuất dữ liệu gốc từ {len(shards_to_recover)} shards còn thiếu...")
    t1_res_ids_set = set(t1_res_df['id'].tolist())

    for s, shard_ids in shards_to_recover:
        sp = os.path.join('data/indices/tier 1', s)
        
        # Nếu toàn bộ docs của shard này đã có sẵn trong tier_1_resume, step 4 sẽ chuyển trực tiếp
        missing_from_both = shard_ids - t1_existing_ids - t1_res_ids_set
        if not missing_from_both:
            print(f"   - Shard {s}: Toàn bộ {len(shard_ids):,} docs đã có sẵn trong tier_1_resume (sẽ chuyển trực tiếp ở bước 4)")
            continue

        # Nếu có docs chỉ nằm trong index mà không có trong tier_1_resume, đọc docs và texts từ shard
        print(f"   - Shard {s}: Có {len(missing_from_both):,} docs chưa có trong resume, đang nạp từ đĩa...")
        df_docs = None
        df_texts = None
        
        if os.path.isdir(sp):
            docs_files = sorted(glob.glob(os.path.join(sp, '**', 'docs', '*.parquet'), recursive=True))
            text_files = sorted(glob.glob(os.path.join(sp, '**', 'text', '*.parquet'), recursive=True))
            
            if docs_files and text_files:
                df_docs = pd.concat([pd.read_parquet(f, columns=['doc_id', 'url']) for f in docs_files], ignore_index=True)
                df_texts = pd.concat([pd.read_parquet(f, columns=['doc_id', 'text']) for f in text_files], ignore_index=True)
        elif s.endswith('.zip'):
            with zipfile.ZipFile(sp, 'r') as z:
                doc_dfs = []
                txt_dfs = []
                for n in z.namelist():
                    if 'docs/' in n and n.endswith('.parquet'):
                        doc_dfs.append(pd.read_parquet(io.BytesIO(z.read(n)), columns=['doc_id', 'url']))
                    elif 'text/' in n and n.endswith('.parquet'):
                        txt_dfs.append(pd.read_parquet(io.BytesIO(z.read(n)), columns=['doc_id', 'text']))
                if doc_dfs and txt_dfs:
                    df_docs = pd.concat(doc_dfs, ignore_index=True)
                    df_texts = pd.concat(txt_dfs, ignore_index=True)

        if df_docs is not None and df_texts is not None:
            # Deduplicate text & merge
            df_texts = df_texts.drop_duplicates(subset=['doc_id'], keep='last')
            df_docs['doc_id'] = df_docs['doc_id'].astype('int64')
            df_texts['doc_id'] = df_texts['doc_id'].astype('int64')
            
            merged = pd.merge(df_docs, df_texts, on='doc_id', how='left')
            merged.rename(columns={'doc_id': 'id'}, inplace=True)
            merged['id'] = merged['id'].astype('int64')
            merged['url'] = merged['url'].astype('string')
            merged['text'] = merged['text'].astype('string')

            # Lọc bỏ những gì đã có trong tier_1
            new_items = merged[~merged['id'].isin(t1_existing_ids) & ~merged['url'].isin(t1_existing_urls)].copy()
            if len(new_items) > 0:
                recovered_dfs.append(new_items)
                print(f"   - Shard {s}: Phục hồi thành công {len(new_items):,} records từ đĩa")

    # 4. Kiểm tra xem có URLs nào từ tier_1_resume thuộc index cần chuyển sang tier_1 không
    is_res_indexed = t1_res_df['id'].isin(all_indexed_ids) | t1_res_df['url'].isin(all_indexed_urls)
    from_res_to_move = t1_res_df[is_res_indexed].copy()
    keep_in_res = t1_res_df[~is_res_indexed].copy()

    # Bỏ qua những records từ resume nếu đã có trong t1
    clean_from_res = from_res_to_move[
        ~from_res_to_move['id'].isin(t1_existing_ids) &
        ~from_res_to_move['url'].isin(t1_existing_urls)
    ].copy()

    if len(clean_from_res) > 0:
        recovered_dfs.append(clean_from_res)
        print(f"   - Từ tier_1_resume: Chuyển thêm {len(clean_from_res):,} records đã index")

    # 5. Gộp vào tier_1 và kiểm tra trùng lặp nội bộ
    print("\n4. Hợp nhất dữ liệu vào tier_1 và kiểm tra tính duy nhất (Unique Deduplication)...")
    if recovered_dfs:
        all_new_data = pd.concat(recovered_dfs, ignore_index=True)
        all_new_data = all_new_data.drop_duplicates(subset=['id']).drop_duplicates(subset=['url'])
        final_t1 = pd.concat([t1_df, all_new_data], ignore_index=True)
    else:
        final_t1 = t1_df.copy()

    final_t1 = final_t1.drop_duplicates(subset=['id']).drop_duplicates(subset=['url']).reset_index(drop=True)
    
    # Dọn dẹp tier_1_resume: chỉ giữ lại những gì CHƯA CÓ trong index và CHƯA CÓ trong final_t1
    final_t1_ids = set(final_t1['id'].tolist())
    final_t1_urls = set(final_t1['url'].tolist())

    final_res = keep_in_res[
        ~keep_in_res['id'].isin(final_t1_ids) &
        ~keep_in_res['url'].isin(final_t1_urls)
    ].drop_duplicates(subset=['id']).drop_duplicates(subset=['url']).reset_index(drop=True)

    print(f"   - tier_1 sau khi hợp nhất:        {len(final_t1):,} records")
    print(f"   - tier_1_resume sau khi dọn dẹp:   {len(final_res):,} records")

    # 6. Ghi an toàn bằng Safe Atomic Write (File .tmp -> Verify -> os.replace)
    print("\n5. Thực hiện ghi dữ liệu an toàn (Safe Atomic Write)...")
    t1_tmp = t1_path + '.tmp'
    res_tmp = t1_res_path + '.tmp'

    # Ghi ra file tạm
    final_t1.to_parquet(t1_tmp, index=False, engine='pyarrow')
    final_res.to_parquet(res_tmp, index=False, engine='pyarrow')

    # Xác thực file tạm không bị hỏng (valid footer & correct row count)
    meta_t1 = pq.read_metadata(t1_tmp)
    meta_res = pq.read_metadata(res_tmp)
    assert meta_t1.num_rows == len(final_t1), "Lỗi: Số dòng file tạm tier_1 không khớp!"
    assert meta_res.num_rows == len(final_res), "Lỗi: Số dòng file tạm tier_1_resume không khớp!"
    print("   - Xác thực file tạm hoàn tất: Footer hợp lệ, metadata toàn vẹn 100%.")

    # Sao lưu file cũ
    shutil.copy2(t1_path, t1_path + '.bak')
    shutil.copy2(t1_res_path, t1_res_path + '.bak')

    # Đổi tên nguyên tử (Atomic replace)
    os.replace(t1_tmp, t1_path)
    os.replace(res_tmp, t1_res_path)
    print("   - Hoán đổi atomic replace thành công vào tier_1.parquet và tier_1_resume.parquet!")

    # 7. Nghiệm thu tổng thể
    print("\n" + "=" * 80)
    print("✅ KẾT QUẢ NGHIỆM THU TỔNG THỂ:")
    print(f"   1. tier_1.parquet:        {len(final_t1):,} records (Đã index, Unique IDs: {final_t1['id'].nunique():,}, Unique URLs: {final_t1['url'].nunique():,})")
    print(f"   2. tier_1_resume.parquet: {len(final_res):,} records (Chưa index, Unique IDs: {final_res['id'].nunique():,}, Unique URLs: {final_res['url'].nunique():,})")
    
    overlap_ids = set(final_t1['id'].tolist()).intersection(set(final_res['id'].tolist()))
    overlap_urls = set(final_t1['url'].tolist()).intersection(set(final_res['url'].tolist()))
    print(f"   3. Trùng lặp ID giữa 2 file:  {len(overlap_ids)}")
    print(f"   4. Trùng lặp URL giữa 2 file: {len(overlap_urls)}")
    print(f"   5. Tỷ lệ khớp với index:      {len(final_t1):,} / {len(all_indexed_ids):,} ({len(final_t1)/len(all_indexed_ids)*100:.2f}%)")
    print("=" * 80)

if __name__ == "__main__":
    main()
