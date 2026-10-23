# Exp 78 — Add one Exp75 CE passage, score >4,5

## Cấu hình

Giữ nguyên toàn bộ Exp74. Với mỗi query, thêm tối đa một passage nguyên văn từ selected document chưa có evidence, chọn theo Exp75 BGE CE score `>4,5`. Đây là mức mở rộng kế tiếp sau Exp77 `>5,5`.

- `282/1.200` queries nhận addition; `282` chunks mới.
- CE score min/mean/median/max: `4,5039 / 5,5970 / 5,3223 / 8,8828`.
- Passage dài trung bình `448,73` ký tự, min/max `278/500`.
- ZIP `99.630.607` bytes; SHA-256 `a59c83f7b6b05d434b89e60e8939aca5145516cb0fae3e64a4e6374f5d60a1ce`.
- Docs và mọi chunk Exp74 giữ nguyên; additions là source substrings, official IDs, tối đa một/query.

## Kết quả BTC

- Final: `0,3222`.
- Docs F2/P/R: `0,3574 / 0,1813 / 0,6086`, không đổi.
- Chunks F2/P/R: `0,2870 / 0,2396 / 0,3688`.

So với Exp77, Chunk F2 và recall cùng tăng `0,0001`, precision giảm `0,0003`; Final tăng `0,0001`. Tiếp tục Exp79 threshold `>3,5`; dừng ladder nếu Chunk F2 không còn tăng.
