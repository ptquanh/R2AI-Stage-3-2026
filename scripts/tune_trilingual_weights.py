import os
import sys
import time
import pickle
import numpy as np
import scipy.sparse as sp
import pandas as pd
from typing import Dict, List, Set, Tuple, Any

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import faiss
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TuneTrilingual")

from src.retrieval.query_encoder import BGEM3QueryEncoder
from src.retrieval.faiss_searcher import FAISSSearcher
from src.retrieval.index_repository import IndexRepository

CACHE_DIR = os.path.join(PROJECT_ROOT, "data", "indices", "new_dataset", ".cache")
CACHE_FILE = os.path.join(CACHE_DIR, "query_encodings_1200.pkl")
INDEX_DIR = os.path.join(PROJECT_ROOT, "data", "indices", "new_dataset", "index")
QUERY_FILE = os.path.join(PROJECT_ROOT, "data", "raw", "btc_provided", "query_translated.parquet")
BTC_LINKS_FILE = os.path.join(PROJECT_ROOT, "data", "raw", "btc_provided", "links_corpus_vi_en_zh.parquet")


def get_or_create_query_encodings():
    os.makedirs(CACHE_DIR, exist_ok=True)
    if os.path.exists(CACHE_FILE):
        logger.info(f"Loading cached query encodings from {CACHE_FILE}...")
        with open(CACHE_FILE, "rb") as f:
            data = pickle.load(f)
        return data["dense_q"], data["lex_vi"], data["lex_zh"], data["lex_en"], data["query_ids"]

    logger.info("Cache not found. Encoding 1,200 trilingual queries with BGE-M3...")
    df = pd.read_parquet(QUERY_FILE)
    queries_vi = df["query"].tolist()
    queries_zh = df["query_zh"].tolist()
    queries_en = df["query_en"].tolist()
    query_ids = df["id"].tolist()

    encoder = BGEM3QueryEncoder()
    encoder._ensure_model_loaded()

    logger.info("Encoding Vietnamese dense vectors...")
    dense_q = encoder.encode_dense(queries_vi)

    logger.info("Encoding Vietnamese sparse lexical...")
    enc_vi = encoder._model.encode(queries_vi, batch_size=8, max_length=1024, return_dense=False, return_sparse=True)
    lex_vi = [dict(w) for w in enc_vi["lexical_weights"]]

    logger.info("Encoding Chinese sparse lexical...")
    enc_zh = encoder._model.encode(queries_zh, batch_size=8, max_length=1024, return_dense=False, return_sparse=True)
    lex_zh = [dict(w) for w in enc_zh["lexical_weights"]]

    logger.info("Encoding English sparse lexical...")
    enc_en = encoder._model.encode(queries_en, batch_size=8, max_length=1024, return_dense=False, return_sparse=True)
    lex_en = [dict(w) for w in enc_en["lexical_weights"]]

    encoder.unload()

    data = {
        "dense_q": dense_q,
        "lex_vi": lex_vi,
        "lex_zh": lex_zh,
        "lex_en": lex_en,
        "query_ids": query_ids
    }
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    logger.info(f"Query encodings cached to {CACHE_FILE}!")
    return dense_q, lex_vi, lex_zh, lex_en, query_ids


