import os, glob, json, argparse, time, sys, zipfile
import numpy as np
import pandas as pd
import scipy.sparse as sp
from FlagEmbedding import BGEM3FlagModel

sys.stdout.reconfigure(encoding='utf-8')

DEFAULT_QUERY_FILE = "data/raw/btc_provided/query_translated.parquet"
FALLBACK_QUERY_FILE = "data/raw/btc_provided/query.parquet"
INDEX_BASE = "data/indices"
VOCAB_SIZE = 250005

def parse_args():
    parser = argparse.ArgumentParser(description="Multilingual Retrieval with BGE-M3 (Dense, Sparse, Hybrid, RRF).")
    parser.add_argument("--query_file", type=str, default=None,
                        help="Path to query parquet file (default: query_translated.parquet if exists else query.parquet)")
    parser.add_argument("--mode", type=str, choices=["dense", "sparse", "hybrid"], default="hybrid",
                        help="Retrieval mode: dense, sparse, or hybrid (default: hybrid)")
    parser.add_argument("--fusion", type=str, choices=["linear", "rrf"], default="rrf",
                        help="Fusion strategy in hybrid mode: linear (score sum) or rrf (reciprocal rank fusion, default: rrf)")
    parser.add_argument("--dense_weight", type=float, default=1.0,
                        help="Weight for dense retrieval (default: 1.0)")
    parser.add_argument("--sparse_weight", type=float, default=1.0,
                        help="Weight for sparse lexical retrieval (default: 1.0)")
    parser.add_argument("--multi_sparse_weights", type=float, nargs="+", default=None,
                        help="List of sparse weights to test simultaneously in one pass, e.g. --multi_sparse_weights 0.5 1.0 1.5")
    parser.add_argument("--rrf_k", type=int, default=60,
                        help="Constant k for Reciprocal Rank Fusion: 1 / (k + rank) (default: 60)")
    parser.add_argument("--zh_weight", type=float, default=1.0,
                        help="Scaling factor for translated Chinese lexical tokens (default: 1.0)")
    parser.add_argument("--cand_pool", type=int, default=150,
                        help="Number of candidates to retain per shard per modality in RRF (default: 150)")
    parser.add_argument("--top_docs", type=int, default=100,
                        help="Maximum relevant documents to output per query (default: 100)")
    parser.add_argument("--top_chunks", type=int, default=98,
                        help="Maximum relevant chunks to output per query (default: 98 for optimal zip <100MB)")
    parser.add_argument("--rerank", action="store_true",
                        help="Enable 2-stage Cross-Encoder reranking")
    parser.add_argument("--rerank_cand_docs", type=int, default=200,
                        help="Number of candidate documents to retrieve in stage 1 for reranking (default: 200)")
    parser.add_argument("--reranker_model", type=str, default="BAAI/bge-reranker-v2-m3",
                        help="Cross-Encoder model for reranking")
    parser.add_argument("--reranker_batch_size", type=int, default=64,
                        help="Batch size for cross-encoder reranking")
    parser.add_argument("--output", type=str, default=None,
                        help="Output JSON filename")
    return parser.parse_args()

def build_query_sparse_matrix(lexical_weights_list, vocab_size=VOCAB_SIZE):
    rows, cols, data = [], [], []
    for q_idx, weights in enumerate(lexical_weights_list):
        for tok_id_str, w in weights.items():
            tok_id = int(tok_id_str)
            if tok_id < vocab_size:
                rows.append(q_idx)
                cols.append(tok_id)
                data.append(float(w))
    if not data:
        return sp.csr_matrix((len(lexical_weights_list), vocab_size), dtype=np.float32)
    return sp.csr_matrix((data, (rows, cols)), shape=(len(lexical_weights_list), vocab_size), dtype=np.float32)

