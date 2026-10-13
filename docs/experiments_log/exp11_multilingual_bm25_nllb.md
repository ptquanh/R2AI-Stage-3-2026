[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 11: Multilingual BM25 + RRF + NLLB Translation

- **Mục tiêu:** Áp dụng mô hình dịch thuật local (NLLB-200 600M) chạy trực tiếp trên GPU Kaggle để mở rộng truy vấn (VI -> EN, ZH) kết hợp với RRF (công thức $k=60$). Đánh giá tính khả thi và hiệu năng của mô hình dịch nhỏ gọn này trong ngữ cảnh y tế.
- **Phương pháp:**
  - Notebook: `09_baseline_bm25_chunk_submission.ipynb`.
  - Dịch Query: Dùng mô hình `facebook/nllb-200-distilled-600M` để dịch sang tiếng Anh và tiếng Trung.
  - Fusion: Chạy 3 luồng BM25s cho 3 ngôn ngữ (mỗi luồng lấy top 300 docs) và kết hợp điểm bằng RRF (công thức k=60), sau đó lấy ra top 100 docs cuối cùng.
  - Chunking: Lấy tối đa 2500 ký tự (sử dụng Sliding Window nếu có). Sau đó ở bước tạo file submission, tiến hành cắt bỏ 100 từ đầu tiên ở mỗi chunk để file zip nộp xuống dưới giới hạn 100MB của BTC (chỉ còn 73.9MB).
- **Kết quả:**
  - `FINAL_SCORE: 0.0679` _(Giảm mạnh từ mốc 0.1206 của Exp 09)_
  - `DOCS_F2MACRO: 0.0803` | `DOCS_PRECISION: 0.0570` | `DOCS_RECALL: 0.1137`
  - `CHUNKS_F2MACRO: 0.0554` | `CHUNKS_PRECISION: 0.0403` | `CHUNKS_RECALL: 0.0778`
- **Phân tích kết quả:**
  - **Docs Recall rớt nghiêm trọng:** So với BM25s thuần (Exp 03, Recall 18.21%), việc dùng NLLB dịch truy vấn kết hợp RRF lại làm Recall tụt xuống 11.37%.
    - _Nguyên nhân:_ Mô hình NLLB-200 600M là mô hình nhỏ gọn nên chất lượng dịch thuật ngữ y khoa chuyên sâu từ tiếng Việt sang EN/ZH có khả năng chưa đủ tốt hoặc bị sai nghĩa. Điều này dẫn tới 2 luồng truy hồi EN và ZH bị nhiễu. Khi kết hợp RRF, những kết quả sai này đã vô tình đẩy các tài liệu chuẩn xác (từ luồng VI) rớt hạng xuống khỏi Top 100.
  - **Chunk F2 thấp do thủ thuật cắt từ:** Việc loại bỏ 100 từ đầu tiên (để "ép" dung lượng zip) thực chất lại gọt mất một lượng lớn thông tin then chốt (do nhiều bài báo trả lời trực tiếp câu hỏi ở phần tóm tắt đầu bài). Điều này trực tiếp kéo Chunk Recall xuống mức thấp (0.0778).
  - **Bài học rút ra:** Việc dịch tự động bằng translation model nhẹ không phải lúc nào cũng tối ưu cho độ chính xác cao. Lời đề nghị sử dụng chuẩn từ điển y khoa ICD-10 của user rất chính xác. Khâu Query Expansion nên ưu tiên dùng các bộ Map/Ontology y khoa chuẩn hóa thay vì RRF đa ngôn ngữ bằng mô hình dịch nhỏ. Kế đó, cần một chiến lược chunking thông minh hơn thay vì gọt xén bớt đầu đuôi.

---

---
[← Exp 10](exp10_dynamic_window_3200.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 12 →](exp12_bge_m3_dense_400k_top10.md)
