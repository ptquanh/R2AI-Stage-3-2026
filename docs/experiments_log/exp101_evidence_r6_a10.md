# Exp 101 — Evidence reallocation: remove 6, add 10

Trạng thái: đã được BTC chấm; regression.

- Bảo vệ top-50 docs.
- Loại evidence của 6 represented tail docs có BGE thấp và thêm passage cho 10 selected docs chưa có evidence.
- Document axis giữ nguyên Exp87.

## Kết quả BTC

```json
{"FINAL_SCORE":0.3220,"DOCS_F2MACRO":0.3583,"CHUNKS_F2MACRO":0.2857,"DOCS_PRECISION":0.1818,"DOCS_RECALL":0.6098,"CHUNKS_PRECISION":0.2302,"CHUNKS_RECALL":0.3737}
```

Recall chunks tăng nhưng precision giảm mạnh hơn; không tiếp tục scale chính sách remove-and-add.
