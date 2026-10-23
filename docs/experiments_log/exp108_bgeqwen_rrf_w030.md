# Exp 108 — BGE/Qwen RRF weight 0,30

Trạng thái: đã được BTC chấm; champion mới.

- Khóa top-150 Exp106; RRF `k=60`, baseline weight `1,0`, Qwen-VI weight `0,30`.
- Thêm trung bình `4,22` docs/query; Qwen rank median `12`, max `22`.
- Chunks giữ nguyên Exp106.

## Kết quả BTC

```json
{"FINAL_SCORE":0.3228,"DOCS_F2MACRO":0.3584,"CHUNKS_F2MACRO":0.2872,"DOCS_PRECISION":0.1817,"DOCS_RECALL":0.6107,"CHUNKS_PRECISION":0.2389,"CHUNKS_RECALL":0.3694}
```

Qwen full-corpus tăng Docs Recall `0,0009`; precision giảm `0,0001` nhưng F2/Final cùng tăng `0,0001`.
