import glob, os, sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

INDEX_BASE = 'data/indices'
chunk_marker_dirs = sorted(glob.glob(os.path.join(INDEX_BASE, '**', 'chunks'), recursive=True))
unique_shard_dirs = []
seen_signatures = {}

print("=== KIỂM TRA TỰ ĐỘNG DEDUPLICATE SHARDS ===")
for d in chunk_marker_dirs:
    s_dir = os.path.dirname(d)
    p_files = sorted(glob.glob(os.path.join(d, 'part_*.parquet')))
    if not p_files:
        continue
    df_sig = pd.read_parquet(p_files[0], columns=['doc_id'])
    sig = (len(p_files), len(df_sig), tuple(df_sig['doc_id'].iloc[:5].tolist()))
    rel_path = os.path.relpath(s_dir, INDEX_BASE).replace('\\', '/')
    if sig in seen_signatures:
        prev_rel = os.path.relpath(seen_signatures[sig], INDEX_BASE).replace('\\', '/')
        print(f"⚠️ [DEDUPLICATE SKIP] Khối '{rel_path}' trùng 100% với '{prev_rel}' -> Tự động bỏ qua!")
    else:
        seen_signatures[sig] = s_dir
        unique_shard_dirs.append(s_dir)

print(f"\n-> Tổng số shard quét được: {len(chunk_marker_dirs)}")
print(f"-> Tổng số shard DUY NHẤT giữ lại: {len(unique_shard_dirs)}")
for s in unique_shard_dirs:
    print('   •', os.path.relpath(s, INDEX_BASE).replace('\\', '/'))
