"""
Kaggle Notebook Cross-Encoder Reranker for R2AI Stage 3 2026.
Runs on Kaggle GPU (Tesla T4 x 2 / P100) with fp16 and batch_size=128.
Processes 180k (Query, Chunk) candidate pairs in ~2-4 minutes!
"""

import os
import gc
import json
import zipfile
import time
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple

# 1. Install FlagEmbedding if running on Kaggle
# !pip install -q FlagEmbedding

from FlagEmbedding import FlagReranker


def find_candidates_file() -> str:
    """Finds candidates parquet file in Kaggle input or current directory."""
    possible_paths = [
        "candidates_stage1_chunks250.parquet",
        "/kaggle/input/candidates_stage1_chunks250.parquet",
        "/kaggle/working/candidates_stage1_chunks250.parquet",
        "candidates_stage1_top150.parquet",
        "/kaggle/input/candidates_stage1_top150.parquet",
    ]
    # Check any subfolder in /kaggle/input
    if os.path.exists("/kaggle/input"):
        for root, _, files in os.walk("/kaggle/input"):
            for f in files:
                if f.endswith(".parquet") and "candidate" in f.lower():
                    return os.path.join(root, f)

    for p in possible_paths:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("Could not find candidates parquet file! Please upload candidates_stage1_chunks250.parquet to Kaggle.")


def main():
    t0 = time.time()
    input_file = find_candidates_file()
    print(f"📂 Loading candidate pairs from: {input_file}...")
    df = pd.read_parquet(input_file)
    print(f"Loaded {len(df):,} candidate rows across {df['query_id'].nunique():,} unique queries.")

    # 2. Form Language-Aligned Pairs
    print("🧠 Forming cross-lingual pairs (Chinese chunks -> query_zh, English chunks -> query_en, etc.)...")
    pairs: List[List[str]] = []
    
    for row in df.itertuples(index=False):
        chunk_text = str(row.chunk_text or "")
        
        # Detect Chinese characters
        is_zh = any('\u4e00' <= char <= '\u9fff' for char in chunk_text[:200])
        # Detect predominantly English text (Latin characters, high ratio)
        ascii_chars = sum(1 for c in chunk_text[:200] if ord(c) < 128 and c.isalpha())
        is_en = (ascii_chars / max(len(chunk_text[:200]), 1)) > 0.75 and not any(ord(c) > 255 for c in chunk_text[:100])

        if is_zh and hasattr(row, "query_zh") and row.query_zh and str(row.query_zh).strip():
            q_text = str(row.query_zh)
        elif is_en and hasattr(row, "query_en") and row.query_en and str(row.query_en).strip():
            q_text = str(row.query_en)
        else:
            q_text = str(row.query_vi)

        pairs.append([q_text, chunk_text])

    print(f"Total pairs formed: {len(pairs):,}")

    # 3. Load FlagReranker on GPU
    print("\n🚀 Loading BAAI/bge-reranker-v2-m3 (FP16)...")
    reranker = FlagReranker("BAAI/bge-reranker-v2-m3", use_fp16=True)

    # 4. Compute Scores in Batches
    batch_size = 128
    max_length = 512
    print(f"⚡ Scoring {len(pairs):,} pairs (batch_size={batch_size}, max_length={max_length})...")
    t_score = time.time()
    
    scores = reranker.compute_score(
        pairs,
        batch_size=batch_size,
        max_length=max_length
    )
    if isinstance(scores, (int, float)):
        scores = [float(scores)]
    
    df["reranker_score"] = scores
    print(f"✅ Scoring completed in {time.time() - t_score:.2f}s ({(len(pairs)/(time.time() - t_score)):.1f} pairs/sec)!")

    # Release model memory
    del reranker, pairs
    gc.collect()

    # 5. Hybrid Score Blending & Candidate Selection
    # S_final = 0.25 * norm(stage1_score) + 0.75 * norm(reranker_score)
    print("\n🎯 Applying Hybrid Score Blending (75% Cross-Encoder + 25% Stage 1)...")
    
    # Min-max normalize per query for safe interpolation
    def normalize_group(g):
        s1 = g["stage1_score"].values
        s2 = g["reranker_score"].values
        
        s1_norm = (s1 - s1.min()) / (s1.max() - s1.min() + 1e-6) if s1.max() > s1.min() else np.ones_like(s1)
        s2_norm = (s2 - s2.min()) / (s2.max() - s2.min() + 1e-6) if s2.max() > s2.min() else np.ones_like(s2)
        
        g["final_score"] = 0.75 * s2_norm + 0.25 * s1_norm
        return g

    df = df.groupby("query_id", group_keys=False).apply(normalize_group)

    # 6. Extract Top 100 Documents & Top 98 Chunks per query
    print("📦 Extracting Top 100 Documents and Top 98 Chunks...")
    submission_data = []

    for q_id, group in df.groupby("query_id"):
        # Sort descending by final score
        sorted_g = group.sort_values("final_score", ascending=False)

        seen_docs = set()
        seen_chunks = set()
        relevant_docs = []
        relevant_chunks = []

        for row in sorted_g.itertuples(index=False):
            doc_id = int(row.doc_id)
            chunk_txt = str(row.chunk_text or "").strip()

            if doc_id not in seen_docs and len(relevant_docs) < 100:
                seen_docs.add(doc_id)
                relevant_docs.append(doc_id)

            if chunk_txt and chunk_txt not in seen_chunks and len(relevant_chunks) < 98:
                seen_chunks.add(chunk_txt)
                relevant_chunks.append({
                    "doc_id": doc_id,
                    "chunk_text": chunk_txt
                })

        submission_data.append({
            "id": int(q_id),
            "relevant_docs": relevant_docs,
            "relevant_chunks": relevant_chunks
        })

    # Sort queries by id
    submission_data.sort(key=lambda x: x["id"])

    # 7. Export to JSON & Zip
    out_json = "submission_bgem3_cross_encoder_reranked.json"
    out_zip = "submission_bgem3_cross_encoder_reranked.zip"

    print(f"Writing {len(submission_data)} queries to {out_json}...")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(submission_data, f, ensure_ascii=False, indent=2)

    print(f"Compressing to {out_zip}...")
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(out_json, arcname="submission.json")

    # 8. Integrity Validation
    zip_size_mb = os.path.getsize(out_zip) / (1024 * 1024)
    avg_docs = np.mean([len(item["relevant_docs"]) for item in submission_data])
    avg_chunks = np.mean([len(item["relevant_chunks"]) for item in submission_data])

    print("\n" + "=" * 70)
    print("✨ SUBMISSION RERANKED HOÀN TẤT!")
    print(f" - Tổng số câu hỏi: {len(submission_data)} / 1,200")
    print(f" - Trung bình Docs / Query: {avg_docs:.1f}")
    print(f" - Trung bình Chunks / Query: {avg_chunks:.1f}")
    print(f" - Dung lượng file ZIP: {zip_size_mb:.2f} MB (An toàn < 100 MB: {zip_size_mb < 100})")
    print(f" - Tổng thời gian chạy: {time.time() - t0:.2f}s")
    print("=" * 70)


if __name__ == "__main__":
    main()
