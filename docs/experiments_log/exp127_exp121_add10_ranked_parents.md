# Exp127 — Exp121 + 10 ranked full-parent additions

## Hypothesis

Exp122 added 19 full-source parents/query to Exp121 and moved chunk precision/recall from `0.2668/0.4174` to `0.2512/0.4682`, improving chunk F2 from `0.3238` to `0.3446`. Exp127 keeps every Exp121 chunk and tests the first 10 of Exp122's 19 rank-ordered additions, targeting a midpoint on the recall/precision tradeoff. Docs and the complete Exp121 evidence set are unchanged.

## Artifact and validation

- ZIP: `submission_exp127_exp121_add10_ranked_parents.zip` (`91,768,159` bytes; decimal 100 MB limit respected).
- 1,200 queries; 12,000 new full-parent chunks (10/query); 119,308 total chunks.
- Every Exp121 chunk is preserved exactly. New parents are the first 10 of Exp122's selected-document-rank additions.
- ZIP has one root `submission.json`, LZMA method, CRC passes.
- ZIP SHA-256: `17b04ee76059bace8a242195daf1e7b84b8e867f6b848e76eb5bb1bc1b50ce7e`.

## BTC result

Pending manual submission. Expected Docs metrics are identical to Exp121/122; chunk metrics and Final Score must be measured by BTC. Do not treat high precision as proof of a better F2 without the official result.
