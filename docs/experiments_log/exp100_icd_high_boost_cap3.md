# Exp 100 — ICD high-specificity rerank cap3

Trạng thái: đã được BTC chấm.

- 259 query đủ điều kiện; 255 queries thực sự thay đổi.
- Swap tổng cộng 619 docs, tối đa 3/query; vẫn giữ 216 docs/query.
- Top-50 và chunks Exp87 bất biến.

## Kết quả BTC

```json
{"FINAL_SCORE":0.3226,"DOCS_F2MACRO":0.3582,"CHUNKS_F2MACRO":0.2870,"DOCS_PRECISION":0.1817,"DOCS_RECALL":0.6097,"CHUNKS_PRECISION":0.2396,"CHUNKS_RECALL":0.3688}
```

Docs F2 giảm `0,0001`; dừng ICD rerank/hard-filter ở thiết kế này.
