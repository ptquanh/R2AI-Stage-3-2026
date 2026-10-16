"""Combine document predictions and chunk predictions from two submissions."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--docs-source",
        type=Path,
        default=ROOT / "submission_exp46_docs125_dense_tail_clean1115k.json",
    )
    parser.add_argument(
        "--chunks-source",
        type=Path,
        default=ROOT / "submission_exp47_merged_chunk_envelopes.json",
    )
    parser.add_argument(
        "--official-corpus",
        type=Path,
        default=ROOT / "data/raw/btc_provided/links_corpus_vi_en_zh.parquet",
    )
    parser.add_argument(
        "--out-prefix",
        type=Path,
        default=ROOT / "submission_exp50_docs125_merged_envelopes",
    )
    args = parser.parse_args()

    docs_data = load(args.docs_source)
    chunks_data = load(args.chunks_source)
    chunks_by_id = {int(item["id"]): item for item in chunks_data}
    if len(docs_data) != 1200 or len(chunks_by_id) != 1200:
        raise AssertionError("Both sources must contain 1,200 unique queries")

    official_ids = set(
        pd.read_parquet(args.official_corpus, columns=["id"])["id"].astype(int)
    )
    output: list[dict] = []
    for docs_item in docs_data:
        query_id = int(docs_item["id"])
        chunks_item = chunks_by_id.get(query_id)
        if chunks_item is None:
            raise AssertionError(f"Missing query {query_id} in chunks source")

        docs = [int(doc_id) for doc_id in docs_item["relevant_docs"]]
        chunks = chunks_item["relevant_chunks"]
        if len(docs) != 125 or len(set(docs)) != 125:
            raise AssertionError(f"Query {query_id} does not contain 125 unique docs")
        if not set(docs).issubset(official_ids):
            raise AssertionError(f"Query {query_id} has an out-of-corpus document")

        seen_chunks: set[tuple[int, str]] = set()
        for chunk in chunks:
            key = (int(chunk["doc_id"]), str(chunk["chunk_text"]))
            if key[0] not in official_ids or not key[1] or key in seen_chunks:
                raise AssertionError(f"Invalid/duplicate chunk for query {query_id}")
            seen_chunks.add(key)

        output.append(
            {"id": query_id, "relevant_docs": docs, "relevant_chunks": chunks}
        )

    output.sort(key=lambda item: item["id"])
    if [item["id"] for item in output] != sorted(chunks_by_id):
        raise AssertionError("Query ID sets differ between sources")
    if any(
        item["relevant_docs"] != source["relevant_docs"]
        for item, source in zip(output, sorted(docs_data, key=lambda value: int(value["id"])))
    ):
        raise AssertionError("Document predictions changed during combination")
    if any(
        item["relevant_chunks"] != chunks_by_id[item["id"]]["relevant_chunks"]
        for item in output
    ):
        raise AssertionError("Chunk predictions changed during combination")

    json_path = args.out_prefix.with_suffix(".json")
    zip_path = args.out_prefix.with_suffix(".zip")
    manifest_path = args.out_prefix.with_name(args.out_prefix.name + "_manifest.json")
    json_path.write_text(
        json.dumps(output, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    with zipfile.ZipFile(
        zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        archive.write(json_path, arcname="submission.json")
    if zip_path.stat().st_size >= 100_000_000:
        raise ValueError(f"ZIP exceeds decimal 100 MB: {zip_path.stat().st_size:,} bytes")

    with zip_path.open("rb") as handle:
        sha256 = hashlib.file_digest(handle, "sha256").hexdigest()
    chunk_counts = [len(item["relevant_chunks"]) for item in output]
    manifest = {
        "experiment": "exp50_docs125_merged_envelopes",
        "docs_source": args.docs_source.name,
        "chunks_source": args.chunks_source.name,
        "queries": len(output),
        "docs_per_query": 125,
        "chunks_per_query": {
            "min": min(chunk_counts),
            "mean": sum(chunk_counts) / len(chunk_counts),
            "max": max(chunk_counts),
        },
        "expected_metrics_if_axis_independence_holds": {
            "docs_f2macro": 0.3336,
            "chunks_f2macro": 0.2851,
            "final_score": 0.30935,
        },
        "zip_bytes": zip_path.stat().st_size,
        "zip_sha256": sha256,
        "validation": {
            "docs_identical_to_exp46": True,
            "chunks_identical_to_exp47": True,
            "official_doc_ids_only": True,
            "unique_docs_and_chunks_per_query": True,
            "single_json_at_zip_root": True,
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
