[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 07: BM25s Top 100 + Nộp Naive Chunks (1200 chars đầu)

- **Mục tiêu:** Kiểm tra xem nếu trích xuất một đoạn text đơn giản (naive window: lấy 1200 ký tự đầu của mỗi tài liệu tìm được) thì điểm `CHUNKS_F2` sẽ thay đổi như thế nào, nhằm thoát khỏi cảnh điểm Chunk bị 0 liên tục.
- **Phương pháp:**
  - Vẫn giữ nguyên kết quả truy hồi tài liệu (Docs) giống y hệt Exp 03 (dùng `bm25s`, top 100).
  - Với mỗi tài liệu lọt vào top 100, cắt 1200 ký tự đầu tiên để nộp dưới dạng `relevant_chunks`.
- **Kết quả:**
  - `FINAL_SCORE: 0.0842` _(Tăng từ 0.0677)_
  - `DOCS_F2MACRO: 0.1366` | `DOCS_PRECISION: 0.1048` | `DOCS_RECALL: 0.1821`
  - `CHUNKS_F2MACRO: 0.0318` | `CHUNKS_PRECISION: 0.0252` | `CHUNKS_RECALL: 0.0431`
- **Phân tích kết quả (Key Insights):**
  1. **Tài liệu (Docs) ổn định:** Do không thay đổi thuật toán tìm tài liệu, điểm Docs F2 hoàn toàn giống Exp 03.
  2. **Thoát khỏi điểm Chunk 0:** Phương pháp "cắt thô" đã giúp điểm CHUNKS_F2 nhích lên 0.0318, qua đó kéo FINAL_SCORE lên 0.0842.
  3. **Tuy nhiên, 1200 ký tự đầu là chưa đủ tốt:**
     - Mặc dù Docs Recall là ~18.2%, nhưng Chunks Recall chỉ đạt 4.31%.
     - Điều này chứng tỏ trong số các tài liệu tìm đúng, chưa tới 1/4 có chứa đáp án thực sự trong 1200 ký tự đầu tiên.
     - Rất nhiều trang web chứa "boilerplate" (thanh điều hướng, footer, quảng cáo) hoặc đáp án nằm sâu ở bên dưới, nên việc lấy 1200 ký tự đầu tiên bị "trượt" khỏi tiêu chuẩn Overlap > 0.5 với Ground Truth Chunk.
  4. **Kết luận / Bước tiếp theo:** Để có điểm chunk cao thực sự (vượt qua 0.18), không thể cắt chuỗi thô mà bắt buộc phải dùng mô hình LLM / Cross-encoder để xác định chính xác vị trí đoạn văn chứa thông tin trả lời (Semantic Chunking & Reranking) hoặc loại bỏ boilerplate trước khi cắt chunk.

---

---
[← Exp 06](exp06_multilingual_bm25_rrf.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 08 →](exp08_window_100_2500.md)
