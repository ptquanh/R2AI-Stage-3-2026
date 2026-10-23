# Exp 66 — Cached CE Consensus, Head-150 / Pool-500

## Mục tiêu

Kiểm tra bão hòa của cached cross-encoder consensus sau chiến thắng Exp65. Chỉ mở candidate pool thêm 100 ranks; mọi policy còn lại giữ nguyên.

## Cấu hình

- Champion nền/chunk source: Exp63.
- Khóa cứng ranks 1–150 của Exp63.
- Mở dense candidate pool từ rank 400 lên 500.
- Trong ranks 151–500, ưu tiên documents thuộc top-100 BGE cross-encoder Exp38.
- Xuất đúng 216 unique documents/query.
- Chunks giống Exp63 value-by-value: gap 2.000, span 8.000.

## Mức thay đổi

So với Exp63:

- Queries thay đổi: `941/1.200`.
- Swaps/query min/mean/median/max: `0 / 5,177 / 4 / 47`.
- Original rank của docs được đưa vào: `217–498`, trung bình `288,12`, trung vị `270`.

So với Exp65 pool-400:

- Queries thay đổi thêm: `185/1.200`.
- Swaps bổ sung/query trung bình: `0,338`.
- Trung vị swaps bổ sung: `0`.
- Tối đa swaps bổ sung: `13`.

## Audit

- Đủ 1.200 query, đúng 216 unique official IDs/query.
- Mọi document được thêm đều thuộc top-100 BGE cross-encoder Exp38 của cùng query.
- Top-150 khớp Exp63 value-by-value.
- Chunks khớp Exp63 value-by-value.
- ZIP chỉ chứa `submission.json`; CRC hợp lệ.
- Tests: `4 passed`.
- Kích thước ZIP: `98.171.260` bytes.
- SHA-256: `889504d2c90b34985f97f613c71f1a8f97edc1d00dfb6f96310b84a5d8f2e5df`.

## Kết quả BTC

| Metric | Exp66 | Exp65 | Chênh lệch |
| --- | ---: | ---: | ---: |
| FINAL_SCORE | 0.3173 | 0.3172 | +0.0001 |
| DOCS_F2MACRO | 0.3490 | 0.3489 | +0.0001 |
| CHUNKS_F2MACRO | 0.2855 | 0.2855 | 0.0000 |
| DOCS_PRECISION | 0.1777 | 0.1777 | 0.0000 |
| DOCS_RECALL | 0.5927 | 0.5925 | +0.0002 |
| CHUNKS_PRECISION | 0.2419 | 0.2419 | 0.0000 |
| CHUNKS_RECALL | 0.3654 | 0.3654 | 0.0000 |

## Kết luận

Exp66 là champion mới nhưng chỉ tăng sát độ phân giải leaderboard. Cached CE consensus đã gần cạn sau rank 500; dừng sweep pool theo bước 100 và chuyển sang inference cross-encoder mới trên candidate pool full-corpus hiện tại.
