"""Align embedded_samples.parquet with the validated active index.

The operation is transactional: copy the original registry to a timestamped
backup, stream only active-index document IDs to a temporary parquet, validate
the exact ID set, then atomically replace the registry.
"""

from __future__ import annotations

import gc
import os
import shutil
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
REGISTRY = DATA_DIR / "embedded_samples.parquet"
INDEX_META = DATA_DIR / "indices" / "new_dataset" / "index" / "chunks_metadata.parquet"
BACKUP = DATA_DIR / "embedded_samples.parquet.pre_clean_rebuild_20261016T155529.bak"
TEMP = DATA_DIR / "embedded_samples.clean_rebuild_tmp.parquet"
EXPECTED_ROWS = 1_115_733
EXPECTED_REMOVED = 40_616


def main() -> None:
    if BACKUP.exists() or TEMP.exists():
        raise FileExistsError("Backup or temporary registry path already exists")

    active_table = pq.read_table(INDEX_META, columns=["doc_id"])
    active_ids = set(active_table["doc_id"].to_pylist())
    if len(active_ids) != EXPECTED_ROWS:
        raise RuntimeError(f"Unexpected active index docs: {len(active_ids):,}")
    active_values = pa.array(sorted(active_ids), type=pa.int64())

    source = pq.ParquetFile(REGISTRY)
    initial_rows = source.metadata.num_rows
    shutil.copy2(REGISTRY, BACKUP)

    written = 0
    with pq.ParquetWriter(TEMP, source.schema_arrow, compression="snappy") as writer:
        for batch in source.iter_batches(batch_size=25_000):
            keep = pc.is_in(batch["id"], value_set=active_values)
            filtered = batch.filter(keep)
            if filtered.num_rows:
                writer.write_batch(filtered)
                written += filtered.num_rows
    source.close()
    del source
    gc.collect()

    if initial_rows - written != EXPECTED_REMOVED:
        raise RuntimeError(
            f"Expected to remove {EXPECTED_REMOVED:,} rows, removed {initial_rows - written:,}"
        )
    if written != EXPECTED_ROWS:
        raise RuntimeError(f"Unexpected filtered registry rows: {written:,}")

    check_ids = pq.read_table(TEMP, columns=["id"])["id"].to_pylist()
    if len(check_ids) != EXPECTED_ROWS or set(check_ids) != active_ids:
        raise RuntimeError("Filtered registry does not exactly match active index IDs")

    os.replace(TEMP, REGISTRY)
    print(f"embedded registry: {initial_rows:,} -> {written:,} rows")
    print(f"removed invalid rows: {initial_rows - written:,}")
    print(f"recoverable backup: {BACKUP}")


if __name__ == "__main__":
    main()
