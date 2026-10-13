[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 20: Pure BM25 via SQLite FTS5 (1.35M docs)

- **Mục tiêu:** Kiểm chứng giả thuyết (tin đồn từ Top 1) rằng "chỉ cần cào hết data và chạy BM25 là điểm sẽ > 0.3x".
- **Phương pháp:**
  - Lập chỉ mục bằng **SQLite FTS5** trên `tier_1_resume.parquet` và `tier_other.parquet` (tổng cộng **1.358.107 bài viết**). Chú ý: file `tier_2.parquet` (254k docs) bị lỗi I/O nên không được nạp.
  - Tokenization: Dùng `unicode61` mặc định của SQLite (bỏ dấu tiếng Việt).
  - Search: Nối các từ trong query bằng `OR` (`MATCH 'từ1 OR từ2'`).
  - Chunking: Hàm `sliding_window_extract` tìm đoạn 2500 ký tự chứa nhiều keyword nhất.
- **Kết quả:**
  - `FINAL_SCORE: 0.0677` _(Rất thấp, ngang ngửa với Exp 06)_
  - `DOCS_F2MACRO: 0.0736` | `DOCS_PRECISION: 0.0589` | `DOCS_RECALL: 0.0965`
  - `CHUNKS_F2MACRO: 0.0617` | `CHUNKS_PRECISION: 0.0512` | `CHUNKS_RECALL: 0.0798`
- **Phân tích Đột phá (Bác bỏ giả thuyết "Chỉ cần BM25 là 0.3x"):**
  1. **Điểm số quá tệ:** Document Recall chỉ đạt **9.65%**, thấp hơn rất nhiều so với phương pháp Dense Hybrid (Recall 22.3% trên 700k docs) dù kho dữ liệu lớn gần gấp đôi (1.35M docs).
  2. **Nguyên nhân cốt lõi từ SQLite FTS5:**
     - _Diacritic Stripping:_ FTS5 mặc định bỏ dấu tiếng Việt (ví dụ `đường` -> `duong`), gây nhiễu loạn ngữ nghĩa nghiêm trọng.
     - _Nhiễu Stopword:_ Không có bước loại bỏ stopword ("của", "và", "những"). Khi query bằng toán tử `OR`, các tài liệu chứa nhiều từ nối (nhưng không liên quan đến bệnh) sẽ bị đẩy rank lên rất cao.
     - _Unigram Matching:_ Tiếng Việt đa phần là từ ghép (bi-gram). BM25 dựa trên unigram không thể phân biệt "bệnh viện" với các tài liệu có từ "bệnh" và từ "viện" nằm rải rác.
  3. **Tác động từ việc mất `tier_2`:** Việc hụt mất 250k tài liệu chắc chắn làm giảm Recall, nhưng không đủ để giải thích mức sụt giảm khổng lồ từ mốc "tin đồn" 0.3x xuống tận 0.06x.
- **Kết luận (Next Steps):**
  - Giả thuyết "Chỉ cần BM25 là 0.3x" bị bác bỏ (ít nhất là với cách implement BM25 thô sơ này). Rất có thể Top 1 đã ám chỉ "BM25 có bộ Analyzer/Tokenizer tiếng Việt chuẩn (như Elasticsearch + VnCoreNLP) kết hợp hybrid", hoặc pipeline của họ xịn hơn rất nhiều.
  - Hướng đi đúng đắn nhất của đội chúng ta vẫn là **Hybrid Retrieval (BGE-M3 Dense + Sparse)**. Việc cần làm ngay bây giờ là tạo vector embedding cho toàn bộ 1.35M docs này thay vì dùng BM25 thuần túy.

---

---
[← Exp 19](exp19_bge_m3_linear_hybrid.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 21 →](exp21_bge_m3_tier2.md)
