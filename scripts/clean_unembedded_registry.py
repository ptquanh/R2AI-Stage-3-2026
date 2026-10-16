"""Remove non-official rows from data/unembedded_samples.parquet safely."""

from __future__ import annotations

import gc
import os
import shutil
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
SOURCE = DATA_DIR / "unembedded_samples.parquet"
OFFICIAL = DATA_DIR / "raw" / "btc_provided" / "links_corpus_vi_en_zh.parquet"
EMBEDDED = DATA_DIR / "embedded_samples.parquet"
BACKUP = DATA_DIR / "unembedded_samples.parquet.pre_official_filter_20261016.bak"
TEMP = DATA_DIR / "unembedded_samples.official_filter_tmp.parquet"

EXPECTED_INITIAL = 94_399
EXPECTED_REMOVED = 4_370
EXPECTED_FINAL = 90_029


def main() -> None:
    if BACKUP.exists() or TEMP.exists():
        raise FileExistsError("Backup or temporary output already exists")

    official = pq.read_table(OFFICIAL, columns=["id", "url"])
    official_pairs = set(zip(official["id"].to_pylist(), official["url"].to_pylist()))

    source = pq.ParquetFile(SOURCE)
    if source.metadata.num_rows != EXPECTED_INITIAL:
        raise RuntimeError(
            f"Unexpected source rows: {source.metadata.num_rows:,} != {EXPECTED_INITIAL:,}"
        )

    shutil.copy2(SOURCE, BACKUP)
    written = 0
    with pq.ParquetWriter(TEMP, source.schema_arrow, compression="snappy") as writer:
        for batch in source.iter_batches(batch_size=25_000):
            ids = batch["id"].to_pylist()
            urls = batch["url"].to_pylist()
            mask = pa.array(
                [(doc_id, url) in official_pairs for doc_id, url in zip(ids, urls)],
                type=pa.bool_(),
            )
            filtered = batch.filter(mask)
            if filtered.num_rows:
                writer.write_batch(filtered)
                written += filtered.num_rows
    source.close()
    del source
    gc.collect()

    removed = EXPECTED_INITIAL - written
    if removed != EXPECTED_REMOVED or written != EXPECTED_FINAL:
        raise RuntimeError(
            f"Unexpected filter result: kept {written:,}, removed {removed:,}"
        )

    filtered = pq.read_table(TEMP, columns=["id", "url"])
    filtered_ids = filtered["id"].to_pylist()
    filtered_urls = filtered["url"].to_pylist()
    filtered_pairs = set(zip(filtered_ids, filtered_urls))
    if len(filtered_pairs) != EXPECTED_FINAL:
        raise RuntimeError("Duplicate (id, url) pairs remain after filtering")
    if any(pair not in official_pairs for pair in filtered_pairs):
        raise RuntimeError("A non-official pair remains after filtering")

    embedded = pq.read_table(EMBEDDED, columns=["id", "url"])
    embedded_ids = set(embedded["id"].to_pylist())
    embedded_urls = set(embedded["url"].to_pylist())
    if embedded_ids.intersection(filtered_ids):
        raise RuntimeError("ID overlap detected with embedded_samples.parquet")
    if embedded_urls.intersection(filtered_urls):
        raise RuntimeError("URL overlap detected with embedded_samples.parquet")

    os.replace(TEMP, SOURCE)
    print(f"unembedded registry: {EXPECTED_INITIAL:,} -> {written:,} rows")
    print(f"removed non-official rows: {removed:,}")
    print(f"recoverable backup: {BACKUP}")


if __name__ == "__main__":
    main()
