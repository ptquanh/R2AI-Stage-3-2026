# Exp 110 — BGE/Qwen RRF weight 0,35

Trạng thái: đã được BTC chấm; champion hiện tại.

- Khóa top-150 Exp106; RRF `k=60`, baseline weight `1,0`, Qwen-VI weight `0,35`.
- Thêm trung bình `7,82` docs/query; Qwen rank median `18`, max `36`.
- Chunks giữ nguyên Exp106.

## Kết quả BTC

```json
{"FINAL_SCORE":0.3229,"DOCS_F2MACRO":0.3586,"CHUNKS_F2MACRO":0.2872,"DOCS_PRECISION":0.1816,"DOCS_RECALL":0.6114,"CHUNKS_PRECISION":0.2389,"CHUNKS_RECALL":0.3694}
```

So với Exp108, recall tăng `0,0007`, Docs F2 tăng `0,0002`, Final tăng `0,0001`; Qwen weight ladder vẫn tăng nhưng precision tiếp tục giảm nhẹ.
