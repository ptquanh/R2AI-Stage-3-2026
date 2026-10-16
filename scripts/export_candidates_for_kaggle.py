"""
Export Stage 1 Top Candidates for Kaggle Cross-Encoder Reranking.
Extracts Top 150 candidates per query using the sweet-spot Trilingual FAISS Hybrid configuration.
"""

import os
import sys
import time
import pickle
import numpy as np
import scipy.sparse as sp
import pandas as pd
from typing import Dict, List, Set, Tuple

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import faiss
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ExportCandidates")

CACHE_FILE = os.path.join(PROJECT_ROOT, "data", "indices", "new_dataset", ".cache", "query_encodings_1200.pkl")
INDEX_DIR = os.path.join(PROJECT_ROOT, "data", "indices", "new_dataset", "index")
QUERY_FILE = os.path.join(PROJECT_ROOT, "data", "raw", "btc_provided", "query_translated.parquet")
BTC_LINKS_FILE = os.path.join(PROJECT_ROOT, "data", "raw", "btc_provided", "links_corpus_vi_en_zh.parquet")
OUTPUT_PARQUET = os.path.join(PROJECT_ROOT, "data", "candidates_stage1_chunks250.parquet")


def build_fused_sparse_matrix(
    lex_vi: List[Dict[str, float]],
    lex_zh: List[Dict[str, float]],
    lex_en: List[Dict[str, float]],
    zh_w: float = 1.0,
    en_w: float = 0.5,
    vocab_size: int = 250005
) -> sp.csr_matrix:
    num_queries = len(lex_vi)
    rows, cols, data = [], [], []

    for q_idx in range(num_queries):
        merged = dict(lex_vi[q_idx])

        if zh_w > 0:
            for tok, val in lex_zh[q_idx].items():
                merged[tok] = max(merged.get(tok, 0.0), float(val) * zh_w)

        if en_w > 0:
            for tok, val in lex_en[q_idx].items():
                merged[tok] = max(merged.get(tok, 0.0), float(val) * en_w)

        for tok_id_str, weight in merged.items():
            tok_id = int(tok_id_str)
            if tok_id < vocab_size:
                rows.append(q_idx)
                cols.append(tok_id)
                data.append(float(weight))

    return sp.csr_matrix((data, (rows, cols)), shape=(num_queries, vocab_size), dtype=np.float32)


