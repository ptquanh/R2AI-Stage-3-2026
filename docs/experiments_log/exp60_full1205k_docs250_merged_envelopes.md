# Exp 60 — Full 1.205M Docs Top-250

## Cấu hình

- Giữ nguyên 225 documents đầu của Exp59.
- Thêm 25 dense-tail documents mới ở rank 226–250 cho mỗi query.
- Tổng cộng `30.000` vị trí document mới trên 1.200 query.
- Chunks giống hệt Exp59 value-by-value.

## Kết quả BTC

| Metric | Exp60 | Exp59 | Chênh lệch |
| --- | ---: | ---: | ---: |
| FINAL_SCORE | 0.3145 | 0.3156 | -0.0011 |
| DOCS_F2MACRO | 0.3437 | 0.3459 | -0.0022 |
| CHUNKS_F2MACRO | 0.2853 | 0.2853 | 0.0000 |
| DOCS_PRECISION | 0.1627 | 0.1727 | -0.0100 |
| DOCS_RECALL | 0.6178 | 0.5965 | +0.0213 |
| CHUNKS_PRECISION | 0.2414 | 0.2414 | 0.0000 |
| CHUNKS_RECALL | 0.3653 | 0.3653 | 0.0000 |

## Audit và kết luận

- JSON có đúng `250` unique official IDs/query.
- 225 IDs đầu khớp Exp59 trên đủ 1.200 query.
- Tail 226–250 gồm `30.000` vị trí mới; chunks không đổi.
- Recall tiếp tục tăng, nhưng precision loss đã lớn hơn lợi ích recall theo Docs F2.
- Đây là bước giảm đầu tiên của sweep top-k: top-225 là champion trong các mốc đã đo.

**Quyết định:** không thử top-275. Thu hẹp quanh đỉnh; nội suy ba mốc 200/225/250 cho cực đại khoảng 216 docs/query, vì vậy Exp61 sẽ thử top-216 và giữ nguyên chunks.
