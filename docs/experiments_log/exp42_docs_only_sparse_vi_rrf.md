[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 42: Docs-only conservative VI sparse RRF

## Mục tiêu

Ablation sạch sau regression của Exp41: đo riêng giá trị của BGE-M3 sparse retrieval độc lập, không thay chunk ranking, không dùng dense EN/ZH và không thay mạnh champion document ranking.

## Kết quả BTC

- Final Score: `0,2966`.
- Docs F2: `0,3173`; Precision `0,2471`; Recall `0,4237`.
- Chunks F2: `0,2759`; Precision `0,2238`; Recall `0,3608`.

So với Exp40, Final giảm `0,0025`; Docs F2 giảm `0,0050`; Docs Precision giảm `0,0050`; Docs Recall giảm `0,0048`. Toàn bộ chỉ số chunk giữ nguyên chính xác, xác nhận submission đã cô lập đúng document branch.

**Kết luận:** sparse VI độc lập với weight `0,5` không cải thiện champion. Việc thay trung bình 5,53 docs/query vẫn loại nhiều ground-truth hơn số candidate mới cứu được. Không tiếp tục tune quanh weight này trước khi thử các branch có prior tốt hơn.

## Cấu hình

- Baseline: `submission_bgem3_trilingual_105m_corpus.json` của Exp40.
- Giữ nguyên chính xác toàn bộ `relevant_chunks` của Exp40: 98 chunks/query.
- Nhánh mới duy nhất: BGE-M3 sparse từ query tiếng Việt, retrieval độc lập top-500 trên toàn bộ 1.590.459 chunks của index sạch.
- Collapse chunk ranking thành document ranking trước khi fusion.
- RRF: champion ranking weight `1,0`; sparse VI weight `0,5`; `rrf_k=60`.
- Giữ 100 documents/query.
- Không dùng query EN/ZH, dense multilingual hoặc BM25.

## Mức thay đổi được khống chế

- Trung bình thay 5,5275/100 documents/query so với Exp40.
- Median 5; percentile 90 là 11; min 0; max 13.
- 1.137/1.200 query có ít nhất một document thay đổi.
- Thấp hơn nhiều so với Exp41: 35,97 documents mới/query.

## Validation

- 1.200 query, 100 documents/query.
- Tất cả document IDs thuộc corpus chính thức.
- `relevant_chunks` giống Exp40 ở mức JSON value cho từng query.
- ZIP: 97.411.198 byte, dưới 100 MB hệ thập phân.
- SHA-256: `d4eca06ee1c7c06864f8642c0d506811002503921c2eb490f64bec30070cb2bb`.

## Artifact

- Submission: `submission_exp42_docs_only_sparse_vi_rrf.zip`
- Generator: `scripts/generate_docs_only_sparse_ablation.py`
- Manifest: `submission_exp42_docs_only_sparse_vi_rrf_manifest.json`
- Sparse cache: `data/indices/new_dataset/index/.cache/exp41_true_union/sparse_top500_vi_only.npz`

## Cách đọc kết quả

- Chunks F2 phải bằng Exp40 (`0,2759`) nếu scorer BTC deterministic; bất kỳ chênh lệch nào sẽ là tín hiệu backend hoặc artifact không ổn định vì chunks được giữ nguyên hoàn toàn.
- [x] Docs F2 giảm: bỏ sparse VI injection weight `0,5`.
- [ ] Thử dense ZH riêng theo cùng protocol docs-only; chỉ thử dense EN nếu ZH có tín hiệu hoặc còn budget submission.