def main():
    t0 = time.time()
    logger.info("🚀 Starting Chunk-Level Stage 1 Candidate Extraction for Kaggle Reranking...")

    # 1. Load cached query encodings & query text
    if not os.path.exists(CACHE_FILE):
        raise FileNotFoundError(f"Cache file {CACHE_FILE} not found. Please run query encoding first.")

    logger.info(f"Loading cached query encodings from {CACHE_FILE}...")
    with open(CACHE_FILE, "rb") as f:
        cache_data = pickle.load(f)

    dense_q = cache_data["dense_q"]
    lex_vi = cache_data["lex_vi"]
    lex_zh = cache_data["lex_zh"]
    lex_en = cache_data["lex_en"]
    query_ids = cache_data["query_ids"]

    df_queries = pd.read_parquet(QUERY_FILE)
    queries_vi_map = dict(zip(df_queries["id"].values, df_queries["query"].values))
    queries_zh_map = dict(zip(df_queries["id"].values, df_queries["query_zh"].values))
    queries_en_map = dict(zip(df_queries["id"].values, df_queries["query_en"].values))

    # 2. Load valid BTC doc IDs
    logger.info(f"Loading valid doc IDs from {BTC_LINKS_FILE}...")
    df_links = pd.read_parquet(BTC_LINKS_FILE, columns=["id"])
    valid_doc_ids = set(df_links["id"].values)
    del df_links
    logger.info(f"Loaded {len(valid_doc_ids):,} valid BTC doc IDs.")

    # 3. Load metadata & FAISS index
    meta_path = os.path.join(INDEX_DIR, "chunks_metadata.parquet")
    logger.info(f"Loading metadata from {meta_path}...")
    df_meta = pd.read_parquet(meta_path, columns=["doc_id", "start", "end"])
    doc_ids_arr = df_meta["doc_id"].values
    starts_arr = df_meta["start"].values
    ends_arr = df_meta["end"].values
    del df_meta

    faiss_bin = os.path.join(INDEX_DIR, "faiss_index_flat_ip.bin")
    logger.info(f"Reading FAISS memory-mapped index from {faiss_bin}...")
    faiss_index = faiss.read_index(faiss_bin, faiss.IO_FLAG_MMAP)

    sparse_npz = os.path.join(INDEX_DIR, "sparse_csr.npz")
    logger.info(f"Loading Sparse CSR matrix from {sparse_npz}...")
    corpus_sparse = sp.load_npz(sparse_npz)

    # 4. Hybrid Search Configuration (Sweet-spot: zh=1.0, en=0.5, sparse_w=0.20, buffer=500)
    cand_buffer = 500
    target_chunks = 200
    min_unique_docs = 110
    max_chunks = 250
    sparse_w = 0.20

    logger.info(f"Running FAISS Dense search (buffer={cand_buffer}) for {len(query_ids)} queries...")
    dense_norm = dense_q.astype(np.float32)
    faiss.normalize_L2(dense_norm)
    t_faiss = time.time()
    scores_dense, top_indices = faiss_index.search(dense_norm, cand_buffer)
    logger.info(f"Dense search completed in {time.time() - t_faiss:.2f}s.")

    logger.info("Building fused sparse query matrix (zh_w=1.0, en_w=0.5)...")
    q_sparse = build_fused_sparse_matrix(lex_vi, lex_zh, lex_en, zh_w=1.0, en_w=0.5)

    # 5. Rescore and pick Top 200-250 candidate chunks (preserving multiple chunks per doc!)
    logger.info("Computing Hybrid scores and selecting chunk-level candidates...")
    needed_doc_ids: Set[int] = set()
    staged_cands: List[List[Tuple[float, int, int, int]]] = [[] for _ in range(len(query_ids))]

    for q_idx in range(len(query_ids)):
        c_indices = top_indices[q_idx, :cand_buffer]
        d_scores = scores_dense[q_idx, :cand_buffer]

        sub_sparse = corpus_sparse[c_indices]
        s_scores = sub_sparse.dot(q_sparse[q_idx].T).toarray().ravel()
        hybrid_scores = d_scores + sparse_w * s_scores

        sort_order = np.argsort(hybrid_scores)[::-1]
        seen_chunks = set()
        seen_docs = set()
        cands_for_q = []

        for r in sort_order:
            row_idx = c_indices[r]
            d_id = int(doc_ids_arr[row_idx])
            if d_id not in valid_doc_ids:
                continue

            start = int(starts_arr[row_idx])
            end = int(ends_arr[row_idx])
            chunk_key = (d_id, start, end)

            if chunk_key not in seen_chunks:
                seen_chunks.add(chunk_key)
                seen_docs.add(d_id)
                needed_doc_ids.add(d_id)
                score = float(hybrid_scores[r])
                cands_for_q.append((score, d_id, start, end))

            # Stop condition: enough chunks AND enough unique documents
            if len(cands_for_q) >= target_chunks and len(seen_docs) >= min_unique_docs:
                break
            if len(cands_for_q) >= max_chunks:
                break

        staged_cands[q_idx] = cands_for_q

    logger.info(f"Identified {len(needed_doc_ids):,} unique candidate docs across all 1,200 queries.")

    # 6. Lazy load text shards for candidate docs
    t_text = time.time()
    import glob
    text_dir = os.path.join(INDEX_DIR, "text")
    part_files = sorted(glob.glob(os.path.join(text_dir, "part_*.parquet")))
    texts_map: Dict[int, str] = {}

    for p in part_files:
        try:
            df_t = pd.read_parquet(p, columns=["doc_id", "text"])
            sub = df_t[df_t["doc_id"].isin(needed_doc_ids)]
            for row in sub.itertuples(index=False):
                texts_map[int(row.doc_id)] = str(row.text)
            if len(texts_map) >= len(needed_doc_ids):
                break
        except Exception as e:
            logger.warning(f"Error reading {p}: {e}")

    logger.info(f"Loaded {len(texts_map):,}/{len(needed_doc_ids):,} candidate doc texts in {time.time() - t_text:.2f}s.")

    # 7. Materialize into structured DataFrame
    logger.info("Materializing candidate DataFrame...")
    records = []
    for q_idx, q_id in enumerate(query_ids):
        q_vi = queries_vi_map.get(q_id, "")
        q_zh = queries_zh_map.get(q_id, "")
        q_en = queries_en_map.get(q_id, "")

        for rank, (score, doc_id, start, end) in enumerate(staged_cands[q_idx], start=1):
            full_text = texts_map.get(doc_id, "")
            chunk_text = full_text[start:end] if full_text else ""

            records.append({
                "query_id": int(q_id),
                "query_vi": q_vi,
                "query_zh": q_zh,
                "query_en": q_en,
                "doc_id": int(doc_id),
                "chunk_text": chunk_text,
                "stage1_score": float(score),
                "stage1_rank": int(rank)
            })

    df_out = pd.DataFrame(records)
    logger.info(f"Generated {len(df_out):,} candidate rows. Saving to {OUTPUT_PARQUET}...")
    df_out.to_parquet(OUTPUT_PARQUET, index=False, compression="snappy")

    file_size_mb = os.path.getsize(OUTPUT_PARQUET) / (1024 * 1024)
    logger.info(f"✅ Successfully exported candidates to {OUTPUT_PARQUET} ({file_size_mb:.2f} MB) in {time.time() - t0:.2f}s!")


if __name__ == "__main__":
    main()
