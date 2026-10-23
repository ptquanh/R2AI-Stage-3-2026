# Exp 92 — BGE/Qwen blend α=0,05, cap1

Trạng thái: đã được BTC chấm.

- Baseline: Exp87; top-50 và chunks bất biến.
- Blend BGE với Qwen trọng số `0,05`, tối đa một swap/query.
- 1.188 queries thay đổi; trung bình `0,99` swap/query.

## Kết quả BTC

```json
{"FINAL_SCORE":0.3226,"DOCS_F2MACRO":0.3582,"CHUNKS_F2MACRO":0.2870,"DOCS_PRECISION":0.1817,"DOCS_RECALL":0.6098,"CHUNKS_PRECISION":0.2396,"CHUNKS_RECALL":0.3688}
```

Final hòa Exp87 sau làm tròn nhưng Docs F2 giảm `0,0001`; chưa chứng minh reranker Qwen cải thiện membership.
