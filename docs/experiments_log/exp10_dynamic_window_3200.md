[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 10: Dynamic Window (3200 chars, top k=70)

- **Mục tiêu:** Khai thác tối đa giới hạn 1024 tokens chuẩn (tương đương 3200 ký tự) để lấy ngữ cảnh đầy đủ hơn, nâng điểm Chunk Recall. Tuy nhiên, vì 3200 ký tự $\times$ 100 docs vượt quá 100MB khi zip, ta buộc phải đánh đổi bằng cách giảm số lượng Docs nộp (giảm $k$ từ 100 xuống 70).
- **Phương pháp:**
  - Docs: Giảm số ứng viên lấy từ BM25s xuống top $k=70$ (thay vì 100).
  - Chunks: Sử dụng Dynamic Sliding Window với max size `win_chars = 3200`.
- **Kết quả:**
  - `FINAL_SCORE: 0.1156` _(Giảm từ 0.1206)_
  - `DOCS_F2MACRO: 0.1278` | `DOCS_PRECISION: 0.1226` | `DOCS_RECALL: 0.1553`
  - `CHUNKS_F2MACRO: 0.1034` | `CHUNKS_PRECISION: 0.1012` | `CHUNKS_RECALL: 0.1254`
- **Phân tích kết quả:**
  - **Đánh đổi Recall là sai lầm:** Khi giảm top $k=70$, DOCS RECALL đã rớt thẳng từ 18.21% xuống 15.53% (mất gần 3%). Kéo theo đó, mặc dù độ rộng Chunk 3200 ký tự giúp Docs Precision và Chunk Precision tăng lên cao nhất lịch sử (tương ứng 12.26% và 10.12%), nhưng công thức F2 Macro của BTC thiên vị Recall cực nặng (Recall trọng số 4 so với Precision trọng số 1).
  - **Kết luận:** **Tuyệt đối không giảm $k$ xuống dưới 100 (tốt nhất là giữ $k \ge 100$).** Việc hy sinh Document Recall để chừa dung lượng cho Chunk lớn hơn đem lại bất lợi ("lợi bất cập hại"). Lộ trình tốt nhất để tăng điểm lúc này là dùng $k=100$, ép `win_chars = 2500` như Exp 09 và tìm cách mở rộng truy vấn (Multilingual BM25) hoặc dùng mô hình phân giải để tăng Docs Recall từ 18% lên 30% thay vì can thiệp vào Chunk quá lớn gây phình dung lượng.

---

---
[← Exp 09](exp09_dynamic_window_2500.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 11 →](exp11_multilingual_bm25_nllb.md)
