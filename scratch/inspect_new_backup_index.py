import os, glob
import pandas as pd

new_backup_dir = "data/indices/new_dataset/index_backup_unembedded_samples_0-100-20261014T033450Z-1-001/index_backup_unembedded_samples_0-100"
p_docs = sorted(glob.glob(os.path.join(new_backup_dir, "docs", "part_*.parquet")))
print(f"Found {len(p_docs)} doc part files in {new_backup_dir}")

backup_doc_ids = set()
for p in p_docs:
    df_p = pd.read_parquet(p, columns=["doc_id"])
    backup_doc_ids.update(df_p["doc_id"].unique())

print(f"Total unique doc_ids in new backup index: {len(backup_doc_ids):,}")

# Compare with unembedded_samples
p_unemb = "data/unembedded_samples.parquet"
df_unemb = pd.read_parquet(p_unemb, columns=["id"])
unemb_ids = set(df_unemb["id"].unique())
print(f"Total IDs in unembedded_samples.parquet: {len(unemb_ids):,}")

overlap_unemb = unemb_ids.intersection(backup_doc_ids)
print(f"Overlap with unembedded_samples: {len(overlap_unemb):,} / {len(backup_doc_ids):,} ({len(overlap_unemb)/len(backup_doc_ids)*100:.2f}%)")

# Compare with embedded_samples
p_emb = "data/embedded_samples.parquet"
df_emb = pd.read_parquet(p_emb, columns=["id"])
emb_ids = set(df_emb["id"].unique())
print(f"Total IDs in embedded_samples.parquet: {len(emb_ids):,}")

overlap_emb = emb_ids.intersection(backup_doc_ids)
print(f"Overlap with embedded_samples: {len(overlap_emb):,} / {len(backup_doc_ids):,} ({len(overlap_emb)/len(backup_doc_ids)*100:.2f}%)")

# Check if there are any other folders in data/indices
print("\nChecking any other doc parts across all of data/indices:")
all_doc_parts = sorted(glob.glob("data/indices/**/docs/part_*.parquet", recursive=True))
for dp in all_doc_parts:
    df_dp = pd.read_parquet(dp, columns=["doc_id"])
    print(f"  {dp}: {len(df_dp):,} rows, {df_dp['doc_id'].nunique():,} unique doc_ids")
