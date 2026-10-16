"""Merge successful local crawl rows and audit intentionally excluded URLs.

The update is recoverable (timestamped backups), uses atomic replacement for
each parquet, and verifies that embedded/unembedded/remaining/excluded remain
a disjoint exact partition of the official BTC corpus.
"""

from __future__ import annotations

import glob
import os
import shutil
import time
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EMBEDDED = DATA / "embedded_samples.parquet"
UNEMBEDDED = DATA / "unembedded_samples.parquet"
REMAINING = DATA / "remaining_urls.parquet"
EXCLUDED = DATA / "excluded_urls.parquet"
OFFICIAL = DATA / "raw/btc_provided/links_corpus_vi_en_zh.parquet"
RECOVERED_DIR = DATA / "raw/corpus_text/local_recovered"

EXCLUDED_DOMAINS = {"thaythuocvietnam.vn"}


def normalized_domain(url: str) -> str:
    return (urlparse(str(url)).hostname or "").lower().removeprefix("www.")


def belongs_to_domain(url: str, domain: str) -> bool:
    host = normalized_domain(url)
    return host == domain or host.endswith("." + domain)


def atomic_write(frame: pd.DataFrame, path: Path) -> None:
    temp = path.with_name(path.name + ".tmp")
    frame.to_parquet(temp, index=False, compression="snappy")
    os.replace(temp, path)


def assert_unique(frame: pd.DataFrame, name: str) -> None:
    if frame["id"].duplicated().any():
        raise AssertionError(f"{name} contains duplicate IDs")
    if frame["url"].astype(str).duplicated().any():
        raise AssertionError(f"{name} contains duplicate URLs")


