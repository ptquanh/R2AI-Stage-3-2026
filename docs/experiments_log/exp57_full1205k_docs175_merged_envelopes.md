# Exp 57 — Full 1.205M Docs Top-175

## Cấu hình

- Cùng active index `1.205.935` documents và dense ranking với Exp56.
- Giữ nguyên 150 documents đầu của Exp56.
- Thêm dense tail rank 151–175, tổng cộng `175` documents/query.
- Chunks giống hệt Exp56 value-by-value.

## Kết quả BTC

| Metric | Score | So với Exp56 |
| --- | ---: | ---: |
| FINAL_SCORE | 0.3150 | +0.0019 |
| DOCS_F2MACRO | 0.3448 | +0.0040 |
| CHUNKS_F2MACRO | 0.2853 | 0.0000 |
| DOCS_PRECISION | 0.1966 | -0.0148 |
| DOCS_RECALL | 0.5408 | +0.0320 |
| CHUNKS_PRECISION | 0.2414 | 0.0000 |
| CHUNKS_RECALL | 0.3653 | 0.0000 |

## Kết luận

Dense tail 151–175 vẫn tăng F2, dù lợi ích Docs F2 giảm từ `+0,0065` ở bước trước xuống `+0,0040`. Tiếp tục thử top-200; dừng mở rộng nếu Docs F2 không còn tăng hoặc tăng dưới mức đủ bù chi phí slot.
