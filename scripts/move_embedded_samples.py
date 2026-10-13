"""Move newly embedded samples from unembedded_samples.parquet to embedded_samples.parquet."""

import glob
import logging
import os
import sys
import pandas as pd

if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


def main():
    unembedded_path = "data/unembedded_samples.parquet"
    embedded_path = "data/embedded_samples.parquet"
    indices_dirs = [
        "data/indices/new_dataset/0-100k",
        "data/indices/new_dataset/100-200k"
    ]

    # 1. Collect all embedded IDs from index directories
    logger.info("Scanning embedded IDs from 0-100k and 100-200k...")
    all_embedded_ids = set()
    for d in indices_dirs:
        docs_files = sorted(glob.glob(os.path.join(d, "index", "docs", "*.parquet")))
        if not docs_files:
            # Fallback to text if docs not found
            docs_files = sorted(glob.glob(os.path.join(d, "index", "text", "*.parquet")))

        folder_ids = set()
        for f in docs_files:
            df_part = pd.read_parquet(f, columns=["doc_id"])
            folder_ids.update(df_part["doc_id"].astype("int64"))

        logger.info(f"  • {d}: {len(folder_ids):,} unique doc_ids found")
        all_embedded_ids.update(folder_ids)

    logger.info(f"Total newly embedded IDs to move: {len(all_embedded_ids):,}")

    # 2. Read unembedded_samples.parquet
    logger.info(f"Loading {unembedded_path}...")
    df_unembedded = pd.read_parquet(unembedded_path)
    initial_unembedded_cnt = len(df_unembedded)
    logger.info(f"Current unembedded samples: {initial_unembedded_cnt:,}")

    # 3. Partition unembedded samples
    is_embedded = df_unembedded["id"].isin(all_embedded_ids)
    df_to_move = df_unembedded[is_embedded].copy()
    df_unembedded_remaining = df_unembedded[~is_embedded].copy()

    logger.info(f"Samples matching embedded IDs (to move): {len(df_to_move):,}")
    logger.info(f"Remaining unembedded samples: {len(df_unembedded_remaining):,}")

    assert len(df_to_move) == len(all_embedded_ids), (
        f"Mismatch: found {len(df_to_move):,} matching samples in unembedded, "
        f"expected {len(all_embedded_ids):,}!"
    )
    assert len(df_unembedded_remaining) + len(df_to_move) == initial_unembedded_cnt, "Sum mismatch!"

    # 4. Read embedded_samples.parquet
    logger.info(f"Loading {embedded_path}...")
    df_embedded = pd.read_parquet(embedded_path)
    initial_embedded_cnt = len(df_embedded)
    logger.info(f"Current embedded samples: {initial_embedded_cnt:,}")

    # Check for no pre-existing overlap
    overlap = set(df_embedded["id"]).intersection(set(df_to_move["id"]))
    assert len(overlap) == 0, f"Found {len(overlap)} duplicate IDs already in embedded_samples!"

    # 5. Append df_to_move to the end of df_embedded
    logger.info("Appending new samples to the end of embedded_samples...")
    df_embedded_updated = pd.concat([df_embedded, df_to_move], ignore_index=True)

    # 6. Verification
    expected_embedded_cnt = initial_embedded_cnt + len(df_to_move)
    assert len(df_embedded_updated) == expected_embedded_cnt, "Updated embedded count mismatch!"
    assert df_embedded_updated["id"].nunique() == expected_embedded_cnt, "Duplicate IDs in updated embedded!"
    assert df_unembedded_remaining["id"].nunique() == len(df_unembedded_remaining), "Duplicate IDs in remaining unembedded!"

    # Check zero overlap between updated files
    final_overlap = set(df_embedded_updated["id"]).intersection(set(df_unembedded_remaining["id"]))
    assert len(final_overlap) == 0, "Overlap detected between embedded and unembedded files!"

    # Check that initial samples in embedded have not changed order or content
    assert (df_embedded_updated.iloc[:initial_embedded_cnt]["id"] == df_embedded["id"]).all(), "Original embedded order modified!"

    logger.info("Verification passed 100% on all integrity assertions!")

    # 7. Atomic write both files
    tmp_embedded = embedded_path + ".tmp"
    tmp_unembedded = unembedded_path + ".tmp"

    logger.info(f"Saving temporary files: {tmp_embedded} and {tmp_unembedded}...")
    df_embedded_updated.to_parquet(tmp_embedded, index=False)
    df_unembedded_remaining.to_parquet(tmp_unembedded, index=False)

    # Verify temporary files
    df_test_emb = pd.read_parquet(tmp_embedded)
    df_test_unemb = pd.read_parquet(tmp_unembedded)
    assert len(df_test_emb) == expected_embedded_cnt
    assert len(df_test_unemb) == len(df_unembedded_remaining)

    # Replace original files
    os.replace(tmp_embedded, embedded_path)
    os.replace(tmp_unembedded, unembedded_path)

    logger.info("=" * 70)
    logger.info("🎉 HOÀN THÀNH MOVE SAMPLES THÀNH CÔNG!")
    logger.info(f"   • embedded_samples.parquet:   {initial_embedded_cnt:,} -> {len(df_test_emb):,} (+{len(df_to_move):,})")
    logger.info(f"   • unembedded_samples.parquet: {initial_unembedded_cnt:,} -> {len(df_test_unemb):,} (-{len(df_to_move):,})")
    logger.info(f"   • Tổng số samples quản lý:    {len(df_test_emb) + len(df_test_unemb):,} (Không đổi)")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
