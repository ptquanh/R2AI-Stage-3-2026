import pandas as pd
import numpy as np
import sys
from FlagEmbedding import BGEM3FlagModel

sys.stdout.reconfigure(encoding='utf-8')

df_q = pd.read_parquet('data/raw/btc_provided/query_translated.parquet')
queries = df_q['query'].iloc[:3].tolist()
model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)
enc = model.encode(queries, return_dense=True, return_sparse=False)
q_vecs = np.array(enc['dense_vecs']).astype(np.float32)

c_vecs = np.load('data/indices/tier 1/1300-1400k/index/emb_dense/vec_0000.npy').astype(np.float32)
scores = q_vecs @ c_vecs.T

for i, q in enumerate(queries):
    top15 = np.sort(scores[i])[::-1][:15]
    print(f"\nQ{i+1}: '{q}'")
    print("   Top 15 dense scores:", [round(float(x), 4) for x in top15])
    print(f"   Count >= 0.73: {sum(1 for x in scores[i] if x >= 0.73)}")
    print(f"   Count >= 0.70: {sum(1 for x in scores[i] if x >= 0.70)}")
    print(f"   Count >= 0.65: {sum(1 for x in scores[i] if x >= 0.65)}")
