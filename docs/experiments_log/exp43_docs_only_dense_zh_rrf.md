[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 43: Docs-only conservative dense ZH RRF

## Mục tiêu

Đo riêng giá trị của dense retrieval bằng query tiếng Trung trên corpus đa ngữ, sau khi Exp42 xác nhận sparse VI độc lập không cải thiện Docs F2.

## Kết quả BTC

- Final Score: `0,2958`.
- Docs F2: `0,3158`; Precision `0,2459`; Recall `0,4215`.
- Chunks F2: `0,2759`; Precision `0,2238`; Recall `0,3608`.

So với Exp40, Final giảm `0,0033`; Docs F2 giảm `0,0065`; Docs Precision giảm `0,0062`; Docs Recall giảm `0,0070`. Chunks giữ nguyên hoàn toàn như thiết kế.

**Kết luận:** dense ZH injection weight `0,45` bị loại. Cùng với Exp42, hai independent branch được thử riêng đều làm giảm cả precision lẫn recall. Không tiếp tục dense EN vì prior từ lịch sử yếu hơn ZH; chuyển budget sang output policy trên champion ranking.

## Cấu hình

- Baseline document ranking và toàn bộ chunks lấy từ Exp40.
- Giữ nguyên chính xác 98 chunks/query của Exp40.
- Candidate branch duy nhất: dense ZH top-500, retrieval độc lập trên toàn bộ 1.590.459 chunks.
- Collapse chunk ranking thành document ranking trước fusion.
- RRF: baseline weight `1,0`; dense ZH weight `0,45`; `rrf_k=60`.
- Không dùng dense EN, sparse injection hoặc BM25.

## Change budget

- Trung bình thay 5,6392/100 documents/query.
- Median 7; percentile 90 là 8; min 0; max 10.
- 1.129/1.200 query thay ít nhất một document.
- Mức thay tương đương Exp42 (5,5275), giúp so sánh branch công bằng hơn.

## Validation

- 1.200 query, 100 document IDs hợp lệ/query.
- `relevant_chunks` giống Exp40 ở mức JSON value.
- ZIP: 97.421.321 byte, dưới 100 MB hệ thập phân.
- SHA-256: `12b985d51e21b84231ffc0f34e88602b95afac25f611d5aeba19c8ee03bf5f04`.

## Artifact

- Submission: `submission_exp43_docs_only_dense_zh_rrf.zip`
- Generator: `scripts/generate_docs_only_sparse_ablation.py`
- Manifest: `submission_exp43_docs_only_dense_zh_rrf_manifest.json`

## Cách đọc kết quả

- Chunks F2 phải giữ đúng `0,2759` nếu scorer deterministic.
- [x] Docs F2 ≤ `0,3223`: loại dense ZH injection.
- [x] Chuyển sang document output policy; chưa thử dense EN để tránh dùng lượt nộp cho prior yếu.
