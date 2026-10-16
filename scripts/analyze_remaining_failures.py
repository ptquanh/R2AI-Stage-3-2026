"""Summarize remaining crawl coverage against local_recovered history."""

from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def domain(url: str) -> str:
    return (urlparse(str(url)).hostname or "").lower().removeprefix("www.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remaining", type=Path, default=ROOT / "data/remaining_urls.parquet")
    parser.add_argument(
        "--recovered-dir",
        type=Path,
        default=ROOT / "data/raw/corpus_text/local_recovered",
    )
    args = parser.parse_args()

    remaining = pd.read_parquet(args.remaining, columns=["id", "url"])
    parts = []
    for file_path in sorted(args.recovered_dir.rglob("*.parquet")):
        part = pd.read_parquet(file_path)
        if {"id", "status"}.issubset(part.columns):
            part = part[[column for column in ("id", "status", "reason") if column in part.columns]].copy()
            part["source_file"] = file_path.name
            parts.append(part)

    history = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=["id", "status", "reason"])
    latest = history.drop_duplicates("id", keep="last")
    merged = remaining.merge(latest, on="id", how="left")
    merged["domain"] = merged["url"].map(domain)
    merged["status"] = merged["status"].fillna("no_persisted_result")
    merged["reason"] = merged["reason"].fillna("No persisted result")

    rows = []
    for host, group in merged.groupby("domain"):
        top_reason = group["reason"].value_counts()
        rows.append(
            {
                "domain": host,
                "remaining": len(group),
                "no_persisted_result": int(group["status"].eq("no_persisted_result").sum()),
                "dropped": int(group["status"].eq("dropped").sum()),
                "error": int(group["status"].eq("error").sum()),
                "top_reason": top_reason.index[0],
                "top_reason_count": int(top_reason.iloc[0]),
            }
        )

    report = pd.DataFrame(rows).sort_values(["remaining", "domain"], ascending=[False, True])
    print(f"Remaining URLs: {len(remaining):,}")
    print(f"Domains: {remaining['url'].map(domain).nunique():,}")
    print(report.to_string(index=False))


if __name__ == "__main__":
    main()
