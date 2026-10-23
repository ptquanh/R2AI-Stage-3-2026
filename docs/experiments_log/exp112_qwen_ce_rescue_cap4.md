# Exp 112 — Qwen candidate rescue + BGE cross-encoder, cap4

Trạng thái: hủy nộp sau regression của Exp111.

- Cùng candidate pool và CE gate với Exp111.
- CE margin tối thiểu `0,50`; tối đa 4 swaps/query.
- 1.094 queries thay đổi; tổng 3.429 swaps, trung bình `2,86`/query.
- CE margin mean `2,6374`, median `2,3203`; Qwen rank median `40`.
- Chunks giữ nguyên Exp110; ZIP `99.772.517` bytes và CRC hợp lệ.

Biến thể này mở rộng exposure thêm 1.388 documents so với Exp111. Không nộp trước Exp111 vì rủi ro precision cao hơn.

