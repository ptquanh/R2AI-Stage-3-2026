[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 02: BM25s trên 2.1 triệu tài liệu (Top k = 5)

- **Mục tiêu:** Kiểm tra khả năng truy hồi của thư viện BM25s siêu tốc trên toàn bộ kho corpus crawl được (~2.1M documents) với ngưỡng lựa chọn chặt chẽ ($k=5$).
- **Phương pháp:**
  - Sử dụng thư viện `bm25s` để index toàn bộ ~2.1 triệu tài liệu.
  - Chỉ lấy $k=5$ tài liệu có score cao nhất cho mỗi câu truy vấn.
- **Kết quả:**
  - `FINAL_SCORE: 0.0` (DOCS_F2 = 0.0, DOCS_RECALL = 0.0, CHUNKS_F2 = 0.0).
- **Phân tích kết quả:**
  - Trên không gian tìm kiếm cực lớn (2.1M tài liệu so với tập nhỏ của baseline), việc chỉ lấy top 5 là quá hẹp. BM25 thuần túy bị nhiễu bởi các tài liệu dài hoặc trùng lặp từ khóa ngẫu nhiên, khiến các tài liệu thực sự liên quan không lọt nổi vào top 5.
  - Dẫn đến Recall bằng 0 tuyệt đối.

---

---
[← Exp 01](exp01_format_error.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 03 →](exp03_bm25s_top100.md)
