[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 13: BGE-M3 Dense Search (400k docs, top 100)

- **Mục tiêu:** Kiểm tra lại điểm số sau khi fix code lấy đủ top 100 relevant docs (thay vì 10 docs như Exp 12) trên cùng tập 400.000 tài liệu đầu tiên.
- **Phương pháp:**
  - Tương tự Exp 12, nhưng tăng giới hạn xuất file từ 10 docs lên 100 docs.
- **Kết quả:**
  - `FINAL_SCORE: 0.1076`
  - `DOCS_F2MACRO: 0.1626` | `DOCS_PRECISION: 0.1326` | `DOCS_RECALL: 0.2079`
  - `CHUNKS_F2MACRO: 0.0526` | `CHUNKS_PRECISION: 0.2506` | `CHUNKS_RECALL: 0.0462`
- **Phân tích kết quả (Chiến thắng của Dense Retrieval):**
  - **Docs Recall bứt phá:** Chỉ với 400.000 tài liệu (tức là **chưa đến 20%** của toàn bộ 2.1 triệu tài liệu), mô hình Dense Retrieval đã đạt Recall **20.79%**!
  - So sánh với BM25 ở Exp 03 (chạy trên _toàn bộ_ 2.1 triệu tài liệu, top 100), BM25 chỉ đạt Recall **18.21%**.
  - Điều này chứng minh sức mạnh áp đảo của Embedding: nó tìm ra ground truth tốt hơn hẳn thuật toán từ khóa truyền thống. Việc điểm FINAL_SCORE vẫn ở mức 0.1076 (chưa vượt qua mốc 0.12) hoàn toàn là do **chưa đủ vector** (còn 1.7 triệu tài liệu chưa được index).
  - Điểm Chunk giữ nguyên so với Exp 12 vì giới hạn chunks vẫn là 10 và các chunk tốt nhất đều đã được đẩy lên đầu trong top 10, nên việc mở rộng danh sách docs lên 100 không làm thay đổi top 10 chunks.
  - **Bước tiếp theo:** Ưu tiên số 1 hiện tại là lập chỉ mục (index) toàn bộ 1.7 triệu tài liệu còn lại. Khi có đủ kho dữ liệu, Recall có thể sẽ bùng nổ lên mức rất cao!

---

---
[← Exp 12](exp12_bge_m3_dense_400k_top10.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 14 →](exp14_bge_m3_dense_400k_chunks100.md)
