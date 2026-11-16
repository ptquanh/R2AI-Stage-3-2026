# Exp143 — Add P2a spans to long chunks

## Hypothesis

An exact shorter span can provide a better two-sided LCS match for some long predictions while the original prediction remains available. This is append-only and does not assume the P2a score is calibrated relevance.

## Configuration and artifact

- Control: BTC-scored Exp142 (`submission_exp142_missing_owners_add5.zip`), 183,703 docs and 123,835 chunks.
- Restrict to the longest decile of control chunks for which P2a has an exact `chunk_sha256` match (cutoff 7,152 characters).
- For each eligible chunk, choose its highest normalized-score P2a window; append up to 3 windows/query by score.
- P2a windows were prepared from an earlier chunk artifact. Builder verifies the chunk hash matches the current control and the window text equals the exact source slice at the stored offsets.
- Candidate: `submission_exp143_p2a_long_chunks_add3.zip`; 1,200 queries, 183,703 docs, 3,436 additions, 127,271 total chunks; 94,478,622 bytes.
- SHA-256: `039eb431209008b00eeb7b8df76b4d784c20a677c1b375444a167bf19f229649`.
- Audit: `data/audits/final_public_sprint_20261027/exp143_audit.json` — passed; docs unchanged, all Exp142 chunks preserved as exact prefix, no within-query duplicate chunks, ZIP CRC passed.

## Result and interpretation

BTC result: **Final 0.3190**, Docs F2/P/R `0.3731 / 0.2261 / 0.5631`; Chunks F2/P/R `0.2648 / 0.2047 / 0.3510`.

Against Exp142, docs metrics are unchanged; chunk F2 rose `+0.0009`, precision fell `-0.0022`, recall rose `+0.0030`, and Final rose `+0.0005`. Exp143 is the current champion; retain Exp142 as fallback. The gain is small, so stop P2a window/cap sweeps.
