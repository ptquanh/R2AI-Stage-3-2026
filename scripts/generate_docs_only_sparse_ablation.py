"""Create a docs-only RRF ablation while preserving champion chunks exactly."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline",
        type=Path,
        default=ROOT / "submission_bgem3_trilingual_105m_corpus.json",
    )
    parser.add_argument(
        "--sparse-cache",
        type=Path,
        default=ROOT / "data/indices/new_dataset/index/.cache/exp41_true_union/sparse_top500_vi_only.npz",
    )
    parser.add_argument("--candidate-cache", type=Path, default=None)
    parser.add_argument("--candidate-rows-key", default="rows")
    parser.add_argument("--candidate-label", default="sparse_vi")
    parser.add_argument("--experiment", default="exp42_docs_only_sparse_vi_rrf")
    parser.add_argument(
        "--metadata",
        type=Path,
        default=ROOT / "data/indices/new_dataset/index/chunks_metadata.parquet",
    )
    parser.add_argument(
        "--official-corpus",
        type=Path,
        default=ROOT / "data/raw/btc_provided/links_corpus_vi_en_zh.parquet",
    )
    parser.add_argument(
        "--out-prefix",
        type=Path,
        default=ROOT / "submission_exp42_docs_only_sparse_vi_rrf",
    )
    parser.add_argument("--baseline-weight", type=float, default=1.0)
    parser.add_argument("--sparse-weight", "--candidate-weight", dest="sparse_weight", type=float, default=0.5)
    parser.add_argument("--rrf-k", type=int, default=60)
    parser.add_argument("--top-docs", type=int, default=100)
    return parser.parse_args()


def collapse_rows_to_doc_ranking(rows: np.ndarray, row_doc_ids: np.ndarray) -> list[int]:
    ranking: list[int] = []
    seen: set[int] = set()
    for row in rows:
        row = int(row)
        if row < 0:
            continue
        doc_id = int(row_doc_ids[row])
        if doc_id not in seen:
            seen.add(doc_id)
            ranking.append(doc_id)
    return ranking


def fuse_docs(
    baseline_docs: list[int],
    sparse_docs: list[int],
    baseline_weight: float,
    sparse_weight: float,
    rrf_k: int,
    top_docs: int,
) -> list[int]:
    scores: dict[int, float] = defaultdict(float)
    for rank, doc_id in enumerate(baseline_docs, start=1):
        scores[int(doc_id)] += baseline_weight / (rrf_k + rank)
    for rank, doc_id in enumerate(sparse_docs, start=1):
        scores[int(doc_id)] += sparse_weight / (rrf_k + rank)
    return sorted(scores, key=lambda doc_id: (-scores[doc_id], doc_id))[:top_docs]


def main() -> None:
    args = parse_args()
    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    candidate_cache = args.candidate_cache or args.sparse_cache
    sparse = np.load(candidate_cache)
    sparse_rows = sparse[args.candidate_rows_key]
    row_doc_ids = pd.read_parquet(args.metadata, columns=["doc_id"])["doc_id"].to_numpy(dtype=np.int64)
    official_doc_ids = set(
        pd.read_parquet(args.official_corpus, columns=["id"])["id"].astype(np.int64).tolist()
    )

    if len(baseline) != sparse_rows.shape[0]:
        raise ValueError("Baseline and sparse cache have different query counts")
    if "query_ids" in sparse.files:
        baseline_ids = np.asarray([item["id"] for item in baseline], dtype=np.int64)
        if not np.array_equal(baseline_ids, sparse["query_ids"]):
            raise ValueError("Baseline and sparse cache query IDs/order differ")

    output = []
    changes = []
    for query_idx, item in enumerate(baseline):
        old_docs = [int(doc_id) for doc_id in item["relevant_docs"]]
        sparse_docs = collapse_rows_to_doc_ranking(sparse_rows[query_idx], row_doc_ids)
        new_docs = fuse_docs(
            old_docs,
            sparse_docs,
            args.baseline_weight,
            args.sparse_weight,
            args.rrf_k,
            args.top_docs,
        )
        if len(new_docs) != args.top_docs or len(set(new_docs)) != len(new_docs):
            raise ValueError(f"Query {item['id']} has invalid document output")
        if any(doc_id not in official_doc_ids for doc_id in new_docs):
            raise ValueError(f"Query {item['id']} contains an out-of-corpus document")
        changes.append(len(set(new_docs).difference(old_docs)))
        output.append(
            {
                "id": int(item["id"]),
                "relevant_docs": new_docs,
                # Preserve the champion chunks byte-for-byte at the JSON value level.
                "relevant_chunks": item["relevant_chunks"],
            }
        )

    if any(new["relevant_chunks"] != old["relevant_chunks"] for new, old in zip(output, baseline)):
        raise AssertionError("Docs-only invariant failed: chunks changed")

    args.out_prefix.parent.mkdir(parents=True, exist_ok=True)
    json_path = args.out_prefix.with_suffix(".json")
    zip_path = args.out_prefix.with_suffix(".zip")
    json_path.write_text(
        json.dumps(output, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.write(json_path, arcname="submission.json")
    if zip_path.stat().st_size >= 100_000_000:
        raise ValueError(f"ZIP exceeds decimal 100 MB: {zip_path.stat().st_size} bytes")
    with zip_path.open("rb") as handle:
        sha256 = hashlib.file_digest(handle, "sha256").hexdigest()

    stats = {
        "experiment": args.experiment,
        "baseline": str(args.baseline),
        "candidate_cache": str(candidate_cache),
        "candidate_rows_key": args.candidate_rows_key,
        "candidate_label": args.candidate_label,
        "baseline_weight": args.baseline_weight,
        "candidate_weight": args.sparse_weight,
        "rrf_k": args.rrf_k,
        "queries": len(output),
        "docs_per_query": args.top_docs,
        "chunks_preserved_from_baseline": True,
        "changed_docs_mean": float(np.mean(changes)),
        "changed_docs_median": float(np.median(changes)),
        "changed_docs_p90": float(np.percentile(changes, 90)),
        "changed_docs_min": int(np.min(changes)),
        "changed_docs_max": int(np.max(changes)),
        "queries_changed": int(np.count_nonzero(changes)),
        "zip_bytes": zip_path.stat().st_size,
        "zip_sha256": sha256,
    }
    manifest_path = args.out_prefix.with_name(args.out_prefix.name + "_manifest.json")
    manifest_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
