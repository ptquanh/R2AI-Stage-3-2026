# Exp142 — Add five missing-owner parents per query

## Hypothesis

Some retrieved documents may add chunk recall when their verbatim source parent is emitted, even though no chunk for that document appeared in the original best-axis chunk set. This is a bounded append-only treatment.

## Configuration and artifact

- Control: Exp139 keep90 (`submission_qwen4b_chunks_keep90_full.zip`): 183,703 docs/query-doc pairs and 117,835 chunks.
- Keep all control docs and chunks unchanged.
- Candidate pool: returned docs missing from the original 130,108-chunk set; rank by equal-weight Qwen4B/BGE P1 reciprocal-rank fusion, `k=60`; up to 5 parents/query.
- Source: full verbatim text from the active index; 5,708 unique source parents selected and reused where applicable, yielding 6,000 appended chunk rows (5/query).
- Candidate: `submission_exp142_missing_owners_add5.zip`, 94,214,806 bytes; expected below the 100 MB submission cap.
- SHA-256: `7b545b65765c528e1abb708a89bd65be1ef57f507f04c101fc722bc094627a82`.
- Independent audit report: `data/audits/final_public_sprint_20261027/exp142_audit.json` — passed. It verifies official corpus membership, missing-owner eligibility against the original chunk set, verbatim text against the active index, unchanged docs, exact preservation of all control chunks, cardinalities and ZIP CRC.

## Result and interpretation

BTC result: **Final 0.3185**, Docs F2/P/R `0.3731 / 0.2261 / 0.5631`; Chunks F2/P/R `0.2639 / 0.2069 / 0.3480`.

Against Exp139, docs metrics are unchanged. Chunk F2 increased `+0.0048`, precision fell `-0.0032`, and recall rose `+0.0111`; Final increased `+0.0024`. Exp142 was the best confirmed artifact before Exp143 and remains its fallback. Avoid attributing the gain to any one of the five additions/query without per-addition labels.
