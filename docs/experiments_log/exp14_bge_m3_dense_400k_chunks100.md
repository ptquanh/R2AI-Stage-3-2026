[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 14: BGE-M3 Dense Search (400k docs, top 100 chunks)

- **Mục tiêu:** Cập nhật file nộp bài sau khi phát hiện và loại bỏ hardcode `len(relevant_chunks) < 10` trong `run_local_submission.py`. BTC không giới hạn số chunk nộp. Cho phép xuất tối đa 100 chunks.
- **Phương pháp:**
  - Giữ nguyên khối 400k docs. Cấu hình lấy `100` relevant docs và `100` relevant chunks (giới hạn 100).
- **Kết quả:**
  - `FINAL_SCORE: 0.1557` (Kỷ lục mới!)
  - `DOCS_F2MACRO: 0.1626` | `DOCS_PRECISION: 0.1326` | `DOCS_RECALL: 0.2079`
  - `CHUNKS_F2MACRO: 0.1488` | `CHUNKS_PRECISION: 0.1279` | `CHUNKS_RECALL: 0.1854`
- **Phân tích kết quả:**
  - **Kỷ lục mới bị phá vỡ:** Việc tăng chunk từ 10 lên 100 đã khiến **CHUNKS_RECALL nhảy vọt từ 4.62% lên 18.54%** (tăng gấp 4 lần)! Điều này đẩy điểm CHUNKS_F2MACRO lên 0.1488, qua đó kéo `FINAL_SCORE` lên mốc **0.1557** cao nhất từ đầu cuộc thi tới giờ.
  - Sức mạnh của Dense Retrieval: Điểm cao nhất trước đó là Exp 09 (0.1206) có được sau khi chạy thuật toán Sliding Window tinh xảo qua **2.1 triệu tài liệu**. Ở Exp 14 này, dù chỉ mới lấy **19% dữ liệu**, chúng ta đã vượt mốc 0.15.
  - **Bước tiếp theo (Bắt buộc):** Chạy tiếp index trên phần 1.7 triệu tài liệu còn lại. Khi 100% dữ liệu có vector, Final Score hứa hẹn sẽ bùng nổ vượt 0.2 hoặc cao hơn nữa.

---

---
[← Exp 13](exp13_bge_m3_dense_400k_top100.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 15 →](exp15_bge_m3_dense_700k.md)