def build_fused_sparse_matrix(
    lex_vi: List[Dict[str, float]],
    lex_zh: List[Dict[str, float]],
    lex_en: List[Dict[str, float]],
    zh_w: float,
    en_w: float,
    vocab_size: int = 250005
) -> sp.csr_matrix:
    num_queries = len(lex_vi)
    rows, cols, data = [], [], []

    for q_idx in range(num_queries):
        merged = dict(lex_vi[q_idx])

        # Merge Chinese
        if zh_w > 0:
            for tok, val in lex_zh[q_idx].items():
                merged[tok] = max(merged.get(tok, 0.0), float(val) * zh_w)

        # Merge English
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
    dense_q, lex_vi, lex_zh, lex_en, query_ids = get_or_create_query_encodings()

    # Load valid doc IDs
    index_repo = IndexRepository(index_base=os.path.dirname(INDEX_DIR))
    valid_doc_ids = index_repo.load_valid_doc_ids(BTC_LINKS_FILE)
    logger.info(f"Loaded {len(valid_doc_ids):,} valid BTC doc IDs.")

    # Load metadata
    meta_path = os.path.join(INDEX_DIR, "chunks_metadata.parquet")
    logger.info(f"Loading chunks metadata from {meta_path}...")
    df_meta = pd.read_parquet(meta_path, columns=["doc_id"])
    doc_ids_arr = df_meta["doc_id"].values
    del df_meta

    # Load FAISS Index
    faiss_bin = os.path.join(INDEX_DIR, "faiss_index_flat_ip.bin")
    logger.info(f"Reading FAISS index from {faiss_bin}...")
    faiss_index = faiss.read_index(faiss_bin, faiss.IO_FLAG_MMAP)
    num_total_chunks = faiss_index.ntotal

    # Load Sparse matrix
    sparse_npz = os.path.join(INDEX_DIR, "sparse_csr.npz")
    logger.info(f"Loading sparse CSR from {sparse_npz}...")
    corpus_sparse = sp.load_npz(sparse_npz)

    # Define Tuning Configurations
    # Baseline: Exp 36 (zh=1.0, en=0.5, sparse_w=0.20, buffer=400)
    tuning_configs = [
        {"name": "Exp36_Baseline",     "zh_w": 1.0, "en_w": 0.5, "sparse_w": 0.20, "buffer": 400},
        # English Weight Tuning
        {"name": "EN_Low_0.3",         "zh_w": 1.0, "en_w": 0.3, "sparse_w": 0.20, "buffer": 400},
        {"name": "EN_High_0.8",        "zh_w": 1.0, "en_w": 0.8, "sparse_w": 0.20, "buffer": 400},
        {"name": "EN_Equal_1.0",       "zh_w": 1.0, "en_w": 1.0, "sparse_w": 0.20, "buffer": 400},
        # Chinese Weight Tuning
        {"name": "ZH_Low_0.8",         "zh_w": 0.8, "en_w": 0.5, "sparse_w": 0.20, "buffer": 400},
        {"name": "ZH_High_1.2",        "zh_w": 1.2, "en_w": 0.5, "sparse_w": 0.20, "buffer": 400},
        # Sparse Weight (Linear Hybrid Sensitivity)
        {"name": "Sparse_Low_0.15",    "zh_w": 1.0, "en_w": 0.5, "sparse_w": 0.15, "buffer": 400},
        {"name": "Sparse_High_0.25",   "zh_w": 1.0, "en_w": 0.5, "sparse_w": 0.25, "buffer": 400},
        # Combined Best Hypothesis (English-Rich with Mild Sparse)
        {"name": "EN0.8_Sparse0.15",   "zh_w": 1.0, "en_w": 0.8, "sparse_w": 0.15, "buffer": 400},
        {"name": "EN0.8_Sparse0.25",   "zh_w": 1.0, "en_w": 0.8, "sparse_w": 0.25, "buffer": 400},
        # Expanded Candidate Buffer
        {"name": "Buffer_800",         "zh_w": 1.0, "en_w": 0.5, "sparse_w": 0.20, "buffer": 800},
        {"name": "Buffer_800_EN0.8",   "zh_w": 1.0, "en_w": 0.8, "sparse_w": 0.20, "buffer": 800},
    ]

    max_buffer = max(cfg["buffer"] for cfg in tuning_configs)
    logger.info(f"Running FAISS Dense search with max_buffer={max_buffer} for 1,200 queries...")
    dense_norm = dense_q.astype(np.float32)
    faiss.normalize_L2(dense_norm)
    t_f = time.time()
    scores_dense_all, top_indices_all = faiss_index.search(dense_norm, max_buffer)
    logger.info(f"FAISS Dense Search completed in {time.time() - t_f:.2f}s.")

    # Cache fused sparse matrices for unique (zh_w, en_w) pairs
    unique_pairs = {(cfg["zh_w"], cfg["en_w"]) for cfg in tuning_configs}
    sparse_matrices: Dict[Tuple[float, float], sp.csr_matrix] = {}
    for zh_w, en_w in unique_pairs:
        sparse_matrices[(zh_w, en_w)] = build_fused_sparse_matrix(lex_vi, lex_zh, lex_en, zh_w, en_w)

    results_by_config: Dict[str, List[List[int]]] = {}

    logger.info("Executing candidate ranking for each configuration...")
    for cfg in tuning_configs:
        cfg_name = cfg["name"]
        zh_w, en_w = cfg["zh_w"], cfg["en_w"]
        sw = cfg["sparse_w"]
        buf = cfg["buffer"]
        q_sparse = sparse_matrices[(zh_w, en_w)]

        top100_docs_list: List[List[int]] = []

        for q_idx in range(len(query_ids)):
            c_indices = top_indices_all[q_idx, :buf]
            d_scores = scores_dense_all[q_idx, :buf]

            sub_sparse = corpus_sparse[c_indices]
            s_scores = sub_sparse.dot(q_sparse[q_idx].T).toarray().ravel()

            hybrid_scores = d_scores + sw * s_scores

            # Sort descending
            sort_order = np.argsort(hybrid_scores)[::-1]
            seen_docs = set()
            rel_docs = []

            for r in sort_order:
                row_idx = c_indices[r]
                d_id = int(doc_ids_arr[row_idx])
                if valid_doc_ids is not None and d_id not in valid_doc_ids:
                    continue
                if d_id not in seen_docs:
                    seen_docs.add(d_id)
                    rel_docs.append(d_id)
                    if len(rel_docs) == 100:
                        break

            top100_docs_list.append(rel_docs)

        results_by_config[cfg_name] = top100_docs_list
        logger.info(f"Finished candidate selection for config '{cfg_name}'.")

    # -------------------------------------------------------------
    # COMPARATIVE SHIFT ANALYSIS vs BASELINE (Exp36_Baseline)
    # -------------------------------------------------------------
    base_results = results_by_config["Exp36_Baseline"]

    # Load URL domain mapping for domain analysis
    logger.info("Loading URL domain map for deep domain breakdown...")
    df_links = pd.read_parquet(BTC_LINKS_FILE)
    id_to_url = dict(zip(df_links["id"].values, df_links["url"].values))
    del df_links

    from urllib.parse import urlparse

    def get_domain(doc_id: int) -> str:
        u = id_to_url.get(doc_id, "")
        if not u:
            return "unknown"
        netloc = urlparse(u).netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc or "unknown"

    print("\n" + "=" * 105)
    print("BANG PHAN TICH CANDIDATE SHIFT DA NGU (SO VOI EXP 36 BASELINE)")
    print("=" * 105)
    print(f"{'Config Name':<20} | {'zh_w':<5} | {'en_w':<5} | {'sp_w':<5} | {'buf':<5} | {'Avg Jaccard':<12} | {'Avg Overlap':<12} | {'New Docs/Q':<11} | {'Total New':<10}")
    print("-" * 105)

    summary_rows = []
    for cfg in tuning_configs:
        cfg_name = cfg["name"]
        cand_list = results_by_config[cfg_name]

        jaccards = []
        overlaps = []
        new_docs_per_q = []
        all_new_docs_set = set()

        for q_idx in range(len(query_ids)):
            b_set = set(base_results[q_idx])
            c_set = set(cand_list[q_idx])

            intersection = len(b_set.intersection(c_set))
            union = len(b_set.union(c_set))
            jaccard = intersection / union if union > 0 else 1.0

            jaccards.append(jaccard)
            overlaps.append(intersection)
            new_in_q = c_set - b_set
            new_docs_per_q.append(len(new_in_q))
            all_new_docs_set.update(new_in_q)

        avg_jaccard = np.mean(jaccards)
        avg_overlap = np.mean(overlaps)
        avg_new_per_q = np.mean(new_docs_per_q)
        total_new_docs = len(all_new_docs_set)

        # Domain breakdown of new docs
        domain_counts: Dict[str, int] = {}
        for d_id in all_new_docs_set:
            dom = get_domain(d_id)
            domain_counts[dom] = domain_counts.get(dom, 0) + 1

        top_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        top_dom_str = ", ".join([f"{d}:{cnt}" for d, cnt in top_domains]) if top_domains else "None"

        summary_rows.append({
            "name": cfg_name,
            "zh_w": cfg["zh_w"],
            "en_w": cfg["en_w"],
            "sparse_w": cfg["sparse_w"],
            "buffer": cfg["buffer"],
            "avg_jaccard": avg_jaccard,
            "avg_overlap": avg_overlap,
            "avg_new_per_q": avg_new_per_q,
            "total_new_docs": total_new_docs,
            "top_domains": top_dom_str
        })

        print(f"{cfg_name:<20} | {cfg['zh_w']:<5.1f} | {cfg['en_w']:<5.1f} | {cfg['sparse_w']:<5.2f} | {cfg['buffer']:<5} | {avg_jaccard:<12.4f} | {avg_overlap:<12.1f} | {avg_new_per_q:<11.1f} | {total_new_docs:<10,}")

    print("=" * 105)
    print("\nTOP DOMAINS CUA CAC TAI LIEU MOI DUOC KEO VAO:")
    for row in summary_rows:
        if row["total_new_docs"] > 0:
            print(f" - [{row['name']}]: {row['top_domains']}")

    print(f"\nToan bo phan tich hoan tat trong {time.time() - t0:.2f}s!")


if __name__ == "__main__":
    main()
