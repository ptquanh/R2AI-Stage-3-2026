# Exp 58 — Full 1.205M Docs Top-200

## Cấu hình

- Cùng active index `1.205.935` documents và dense ranking với Exp57.
- Giữ nguyên 175 documents đầu của Exp57.
- Thêm dense tail rank 176–200, tổng cộng `200` documents/query.
- Chunks giống hệt Exp57 value-by-value.

## Kết quả BTC

| Metric | Score | So với Exp57 |
| --- | ---: | ---: |
| FINAL_SCORE | 0.3154 | +0.0004 |
| DOCS_F2MACRO | 0.3455 | +0.0007 |
| CHUNKS_F2MACRO | 0.2853 | 0.0000 |
| DOCS_PRECISION | 0.1834 | -0.0132 |
| DOCS_RECALL | 0.5690 | +0.0282 |
| CHUNKS_PRECISION | 0.2414 | 0.0000 |
| CHUNKS_RECALL | 0.3653 | 0.0000 |

## Kết luận

Top-200 vẫn thắng nhưng lợi ích biên Docs F2 chỉ còn `+0,0007`, giảm mạnh so với hai bước trước. Chưa thể tuyên bố bão hòa vì điểm vẫn tăng; tiếp tục top-225 và dừng tại bước đầu tiên không tăng, sau đó có thể kiểm tra midpoint nếu cần.
