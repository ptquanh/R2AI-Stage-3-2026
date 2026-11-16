# Qwen4B original-chunk pilot

- Date: 2026-10-26
- Purpose: score the exact chunk strings from the 0.3148 best-axis control before any filtering; this pilot is a systems/provenance check, not a local relevance evaluation.
- Model: `Qwen/Qwen3-Reranker-4B` at immutable revision `22e683669bc0f0bd69640a1354a6d0aebcfeede5`.
- Input: 120 fixed pilot queries, 12.880 chunks; Parquet SHA-256 `5697bdd7a1aae512b0c53d93fdb84994ee408448632b3e2df9aef77fde485240`.
- Result: 12.695 `ok`, 185 `too_long` (1,436%), zero inference errors. Independent audit found full pair coverage, zero source/hash lineage mismatches, finite scores for every successful row, and no implicit truncation.
- Throughput: approximately 0,615 and 0,607 pair/s on the two T4 workers. A two-part full run would take about 15 hours/part, so it is rejected operationally; full scoring is split into four balanced 300-query parts at roughly 7,4 hours/part.
- Score diagnostics only: normalized p10/median/p90 `0,0248/0,7879/0,9871`. This indicates usable score spread but does not establish relevance without BTC labels.
- Audit: `data/audits/qwen4b_chunks_pilot/audit.json`.
- Full-run blocker: the current Kaggle account has 0 GPU hours remaining until 2026-10-31 07:00 Asia/Bangkok. The four full notebooks are prepared but not started.

Decision: continue full scoring on a second Kaggle account; do not build a submission from pilot scores and do not alter chunk text or segmentation.
