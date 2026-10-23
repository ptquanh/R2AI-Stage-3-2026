# Exp 104 — Shrink 8 chunks, add 10 passages

Trạng thái: đã được BTC chấm; regression nghiêm trọng.

- Thay 8 long chunks bằng strict verbatim BGE passages ngắn hơn rồi thêm 10 passages mới.
- Documents giữ nguyên Exp87.

## Kết quả BTC

```json
{"FINAL_SCORE":0.3133,"DOCS_F2MACRO":0.3583,"CHUNKS_F2MACRO":0.2682,"DOCS_PRECISION":0.1818,"DOCS_RECALL":0.6098,"CHUNKS_PRECISION":0.2082,"CHUNKS_RECALL":0.3559}
```

Việc rút ngắn envelope làm mất cả precision lẫn recall. Long verbatim envelopes đang chứa vùng khớp nhãn quan trọng.
