[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 00: BM25 Baseline (BTC cung cấp)

- **Phương pháp:** Thuật toán đếm tần suất từ khóa BM25 truyền thống, không dùng AI hay Vector Embedding.
- **Phân tích kết quả:**
  - **Truy hồi cấp Document (Tài liệu):** Điểm F2 đạt 0.5587. Precision rất cao (0.8805) nhưng Recall chỉ ở mức trung bình (0.5146).
    👉 _Nhận xét:_ Chữ nào giống chữ đó thì BM25 tìm rất trúng (Precision cao), nhưng nó bỏ sót một nửa số tài liệu liên quan (Recall thấp) vì không hiểu được từ đồng nghĩa hoặc các thuật ngữ y khoa tương đương.
  - **Truy hồi cấp Chunk (Đoạn văn):** Điểm F2 siêu thấp (0.1941), Recall cực kỳ tệ (0.1755).
    👉 _Nhận xét:_ BM25 gần như thất bại hoàn toàn trong việc trích xuất chính xác đoạn chứa thông tin "chốt". Thuật toán Chunking của Baseline khả năng cao đang cắt vỡ ngữ nghĩa hoặc chunk nộp lên không overlap đủ với Ground Truth.
- **Mục tiêu cho Pipeline R2AI của chúng ta:**
  1. Tăng vọt Recall bằng cách thêm Vector Embedding + Medical Ontology.
  2. Áp dụng Semantic Chunking khắt khe (< 1024 tokens) để cứu vãn điểm Chunks F2.

---

---
[Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 01 →](exp01_format_error.md)
