# Exp129 — Exp121 + 15 ranked full-parent additions

## Hypothesis

Exp122's 19 additions improved chunk F2 versus Exp121, while lower-cardinality variants Exp127 (10) and Exp128 (5) test whether precision can be recovered. Exp129 takes 15 of the same rank-ordered additions, giving a near-control interpolation between the 19- and 10-addition settings. All Exp121 evidence and the document axis are preserved.

## Artifact and validation

- ZIP: `submission_exp129_exp121_add15_ranked_parents.zip` (`95,983,329` bytes; below decimal 100 MB).
- 1,200 queries; 18,000 new parents (15/query); 125,308 total chunks.
- One root `submission.json`, ZIP-LZMA, CRC passes; every Exp121 chunk prefix is preserved. Script fails closed if limits or prefix invariants do not hold.
- ZIP SHA-256: `50059f3f01e0ad9bdca109fba32955f85031ac938b88ee4d54001a467cde6f45`.

## BTC result

```json
{
  "FINAL_SCORE": 0.3500,
  "DOCS_F2MACRO": 0.3586,
  "CHUNKS_F2MACRO": 0.3414,
  "DOCS_PRECISION": 0.1816,
  "DOCS_RECALL": 0.6114,
  "CHUNKS_PRECISION": 0.2547,
  "CHUNKS_RECALL": 0.4591
}
```

The leaderboard displayed Final as `0.35`; it is recorded as `0.3500` only to keep the log schema at four decimals.

Compared with Exp122 (19 additions), reducing to 15 additions left the document axis unchanged and raised chunk precision by `+0.0035`, but chunk recall fell by `-0.0091`. Chunk F2 therefore fell by `-0.0032` and Final by about `-0.0016`. This is direct evidence that the current operating point is recall-limited under F2; do not submit the still-smaller Exp127/128 variants unless they answer a different diagnostic question.
