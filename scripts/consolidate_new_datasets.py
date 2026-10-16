"""
Consolidate 0-100k-2, 200-300k, and 300-400k into the main index:
data/indices/new_dataset/index

Ensures:
1. Continuous, collision-free chunk IDs across all 1.38M chunks.
2. 1-to-1 correspondence between emb_dense parts and chunks parts (14 parts total).
3. Text parts appended sequentially (60 parts total, ~962k docs).
4. Full validation and stats.json update.
"""

import os
import sys
import time
import json
import shutil
import numpy as np
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = "data/indices/new_dataset"
TARGET_INDEX = os.path.join(BASE_DIR, "index")
SOURCES = [
    {
        "name": "0-100k-2",
        "dir": os.path.join(BASE_DIR, "0-100k-2/index"),
        "expected_chunks": 131357,
        "expected_docs": 99941,
        "emb_start_part": 10,
        "text_start_part": 30,
    },
    {
        "name": "200-300k",
        "dir": os.path.join(BASE_DIR, "200-300k/index"),
        "expected_chunks": 100167,
        "expected_docs": 99827,
        "emb_start_part": 12,
        "text_start_part": 40,
    },
    {
        "name": "300-400k",
        "dir": os.path.join(BASE_DIR, "300-400k/index"),
        "expected_chunks": 100345,
        "expected_docs": 99714,
        "emb_start_part": 13,
        "text_start_part": 50,
    }
]


