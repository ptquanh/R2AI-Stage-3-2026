# Exp 113 — Qwen candidate rescue + BGE cross-encoder, cap4 margin1

Trạng thái: hủy nộp sau regression của Exp111.

- Cùng candidate pool với Exp111/112.
- CE margin tối thiểu tăng lên `1,00`; tối đa 4 swaps/query.
- 1.055 queries thay đổi; tổng 3.005 swaps, trung bình `2,50`/query.
- CE margin mean `2,9021`, median `2,5796`; Qwen rank median `41`.
- Chunks giữ nguyên Exp110; ZIP `99.772.653` bytes và CRC hợp lệ.

Đây là điểm giữa Exp111 và Exp112 về mức churn, nhưng cho phép 4 additions ở những query có nhiều candidate CE mạnh.

