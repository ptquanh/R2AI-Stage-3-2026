"""
Gộp index mới từ data/indices/new_dataset/index_backup_unembedded_samples_0-100_2
vào kho chỉ mục chính data/indices/new_dataset/index và tái lập chỉ mục (FAISS, Sparse CSR, Metadata).

Quy trình:
1. Gộp 119,701 chunks và 94,575 docs:
   - chunks_id offset: +1,381,239
   - emb_dense: thêm 2 parts (part_0014, part_0015)
   - chunks: thêm 2 parts (part_0014, part_0015)
   - text: thêm 10 parts (part_0060..part_0069)
   - stats.json: cập nhật 1,056,901 docs và 1,500,940 chunks
2. Xây dựng FAISS Index FlatIP (1,500,940 vectors, dim 1024).
3. Hợp nhất ma trận thưa Sparse CSR (1,500,940 x 250,005) bằng direct array concatenation (siêu nhanh, ít RAM).
4. Hợp nhất Chunks Metadata mapping (1,500,940 rows).
5. Kiểm thử Memory-Mapped FAISSSearcher.
"""

import os
import sys
import glob
import time
import json
import shutil
import numpy as np
import pandas as pd
import scipy.sparse as sp
import faiss

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = "data/indices/new_dataset"
TARGET_INDEX = os.path.join(BASE_DIR, "index")
SOURCE_BASE = os.path.join(BASE_DIR, "index_backup_unembedded_samples_0-100_2")
SOURCE_INDEX = os.path.join(SOURCE_BASE, "index_backup_unembedded_samples_0-100_2") if os.path.exists(os.path.join(SOURCE_BASE, "index_backup_unembedded_samples_0-100_2")) else SOURCE_BASE


