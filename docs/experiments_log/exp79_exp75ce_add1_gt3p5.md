# Exp 79 — Add one Exp75 CE passage, score >3,5

## Cấu hình

Giữ nguyên Exp74, thêm tối đa một passage/query từ selected document chưa có evidence khi Exp75 BGE CE score `>3,5`.

- `490/1.200` queries nhận addition; `490` chunks mới.
- CE score min/mean/median/max: `3,5020 / 4,9023 / 4,6855 / 8,8828`.
- Passage dài trung bình `445,39` ký tự, min/max `252/500`.
- ZIP `99.678.050` bytes; SHA-256 `b188e870517a382f9f01d744b45a8a2ac4fa66e9642d00a60f9011a54a232084`.
- Docs và mọi chunk Exp74 giữ nguyên; additions là source substrings, official IDs, tối đa một/query.

## Kết quả BTC

- Final: `0,3222`.
- Docs F2/P/R: `0,3574 / 0,1813 / 0,6086`, không đổi.
- Chunks F2/P/R: `0,2870 / 0,2393 / 0,3690`.

Exp79 hòa Exp78 về Final và Chunk F2 sau làm tròn; recall tăng `0,0002` nhưng precision giảm `0,0003`. Ladder đã bão hòa. Dừng trước Exp80 threshold `>2,5`; giữ Exp78 làm biến thể ưu tiên vì cùng F2 nhưng precision cao hơn.
