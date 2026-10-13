[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 06: Multilingual BM25 + Query Expansion + RRF + BGE Reranker (Nộp top 100)

- **Mục tiêu:** Tối đa hóa Recall bằng cách mở rộng truy vấn (VI, EN, ZH) kết hợp RRF (lấy top 500) và dùng BGE-M3 Reranker để chọn ra top 100 nộp bài.
- **Phương pháp:**
  - Stage 1: Groq API Query Expansion (y khoa) -> Dịch sang 3 ngôn ngữ -> BM25s -> Reciprocal Rank Fusion (RRF $k=60$) lấy ra 500 candidates tốt nhất.
  - Stage 2: BGE-M3 Reranker đánh giá 500 ứng viên này và giữ lại Top 100 để nộp.
- **Kết quả:**
  - `FINAL_SCORE: 0.0677`
  - `DOCS_F2MACRO: 0.1354` | `DOCS_PRECISION: 0.1043` | `DOCS_RECALL: 0.1804`
  - `CHUNKS_F2MACRO: 0.0` | `CHUNKS_PRECISION: 0.0` | `CHUNKS_RECALL: 0.0`
- **Phân tích kết quả (Key Insights):**
  - **Điểm số gần như y hệt Exp 03 (BM25s chay top 100):** Kết quả này (Recall 18.04%, Precision 10.43%) gần như trùng khớp hoàn toàn với Exp 03 (Recall 18.21%, Precision 10.48%).
  - **Nút thắt ở Zero-shot Reranker (Out-of-domain):** Mặc dù Stage 1 có thể đã gom được Recall lên rất cao (>30% như Exp 04), nhưng mô hình BGE-M3 Reranker (vốn được train chung chung) đã không thể nhận diện chính xác độ liên quan trong ngữ cảnh y khoa tiếng Việt. Hậu quả là khi cắt lấy top 100 sau re-rank, nó đã đẩy nhiều tài liệu đúng xuống dưới và kéo Recall tụt trở lại mức 18%.
  - **Nhiễu từ Query Expansion:** Việc mở rộng truy vấn bằng LLM và dịch sang tiếng Anh/Trung có thể đã đưa vào top 500 quá nhiều tài liệu nhiễu (dài, chứa các từ khóa học thuật nhưng không có đáp án cụ thể cho câu hỏi), khiến reranker bị "đánh lừa".

---

---
[← Exp 05](exp05_bm25s_bge_reranker.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 07 →](exp07_naive_chunks_1200.md)
