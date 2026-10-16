import os, glob
import pandas as pd

p_unemb = 'data/unembedded_samples.parquet'
p_emb = 'data/embedded_samples.parquet'

print(f"Checking {p_unemb}:", flush=True)
if os.path.exists(p_unemb):
    df_u_ids = pd.read_parquet(p_unemb, columns=['id'])
    print(f"  Rows: {len(df_u_ids):,}", flush=True)
    print(f"  Unique IDs: {df_u_ids['id'].nunique():,}", flush=True)
    unemb_ids = set(df_u_ids['id'].unique())
else:
    print("  Does not exist!", flush=True)
    unemb_ids = set()

print(f"\nChecking {p_emb}:", flush=True)
if os.path.exists(p_emb):
    df_e_ids = pd.read_parquet(p_emb, columns=['id'])
    print(f"  Rows: {len(df_e_ids):,}", flush=True)
    print(f"  Unique IDs: {df_e_ids['id'].nunique():,}", flush=True)
    emb_ids = set(df_e_ids['id'].unique())
else:
    print("  Does not exist!", flush=True)
    emb_ids = set()

print("\nChecking all index metadata files:", flush=True)
meta_files = sorted(glob.glob('data/indices/**/chunks_metadata.parquet', recursive=True))
all_index_doc_ids = set()
for m in meta_files:
    df_m = pd.read_parquet(m, columns=['doc_id'])
    n_docs = df_m['doc_id'].nunique()
    print(f"  {m}: {len(df_m):,} chunks, {n_docs:,} unique doc_ids", flush=True)
    all_index_doc_ids.update(df_m['doc_id'].unique())

print(f"\nTotal unique doc_ids across all index folders: {len(all_index_doc_ids):,}", flush=True)

# Check overlap
overlap_unemb = unemb_ids.intersection(all_index_doc_ids)
print(f"Overlap between unembedded_samples and index: {len(overlap_unemb):,} / {len(unemb_ids):,} ({len(overlap_unemb)/max(len(unemb_ids), 1)*100:.2f}%)", flush=True)

overlap_emb = emb_ids.intersection(all_index_doc_ids)
print(f"Overlap between embedded_samples and index: {len(overlap_emb):,} / {len(emb_ids):,} ({len(overlap_emb)/max(len(emb_ids), 1)*100:.2f}%)", flush=True)

missing_in_emb = all_index_doc_ids - emb_ids
print(f"Index doc_ids missing in embedded_samples: {len(missing_in_emb):,}", flush=True)

overlap_between_emb_unemb = emb_ids.intersection(unemb_ids)
print(f"Overlap between embedded_samples and unembedded_samples: {len(overlap_between_emb_unemb):,}", flush=True)
