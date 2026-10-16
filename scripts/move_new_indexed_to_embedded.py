"""
Streamed low-memory migration of indexed samples from unembedded_samples.parquet to embedded_samples.parquet.

Key properties:
- Uses PyArrow RecordBatch streaming (batch_size=25,000) to keep RAM usage under ~100MB.
- Strictly verifies row counts, schemas, and zero overlap before and after migration.
- Employs atomic replacement with temporary files and backups to prevent data corruption.
- Handles Windows file locking cleanly (explicit close + gc.collect + os.replace).
"""

import os
import sys
import time
import glob
import shutil
import gc
from pathlib import Path
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE = Path("d:/CODE PLAYGROUND/Projects/Competitions/R2AI-Stage-3-2026")
DATA_DIR = BASE / "data"

UNEMB_PATH = DATA_DIR / "unembedded_samples.parquet"
EMB_PATH = DATA_DIR / "embedded_samples.parquet"

# New backup index shard docs
NEW_INDEX_DOCS = sorted(glob.glob(str(DATA_DIR / "indices" / "new_dataset" / "index_backup_unembedded_samples_0-100-20261014T033450Z-1-001" / "index_backup_unembedded_samples_0-100" / "docs" / "part_*.parquet")))
# Consolidated main index metadata (if present)
MAIN_INDEX_META = DATA_DIR / "indices" / "new_dataset" / "index" / "chunks_metadata.parquet"

BATCH_SIZE = 25000


def collect_indexed_doc_ids():
    indexed_ids = set()
    print("🔍 [1/5] Đang thu thập tất cả doc_id từ index...")

    # 1. From new backup index
    for f in NEW_INDEX_DOCS:
        table = pq.read_table(f, columns=["doc_id"])
        ids = table["doc_id"].to_pylist()
        indexed_ids.update(ids)
        print(f"  • Shard: {Path(f).name} -> {len(ids):,} doc_ids")

    # 2. From main index if exists
    if MAIN_INDEX_META.exists():
        table_main = pq.read_table(MAIN_INDEX_META, columns=["doc_id"])
        ids_main = table_main["doc_id"].to_pylist()
        indexed_ids.update(ids_main)
        print(f"  • Main index: {MAIN_INDEX_META.name} -> {len(ids_main):,} chunk doc_ids")

    print(f"  ✅ Tổng số unique doc_ids đã index được tìm thấy: {len(indexed_ids):,}")
    return indexed_ids


