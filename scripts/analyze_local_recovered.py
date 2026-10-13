import glob
import os
import sys
from urllib.parse import urlparse
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

rec_files = sorted(glob.glob('data/raw/corpus_text/local_recovered/*.parquet'))
print(f"Total part files in local_recovered: {len(rec_files)}")

if not rec_files:
    print("No files found!")
    sys.exit(0)

dfs = []
for f in rec_files:
    try:
        df = pd.read_parquet(f)
        dfs.append(df)
    except Exception as e:
        print(f"Error reading {f}: {e}")

if not dfs:
    print("No data!")
    sys.exit(0)

all_df = pd.concat(dfs, ignore_index=True)
print(f"Total records in local_recovered: {len(all_df):,}")
print("Columns:", all_df.columns.tolist())

print("\n" + "=" * 60)
print("1. STATUS DISTRIBUTION")
print("=" * 60)
if 'status' in all_df.columns:
    print(all_df['status'].value_counts(dropna=False))

print("\n" + "=" * 60)
print("2. REASON DISTRIBUTION (FOR DROPPED / ERROR)")
print("=" * 60)
if 'reason' in all_df.columns:
    print(all_df['reason'].value_counts(dropna=False).head(20))

print("\n" + "=" * 60)
print("3. DOMAIN BREAKDOWN BY STATUS")
print("=" * 60)
if 'url' in all_df.columns:
    all_df['domain'] = all_df['url'].apply(lambda u: urlparse(str(u)).netloc)
    print(pd.crosstab(all_df['domain'], all_df['status'], margins=True).sort_values(by='All', ascending=False).head(25))

print("\n" + "=" * 60)
print("4. SUCCESS SAMPLES - TEXT LENGTH & LANGUAGE")
print("=" * 60)
df_succ = all_df[all_df['status'] == 'success'] if 'status' in all_df.columns else all_df
print(f"Total SUCCESS samples: {len(df_succ):,}")
if len(df_succ) > 0 and 'text' in df_succ.columns:
    lens = df_succ['text'].dropna().apply(len)
    print(lens.describe())
    
    # Language detection rough check (Vietnamese vs Chinese vs others)
    def detect_lang(t):
        if not t or not isinstance(t, str):
            return 'empty'
        has_zh = any('\u4e00' <= c <= '\u9fff' for c in t[:300])
        if has_zh:
            return 'zh'
        # Check Vietnamese specific diacritics
        vn_chars = set('àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđĐ')
        if any(c in vn_chars for c in t[:300]):
            return 'vi'
        return 'en/other'
        
    df_succ['lang'] = df_succ['text'].apply(detect_lang)
    print("\nLanguage breakdown of SUCCESS:")
    print(df_succ['lang'].value_counts())

print("\n" + "=" * 60)
print("5. CROSS-CHECK WITH CORPUS TIERS & REMAINING QUEUES")
print("=" * 60)
tier_files = {
    'tier_1': 'data/raw/final_corpus_text/tier_1.parquet',
    'tier_1_resume': 'data/raw/final_corpus_text/tier_1_resume.parquet',
    'tier_2': 'data/raw/final_corpus_text/tier_2.parquet',
    'tier_other': 'data/raw/final_corpus_text/tier_other.parquet',
    'remaining_fast': 'data/raw/final_corpus_text/remaining_urls_fast.parquet',
    'remaining_selenium': 'data/raw/final_corpus_text/remaining_urls_selenium.parquet',
    'dropped_safe': 'data/raw/final_corpus_text/dropped_safe_offtopic_urls.parquet'
}

succ_ids = set(df_succ['id'].astype(str)) if len(df_succ) > 0 else set()
succ_urls = set(df_succ['url'].astype(str)) if len(df_succ) > 0 else set()

df_drop = all_df[all_df['status'] == 'dropped'] if 'status' in all_df.columns else pd.DataFrame()
drop_ids = set(df_drop['id'].astype(str)) if len(df_drop) > 0 else set()
drop_urls = set(df_drop['url'].astype(str)) if len(df_drop) > 0 else set()

print("\n--- PHÂN BỔ 22,766 SUCCESS URLs THEO CÁC TIER ---")
for name, path in tier_files.items():
    if os.path.exists(path):
        df_target = pd.read_parquet(path, columns=['id', 'url'])
        target_ids = set(df_target['id'].astype(str))
        target_urls = set(df_target['url'].astype(str))
        overlap_ids = len(succ_ids.intersection(target_ids))
        overlap_urls = len(succ_urls.intersection(target_urls))
        print(f"Overlap with {name:<20}: IDs={overlap_ids:,} | URLs={overlap_urls:,}")

print("\n--- PHÂN BỔ 28,264 DROPPED URLs THEO CÁC TIER ---")
for name, path in tier_files.items():
    if os.path.exists(path):
        df_target = pd.read_parquet(path, columns=['id', 'url'])
        target_ids = set(df_target['id'].astype(str))
        target_urls = set(df_target['url'].astype(str))
        overlap_ids = len(drop_ids.intersection(target_ids))
        overlap_urls = len(drop_urls.intersection(target_urls))
        print(f"Overlap with {name:<20}: IDs={overlap_ids:,} | URLs={overlap_urls:,}")

