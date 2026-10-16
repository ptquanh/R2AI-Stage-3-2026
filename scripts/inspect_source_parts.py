import os
import glob
import pandas as pd
import numpy as np

src_dir = 'data/indices/new_dataset/index_backup_unembedded_samples_0-100_2/index_backup_unembedded_samples_0-100_2'

print("Source chunks:")
chunk_files = sorted(glob.glob(os.path.join(src_dir, 'chunks', 'part_*.parquet')))
for cf in chunk_files:
    df = pd.read_parquet(cf)
    print(f"  {os.path.basename(cf)}: rows={len(df):,}, cols={df.columns.tolist()}, min_id={df['chunk_id'].min():,}, max_id={df['chunk_id'].max():,}")

print("\nSource text:")
text_files = sorted(glob.glob(os.path.join(src_dir, 'text', 'part_*.parquet')))
total_text_rows = 0
for tf in text_files:
    df = pd.read_parquet(tf, columns=['doc_id'])
    total_text_rows += len(df)
    print(f"  {os.path.basename(tf)}: rows={len(df):,}")
print(f"Total text rows: {total_text_rows:,}")

print("\nSource emb_dense:")
emb_dir = os.path.join(src_dir, 'emb_dense')
id_files = sorted(glob.glob(os.path.join(emb_dir, 'ids_*.npy')))
total_emb_rows = 0
for id_f in id_files:
    ids = np.load(id_f)
    total_emb_rows += len(ids)
    vec_f = id_f.replace('ids_', 'vec_')
    sp_f = id_f.replace('ids_', 'sp_').replace('.npy', '.npz')
    vec_sz = os.path.getsize(vec_f) / (1024*1024)
    sp_sz = os.path.getsize(sp_f) / (1024*1024)
    print(f"  {os.path.basename(id_f)}: len={len(ids):,}, min={ids.min():,}, max={ids.max():,} | vec: {vec_sz:.1f} MB | sp: {sp_sz:.1f} MB")
print(f"Total emb rows: {total_emb_rows:,}")
