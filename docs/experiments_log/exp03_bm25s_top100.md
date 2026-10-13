[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 03: BM25s trên 2.1 triệu tài liệu (Top k = 100)

- **Mục tiêu:** Nới rộng candidate pool lên top 100 để xem liệu BM25s có bắt được tài liệu liên quan không.
- **Phương pháp:**
  - BM25s trên ~2.1M tài liệu.
  - Lấy top $k=100$ tài liệu cho mỗi query.
- **Kết quả:**
  - `FINAL_SCORE: 0.0683`
  - `DOCS_F2MACRO: 0.1366` | `DOCS_PRECISION: 0.1048` | `DOCS_RECALL: 0.1821`
  - `CHUNKS_F2MACRO: 0.0` | `CHUNKS_PRECISION: 0.0` | `CHUNKS_RECALL: 0.0`
- **Phân tích kết quả:**
  - **Tài liệu (Docs):** Mở rộng từ $k=5$ lên $k=100$ ngay lập tức mở khóa Recall từ **0% lên 18.21%**! Precision đạt 10.48%.
  - **Đoạn văn (Chunks):** Điểm bằng 0.0 do chưa có mô-đun Semantic Chunking hoặc chưa submit chunks hợp lệ.
  - Chứng minh BM25s đã bắt đầu tìm thấy tài liệu liên quan, nhưng $k=100$ vẫn còn bỏ sót hơn 81% tài liệu ground truth.

---

---
[← Exp 02](exp02_bm25s_top5.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 04 →](exp04_bm25s_top500.md)
