# Exp 65 — Cached CE Consensus, Head-150 / Pool-400

## Mục tiêu

Mở rộng có kiểm soát cấu hình chiến thắng Exp64 để kiểm tra các cross-encoder consensus documents nằm sâu hơn rank 300. Chỉ candidate pool thay đổi; mọi policy khác giữ nguyên.

## Cấu hình

- Champion nền/chunk source: Exp63.
- Khóa cứng ranks 1–150 của Exp63.
- Mở dense candidate pool từ rank 300 lên 400.
- Trong ranks 151–400, ưu tiên documents thuộc top-100 BGE cross-encoder Exp38.
- Xuất đúng 216 unique documents/query.
- Chunks giống Exp63 value-by-value: gap 2.000, span 8.000.

## Mức thay đổi

So với Exp63:

- Queries thay đổi: `941/1.200`.
- Swaps/query min/mean/median/max: `0 / 4,838 / 4 / 39`.
- Original rank của docs được đưa vào: `217–400`, trung bình `278,13`, trung vị `265`.

So với Exp64 pool-300:

- Queries thay đổi thêm: `583/1.200`.
- Swaps bổ sung/query trung bình: `1,439`.
- Trung vị swaps bổ sung: `0`.
- Tối đa swaps bổ sung: `18`.

## Audit

- Đủ 1.200 query, đúng 216 unique official IDs/query.
- Mọi document được thêm đều thuộc top-100 BGE cross-encoder Exp38 của cùng query.
- Top-150 khớp Exp63 value-by-value.
- Chunks khớp Exp63 value-by-value.
- ZIP chỉ chứa `submission.json`; CRC hợp lệ.
- Tests: `4 passed`.
- Kích thước ZIP: `98.171.366` bytes.
- SHA-256: `361fc5012cdc9225d8c592221bed3203b88a793e7226b10e8651bda45c6a9cbc`.

## Kết quả BTC

| Metric | Exp65 | Exp64 | Chênh lệch |
| --- | ---: | ---: | ---: |
| FINAL_SCORE | 0.3172 | 0.3166 | +0.0006 |
| DOCS_F2MACRO | 0.3489 | 0.3478 | +0.0011 |
| CHUNKS_F2MACRO | 0.2855 | 0.2855 | 0.0000 |
| DOCS_PRECISION | 0.1777 | 0.1772 | +0.0005 |
| DOCS_RECALL | 0.5925 | 0.5901 | +0.0024 |
| CHUNKS_PRECISION | 0.2419 | 0.2419 | 0.0000 |
| CHUNKS_RECALL | 0.3654 | 0.3654 | 0.0000 |

## Kết luận

Exp65 là champion mới. Mở candidate pool thêm 100 ranks tiếp tục tăng đồng thời document precision và recall, trong khi chunks bất biến. Cached cross-encoder consensus chưa bão hòa ở pool-400; thử pool-500 với mọi tham số khác giữ nguyên.
