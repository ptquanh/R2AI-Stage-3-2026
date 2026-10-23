# Exp 59 — Full 1.205M Docs Top-225

## Cấu hình

- Giữ nguyên 200 documents đầu của Exp58.
- Thêm 25 dense-tail documents mới ở rank 201–225 cho mỗi query.
- Tổng cộng `30.000` vị trí document mới trên 1.200 query.
- Chunks giống hệt Exp58 value-by-value.

## Kết quả BTC

| Metric | Exp59 | Exp58 | Chênh lệch |
| --- | ---: | ---: | ---: |
| FINAL_SCORE | 0.3156 | 0.3154 | +0.0002 |
| DOCS_F2MACRO | 0.3459 | 0.3455 | +0.0004 |
| CHUNKS_F2MACRO | 0.2853 | 0.2853 | 0.0000 |
| DOCS_PRECISION | 0.1727 | 0.1834 | -0.0107 |
| DOCS_RECALL | 0.5965 | 0.5690 | +0.0275 |
| CHUNKS_PRECISION | 0.2414 | 0.2414 | 0.0000 |
| CHUNKS_RECALL | 0.3653 | 0.3653 | 0.0000 |

## Audit và kết luận

- JSON có đúng `225` unique official IDs/query.
- 200 IDs đầu khớp Exp58 trên đủ 1.200 query.
- Tail 201–225 gồm `30.000` vị trí mới; chunks không đổi.
- Precision giảm và recall tăng, xác nhận scorer có xét tail 201–225.
- Bộ metric giống Exp58 được báo trước đó là do nhập nhầm kết quả, không phải cap của evaluator.

**Quyết định:** Exp59 top-225 là champion mới. Tiếp tục sweep top-250 vì Docs F2 vẫn tăng, nhưng lợi ích biên chỉ còn `+0,0004`.
