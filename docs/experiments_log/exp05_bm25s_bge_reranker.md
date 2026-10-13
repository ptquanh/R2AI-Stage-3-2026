[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 05: BM25s (Top 100) + BGE Reranker (Nộp top 5)

- **Mục tiêu:** Áp dụng mô hình Cross-Encoder (BAAI/bge-reranker-v2-m3) để re-rank các candidates do BM25 truy hồi, nhằm tăng Precision.
- **Phương pháp:**
  - Stage 1: BM25s lấy ra top $k=100$ candidates.
  - Stage 2: Truyền 100 văn bản này vào BGE-M3 Reranker.
  - Lấy top 5 kết quả sau khi rerank để nộp (không nộp chunks).
- **Kết quả:**
  - `FINAL_SCORE: 0.0232`
  - `DOCS_F2MACRO: 0.0464` | `DOCS_PRECISION: 0.3491` | `DOCS_RECALL: 0.0396`
  - `CHUNKS_F2MACRO: 0.0` | `CHUNKS_PRECISION: 0.0` | `CHUNKS_RECALL: 0.0`
- **Phân tích kết quả:**
  - **Precision tăng vọt:** BGE-M3 đã làm việc rất hiệu quả khi tăng Docs Precision lên **34.91%** (so với 4.08% của Exp 04 và 10.48% của Exp 03).
  - **Recall rớt thảm (Bottleneck):** Điểm yếu lớn nhất ở đây là Docs Recall chỉ đạt **3.96%**. Lý do:
    1. Đầu vào cho reranker chỉ là Top 100 từ BM25 (chỉ cover được 18.21% Recall tối đa theo Exp 03).
    2. Chỉ lấy top 5 để submit là quá khắt khe, gạt bỏ nhiều tài liệu ground truth khác nằm ngoài top 5. Chú ý điểm thi F2 Macro luôn ưu tiên Recall hơn Precision (trọng số Recall cao gấp 4 lần Precision).

---

---
[← Exp 04](exp04_bm25s_top500.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 06 →](exp06_multilingual_bm25_rrf.md)
