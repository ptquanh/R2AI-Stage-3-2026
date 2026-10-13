[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 12: BGE-M3 Dense Search (400k docs, top 10)

- **Mục tiêu:** Thử nghiệm phương pháp tìm kiếm Dense Retrieval trực tiếp bằng model `BAAI/bge-m3` trên tập 400.000 tài liệu đầu tiên đã được lập chỉ mục (index).
- **Phương pháp:**
  - Embedding: Dùng BGE-M3 mã hóa query và đối chiếu (dot product) với index của 400k docs.
  - Ranking: Kết hợp điểm từ 4 khối 100k, lấy ra top các chunks.
  - Lỗi cấu hình: Do nhầm lẫn trong code `run_local_submission.py`, thuật toán đã giới hạn `relevant_docs` ở mức tối đa **10 docs** thay vì 100 docs (mức thực nghiệm cho thấy đem lại điểm Recall tốt).
- **Kết quả:**
  - `FINAL_SCORE: 0.0621`
  - `DOCS_F2MACRO: 0.0717` | `DOCS_PRECISION: 0.3250` | `DOCS_RECALL: 0.0633`
  - `CHUNKS_F2MACRO: 0.0526` | `CHUNKS_PRECISION: 0.2506` | `CHUNKS_RECALL: 0.0462`
- **Phân tích kết quả:**
  - **Precision tăng rất mạnh:** Docs Precision lên đến **32.50%** và Chunk Precision lên đến **25.06%**. Điều này cho thấy khả năng matching vector của BGE-M3 cực kỳ chính xác. Những tài liệu và đoạn trích mà nó đẩy lên đầu đa phần là rất đúng.
  - **Recall rớt thê thảm:** Do nộp tối đa có 10 docs, model bỏ sót phần lớn ground truth (Docs Recall chỉ đạt 6.33%). Vì công thức tính của Kaggle (F2 Macro) phạt rất nặng lỗi Recall thấp, nên Final Score bị kéo tụt xuống mức 0.0621.
  - **Hướng khắc phục:** Sửa lại code `run_local_submission.py` để nộp đủ **100 docs** (để tối đa hóa Recall theo kinh nghiệm) và **10 chunks** như quy định. Với Precision cao như vậy, khi mở rộng lên 100 docs, điểm số hứa hẹn sẽ tăng vọt. Kế hoạch tiếp theo là chạy nốt index cho phần còn lại của tập 2.1 triệu tài liệu.

---

---
[← Exp 11](exp11_multilingual_bm25_nllb.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 13 →](exp13_bge_m3_dense_400k_top100.md)
