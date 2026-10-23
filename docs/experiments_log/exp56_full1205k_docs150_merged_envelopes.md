# Exp 56 — Full 1.205M Docs Top-150

## Cấu hình

- Cùng active index `1.205.935` documents và cùng dense ranking với Exp51.
- Giữ nguyên thứ tự 125 documents đầu của Exp51.
- Thêm dense tail rank 126–150, tổng cộng `150` documents/query.
- Chunks giống hệt Exp51 value-by-value.

## Kết quả BTC

| Metric | Score | So với Exp51 |
| --- | ---: | ---: |
| FINAL_SCORE | 0.3131 | +0.0033 |
| DOCS_F2MACRO | 0.3408 | +0.0065 |
| CHUNKS_F2MACRO | 0.2853 | 0.0000 |
| DOCS_PRECISION | 0.2114 | -0.0184 |
| DOCS_RECALL | 0.5088 | +0.0378 |
| CHUNKS_PRECISION | 0.2414 | 0.0000 |
| CHUNKS_RECALL | 0.3653 | 0.0000 |

## Kết luận

Với F2, recall tăng `0,0378` bù được precision giảm `0,0184`, tạo Docs F2 `+0,0065`. Dense tail 126–150 vẫn có mật độ ground truth đủ cao; cần tiếp tục sweep top-175 trước khi kết luận điểm tối ưu document count.