def main():
    print("=" * 80)
    print("🚀 BẮT ĐẦU GỘP 0-100K-2, 200-300K, 300-400K VÀO CHỈ MỤC CHÍNH")
    print(f"Target: {TARGET_INDEX}")
    print("=" * 80)
    t0 = time.time()

    # 1. Kiểm tra tồn tại thư mục
    if not os.path.exists(TARGET_INDEX):
        raise FileNotFoundError(f"Không tìm thấy target index: {TARGET_INDEX}")
    for s in SOURCES:
        if not os.path.exists(s["dir"]):
            raise FileNotFoundError(f"Không tìm thấy source dir: {s['dir']}")

    target_emb = os.path.join(TARGET_INDEX, "emb_dense")
    target_chunks = os.path.join(TARGET_INDEX, "chunks")
    target_text = os.path.join(TARGET_INDEX, "text")

    # 2. Đọc trạng thái index hiện tại
    stats_path = os.path.join(TARGET_INDEX, "stats.json")
    with open(stats_path, "r", encoding="utf-8") as f:
        curr_stats = json.load(f)

    curr_total_chunks = curr_stats["total_chunks"]  # 1,049,370
    curr_total_docs = curr_stats["total_docs"]      # 662,844
    curr_emb_parts = curr_stats["emb_parts"]        # 10 (0000..0009)
    curr_text_parts = curr_stats["text_parts"]      # 30 (0000..0029)

    print(f"Index hiện tại: {curr_total_docs:,} docs | {curr_total_chunks:,} chunks")
    print(f"  Emb parts: {curr_emb_parts} | Chunks parts: {curr_emb_parts} | Text parts: {curr_text_parts}")

    running_chunk_offset = curr_total_chunks
    total_added_chunks = 0
    total_added_docs = 0

    for s in SOURCES:
        s_name = s["name"]
        s_dir = s["dir"]
        offset = running_chunk_offset
        emb_part_start = s["emb_start_part"]
        text_part_start = s["text_start_part"]

        print(f"\n--- Đang xử lý khối: {s_name} (Chunk offset: +{offset:,}) ---")
        t_b = time.time()

        src_emb_dir = os.path.join(s_dir, "emb_dense")
        src_chunks_dir = os.path.join(s_dir, "chunks")
        src_text_dir = os.path.join(s_dir, "text")

        # 3.1. Đọc toàn bộ chunks và áp dụng offset
        src_chunk_files = sorted([os.path.join(src_chunks_dir, f) for f in os.listdir(src_chunks_dir) if f.startswith("part_") and f.endswith(".parquet")])
        print(f"  Reading {len(src_chunk_files)} chunk parquet files...")
        c_dfs = [pd.read_parquet(cf, columns=["chunk_id", "doc_id", "start", "end"]) for cf in src_chunk_files]
        all_chunks_df = pd.concat(c_dfs, ignore_index=True)
        n_chunks = len(all_chunks_df)
        assert n_chunks == s["expected_chunks"], f"Số chunks {n_chunks} không khớp mong đợi {s['expected_chunks']}"

        all_chunks_df["chunk_id"] = all_chunks_df["chunk_id"].astype(np.int64) + offset
        print(f"  -> Total chunks: {n_chunks:,}. Range chunk_id: [{all_chunks_df['chunk_id'].min():,}, {all_chunks_df['chunk_id'].max():,}]")

        # 3.2. Xử lý emb_dense parts (ids, vec, sp) và chia chunks parquet tương ứng 1-1
        src_id_files = sorted([f for f in os.listdir(src_emb_dir) if f.startswith("ids_") and f.endswith(".npy")])
        print(f"  Processing {len(src_id_files)} embedding parts...")

        chunk_slice_start = 0
        for p_idx, id_f in enumerate(src_id_files):
            target_part_num = emb_part_start + p_idx
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

            # Cắt và lưu chunks/part_*.parquet tương ứng chính xác với part_len
            chunk_slice_end = chunk_slice_start + part_len
            part_chunk_df = all_chunks_df.iloc[chunk_slice_start:chunk_slice_end]
            tgt_chunk_path = os.path.join(target_chunks, f"part_{part_tag}.parquet")
            part_chunk_df.to_parquet(tgt_chunk_path, index=False, compression="snappy")

            # Kiểm tra nhanh khớp 100% giữa ids và chunks
            assert np.array_equal(ids_arr_shifted, part_chunk_df["chunk_id"].values), (
                f"Lỗi không khớp chunk_id tại part {part_tag}!"
            )

            print(f"    ✓ Part #{part_tag}: {part_len:,} chunks (ids, vec, sp, chunks)")
            chunk_slice_start = chunk_slice_end

        assert chunk_slice_start == n_chunks, f"Không khớp tổng số chunks: {chunk_slice_start} != {n_chunks}"
        total_added_chunks += n_chunks
        running_chunk_offset += n_chunks

        # 3.3. Xử lý text parts
        src_text_files = sorted([f for f in os.listdir(src_text_dir) if f.startswith("part_") and f.endswith(".parquet")])
        print(f"  Copying {len(src_text_files)} text parquet files...")
        batch_docs = 0
        for t_idx, tf in enumerate(src_text_files):
            target_text_num = text_part_start + t_idx
            text_tag = f"{target_text_num:04d}"
            src_tf_path = os.path.join(src_text_dir, tf)
            tgt_tf_path = os.path.join(target_text, f"part_{text_tag}.parquet")
            shutil.copy2(src_tf_path, tgt_tf_path)
            # Đếm số doc
            df_t = pd.read_parquet(src_tf_path, columns=["doc_id"])
            batch_docs += len(df_t)

        assert batch_docs == s["expected_docs"], f"Số docs {batch_docs} không khớp mong đợi {s['expected_docs']}"
        print(f"    ✓ Đã thêm {len(src_text_files)} text parts ({batch_docs:,} docs) từ part_{text_part_start:04d} đến part_{text_part_start + len(src_text_files) - 1:04d}")
        total_added_docs += batch_docs
        print(f"  Hoàn tất khối {s_name} trong {time.time() - t_b:.1f}s")

    # 4. Cập nhật stats.json
    final_total_docs = curr_total_docs + total_added_docs
    final_total_chunks = curr_total_chunks + total_added_chunks

    new_stats = {
        "index_name": "ViBioMIR_Consolidated_Index",
        "total_docs": final_total_docs,
        "total_chunks": final_total_chunks,
        "dense_dim": 1024,
        "vocab_size": 250005,
        "model": "BAAI/bge-m3",
        "emb_parts": 14,
        "chunks_parts": 14,
        "text_parts": 60,
        "created_at": curr_stats.get("created_at", "2026-10-12 22:39:44"),
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source": "Consolidated index with 462k baseline + 0-100k + 100-200k + 0-100k-2 + 200-300k + 300-400k (total 962,326 docs)"
    }
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(new_stats, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print(f"🎉 ĐÃ HOÀN TẤT GỘP TẤT CẢ VÀO: {TARGET_INDEX}")
    print(f"Tổng tài liệu: {final_total_docs:,} docs (Kỳ vọng: 962,326)")
    print(f"Tổng đoạn văn: {final_total_chunks:,} chunks (Kỳ vọng: 1,381,239)")
    print(f"Emb parts: 14 (ids_0000..0013, vec_0000..0013, sp_0000..0013)")
    print(f"Chunks parts: 14 (part_0000..0013)")
    print(f"Text parts: 60 (part_0000..0059)")
    print(f"Tổng thời gian: {time.time() - t0:.1f}s")
    print("=" * 80)


if __name__ == "__main__":
    main()
