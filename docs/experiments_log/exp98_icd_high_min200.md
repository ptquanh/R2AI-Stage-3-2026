# Exp 98 — ICD high-specificity prune, min 200 docs

Trạng thái: đã được BTC chấm.

- Chỉ tác động 259 query được nhận diện high-specificity.
- Bỏ tổng cộng 3.451 tail docs; tối thiểu còn 200 docs/query.
- Top-50 và chunks Exp87 giữ nguyên.

## Kết quả BTC

```json
{"FINAL_SCORE":0.3226,"DOCS_F2MACRO":0.3583,"CHUNKS_F2MACRO":0.2870,"DOCS_PRECISION":0.1831,"DOCS_RECALL":0.6067,"CHUNKS_PRECISION":0.2396,"CHUNKS_RECALL":0.3688}
```

Precision tăng nhưng recall giảm; F2 không vượt Exp87. ICD prune không tạo bước nhảy.
