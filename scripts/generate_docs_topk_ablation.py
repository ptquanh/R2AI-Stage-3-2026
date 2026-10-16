"""Create a document top-k ablation while preserving chunk outputs exactly."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline",
        type=Path,
        default=ROOT / "submission_bgem3_trilingual_105m_corpus.json",
    )
    parser.add_argument("--top-docs", type=int, default=75)
    parser.add_argument(
        "--official-corpus",
        type=Path,
        default=ROOT / "data/raw/btc_provided/links_corpus_vi_en_zh.parquet",
    )
    parser.add_argument(
        "--out-prefix",
        type=Path,
        default=ROOT / "submission_exp44_docs_top75_chunks_exp40",
    )
    args = parser.parse_args()

    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    official_ids = set(
        pd.read_parquet(args.official_corpus, columns=["id"])["id"].astype(int).tolist()
    )
    output = []
    for item in baseline:
        docs = [int(doc_id) for doc_id in item["relevant_docs"][: args.top_docs]]
        if len(docs) != args.top_docs or len(set(docs)) != len(docs):
            raise ValueError(f"Query {item['id']} does not have {args.top_docs} unique docs")
        if any(doc_id not in official_ids for doc_id in docs):
            raise ValueError(f"Query {item['id']} contains an out-of-corpus doc")
        output.append(
            {
                "id": int(item["id"]),
                "relevant_docs": docs,
                "relevant_chunks": item["relevant_chunks"],
            }
        )
    if any(new["relevant_chunks"] != old["relevant_chunks"] for new, old in zip(output, baseline)):
        raise AssertionError("Chunks changed in a docs-only top-k ablation")

    json_path = args.out_prefix.with_suffix(".json")
    zip_path = args.out_prefix.with_suffix(".zip")
    json_path.write_text(json.dumps(output, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.write(json_path, arcname="submission.json")
    if zip_path.stat().st_size >= 100_000_000:
        raise ValueError(f"ZIP exceeds decimal 100 MB: {zip_path.stat().st_size} bytes")
    with zip_path.open("rb") as handle:
        sha256 = hashlib.file_digest(handle, "sha256").hexdigest()
    manifest = {
        "experiment": f"docs_top{args.top_docs}_chunks_preserved",
        "baseline": str(args.baseline),
        "queries": len(output),
        "docs_per_query": args.top_docs,
        "chunks_preserved_from_baseline": True,
        "zip_bytes": zip_path.stat().st_size,
        "zip_sha256": sha256,
    }
    manifest_path = args.out_prefix.with_name(args.out_prefix.name + "_manifest.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
