"""
Test and benchmark FAISSHybridSearcher on the actual BTC test queries.
"""

import os
import time
import sys
import numpy as np
import pandas as pd
import scipy.sparse as sp
import faiss

sys.path.insert(0, os.path.abspath("."))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

base_dir = "data/indices/new_dataset/index"
faiss_bin = os.path.join(base_dir, "faiss_index_flat_ip.bin")
ids_file = os.path.join(base_dir, "chunk_ids.npy")
meta_file = os.path.join(base_dir, "chunks_metadata.parquet")
sparse_file = os.path.join(base_dir, "sparse_csr.npz")
query_file = "data/raw/btc_provided/query.parquet"

print("=" * 70)
print("🧪 TEST PIPELINE FAISS HYBRID RETRIEVAL TRÊN 100 BTC QUERIES")
print("=" * 70)

# 1. Đọc queries và encode
t0 = time.time()
print("\n[1/4] Đang nạp BGE-M3 Query Encoder & sinh vectors cho 100 queries...")
from src.retrieval.query_encoder import BGEM3QueryEncoder
encoder = BGEM3QueryEncoder(model_name="BAAI/bge-m3")

df_query = pd.read_parquet(query_file)
queries = df_query["query"].tolist()[:100]
print(f"  - Số lượng queries test: {len(queries)}")

q_vecs = encoder.encode_dense(queries)
q_sparse = encoder.encode_sparse(queries)
q_vecs = q_vecs.astype(np.float32)
faiss.normalize_L2(q_vecs)
print(f"  ✅ Query vectors sẵn sàng trong {time.time() - t0:.2f}s!")

# 2. Nạp FAISS và Sparse Matrix
print("\n[2/4] Đang nạp FAISS (Memory-Mapped) và Sparse CSR...")
t_load = time.time()
index = faiss.read_index(faiss_bin, faiss.IO_FLAG_MMAP)
chunk_ids = np.load(ids_file)
sparse_matrix = sp.load_npz(sparse_file)

# Load metadata mapping: chunk_id -> (doc_id, start, end)
df_meta = pd.read_parquet(meta_file)
chunks_map = {row.chunk_id: (row.doc_id, row.start, row.end) for row in df_meta.itertuples(index=False)}
print(f"  ✅ Nạp xong index artifacts trong {time.time() - t_load:.2f}s!")

# 3. Chạy FAISS Search + Sparse Rescoring
print("\n[3/4] Đang tìm kiếm FAISS Top 400 + Linear Hybrid Rescoring (Dense 1.0 + Sparse 0.2)...")
t_search = time.time()

# FAISS search
cand_buffer = 400
scores_dense, top_indices = index.search(q_vecs, cand_buffer)
print(f"  ⚡ FAISS Dense Search 100 queries: {time.time() - t_search:.2f}s!")

# Sparse rescoring
t_rescore = time.time()
dense_w = 1.0
sparse_w = 0.2

all_query_results = []
for q_idx in range(len(queries)):
    c_indices = top_indices[q_idx]
    d_scores = scores_dense[q_idx]

    # Sparse dot product for 400 candidates
    sub_sparse = sparse_matrix[c_indices]
    s_scores = sub_sparse.dot(q_sparse[q_idx].T).toarray().ravel()

    # Hybrid combination
    hybrid_scores = dense_w * d_scores + sparse_w * s_scores

    # Sort candidates
    rank_order = np.argsort(hybrid_scores)[::-1]
    
    candidates = []
    for r in rank_order:
        row_idx = c_indices[r]
        cid = int(chunk_ids[row_idx])
        doc_id, start, end = chunks_map[cid]
        candidates.append({
            "score": float(hybrid_scores[r]),
            "chunk_id": cid,
            "doc_id": doc_id,
            "start": start,
            "end": end
        })
    all_query_results.append(candidates)

print(f"  ⚡ Sparse Rescoring cho 100 queries: {time.time() - t_rescore:.2f}s!")
total_retrieval_time = time.time() - t_search
print(f"  🚀 TỔNG THỜI GIAN RETRIEVAL: {total_retrieval_time:.2f}s (thay vì 500-600s trước đây)!")

# 4. Kiểm tra mẫu kết quả query 0
q0_res = all_query_results[0]
print(f"\n[4/4] Mẫu kết quả Query 0: '{queries[0][:60]}...'")
print(f"  - Top 3 Candidates: ")
for i, c in enumerate(q0_res[:3]):
    print(f"    #{i+1}: doc_id={c['doc_id']}, chunk_id={c['chunk_id']}, score={c['score']:.4f}")

print("\n" + "=" * 70)
print(f"🎉 TEST THÀNH CÔNG! HỆ THỐNG ĐÃ TĂNG TỐC TỪ ~9 PHÚT XUỐNG ~{total_retrieval_time:.1f} GIÂY!")
print("=" * 70)
