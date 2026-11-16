# Exp 139 — Qwen4B original chunk ranking, keep 90%

- Date: 2026-10-27
- Control: best-axis recombination, BTC Final `0.3148`; docs/chunks F2 `0.3731/0.2565`.
- Treatment: for each query, rank the original submitted chunks by Qwen3-Reranker-4B normalized yes/no logit score; keep the top 90% of scored chunks (ceil, minimum one), preserve all chunks over 4,096 tokens because they have no score, and preserve the original chunk order/text. `relevant_docs` is copied exactly from control.
- Kaggle input: 1,200 queries / 130,108 chunks; hash `7f3a746883c9fa52b2eeb06f46c962df940bede87dc9c82d689cd94a16ad6ba1`.
- Model: `Qwen/Qwen3-Reranker-4B`, immutable revision `22e683669bc0f0bd69640a1354a6d0aebcfeede5`.
- Four Kaggle partitions each passed independent coverage and lineage audit: 32,452; 32,408; 32,647; 32,601 rows. Merged result has 130,108 unique query/chunk pairs: 128,419 scored and 1,689 `too_long` (1.298%). All successful scores are finite, all `too_long` rows have no score and exceed the 4,096-token cap, and all query/doc/chunk/text hashes match the exact control source.
- Score diagnostics: normalized score p10/median/p90 `0.02738/0.81405/0.98813`. This describes score spread only; it is not relevance evidence.
- Candidate: `submission_qwen4b_chunks_keep90_full.zip`, 88,723,672 bytes, SHA-256 `593a846ffdbe3e1fe2eaf4f8dd1f65c7e05728d6594a9926b229105531a92549`.
- Candidate treatment retained 117,835 chunks and removed 12,273 (9.43% of original); every query changed, retaining 75–109 chunks/query. All 1,689 `too_long` chunks were preserved. Docs stayed exact to control, and candidate chunks match the ranked policy while preserving exact text and order.
- Independent candidate audit: `data/audits/qwen4b_chunks_full_merged/candidate_audit.json` passed; ZIP is below BTC's decimal 100 MB limit.
- BTC result reported by user:

```json
{
  "FINAL_SCORE": 0.3161,
  "DOCS_F2MACRO": 0.3731,
  "CHUNKS_F2MACRO": 0.2591,
  "DOCS_PRECISION": 0.2261,
  "DOCS_RECALL": 0.5631,
  "CHUNKS_PRECISION": 0.2101,
  "CHUNKS_RECALL": 0.3369
}
```

- Delta vs 0.3148 control: Final `+0.0013`; Docs metrics unchanged; Chunks F2 `+0.0026`, precision `+0.0144`, recall `-0.0058`.
- Interpretation: Qwen4B ranking has a positive but small signal at keep90, mostly improving chunk precision while sacrificing a little recall. Do not repeat full inference for nearby cutoffs; any next cutoff test should reuse this score cache. Do not generalize keep90 to other cutoffs from one point.
- Status: Exp139 is the highest BTC-confirmed score so far, while the exact 0.3148 artifact remains the reproducible reference.

## Exp140 keep80 — same score cache, BTC-scored

- Exp140 policy: keep the top 80% of scored chunks per query by the same Qwen4B ranking; preserve all `too_long` chunks and original text/order; docs remain identical.
- No model inference was rerun. Exp140 is a separate BTC-scored trial and its score is not part of Exp139.
- Artifact: `submission_qwen4b_chunks_keep80_full.zip`, 78,862,766 bytes; SHA-256 `6c24c8c73680a000adf33d42d8789ed6d10e2d4c793bf8a170bf06f33f7bacbe`.
- Retains 104,908 chunks and removes 25,200; independent audit passed at `data/audits/qwen4b_chunks_full_merged/candidate_keep80_audit.json`.
- BTC result reported by user:

```json
{
  "FINAL_SCORE": 0.3154,
  "DOCS_F2MACRO": 0.3731,
  "CHUNKS_F2MACRO": 0.2578,
  "DOCS_PRECISION": 0.2261,
  "DOCS_RECALL": 0.5631,
  "CHUNKS_PRECISION": 0.2245,
  "CHUNKS_RECALL": 0.3259
}
```

- Delta vs Exp139 keep90: Final `-0.0007`; Docs unchanged; Chunks F2 `-0.0013`, precision `+0.0144`, recall `-0.0110`.
- Delta vs 0.3148 reference: Final `+0.0006`; Chunks F2 `+0.0013`. Keep80 is inferior to keep90 on Final and chunk F2, despite higher precision.
- Decision: mark Exp140 non-promoted and stop Qwen cutoff sweeps. The observed precision/recall trade-off is now confirmed at two cutoffs; further gains should target candidate generation or matching-compatible chunk construction, not another nearby threshold.
