# Exp144 — QuerySpec/BM25 candidate expansion with exact BGE-M3 docs rerank

## Hypothesis

The current rerankers may be saturated because they reorder a fixed candidate pool. Query understanding should be used to widen recall, while the original Vietnamese query remains the final semantic scoring signal. This separates candidate generation from relevance scoring and avoids changing chunk segmentation.

## Configuration

- Control: BTC-scored Exp143, Final 0.3190, with 183,703 query-doc pairs and 127,271 chunks.
- QuerySpec coverage: 401/1,200 audited usable records. The interrupted OpenRouter production run stopped on HTTP 402; failed responses are excluded. Remaining rows explicitly fall back to the original query.
- Candidate generation: original Vietnamese BM25 plus production EN/ZH translations and, only for valid QuerySpecs, canonical/atom views. Identical views are deduplicated and fused by weighted RRF (`k=60`), capped at 2,000 docs/query.
- Final scoring: `BAAI/bge-m3` encodes the original Vietnamese query. Every document in the union of Exp143 and the expanded pool receives an exact max-chunk dense score from the active vector index.
- Kaggle notebook: `notebooks/23_exp144_queryspec_dense_2xt4_kaggle.ipynb`; supports one or two T4 GPUs, atomic checkpoint every 25 queries, and outputs only top-400 document rankings and diagnostics.
- Local candidate builder: `scripts/build_exp144_docs_candidates.py`; preserves all Exp143 chunks exactly. The primary `fused130_owner_gated` policy changes only the 401 queries with audited QuerySpecs, fuses the proven Exp143/Qwen ordering with the new exact-dense ordering, then restores every Exp143 chunk owner. Fallback queries retain exact Exp143 docs.

## Decision rule

The primary treatment is `fused130_owner_gated`: for valid QuerySpecs only, weighted RRF (`current=1.0`, `dense=1.25`, `k=60`) selects 130 base documents, then unions every document owning an Exp143 chunk. All fallback rows remain exact control. This admits novel candidates without repeating Exp141's failed owner-floor removal or exposing fallback queries to translation-only drift. `add5` is a safety control; `dynamic4` is retained only as an uncalibrated ablation. Do not submit a blind policy sweep.

Promote only if BTC Docs F2 and Final improve over Exp143. Candidate novelty, local score distributions, translations, or QuerySpec confidence are not labels and cannot establish relevance.

## Status

Candidate pool complete: 1,472,936 pairs over 1,200 queries, no duplicate pair or foreign corpus document; min/median/max candidates are 548/900/2,000. Kaggle input `data/kaggle_inputs/exp144_queryspec_dense_input.zip` is 10,915,573 bytes with SHA-256 `1b8036dba9b2e8cd4c9afba61a6e2a35e2044d5644b4e60793cb1b860640d7fd`. Its rank-preserving control Parquet was checked against all 183,703 Exp143 query-doc pairs.

Kaggle exact-dense run and BTC score are pending.
