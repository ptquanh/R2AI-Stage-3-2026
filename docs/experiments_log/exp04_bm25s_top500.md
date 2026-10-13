[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 04: BM25s trên 2.1 triệu tài liệu (Top k = 500)

- **Mục tiêu:** Tiếp tục tăng ngưỡng $k$ lên 500 để tối đa hóa khả năng bao phủ (Recall) của Stage 1 BM25.
- **Phương pháp:**
  - BM25s trên ~2.1M tài liệu.
  - Lấy top $k=500$ tài liệu cho mỗi query.
- **Kết quả:**
  - `FINAL_SCORE: 0.0594`
  - `DOCS_F2MACRO: 0.1188` | `DOCS_PRECISION: 0.0408` | `DOCS_RECALL: 0.3115`
  - `CHUNKS_F2MACRO: 0.0` | `CHUNKS_PRECISION: 0.0` | `CHUNKS_RECALL: 0.0`
- **So sánh & Đúc kết quan trọng (Key Insights):**
  1. **Recall tăng vọt:** Khi tăng từ $k=100 \to 500$, **DOCS_RECALL tăng từ 18.21% lên 31.15%** (+12.94%). Điều này khẳng định gần 1/3 tài liệu liên quan nằm trong top 500 của BM25s.
  2. **Trade-off Precision vs Recall:** Nộp thẳng 500 tài liệu làm Precision tụt từ 10.48% xuống 4.08%, kéo DOCS_F2 giảm nhẹ từ 0.1366 xuống 0.1188.
  3. **Định hình kiến trúc 2-Stage:**
     - **Stage 1 (BM25s Candidate Generation):** Nên để $k=300 \sim 500$ để giữ Recall ở mức cao nhất có thể (~31%+).
     - **Stage 2 (Qwen Semantic Re-ranking):** Dùng mô hình Cross-Encoder / Qwen-8B re-rank lại 500 ứng viên này, lọc lấy top 10-20 tài liệu chất lượng nhất để đẩy Precision lên lại 80%+, đồng thời trích xuất Chunk chuẩn xác để giải quyết bài toán `CHUNKS_F2 = 0.0`.

---

---
[← Exp 03](exp03_bm25s_top100.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 05 →](exp05_bm25s_bge_reranker.md)
