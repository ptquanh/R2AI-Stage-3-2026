# Exp141 — Qwen top130 docs, keep90 chunks

## Hypothesis

Owner-floor documents retained by the prior joint docs/chunks policy may hurt document precision. This isolates that policy by keeping Exp139 chunks unchanged and switching only document membership to pure Qwen4B top130.

## Configuration and artifact

- 1,200 queries; 156,000 query-doc rows (130/query), selected from the full Qwen4B ranking.
- All 117,835 Exp139 chunks are preserved exactly.
- Output: `submission_exp141_qwen_top130_keep90.zip`.
- Size: 88,621,741 bytes; SHA-256: `8a65382eb9497c2f43084ce405dbd56aaaa17a7e15e9fcd9df14d18586f571d2`.
- Audit: `data/audits/final_public_sprint_20261027/exp141_audit.json`; verified query count, docs against Qwen top130, official corpus membership, and exact chunk equality to Exp139.

## Result

BTC result: **Final 0.3094**, Docs F2/P/R `0.3596 / 0.2356 / 0.5226`; Chunks F2/P/R `0.2591 / 0.2101 / 0.3369`.

Against Exp139 keep90 (Final 0.3161; Docs F2/P/R `0.3731 / 0.2261 / 0.5631`; chunks unchanged), docs precision rose `+0.0095`, but recall fell `-0.0405` and Docs F2 fell `-0.0135`; Final fell `-0.0067`. The 27,703 owner-floor pairs help document recall/F2 on this test. Do not promote this artifact or continue the top-k/owner-release sweep.
