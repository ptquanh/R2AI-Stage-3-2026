[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 09: Dynamic Window (2500 chars, top k=100)

- **Mục tiêu:** Thử nghiệm hàm trượt cửa sổ động `select_best_window` ưu tiên mật độ từ khóa, đồng thời giữ `win_chars = 2500` (để không vượt quá giới hạn file size 100MB của BTC khi nén file json bằng chuẩn Deflated thông thường).
- **Phương pháp:**
  - Docs: Giữ nguyên truy hồi bằng BM25s lấy top $k=100$.
  - Chunks: Chạy thuật toán Sliding Window để tìm đoạn văn (tối đa 2500 ký tự) có chứa nhiều từ khóa từ câu hỏi nhất, thay vì cắt đoạn đầu `[100:2500]` cứng nhắc như Exp 08.
- **Kết quả:**
  - `FINAL_SCORE: 0.1206` _(Tăng từ 0.1182)_
  - `DOCS_F2MACRO: 0.1366` | `DOCS_PRECISION: 0.1048` | `DOCS_RECALL: 0.1821`
  - `CHUNKS_F2MACRO: 0.1047` | `CHUNKS_PRECISION: 0.0826` | `CHUNKS_RECALL: 0.1381`
- **Phân tích kết quả (Key Insights):**
  - **Chunk F2 tiếp tục tăng:** Việc trượt tìm đoạn chứa nhiều keyword đã giúp cắt đoạn chính xác hơn, nâng CHUNKS F2 từ 0.0999 lên 0.1047 (+4.8%).
  - Mốc `FINAL_SCORE` vượt 0.12 đầu tiên trong lịch sử log. Việc giữ Window Size = 2500 tỏ ra tối ưu, vượt qua bài test giới hạn 100MB cho phép nộp file thành công mà không phải đánh đổi Recall.

---

---
[← Exp 08](exp08_window_100_2500.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 10 →](exp10_dynamic_window_3200.md)
