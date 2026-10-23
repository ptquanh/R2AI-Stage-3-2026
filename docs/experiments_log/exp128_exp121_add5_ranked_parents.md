# Exp128 — Exp121 + 5 ranked full-parent additions

## Hypothesis

Exp127/122's parent additions target missing reference chunks, but may dilute chunk precision. Exp128 keeps every Exp121 chunk and takes only the first 5 of Exp122's 19 rank-ordered full-parent additions per query. This is the more selective point in the same precision/recall ladder. Docs and all Exp121 evidence remain unchanged.

## Artifact and validation

- ZIP: `submission_exp128_exp121_add5_ranked_parents.zip` (`87,524,955` bytes; below decimal 100 MB).
- 1,200 queries; intended 6,000 new parents (5/query); 113,308 total chunks.
- Every Exp121 chunk is preserved exactly; additions are the first 5 of Exp122's selected-document-rank additions.
- ZIP has one root `submission.json`, LZMA method, CRC passes. Packaging script confirmed under-limit size and exact Exp121 prefix.
- ZIP SHA-256: `d61283b47e7bf8afe3725d3bb3f5f083b902f062141681de284ce47ddf1b2471`.

## BTC result

Pending manual submission. Docs metrics should match Exp121/122; official BTC results are required to determine whether the narrower chunk output improves macro-F2.
