# Exp 84 — Exp76 head rerank, churn cap 20

Giữ toàn bộ cấu hình/scoring của Exp76, chỉ hạ membership churn cap từ 30 xuống 20. Cap bind trên 49/1.200 queries; mean swaps `11,4925` docs/query. Chunks giữ nguyên Exp74.

- ZIP: `99.551.265` bytes; SHA-256 `154158dfa5ee51dab3c0a97bf11acc12e1deff9b97346bc19d7d48a74422f726`.
- Final: `0,3225`.
- Docs F2/P/R: `0,3582 / 0,1817 / 0,6097`.
- Chunks F2/P/R: `0,2868 / 0,2401 / 0,3685`, đúng control.

Cap20 tăng Docs F2 `+0,0001`, precision `+0,0001`, recall `+0,0005` so với cap30; là Docs champion mới. Test cap10 bằng slot áp chót, sau đó ghép chunk Exp78 với cap Docs tốt nhất.
