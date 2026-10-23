# Exp 85 — Exp76 head rerank, churn cap 10

Giữ toàn bộ cấu hình/scoring của Exp76, chỉ hạ membership churn cap từ 30 xuống 10. Cap bind trên 677/1.200 queries; mean swaps `9,0458` docs/query. Chunks giữ nguyên Exp74.

- ZIP: `99.551.804` bytes; SHA-256 `4d6ebd48c00ec0c115028a6a3ae361ddd00aaebee2b1ff137cc77629f8a5edf7`.
- Final: `0,3226`.
- Docs F2/P/R: `0,3583 / 0,1818 / 0,6098`.
- Chunks F2/P/R: `0,2868 / 0,2401 / 0,3685`, đúng control.

Cap10 tăng Docs F2 `+0,0001`, precision `+0,0001`, recall `+0,0001` so với cap20. Đây là Docs champion mới, nhưng biên tăng cho thấy sweep churn cap đã bão hòa; không tiếp tục thử các cap lân cận.
