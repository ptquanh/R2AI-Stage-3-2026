# Exp 73 — Add Second High-Confidence CE Chunk

## Mục tiêu

Khai thác tín hiệu tích cực của Exp72 cho slot cuối: giữ nguyên champion và chỉ thêm evidence thứ hai có độ tin cậy cao, nhằm tăng chunk recall với mức tăng denominator nhỏ.

## Cấu hình

- Baseline: Exp72.
- Documents: giữ nguyên Exp72 value-by-value.
- Chunks nền: giữ toàn bộ Exp72 chunks theo đúng thứ tự.
- Với mỗi query, chỉ xét documents đã có trong `relevant_docs` nhưng chưa có document đại diện trong `relevant_chunks` Exp72.
- Thêm tối đa một chunk/query và chỉ khi raw BGE cross-encoder score `> 2,5`.
- Model tạo score: `BAAI/bge-reranker-v2-m3`; tái sử dụng caches Exp67/69/70/71, không inference mới.

## Mức thay đổi

- Queries có addition: `624/1.200`.
- Chunks thêm: `624`.
- Chunks/query min/mean/median/max: `67 / 89,707 / 91 / 100`.
- CE score min/mean/median/max của additions: `2,502 / 3,981 / 3,769 / 8,375`.
- Độ dài additions min/mean/median/max: `193 / 1.476,06 / 1.022,5 / 3.479` ký tự.

## Audit

- Đủ `1.200` query; document lists khớp Exp72 value-by-value.
- Mọi Exp72 chunk được giữ nguyên value-by-value và theo đúng thứ tự.
- Chính xác `624` query nhận thêm một chunk; không query nào nhận quá một chunk.
- Mọi addition thuộc document đã được chọn trong Exp72 nhưng chưa có chunk đại diện.
- Mọi chunk mới là substring nguyên văn của source document; tất cả IDs thuộc official corpus.
- Không trùng `(doc_id, chunk_text)` trong query.
- ZIP chỉ chứa `submission.json`; CRC hợp lệ và payload khớp byte-for-byte với JSON ngoài ZIP.
- Tests: `4 passed`.
- Kích thước ZIP: `99.553.194` bytes, dưới giới hạn `100.000.000` bytes.
- JSON SHA-256: `8f9533aea2abf8b98f5190e828f6bafbf9cf045902dc846dc0102752c8670d11`.
- ZIP SHA-256: `9a8caad5951659ae9375e13b58d63558885e3ea50467370756f6dad64f742f8a`.

## Kết quả BTC — nhận ngày 19/10/2026

- FINAL_SCORE: `0,3214` (`+0,0002` so với Exp72).
- DOCS_F2MACRO: `0,3560` (không đổi).
- CHUNKS_F2MACRO: `0,2868` (`+0,0005`).
- DOCS_PRECISION / DOCS_RECALL: `0,1808 / 0,6059` (không đổi).
- CHUNKS_PRECISION: `0,2401` (`-0,0006`).
- CHUNKS_RECALL: `0,3685` (`+0,0010`).

Exp73 là champion nội bộ mới. Addition thứ hai vẫn có lợi cho Chunk F2 nhưng mức tăng quá nhỏ để làm hướng chính cho mục tiêu Final ≥0,38 trong ngày 19/10. Chuyển sang evidence coverage trên toàn bộ selected documents, span expansion có kiểm soát và rerank head theo mục 13 trong [kế hoạch cải thiện điểm](../r2ai_score_improvement_plan.md).