def main():
    args = parse_args()
    mode = args.mode
    fusion = args.fusion if mode == "hybrid" else "linear"

    # Select query file
    query_path = args.query_file
    if query_path is None:
        if os.path.exists(DEFAULT_QUERY_FILE):
            query_path = DEFAULT_QUERY_FILE
        else:
            query_path = FALLBACK_QUERY_FILE

    # Configure run modes / targets
    if args.multi_sparse_weights:
        mode = "hybrid"
        configs = []
        for sw in args.multi_sparse_weights:
            sw_tag = f"{fusion}_w{str(sw).replace('.', '')}"
            out_json = f"submission_bgem3_{sw_tag}.json"
            out_zip = f"submission_bgem3_{sw_tag}.zip"
            configs.append({
                "dense_w": args.dense_weight,
                "sparse_w": sw,
                "tag": sw_tag,
                "out_json": out_json,
                "out_zip": out_zip,
            })
    else:
        if args.output:
            out_json = args.output
        elif args.rerank:
            out_json = f"submission_bgem3_rerank_cand{args.rerank_cand_docs}_top{args.top_docs}.json"
        else:
            out_json = f"submission_bgem3_{mode}_{fusion}.json"
        out_zip = out_json.replace(".json", ".zip")
        configs = [{
            "dense_w": args.dense_weight,
            "sparse_w": args.sparse_weight,
            "tag": "single",
            "out_json": out_json,
            "out_zip": out_zip,
        }]

    print("=" * 70)
    print(f"🚀 MULTILINGUAL BGE-M3 RETRIEVAL PIPELINE")
    print(f"   Mode: {mode.upper()} | Fusion: {fusion.upper()}")
    print(f"   Query file: {query_path}")
    print(f"   Rerank Enabled: {args.rerank}")
    if args.rerank:
        print(f"   Stage 1 Candidates: {args.rerank_cand_docs} -> Reranked Top Docs: {args.top_docs}, Top Chunks: {args.top_chunks}")
        print(f"   Reranker Model: {args.reranker_model} (batch_size={args.reranker_batch_size})")
    print(f"   Configs to evaluate: {len(configs)}")
    for i, cfg in enumerate(configs):
        print(f"   [{i+1}] Dense: {cfg['dense_w']:.2f} | Sparse: {cfg['sparse_w']:.2f} -> {cfg['out_zip']}")
    print(f"   RRF k: {args.rrf_k} | Cand pool per shard: {args.cand_pool}")
    print(f"   Top Docs: {args.top_docs} | Top Chunks: {args.top_chunks}")
    print("=" * 70, flush=True)

    print("\n=== 1. Khởi tạo BGE-M3 (FP16) ===", flush=True)
    model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)

    print(f"\n=== 2. Đọc dữ liệu query từ {query_path} ===", flush=True)
    df_q = pd.read_parquet(query_path)
    queries = df_q['query'].tolist()
    q_ids = df_q['id'].tolist()
    num_queries = len(queries)
    has_zh = 'query_zh' in df_q.columns and (df_q['query_zh'] != '').any()
    queries_zh = df_q['query_zh'].fillna('').tolist() if has_zh else None
    print(f"Đã đọc {num_queries} queries. Hỗ trợ tiếng Trung: {'CÓ (Đa ngữ)' if has_zh else 'KHÔNG (Chỉ tiếng Việt)'}", flush=True)

    print(f"\n=== 3. Đang mã hóa queries (Mode: {mode}) ===", flush=True)
    t0 = time.time()
    need_dense = mode in ["dense", "hybrid"]
    need_sparse = mode in ["sparse", "hybrid"]

    q_vecs = None
    if need_dense:
        print("  - Đang mã hóa Dense vectors (tiếng Việt)...", flush=True)
        enc_dense = model.encode(
            queries,
            batch_size=8,
            max_length=1024,
            return_dense=True,
            return_sparse=False,
            return_colbert_vecs=False
        )
        q_vecs = np.array(enc_dense['dense_vecs']).astype(np.float32)
        print(f"    Dense vectors shape: {q_vecs.shape}", flush=True)

    Q_sparse = None
    if need_sparse:
        print("  - Đang mã hóa Sparse lexical weights (tiếng Việt)...", flush=True)
        enc_vi_sp = model.encode(
            queries,
            batch_size=8,
            max_length=1024,
            return_dense=False,
            return_sparse=True,
            return_colbert_vecs=False
        )
        lexical_vi = enc_vi_sp['lexical_weights']

        if has_zh:
            print(f"  - Đang mã hóa Sparse lexical weights (tiếng Trung, weight={args.zh_weight})...", flush=True)
            enc_zh_sp = model.encode(
                queries_zh,
                batch_size=8,
                max_length=1024,
                return_dense=False,
                return_sparse=True,
                return_colbert_vecs=False
            )
            lexical_zh = enc_zh_sp['lexical_weights']

            print("  - Đang hợp nhất Lexical Weights (Max Fusion: Vi + Zh)...", flush=True)
            fused_lexical = []
            for w_v, w_z in zip(lexical_vi, lexical_zh):
                merged = dict(w_v)
                for tok, val in w_z.items():
                    merged[tok] = max(merged.get(tok, 0.0), float(val) * args.zh_weight)
                fused_lexical.append(merged)
            Q_sparse = build_query_sparse_matrix(fused_lexical, vocab_size=VOCAB_SIZE)
        else:
            Q_sparse = build_query_sparse_matrix(lexical_vi, vocab_size=VOCAB_SIZE)

        print(f"    Sparse query matrix shape: {Q_sparse.shape}, non-zeros: {Q_sparse.nnz}", flush=True)

    print(f"Mã hóa queries hoàn tất trong {time.time() - t0:.2f} giây.", flush=True)

    # Giải phóng VRAM của BGE-M3 để dành toàn bộ GPU cho Reranker sau này
    del model
    import torch
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    print("  -> Đã giải phóng bộ nhớ VRAM của BGE-M3.", flush=True)

    # Initialize candidate collectors
    # For linear fusion: cfg["results"][q_idx] = [(score, doc_id, chunk_text)]
    # For RRF: dense_cand_pool[q_idx] = [(score, chunk_id, doc_id, chunk_text)]
    #          sparse_cand_pool[q_idx] = [(score, chunk_id, doc_id, chunk_text)]
    if fusion == "linear":
        for cfg in configs:
            cfg["results"] = [[] for _ in range(num_queries)]
    else:
        dense_cand_pool = [[] for _ in range(num_queries)]
        sparse_cand_pool = [[] for _ in range(num_queries)]

    # Discover all shard directories automatically under INDEX_BASE
    chunk_marker_dirs = sorted(glob.glob(os.path.join(INDEX_BASE, "**", "chunks"), recursive=True))
    shard_dirs = [os.path.dirname(d) for d in chunk_marker_dirs]

    print("\n=== 4. Bắt đầu tìm kiếm trên các khối dữ liệu ===", flush=True)
    print(f"   Tìm thấy {len(shard_dirs)} khối chỉ mục (shards):", flush=True)
    for s in shard_dirs:
        print(f"    • {os.path.relpath(s, INDEX_BASE).replace(chr(92), '/')}", flush=True)

    t_search_start = time.time()
    for s_idx, idx_dir in enumerate(shard_dirs):
        t_shard = time.time()
        dname = os.path.relpath(idx_dir, INDEX_BASE).replace("\\", "/")
        print(f"\n[{s_idx+1}/{len(shard_dirs)}] Đang Search trên khối: {dname}...", flush=True)

        # Load chunks mapping: chunk_id -> (doc_id, start, end)
        chunks_map = {}
        for p_file in glob.glob(f"{idx_dir}/chunks/part_*.parquet"):
            c_df = pd.read_parquet(p_file, columns=["chunk_id", "doc_id", "start", "end"])
            for row in c_df.itertuples(index=False):
                chunks_map[row.chunk_id] = (row.doc_id, row.start, row.end)

        # Load text mapping: doc_id -> text
        texts_map = {}
        for p_file in glob.glob(f"{idx_dir}/text/part_*.parquet"):
            t_df = pd.read_parquet(p_file, columns=["doc_id", "text"])
            for row in t_df.itertuples(index=False):
                texts_map[row.doc_id] = row.text

        id_files = sorted(glob.glob(f"{idx_dir}/emb_dense/ids_*.npy"))
        Q_BATCH = 200
        for id_file in id_files:
            c_ids = np.load(id_file)
            num_chunks = len(c_ids)

            c_vecs = None
            if need_dense:
                vec_file = id_file.replace("ids_", "vec_")
                c_vecs = np.load(vec_file).astype(np.float32)

            M = None
            if need_sparse:
                sp_file = id_file.replace("ids_", "sp_").replace(".npy", ".npz")
                if os.path.exists(sp_file):
                    z = np.load(sp_file)
                    M = sp.csr_matrix(
                        (z['vals'].astype(np.float32), z['ids'], z['ptr']),
                        shape=(num_chunks, VOCAB_SIZE)
                    )

            # Query-batch processing to prevent memory spikes
            for q_start in range(0, num_queries, Q_BATCH):
                q_end = min(q_start + Q_BATCH, num_queries)

                dense_batch = None
                if need_dense:
                    dense_batch = q_vecs[q_start:q_end] @ c_vecs.T

                sparse_batch = None
                if need_sparse:
                    if M is not None:
                        sparse_batch = (Q_sparse[q_start:q_end].dot(M.T)).toarray()
                    else:
                        sparse_batch = np.zeros((q_end - q_start, num_chunks), dtype=np.float32)

                if fusion == "rrf":
                    # Collect top candidates for Dense and Sparse separately
                    for b_i, q_idx in enumerate(range(q_start, q_end)):
                        # Top dense candidates
                        if need_dense:
                            d_top = np.argsort(dense_batch[b_i])[::-1][:args.cand_pool]
                            for ti in d_top:
                                chunk_id = c_ids[ti]
                                c_info = chunks_map.get(chunk_id)
                                if c_info is None: continue
                                doc_id, start, end = c_info
                                full_text = texts_map.get(doc_id)
                                if full_text is None: continue
                                chunk_text = full_text[start:end]
                                dense_cand_pool[q_idx].append((float(dense_batch[b_i][ti]), chunk_id, int(doc_id), chunk_text))

                        # Top sparse candidates
                        if need_sparse and M is not None:
                            s_top = np.argsort(sparse_batch[b_i])[::-1][:args.cand_pool]
                            for ti in s_top:
                                chunk_id = c_ids[ti]
                                c_info = chunks_map.get(chunk_id)
                                if c_info is None: continue
                                doc_id, start, end = c_info
                                full_text = texts_map.get(doc_id)
                                if full_text is None: continue
                                chunk_text = full_text[start:end]
                                sparse_cand_pool[q_idx].append((float(sparse_batch[b_i][ti]), chunk_id, int(doc_id), chunk_text))
                else:
                    # Linear score combination
                    for cfg in configs:
                        if mode == "dense":
                            scores_batch = dense_batch
                        elif mode == "sparse":
                            scores_batch = sparse_batch
                        else:
                            scores_batch = cfg["dense_w"] * dense_batch + cfg["sparse_w"] * sparse_batch

                        cand_pool_size = max(args.top_docs, args.top_chunks)
                        for b_i, q_idx in enumerate(range(q_start, q_end)):
                            q_scores = scores_batch[b_i]
                            top_idx = np.argsort(q_scores)[::-1][:cand_pool_size]
                            for ti in top_idx:
                                chunk_id = c_ids[ti]
                                score = float(q_scores[ti])
                                c_info = chunks_map.get(chunk_id)
                                if c_info is None: continue
                                doc_id, start, end = c_info
                                full_text = texts_map.get(doc_id)
                                if full_text is None: continue
                                chunk_text = full_text[start:end]
                                cfg["results"][q_idx].append((score, int(doc_id), chunk_text))

        print(f"   Hoàn tất khối {dname} trong {time.time() - t_shard:.2f}s", flush=True)

    print(f"\nToàn bộ quá trình tìm kiếm hoàn tất trong {time.time() - t_search_start:.2f} giây.", flush=True)

    print("\n=== 5. Xếp hạng và Xuất file Submission cho từng cấu hình ===", flush=True)
    reranker = None
    if args.rerank:
        from FlagEmbedding import FlagReranker
        print(f"\n🚀 Đang khởi tạo Cross-Encoder Reranker: {args.reranker_model} (FP16)...", flush=True)
        reranker = FlagReranker(args.reranker_model, use_fp16=True)

    for c_idx, cfg in enumerate(configs):
        print(f"\n--- Đang xử lý [{c_idx+1}/{len(configs)}]: Tag={cfg['tag']}, Dense_w={cfg['dense_w']:.2f}, Sparse_w={cfg['sparse_w']:.2f} ---", flush=True)
        if args.rerank:
            print(f"   [Rerank Mode] Stage 1 Top Candidates: {args.rerank_cand_docs} -> Reranked Top Docs: {args.top_docs}, Top Chunks: {args.top_chunks}", flush=True)
        t_cfg_start = time.time()
        submission_data = []

        for q_idx in range(num_queries):
            if fusion == "rrf":
                # 1. Deduplicate & rank dense
                dense_best = {}
                meta_lookup = {}
                for sc, cid, did, ctxt in dense_cand_pool[q_idx]:
                    if cid not in dense_best or sc > dense_best[cid]:
                        dense_best[cid] = sc
                        meta_lookup[cid] = (did, ctxt)

                dense_sorted = sorted(dense_best.items(), key=lambda x: x[1], reverse=True)
                dense_rank = {cid: rank + 1 for rank, (cid, _) in enumerate(dense_sorted)}

                # 2. Deduplicate & rank sparse
                sparse_best = {}
                for sc, cid, did, ctxt in sparse_cand_pool[q_idx]:
                    if cid not in sparse_best or sc > sparse_best[cid]:
                        sparse_best[cid] = sc
                        if cid not in meta_lookup:
                            meta_lookup[cid] = (did, ctxt)

                sparse_sorted = sorted(sparse_best.items(), key=lambda x: x[1], reverse=True)
                sparse_rank = {cid: rank + 1 for rank, (cid, _) in enumerate(sparse_sorted)}

                # 3. Calculate RRF Score
                all_cids = set(dense_rank.keys()) | set(sparse_rank.keys())
                candidates = []
                for cid in all_cids:
                    rrf_score = 0.0
                    if cid in dense_rank:
                        rrf_score += cfg["dense_w"] / (args.rrf_k + dense_rank[cid])
                    if cid in sparse_rank:
                        rrf_score += cfg["sparse_w"] / (args.rrf_k + sparse_rank[cid])
                    did, ctxt = meta_lookup[cid]
                    candidates.append((rrf_score, did, ctxt))

                candidates.sort(key=lambda x: x[0], reverse=True)
            else:
                candidates = sorted(cfg["results"][q_idx], key=lambda x: x[0], reverse=True)

            if args.rerank and reranker is not None:
                # 1. Thu thập tối đa args.rerank_cand_docs tài liệu ứng viên từ Stage 1
                cand_docs_dict = {}  # doc_id -> (best_chunk_text, stage1_score)
                for score, doc_id, chunk_text in candidates:
                    if not chunk_text or not chunk_text.strip():
                        continue
                    did_int = int(doc_id)
                    if did_int not in cand_docs_dict:
                        cand_docs_dict[did_int] = (chunk_text, score)
                        if len(cand_docs_dict) >= args.rerank_cand_docs:
                            break

                cand_items = list(cand_docs_dict.items())  # [(doc_id, (chunk_text, score)), ...]
                if cand_items:
                    rerank_pairs = []
                    for did_int, (chunk_text, _) in cand_items:
                        # Cross-lingual alignment: dùng query tiếng Trung nếu chunk chứa ký tự chữ Hán
                        is_zh = any('\u4e00' <= char <= '\u9fff' for char in chunk_text[:200])
                        q_str = queries_zh[q_idx] if (is_zh and queries_zh and queries_zh[q_idx]) else queries[q_idx]
                        rerank_pairs.append([q_str, chunk_text])

                    r_scores = reranker.compute_score(
                        rerank_pairs,
                        batch_size=args.reranker_batch_size,
                        max_length=512
                    )
                    if isinstance(r_scores, (int, float)):
                        r_scores = [float(r_scores)]

                    reranked_cand = []
                    for (did_int, (chunk_text, _)), r_score in zip(cand_items, r_scores):
                        reranked_cand.append((float(r_score), did_int, chunk_text))

                    reranked_cand.sort(key=lambda x: x[0], reverse=True)

                    relevant_docs = [int(did) for _, did, _ in reranked_cand[:args.top_docs]]
                    seen_chunk_texts = set()
                    relevant_chunks = []
                    for _, did, ctxt in reranked_cand:
                        if ctxt not in seen_chunk_texts and len(relevant_chunks) < args.top_chunks:
                            seen_chunk_texts.add(ctxt)
                            relevant_chunks.append({
                                "doc_id": int(did),
                                "chunk_text": ctxt
                            })
                else:
                    relevant_docs = []
                    relevant_chunks = []

                if (q_idx + 1) % 100 == 0 or (q_idx + 1) == num_queries:
                    elapsed = time.time() - t_cfg_start
                    rate = (q_idx + 1) / max(elapsed, 0.001)
                    eta = (num_queries - (q_idx + 1)) / max(rate, 0.001)
                    print(f"      [Rerank Progress] {q_idx + 1}/{num_queries} queries ({rate:.1f} q/s, ETA: {eta:.0f}s)...", flush=True)
            else:
                # Filter top docs and top chunks mà không dùng Reranker
                seen_docs = set()
                seen_chunk_texts = set()
                relevant_docs = []
                relevant_chunks = []

                for score, doc_id, chunk_text in candidates:
                    if doc_id not in seen_docs:
                        seen_docs.add(doc_id)
                        relevant_docs.append(int(doc_id))

                    if not chunk_text or not chunk_text.strip():
                        continue

                    if chunk_text not in seen_chunk_texts and len(relevant_chunks) < args.top_chunks:
                        seen_chunk_texts.add(chunk_text)
                        relevant_chunks.append({
                            "doc_id": int(doc_id),
                            "chunk_text": chunk_text
                        })

                    if len(relevant_docs) == args.top_docs and len(relevant_chunks) == args.top_chunks:
                        break

                relevant_docs = relevant_docs[:args.top_docs]

            submission_data.append({
                "id": int(q_ids[q_idx]),
                "relevant_docs": relevant_docs,
                "relevant_chunks": relevant_chunks
            })

        with open(cfg["out_json"], "w", encoding="utf-8") as f:
            json.dump(submission_data, f, ensure_ascii=False, separators=(',', ':'))

        with zipfile.ZipFile(cfg["out_zip"], "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            zf.write(cfg["out_json"], arcname="submission.json")

        zip_sz_mb = os.path.getsize(cfg["out_zip"]) / (1024 * 1024)
        if zip_sz_mb >= 99.0:
            print(f"   ⚠️ File ZIP đạt {zip_sz_mb:.2f} MB (sát ngưỡng 100MB), đang tự động điều chỉnh giảm chunks để đảm bảo an toàn...", flush=True)
            max_c = args.top_chunks - 2
            while zip_sz_mb >= 98.0 and max_c > 10:
                for item in submission_data:
                    item["relevant_chunks"] = item["relevant_chunks"][:max_c]
                with open(cfg["out_json"], "w", encoding="utf-8") as f:
                    json.dump(submission_data, f, ensure_ascii=False, separators=(',', ':'))
                with zipfile.ZipFile(cfg["out_zip"], "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
                    zf.write(cfg["out_json"], arcname="submission.json")
                zip_sz_mb = os.path.getsize(cfg["out_zip"]) / (1024 * 1024)
                print(f"      -> Đã điều chỉnh top_chunks={max_c}: zip size={zip_sz_mb:.2f} MB", flush=True)
                max_c -= 2

        print(f"   🎉 Xuất thành công: {cfg['out_json']}", flush=True)
        print(f"   📦 File ZIP nộp bài: {cfg['out_zip']} ({zip_sz_mb:.2f} MB)", flush=True)
        if zip_sz_mb < 100.0:
            print(f"   ✅ Đạt chuẩn dung lượng (< 100 MB)", flush=True)
        else:
            print(f"   ⚠️ CẢNH BÁO: Dung lượng vượt quá 100 MB!", flush=True)

    print("\n" + "=" * 70, flush=True)
    print("✨ TẤT CẢ CÁC BỘ SUBMISSION ĐÃ SẴN SÀNG!")
    for cfg in configs:
        sz = os.path.getsize(cfg["out_zip"]) / (1024 * 1024)
        print(f" • Dense {cfg['dense_w']} + Sparse {cfg['sparse_w']}: {cfg['out_zip']} ({sz:.2f} MB)")
    print("=" * 70, flush=True)

if __name__ == "__main__":
    main()
