# Exp130 — multilingual BM25 → exact dense document/passage cascade

## Status

Kaggle notebook and private-input package are ready; no Kaggle run or BTC submission has occurred yet.

## Hypothesis

Use the audited multilingual BM25 cache as candidate generation, then exact BGE-M3 chunk-vector similarity to rerank documents and select source-grounded passages. This tests a substantial part of the mentor-day architecture rather than another threshold/cap change.

## Planned configuration

- 1,200 official queries; original Vietnamese query for dense encoding, existing EN/ZH translations for BM25.
- Existing BM25 cache: 1,792,945 rows, VI/EN/ZH branches, 500 results/branch, version `bm25f_idf_pruned_v1`; RRF top pool capped at 1,500 unique docs/query.
- Exact BGE-M3 max-chunk score per candidate doc; dense rerank top 400; output top 216 docs/query.
- Dense-rank indexed source chunks from the selected docs; output 96 exact passages/query using original source offsets.
- ZIP-LZMA with a decimal 100 MB guard and exact source/schema/CRC checks.

## Artifacts and data governance

- Notebook: `notebooks/14_bm25_dense_passage_cascade_kaggle.ipynb`.
- Private Kaggle input ZIP: `data/kaggle_inputs/exp130_bm25_dense_passage_input.zip` (`21,292,058` bytes; CRC pass; SHA-256 `3b54bff640baff54dc891a6d01e5a110fe513e17073a4b6c1a7129aea055911c`). Contains only translated queries and the BM25 candidate cache.
- Attach the active index as a separate **private** Kaggle dataset. It contains 1,724,798 aligned FP16 chunk vectors (3.53 GB) plus text/metadata. Local audit verified all 23 vector ID shards are contiguous and match the metadata row count.
- The exact BGE-M3 commit resolved at runtime, input ZIP hash, index manifest hash, output hashes, cardinalities and CRC are saved in `exp130_manifest.json` in Kaggle output.

## Execution and scoring

Run with `QUERY_LIMIT=120` only to estimate throughput/ETA; a pilot does not create a submission. For a scored artifact set `QUERY_LIMIT=None` and run all queries. Compare official Docs/Chunks F2 separately to Exp122; the experiment changes both document ordering/membership and passage selection, so aggregate score alone cannot identify which stage helped. Score pending; Kaggle execution and manual submission are user-operated.