def main():
    print("=" * 80)
    print("🚀 GỘP INDEX UNEMBEDDED_0-100_2 VÀ TIẾN HÀNH INDEX TOÀN BỘ")
    print(f" • Nguồn: {SOURCE_INDEX}")
    print(f" • Đích:  {TARGET_INDEX}")
    print("=" * 80)
    t0 = time.time()

    # ---------------------------------------------------------
    # BƯỚC 1: KIỂM TRA THƯ MỤC VÀ ĐỌC STATS
    # ---------------------------------------------------------
    if not os.path.exists(TARGET_INDEX):
        raise FileNotFoundError(f"Không tìm thấy target index: {TARGET_INDEX}")
    if not os.path.exists(SOURCE_INDEX):
        raise FileNotFoundError(f"Không tìm thấy source index: {SOURCE_INDEX}")

    target_emb = os.path.join(TARGET_INDEX, "emb_dense")
    target_chunks = os.path.join(TARGET_INDEX, "chunks")
    target_text = os.path.join(TARGET_INDEX, "text")

    stats_path = os.path.join(TARGET_INDEX, "stats.json")
    with open(stats_path, "r", encoding="utf-8") as f:
        curr_stats = json.load(f)

    curr_total_chunks = curr_stats["total_chunks"]  # 1,381,239
    curr_total_docs = curr_stats["total_docs"]      # 962,326
    curr_emb_parts = curr_stats["emb_parts"]        # 14 (0000..0013)
    curr_text_parts = curr_stats["text_parts"]      # 60 (0000..0059)

    print(f"\n[1/5] Trạng thái index hiện tại:")
    print(f"  • Docs: {curr_total_docs:,} | Chunks: {curr_total_chunks:,}")
    print(f"  • Emb parts: {curr_emb_parts} | Chunks parts: {curr_emb_parts} | Text parts: {curr_text_parts}")

    # ---------------------------------------------------------
    # BƯỚC 2: GỘP CHUNKS VÀ EMBEDDINGS (OFFSET +1,381,239)
    # ---------------------------------------------------------
    offset = curr_total_chunks
    print(f"\n[2/5] Đang xử lý gộp chunks và embeddings (Chunk ID Offset: +{offset:,})...")

    src_emb_dir = os.path.join(SOURCE_INDEX, "emb_dense")
    src_chunks_dir = os.path.join(SOURCE_INDEX, "chunks")
    src_text_dir = os.path.join(SOURCE_INDEX, "text")

    # Đọc tất cả chunks từ source
    src_chunk_files = sorted(glob.glob(os.path.join(src_chunks_dir, "part_*.parquet")))
    print(f"  • Đọc {len(src_chunk_files)} chunk parquet files từ source...")
    c_dfs = [pd.read_parquet(cf, columns=["chunk_id", "doc_id", "start", "end", "n_chars", "lang"]) for cf in src_chunk_files]
    all_chunks_df = pd.concat(c_dfs, ignore_index=True)
    n_source_chunks = len(all_chunks_df)
    print(f"  • Tổng chunks trong source: {n_source_chunks:,}")

    # Áp dụng offset cho chunk_id
    all_chunks_df["chunk_id"] = all_chunks_df["chunk_id"].astype(np.int64) + offset
    print(f"  • Range chunk_id mới: [{all_chunks_df['chunk_id'].min():,}, {all_chunks_df['chunk_id'].max():,}]")

    # Gộp emb_dense và chia chunks tương ứng 1-1
    src_id_files = sorted([f for f in os.listdir(src_emb_dir) if f.startswith("ids_") and f.endswith(".npy")])
    print(f"  • Xử lý {len(src_id_files)} embedding parts từ source...")

    chunk_slice_start = 0
    for p_idx, id_f in enumerate(src_id_files):
        target_part_num = curr_emb_parts + p_idx
        part_tag = f"{target_part_num:04d}"

        # Đọc ids array và cộng offset
        ids_arr = np.load(os.path.join(src_emb_dir, id_f)).astype(np.int64)
        ids_arr_shifted = ids_arr + offset
        part_len = len(ids_arr_shifted)

        # Lưu ids_*.npy mới
        tgt_id_path = os.path.join(target_emb, f"ids_{part_tag}.npy")
        np.save(tgt_id_path, ids_arr_shifted)

        # Copy vec_*.npy
        src_vec_name = id_f.replace("ids_", "vec_")
        tgt_vec_path = os.path.join(target_emb, f"vec_{part_tag}.npy")
        shutil.copy2(os.path.join(src_emb_dir, src_vec_name), tgt_vec_path)

        # Copy sp_*.npz
        src_sp_name = id_f.replace("ids_", "sp_").replace(".npy", ".npz")
        tgt_sp_path = os.path.join(target_emb, f"sp_{part_tag}.npz")
        shutil.copy2(os.path.join(src_emb_dir, src_sp_name), tgt_sp_path)

        # Cắt và lưu chunks/part_*.parquet tương ứng chính xác
        chunk_slice_end = chunk_slice_start + part_len
        part_chunk_df = all_chunks_df.iloc[chunk_slice_start:chunk_slice_end].copy()
        tgt_chunk_path = os.path.join(target_chunks, f"part_{part_tag}.parquet")
        part_chunk_df.to_parquet(tgt_chunk_path, index=False, compression="snappy")

        # Kiểm tra khớp 100% giữa ids và chunks
        assert np.array_equal(ids_arr_shifted, part_chunk_df["chunk_id"].values), (
            f"Lỗi không khớp chunk_id tại part {part_tag}!"
        )

        print(f"    ✓ Part #{part_tag}: {part_len:,} chunks (ids, vec, sp, chunks)")
        chunk_slice_start = chunk_slice_end

    assert chunk_slice_start == n_source_chunks, f"Không khớp tổng chunks: {chunk_slice_start} != {n_source_chunks}"

    # Gộp text parts
    src_text_files = sorted([f for f in os.listdir(src_text_dir) if f.startswith("part_") and f.endswith(".parquet")])
    print(f"\n  • Đang sao chép {len(src_text_files)} text parquet files...")
    batch_docs = 0
    for t_idx, tf in enumerate(src_text_files):
        target_text_num = curr_text_parts + t_idx
        text_tag = f"{target_text_num:04d}"
        src_tf_path = os.path.join(src_text_dir, tf)
        tgt_tf_path = os.path.join(target_text, f"part_{text_tag}.parquet")
        shutil.copy2(src_tf_path, tgt_tf_path)
        df_t = pd.read_parquet(src_tf_path, columns=["doc_id"])
        batch_docs += len(df_t)

    print(f"    ✓ Đã thêm {len(src_text_files)} text parts ({batch_docs:,} docs) từ part_{curr_text_parts:04d} đến part_{curr_text_parts + len(src_text_files) - 1:04d}")

    # Cập nhật stats.json
    final_total_docs = curr_total_docs + batch_docs
    final_total_chunks = curr_total_chunks + n_source_chunks
    final_emb_parts = curr_emb_parts + len(src_id_files)
    final_text_parts = curr_text_parts + len(src_text_files)

    new_stats = {
        "index_name": "ViBioMIR_Consolidated_Index",
        "total_docs": final_total_docs,
        "total_chunks": final_total_chunks,
        "dense_dim": 1024,
        "vocab_size": 250005,
        "model": "BAAI/bge-m3",
        "emb_parts": final_emb_parts,
        "chunks_parts": final_emb_parts,
        "text_parts": final_text_parts,
        "created_at": curr_stats.get("created_at", "2026-10-12 22:39:44"),
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source": f"Consolidated index with previous 962k + unembedded_0-100_2 ({batch_docs:,} docs, {n_source_chunks:,} chunks) -> Total {final_total_docs:,} docs"
    }
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(new_stats, f, indent=2, ensure_ascii=False)

    print(f"  ✅ Đã cập nhật {stats_path}: {final_total_docs:,} docs, {final_total_chunks:,} chunks.")

    # ---------------------------------------------------------
    # BƯỚC 3: XÂY DỰNG FAISS INDEX FLAT IP (DENSE)
    # ---------------------------------------------------------
    print("\n" + "=" * 80)
    print(f"[3/5] TIẾN HÀNH XÂY DỰNG FAISS FLAT IP INDEX (dim=1024) TRÊN TẤT CẢ {final_emb_parts} PARTS...")
    print("=" * 80)
    all_id_files = sorted(glob.glob(os.path.join(target_emb, "ids_*.npy")))
    assert len(all_id_files) == final_emb_parts, f"Số lượng id_files {len(all_id_files)} != {final_emb_parts}"

    dim = 1024
    index = faiss.IndexFlatIP(dim)
    all_chunk_ids_list = []

    t_faiss = time.time()
    for i, id_f in enumerate(all_id_files):
        t_p = time.time()
        c_ids = np.load(id_f)
        vec_f = id_f.replace("ids_", "vec_")
        vecs = np.load(vec_f).astype(np.float32)

        index.add(vecs)
        all_chunk_ids_list.append(c_ids)
        print(f"  • [{i+1:02d}/{final_emb_parts:02d}] {os.path.basename(id_f)}: +{len(c_ids):,} vecs -> Index total: {index.ntotal:,} ({time.time() - t_p:.2f}s)")
        del vecs

    all_chunk_ids = np.concatenate(all_chunk_ids_list)
    assert index.ntotal == final_total_chunks, f"FAISS ntotal {index.ntotal:,} != {final_total_chunks:,}"
    print(f"  ✅ Đã add xong toàn bộ {index.ntotal:,} vectors trong {time.time() - t_faiss:.2f}s!")

    # Lưu FAISS index ra đĩa
    faiss_out = os.path.join(TARGET_INDEX, "faiss_index_flat_ip.bin")
    print(f"  💾 Đang ghi FAISS index vào: {faiss_out}...")
    faiss.write_index(index, faiss_out)
    del index
    sz_bin = os.path.getsize(faiss_out) / (1024**2)
    print(f"  ✅ Đã lưu FAISS index thành công ({sz_bin:.1f} MB)!")

    # Lưu chunk_ids.npy
    ids_out = os.path.join(TARGET_INDEX, "chunk_ids.npy")
    np.save(ids_out, all_chunk_ids)
    print(f"  ✅ Đã lưu chunk_ids.npy ({len(all_chunk_ids):,} IDs)!")

    # ---------------------------------------------------------
    # BƯỚC 4: HỢP NHẤT SPARSE CSR BẰNG DIRECT ARRAY CONCATENATION
    # ---------------------------------------------------------
    print("\n" + "=" * 80)
    print(f"[4/5] HỢP NHẤT MA TRẬN THƯA SPARSE CSR (250,005 DIMS)...")
    print("=" * 80)
    t_sp = time.time()

    all_vals = []
    all_indices = []
    all_ptr_offsets = [np.array([0], dtype=np.int64)]
    total_sp_rows = 0
    current_nnz = 0

    for i, id_f in enumerate(all_id_files):
        t_sp_part = time.time()
        sp_f = id_f.replace("ids_", "sp_").replace(".npy", ".npz")
        z = np.load(sp_f)
        vals = z["vals"].astype(np.float32)
        ind = z["ids"].astype(np.int32)
        ptr = z["ptr"].astype(np.int64)

        num_r = len(np.load(id_f))
        assert len(ptr) == num_r + 1, f"Lỗi shape ptr part {id_f}"

        # ptr offset by current_nnz
        all_ptr_offsets.append(ptr[1:] + current_nnz)
        all_vals.append(vals)
        all_indices.append(ind)

        current_nnz += len(vals)
        total_sp_rows += num_r
        print(f"  • [{i+1:02d}/{final_emb_parts:02d}] {os.path.basename(sp_f)}: {num_r:,} rows, {len(vals):,} non-zeros ({time.time() - t_sp_part:.2f}s)")

    print("  • Đang nối các mảng dữ liệu thưa...")
    final_vals = np.concatenate(all_vals)
    del all_vals
    final_indices = np.concatenate(all_indices)
    del all_indices
    final_ptr = np.concatenate(all_ptr_offsets)
    del all_ptr_offsets

    assert total_sp_rows == final_total_chunks, f"Sparse rows {total_sp_rows:,} != {final_total_chunks:,}"
    assert len(final_ptr) == total_sp_rows + 1, "indptr length mismatch!"

    unified_sparse = sp.csr_matrix(
        (final_vals, final_indices, final_ptr),
        shape=(total_sp_rows, 250005)
    )
    sparse_out = os.path.join(TARGET_INDEX, "sparse_csr.npz")
    print(f"  💾 Đang lưu Unified Sparse CSR ({unified_sparse.shape[0]:,} x {unified_sparse.shape[1]:,}, nnz={unified_sparse.nnz:,}) vào {sparse_out}...")
    sp.save_npz(sparse_out, unified_sparse)
    del unified_sparse, final_vals, final_indices, final_ptr
    sz_sp = os.path.getsize(sparse_out) / (1024**2)
    print(f"  ✅ Đã lưu Sparse CSR ({sz_sp:.1f} MB) trong {time.time() - t_sp:.2f}s!")

    # ---------------------------------------------------------
    # BƯỚC 5: HỢP NHẤT CHUNKS METADATA MAPPING & TEST MMAP
    # ---------------------------------------------------------
    print("\n" + "=" * 80)
    print(f"[5/5] HỢP NHẤT CHUNKS METADATA & KIỂM TRA MEMORY-MAPPING...")
    print("=" * 80)
    t_ch = time.time()
    chunk_parts = sorted(glob.glob(os.path.join(target_chunks, "part_*.parquet")))
    assert len(chunk_parts) == final_emb_parts, f"Chunks parts {len(chunk_parts)} != {final_emb_parts}"

    chunks_dfs = [pd.read_parquet(p, columns=["chunk_id", "doc_id", "start", "end"]) for p in chunk_parts]
    df_all_chunks = pd.concat(chunks_dfs, ignore_index=True)
    df_all_chunks = df_all_chunks.drop_duplicates(subset=["chunk_id"])

    assert len(df_all_chunks) == final_total_chunks, f"Chunks meta rows {len(df_all_chunks):,} != {final_total_chunks:,}"
    assert np.array_equal(all_chunk_ids, df_all_chunks["chunk_id"].values), "Chunk IDs không khớp với metadata chunk_id!"

    chunks_meta_out = os.path.join(TARGET_INDEX, "chunks_metadata.parquet")
    df_all_chunks.to_parquet(chunks_meta_out, index=False)
    del df_all_chunks, chunks_dfs
    sz_meta = os.path.getsize(chunks_meta_out) / (1024**2)
    print(f"  ✅ Đã lưu Chunks Metadata ({final_total_chunks:,} chunks, {sz_meta:.1f} MB) trong {time.time() - t_ch:.2f}s!")

    # Test đọc Memory-Mapped FAISS
    print("\n🧪 KIỂM TRA NHANH TỐC ĐỘ NẠP MMAP FAISS INDEX...")
    t_mmap = time.time()
    mmap_index = faiss.read_index(faiss_out, faiss.IO_FLAG_MMAP)
    print(f"  ⚡ Tốc độ nạp index mmap: {time.time() - t_mmap:.4f}s!")
    print(f"  ⚡ Tổng vectors nạp được: {mmap_index.ntotal:,}")

    # Test search giả lập 50 queries
    q_dummy = np.random.randn(50, dim).astype(np.float32)
    faiss.normalize_L2(q_dummy)
    t_search = time.time()
    scores, top_idx = mmap_index.search(q_dummy, 400)
    print(f"  ⚡ Tốc độ search 50 queries (Top 400 candidates): {time.time() - t_search:.3f}s!")

    elapsed_total = time.time() - t0
    print("\n" + "=" * 80)
    print(f"🎉 HOÀN TẤT TOÀN DIỆN TRONG {elapsed_total:.2f}s ({elapsed_total/60:.2f} phút)!")
    print(f" • Tổng tài liệu: {final_total_docs:,} docs (+{batch_docs:,} từ unembedded_0-100_2)")
    print(f" • Tổng đoạn văn: {final_total_chunks:,} chunks (+{n_source_chunks:,})")
    print(f" • FAISS Index:  {sz_bin:.1f} MB ({faiss_out})")
    print(f" • Sparse CSR:   {sz_sp:.1f} MB ({sparse_out})")
    print(f" • Chunks Meta:  {sz_meta:.1f} MB ({chunks_meta_out})")
    print("=" * 80)


if __name__ == "__main__":
    main()