def main() -> None:
    embedded = pd.read_parquet(EMBEDDED)
    unembedded = pd.read_parquet(UNEMBEDDED)
    remaining = pd.read_parquet(REMAINING)
    official = pd.read_parquet(OFFICIAL, columns=["id", "url"])
    if EXCLUDED.exists():
        excluded = pd.read_parquet(EXCLUDED)
    else:
        excluded = pd.DataFrame(columns=["id", "url", "reason", "excluded_at"])

    success_parts = []
    not_found_parts = []
    for file_name in sorted(glob.glob(str(RECOVERED_DIR / "*.parquet"))):
        part = pd.read_parquet(file_name)
        if "status" in part.columns:
            status = part["status"].fillna("").astype(str).str.lower()
            reason = part.get("reason", pd.Series("", index=part.index)).fillna("").astype(str)
            successes_in_part = part[status.eq("success")].copy()
            confirmed_not_found = status.eq("dropped") & reason.str.match(
                r"^HTTP\s+(?:404|410)\s+Not Found$", case=False
            )
            not_found_in_part = part[confirmed_not_found][["id", "url"]].dropna().copy()
            if not not_found_in_part.empty:
                not_found_parts.append(not_found_in_part)
            part = successes_in_part
        if not part.empty:
            part = part[["id", "url", "text"]].dropna(subset=["id", "url", "text"])
            part["text"] = part["text"].astype(str).str.strip()
            part = part[part["text"].str.len() > 0]
            success_parts.append(part)
    successes = (
        pd.concat(success_parts, ignore_index=True).drop_duplicates("id", keep="last")
        if success_parts
        else pd.DataFrame(columns=["id", "url", "text"])
    )
    successes["id"] = successes["id"].astype("int64")
    successes["url"] = successes["url"].astype(str)
    not_found = (
        pd.concat(not_found_parts, ignore_index=True).drop_duplicates("id", keep="last")
        if not_found_parts
        else pd.DataFrame(columns=["id", "url"])
    )
    not_found["id"] = not_found["id"].astype("int64")
    not_found["url"] = not_found["url"].astype(str)
    # A successful result from any part takes precedence over an older 404.
    not_found = not_found[~not_found["id"].isin(set(successes["id"]))].copy()

    official_pairs = set(zip(official["id"].astype(int), official["url"].astype(str)))
    invalid_success = successes[
        ~successes.apply(lambda row: (int(row["id"]), str(row["url"])) in official_pairs, axis=1)
    ]
    if not invalid_success.empty:
        raise AssertionError(f"Recovered successes outside official corpus: {len(invalid_success)}")
    invalid_not_found = not_found[
        ~not_found.apply(lambda row: (int(row["id"]), str(row["url"])) in official_pairs, axis=1)
    ]
    if not invalid_not_found.empty:
        raise AssertionError(f"Recovered 404s outside official corpus: {len(invalid_not_found)}")

    managed_ids = set(embedded["id"].astype(int)) | set(unembedded["id"].astype(int))
    new_successes = successes[~successes["id"].isin(managed_ids)].copy()
    updated_unembedded = pd.concat([unembedded, new_successes], ignore_index=True)
    updated_unembedded = updated_unembedded.drop_duplicates("id", keep="first")

    success_ids = set(successes["id"].astype(int))
    after_success = remaining[~remaining["id"].isin(success_ids)].copy()
    not_found_ids = set(not_found["id"].astype(int))
    not_found_mask = after_success["id"].isin(not_found_ids)
    newly_not_found = after_success[not_found_mask].copy()
    newly_not_found["reason"] = "recovered_http_not_found"
    newly_not_found["excluded_at"] = pd.Timestamp.now(tz="Asia/Bangkok").isoformat()
    after_not_found = after_success[~not_found_mask].copy()

    excluded_mask = pd.Series(False, index=after_not_found.index)
    for domain in EXCLUDED_DOMAINS:
        excluded_mask |= after_not_found["url"].astype(str).map(lambda url: belongs_to_domain(url, domain))
    newly_excluded = after_not_found[excluded_mask].copy()
    newly_excluded["reason"] = "domain_excluded:thaythuocvietnam.vn"
    newly_excluded["excluded_at"] = pd.Timestamp.now(tz="Asia/Bangkok").isoformat()
    updated_remaining = after_not_found[~excluded_mask].copy()

    updated_excluded = pd.concat([excluded, newly_not_found, newly_excluded], ignore_index=True)
    updated_excluded = updated_excluded.drop_duplicates("id", keep="last")

    for name, frame in (
        ("embedded", embedded),
        ("unembedded", updated_unembedded),
        ("remaining", updated_remaining),
        ("excluded", updated_excluded),
    ):
        assert_unique(frame, name)

    official_ids = set(official["id"].astype(int))
    sets = {
        "embedded": set(embedded["id"].astype(int)),
        "unembedded": set(updated_unembedded["id"].astype(int)),
        "remaining": set(updated_remaining["id"].astype(int)),
        "excluded": set(updated_excluded["id"].astype(int)),
    }
    names = list(sets)
    for index, left in enumerate(names):
        if not sets[left].issubset(official_ids):
            raise AssertionError(f"{left} contains IDs outside official corpus")
        for right in names[index + 1 :]:
            overlap = sets[left] & sets[right]
            if overlap:
                raise AssertionError(f"{left}/{right} overlap: {len(overlap)}")
    union = set().union(*sets.values())
    if union != official_ids:
        raise AssertionError(
            f"Partition mismatch: missing={len(official_ids - union)}, extra={len(union - official_ids)}"
        )

    stamp = time.strftime("%Y%m%dT%H%M%S")
    backup_unembedded = DATA / f"unembedded_samples.pre_local_sync_{stamp}.bak.parquet"
    backup_remaining = DATA / f"remaining_urls.pre_local_sync_{stamp}.bak.parquet"
    shutil.copy2(UNEMBEDDED, backup_unembedded)
    shutil.copy2(REMAINING, backup_remaining)

    atomic_write(updated_unembedded, UNEMBEDDED)
    atomic_write(updated_remaining, REMAINING)
    atomic_write(updated_excluded, EXCLUDED)

    print(f"Recovered success unique: {len(successes):,}")
    print(f"Added to unembedded: {len(new_successes):,}")
    print(f"Removed successes from remaining: {len(remaining) - len(after_success):,}")
    print(f"Newly excluded confirmed HTTP 404/410 URLs: {len(newly_not_found):,}")
    print(f"Newly excluded domain URLs: {len(newly_excluded):,}")
    print(f"unembedded: {len(unembedded):,} -> {len(updated_unembedded):,}")
    print(f"remaining: {len(remaining):,} -> {len(updated_remaining):,}")
    print(f"excluded: {len(excluded):,} -> {len(updated_excluded):,}")
    print(f"Backup: {backup_unembedded}")
    print(f"Backup: {backup_remaining}")
    print("Partition invariant: PASS")


if __name__ == "__main__":
    main()