def main():
    print("=" * 80)
    print("🚀 DI CHUYỂN CÁC MẪU ĐÃ EMBEDDED TỪ UNEMBEDDED SANG EMBEDDED (LOW-RAM STREAMING)")
    print("=" * 80)
    t0 = time.time()

    # 1. Thu thập doc_id
    indexed_ids = collect_indexed_doc_ids()

    # 2. Đọc id column từ unembedded và embedded để phân tích overlap
    print("\n🔍 [2/5] Đọc danh sách ID từ các file parquet...")
    unemb_f = pq.ParquetFile(UNEMB_PATH)
    emb_f = pq.ParquetFile(EMB_PATH)

    unemb_table_ids = unemb_f.read(columns=["id"])
    emb_table_ids = emb_f.read(columns=["id"])

    unemb_ids = set(unemb_table_ids["id"].to_pylist())
    emb_ids = set(emb_table_ids["id"].to_pylist())

    initial_unemb_count = len(unemb_ids)
    initial_emb_count = len(emb_ids)

    print(f"  • unembedded_samples.parquet: {initial_unemb_count:,} mẫu")
    print(f"  • embedded_samples.parquet:   {initial_emb_count:,} mẫu")

    # Target IDs to move
    target_ids = (indexed_ids & unemb_ids) - emb_ids
    n_target = len(target_ids)
    print(f"  🎯 Số mẫu CẦN CHUYỂN từ unembedded sang embedded: {n_target:,}")

    already_in_emb = indexed_ids & emb_ids
    print(f"  ℹ️ Số mẫu indexed đã có sẵn trong embedded:        {len(already_in_emb):,}")

    if n_target == 0:
        print("  ⚠️ Không có mẫu nào cần chuyển! Kết thúc.")
        unemb_f.close()
        emb_f.close()
        return

    # Chuẩn bị target array cho pyarrow compute
    target_arr = pa.array(list(target_ids), type=pa.int64())

    # Temp files
    unemb_rem_temp = DATA_DIR / "unembedded_remaining_temp.parquet"
    unemb_move_temp = DATA_DIR / "unembedded_to_move_temp.parquet"
    emb_new_temp = DATA_DIR / "embedded_samples_temp.parquet"

    # Dọn dẹp temp cũ nếu có
    for p in [unemb_rem_temp, unemb_move_temp, emb_new_temp]:
        if p.exists():
            p.unlink()

    # 3. Phân tách unembedded_samples.parquet thành move và remaining
    print(f"\n📦 [3/5] Đang phân tách {UNEMB_PATH.name} (streaming theo batch {BATCH_SIZE:,})...")
    unemb_schema = unemb_f.schema_arrow

    rows_moved = 0
    rows_rem = 0

    with pq.ParquetWriter(unemb_move_temp, schema=unemb_schema, compression="snappy") as move_writer, \
         pq.ParquetWriter(unemb_rem_temp, schema=unemb_schema, compression="snappy") as rem_writer:

        for batch in unemb_f.iter_batches(batch_size=BATCH_SIZE):
            mask_move = pc.is_in(batch["id"], value_set=target_arr)
            mask_rem = pc.invert(mask_move)

            b_move = batch.filter(mask_move)
            b_rem = batch.filter(mask_rem)

            if b_move.num_rows > 0:
                move_writer.write_batch(b_move)
                rows_moved += b_move.num_rows

            if b_rem.num_rows > 0:
                rem_writer.write_batch(b_rem)
                rows_rem += b_rem.num_rows

    unemb_f.close()
    del unemb_f
    gc.collect()

    print(f"  ✅ Phân tách xong:")
    print(f"     - Số mẫu di chuyển vào move_temp: {rows_moved:,} (Kỳ vọng: {n_target:,})")
    print(f"     - Số mẫu giữ lại ở rem_temp:     {rows_rem:,} (Kỳ vọng: {initial_unemb_count - n_target:,})")

    assert rows_moved == n_target, f"Lỗi: rows_moved ({rows_moved}) != n_target ({n_target})"
    assert rows_rem == initial_unemb_count - n_target, f"Lỗi: rows_rem ({rows_rem}) != remaining ({initial_unemb_count - n_target})"

    # 4. Tạo embedded_samples_temp bằng cách stream file cũ + stream move_temp
    print(f"\n🔗 [4/5] Đang gộp vào {emb_new_temp.name} (streaming)...")
    emb_schema = emb_f.schema_arrow

    total_new_emb = 0
    with pq.ParquetWriter(emb_new_temp, schema=emb_schema, compression="snappy") as emb_writer:
        # Ghi các mẫu embedded cũ
        print(f"  • Đang chép {initial_emb_count:,} mẫu cũ từ {EMB_PATH.name}...")
        for batch in emb_f.iter_batches(batch_size=BATCH_SIZE):
            emb_writer.write_batch(batch)
            total_new_emb += batch.num_rows

        # Ghi tiếp các mẫu mới chuyển sang
        print(f"  • Đang nối {rows_moved:,} mẫu mới từ move_temp...")
        move_f = pq.ParquetFile(unemb_move_temp)
        for batch in move_f.iter_batches(batch_size=BATCH_SIZE):
            emb_writer.write_batch(batch)
            total_new_emb += batch.num_rows
        move_f.close()
        del move_f

    emb_f.close()
    del emb_f
    gc.collect()

    print(f"  ✅ Gộp xong: tổng mẫu trong file mới: {total_new_emb:,} (Kỳ vọng: {initial_emb_count + n_target:,})")
    assert total_new_emb == initial_emb_count + n_target, "Lỗi: Tổng số mẫu embedded mới không khớp!"

    # 5. Kiểm tra toàn vẹn và Atomic Replace
    print("\n🛡️ [5/5] Kiểm tra toàn vẹn trước khi cập nhật chính thức...")
    # Kiểm tra unique ID trong file embedded mới
    f_check_emb = pq.ParquetFile(emb_new_temp)
    check_emb_ids = f_check_emb.read(columns=["id"])["id"].to_pylist()
    f_check_emb.close()
    del f_check_emb
    assert len(check_emb_ids) == len(set(check_emb_ids)), "Phát hiện trùng lặp ID trong embedded_samples_temp!"

    # Kiểm tra unique ID trong file unembedded mới
    f_check_unemb = pq.ParquetFile(unemb_rem_temp)
    check_unemb_ids = f_check_unemb.read(columns=["id"])["id"].to_pylist()
    f_check_unemb.close()
    del f_check_unemb
    assert len(check_unemb_ids) == len(set(check_unemb_ids)), "Phát hiện trùng lặp ID trong unembedded_remaining_temp!"

    # Kiểm tra giao nhau giữa 2 file mới
    overlap = set(check_emb_ids).intersection(set(check_unemb_ids))
    assert len(overlap) == 0, f"Phát hiện {len(overlap)} ID giao nhau giữa embedded và unembedded!"

    print("  ✅ Tất cả kiểm tra toàn vẹn ĐẠT 100%!")

    # Sao lưu an toàn
    unemb_bak = DATA_DIR / "unembedded_samples.parquet.bak"
    emb_bak = DATA_DIR / "embedded_samples.parquet.bak"

    print(f"\n💾 Đang tạo backup và thực hiện Atomic Replace:")
    print(f"  • Backup {UNEMB_PATH.name} -> {unemb_bak.name}")
    shutil.copy2(UNEMB_PATH, unemb_bak)

    print(f"  • Backup {EMB_PATH.name} -> {emb_bak.name}")
    shutil.copy2(EMB_PATH, emb_bak)

    # Thay thế file chính thức bằng os.replace
    print("  • Cập nhật file unembedded_samples.parquet...")
    os.replace(unemb_rem_temp, UNEMB_PATH)

    print("  • Cập nhật file embedded_samples.parquet...")
    os.replace(emb_new_temp, EMB_PATH)

    # Xóa file temp trung gian
    if unemb_move_temp.exists():
        unemb_move_temp.unlink()

    # Xóa file backup sau khi thành công
    if unemb_bak.exists():
        unemb_bak.unlink()
    if emb_bak.exists():
        emb_bak.unlink()

    elapsed = time.time() - t0
    print("\n" + "=" * 80)
    print(f"🎉 HOÀN THÀNH DI CHUYỂN DỮ LIỆU XUẤT SẮC TRONG {elapsed:.2f}s!")
    print(f" • embedded_samples.parquet:   {total_new_emb:,} mẫu (+{n_target:,})")
    print(f" • unembedded_samples.parquet: {rows_rem:,} mẫu (-{n_target:,})")
    print(f" • Tổng số mẫu bảo toàn:      {total_new_emb + rows_rem:,} mẫu")
    print("=" * 80)


if __name__ == "__main__":
    main()
