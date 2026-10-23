# Exp 106 — Add-only evidence, BGE≥4

Trạng thái: đã được BTC chấm; champion mới.

- Giữ nguyên toàn bộ documents và chunks Exp87 theo đúng thứ tự.
- Chỉ append một passage cho selected doc chưa có evidence khi BGE≥4.
- 412 queries/chunks được bổ sung; passage hoàn toàn verbatim.

## Kết quả BTC

```json
{"FINAL_SCORE":0.3227,"DOCS_F2MACRO":0.3583,"CHUNKS_F2MACRO":0.2872,"DOCS_PRECISION":0.1818,"DOCS_RECALL":0.6098,"CHUNKS_PRECISION":0.2389,"CHUNKS_RECALL":0.3694}
```

Add-only tăng Chunk F2 `0,0002`; xác nhận không nên xóa hoặc shrink evidence cũ.
