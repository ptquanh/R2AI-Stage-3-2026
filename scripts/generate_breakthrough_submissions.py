"""Generate four metric-aware submission ablations from the Exp45 champion.

The script never mutates the search index.  It creates:

* Exp46: retain Exp45 chunks and append 25 document candidates from the
  clean-index dense top-500 cache.
* Exp47: merge nearby retrieved chunks from the same document into verbatim
  parent envelopes.
* Exp48: keep the top 64 chunks and expand each to a 4,500-character
  verbatim parent window.
* Exp49: keep the top 48 chunks and expand each to a 7,000-character
  verbatim parent window.

All chunk outputs remain exact substrings of documents in the official corpus.
"""

from __future__ import annotations

import hashlib
import json
import statistics
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "submission_exp45_champion_clean1115k.json"
OFFICIAL = ROOT / "data/raw/btc_provided/links_corpus_vi_en_zh.parquet"
INDEX = ROOT / "data/indices/new_dataset/index"
DENSE_CACHE = INDEX / ".cache/exp41_true_union/dense_top500.npz"
META = INDEX / "chunks_metadata.parquet"
TEXT_DIR = INDEX / "text"
MAX_ZIP_BYTES = 100_000_000


def load_json(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_artifact(
    output: list[dict[str, Any]],
    prefix: str,
    experiment: str,
    policy: dict[str, Any],
    texts: dict[int, str] | None = None,
    chunks_preserved_from_baseline: bool = False,
) -> dict[str, Any]:
    json_path = ROOT / f"{prefix}.json"
    zip_path = ROOT / f"{prefix}.zip"
    manifest_path = ROOT / f"{prefix}_manifest.json"

    official_ids = set(pd.read_parquet(OFFICIAL, columns=["id"])["id"].astype(int))
    query_ids = [int(item["id"]) for item in output]
    if len(output) != 1200 or len(set(query_ids)) != 1200:
        raise AssertionError("Submission must contain 1,200 unique queries")

    chunk_lengths: list[int] = []
    for item in output:
        docs = [int(doc_id) for doc_id in item["relevant_docs"]]
        if len(docs) != len(set(docs)):
            raise AssertionError(f"Duplicate document for query {item['id']}")
        if not set(docs).issubset(official_ids):
            raise AssertionError(f"Out-of-corpus document for query {item['id']}")

        seen_chunks: set[tuple[int, str]] = set()
        for chunk in item["relevant_chunks"]:
            doc_id = int(chunk["doc_id"])
            chunk_text = str(chunk["chunk_text"])
            key = (doc_id, chunk_text)
            if doc_id not in official_ids or not chunk_text or key in seen_chunks:
                raise AssertionError(f"Invalid/duplicate chunk for query {item['id']}")
            if texts is not None and chunk_text not in texts.get(doc_id, ""):
                raise AssertionError(
                    f"Non-verbatim chunk for query {item['id']}, doc {doc_id}"
                )
            seen_chunks.add(key)
            chunk_lengths.append(len(chunk_text))

    json_path.write_text(
        json.dumps(output, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    with zipfile.ZipFile(
        zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        archive.write(json_path, arcname="submission.json")
    if zip_path.stat().st_size >= MAX_ZIP_BYTES:
        raise ValueError(
            f"{zip_path.name} exceeds decimal 100 MB: {zip_path.stat().st_size:,} bytes"
        )

    with zip_path.open("rb") as handle:
        sha256 = hashlib.file_digest(handle, "sha256").hexdigest()
    docs_per_query = [len(item["relevant_docs"]) for item in output]
    chunks_per_query = [len(item["relevant_chunks"]) for item in output]
    manifest = {
        "experiment": experiment,
        "baseline": BASELINE.name,
        "policy": policy,
        "queries": len(output),
        "docs_per_query": {
            "min": min(docs_per_query),
            "mean": statistics.fmean(docs_per_query),
            "max": max(docs_per_query),
        },
        "chunks_per_query": {
            "min": min(chunks_per_query),
            "mean": statistics.fmean(chunks_per_query),
            "max": max(chunks_per_query),
        },
        "chunk_chars": {
            "min": min(chunk_lengths),
            "mean": statistics.fmean(chunk_lengths),
            "median": statistics.median(chunk_lengths),
            "max": max(chunk_lengths),
        },
        "zip_bytes": zip_path.stat().st_size,
        "zip_sha256": sha256,
        "validation": {
            "official_doc_ids_only": True,
            "unique_docs_per_query": True,
            "unique_doc_chunk_pairs_per_query": True,
            "verbatim_source_substrings": texts is not None,
            "chunks_preserved_from_baseline": chunks_preserved_from_baseline,
            "single_json_at_zip_root": True,
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return manifest


def make_exp46(baseline: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cache = np.load(DENSE_CACHE, allow_pickle=False)
    metadata = pd.read_parquet(META, columns=["doc_id"])
    row_doc_ids = metadata["doc_id"].to_numpy(dtype=np.int64, copy=False)
    query_ids = cache["query_ids"].astype(int)
    dense_rows = cache["dense_vi_rows"]
    cache_by_query = {int(qid): dense_rows[idx] for idx, qid in enumerate(query_ids)}

    output: list[dict[str, Any]] = []
    for item in baseline:
        query_id = int(item["id"])
        docs = [int(doc_id) for doc_id in item["relevant_docs"]]
        seen = set(docs)
        for row_idx in cache_by_query[query_id]:
            doc_id = int(row_doc_ids[int(row_idx)])
            if doc_id not in seen:
                docs.append(doc_id)
                seen.add(doc_id)
            if len(docs) >= 125:
                break
        if len(docs) < 125:
            raise AssertionError(f"Only {len(docs)} docs available for query {query_id}")
        output.append(
            {
                "id": query_id,
                "relevant_docs": docs[:125],
                "relevant_chunks": item["relevant_chunks"],
            }
        )
    return output


def load_needed_texts(baseline: list[dict[str, Any]]) -> dict[int, str]:
    needed = {
        int(chunk["doc_id"])
        for item in baseline
        for chunk in item["relevant_chunks"]
    }
    texts: dict[int, str] = {}
    for path in sorted(TEXT_DIR.glob("part_*.parquet")):
        frame = pd.read_parquet(path, columns=["doc_id", "text"])
        subset = frame[frame["doc_id"].isin(needed)]
        texts.update(
            (int(row.doc_id), str(row.text)) for row in subset.itertuples(index=False)
        )
        if len(texts) == len(needed):
            break
    missing = needed - set(texts)
    if missing:
        raise AssertionError(f"Missing source texts for {len(missing):,} documents")
    return texts


def locate(text: str, chunk: str) -> tuple[int, int]:
    start = text.find(chunk)
    if start < 0:
        raise AssertionError("Champion chunk is not a source substring")
    return start, start + len(chunk)


def parent_window(text: str, start: int, end: int, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    if end - start >= max_chars:
        return text[start:end]
    extra = max_chars - (end - start)
    left = max(0, start - extra // 2)
    right = min(len(text), end + (extra - (start - left)))
    left = max(0, left - (max_chars - (right - left)))
    return text[left:right]


def make_parent_windows(
    baseline: list[dict[str, Any]],
    texts: dict[int, str],
    top_chunks: int,
    max_chars: int,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for item in baseline:
        chunks: list[dict[str, Any]] = []
        seen: set[tuple[int, str]] = set()
        for chunk in item["relevant_chunks"][:top_chunks]:
            doc_id = int(chunk["doc_id"])
            source = texts[doc_id]
            start, end = locate(source, str(chunk["chunk_text"]))
            expanded = parent_window(source, start, end, max_chars)
            key = (doc_id, expanded)
            if key not in seen:
                seen.add(key)
                chunks.append({"doc_id": doc_id, "chunk_text": expanded})
        output.append(
            {
                "id": int(item["id"]),
                "relevant_docs": [int(doc_id) for doc_id in item["relevant_docs"]],
                "relevant_chunks": chunks,
            }
        )
    return output


def make_merged_envelopes(
    baseline: list[dict[str, Any]],
    texts: dict[int, str],
    max_gap: int = 2_000,
    max_span: int = 7_000,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for item in baseline:
        by_doc: dict[int, list[tuple[int, int, int]]] = defaultdict(list)
        for rank, chunk in enumerate(item["relevant_chunks"]):
            doc_id = int(chunk["doc_id"])
            start, end = locate(texts[doc_id], str(chunk["chunk_text"]))
            by_doc[doc_id].append((rank, start, end))

        ranked_envelopes: list[tuple[int, int, str]] = []
        for doc_id, spans in by_doc.items():
            spans.sort(key=lambda value: value[1])
            clusters: list[list[tuple[int, int, int]]] = []
            for span in spans:
                if not clusters:
                    clusters.append([span])
                    continue
                cluster = clusters[-1]
                cluster_start = min(value[1] for value in cluster)
                cluster_end = max(value[2] for value in cluster)
                new_start = min(cluster_start, span[1])
                new_end = max(cluster_end, span[2])
                gap = max(0, span[1] - cluster_end)
                if gap <= max_gap and new_end - new_start <= max_span:
                    cluster.append(span)
                else:
                    clusters.append([span])
            for cluster in clusters:
                rank = min(value[0] for value in cluster)
                start = min(value[1] for value in cluster)
                end = max(value[2] for value in cluster)
                ranked_envelopes.append((rank, doc_id, texts[doc_id][start:end]))

        ranked_envelopes.sort(key=lambda value: value[0])
        chunks = [
            {"doc_id": doc_id, "chunk_text": chunk_text}
            for _, doc_id, chunk_text in ranked_envelopes
        ]
        output.append(
            {
                "id": int(item["id"]),
                "relevant_docs": [int(doc_id) for doc_id in item["relevant_docs"]],
                "relevant_chunks": chunks,
            }
        )
    return output


def main() -> None:
    baseline = load_json(BASELINE)
    texts = load_needed_texts(baseline)

    exp46 = make_exp46(baseline)
    if any(
        new["relevant_chunks"] != old["relevant_chunks"]
        for new, old in zip(exp46, baseline)
    ):
        raise AssertionError("Exp46 must preserve every Exp45 chunk exactly")
    write_artifact(
        exp46,
        "submission_exp46_docs125_dense_tail_clean1115k",
        "exp46_docs125_dense_tail_clean1115k",
        {
            "documents": "Exp45 top-100 plus clean-index dense-VI tail to 125",
            "chunks": "preserved exactly from Exp45",
        },
        texts,
        chunks_preserved_from_baseline=True,
    )

    exp47 = make_merged_envelopes(baseline, texts)
    write_artifact(
        exp47,
        "submission_exp47_merged_chunk_envelopes",
        "exp47_merged_chunk_envelopes",
        {
            "documents": "preserved exactly from Exp45",
            "chunks": "merge same-document spans when gap <= 2,000 and envelope <= 7,000 chars",
        },
        texts,
    )

    for number, top_chunks, max_chars in ((48, 64, 4_500), (49, 48, 7_000)):
        output = make_parent_windows(baseline, texts, top_chunks, max_chars)
        write_artifact(
            output,
            f"submission_exp{number}_parent{max_chars}_top{top_chunks}",
            f"exp{number}_parent{max_chars}_top{top_chunks}",
            {
                "documents": "preserved exactly from Exp45",
                "chunks": f"Exp45 top-{top_chunks}, expanded verbatim to at most {max_chars} chars",
            },
            texts,
        )


if __name__ == "__main__":
    main()
