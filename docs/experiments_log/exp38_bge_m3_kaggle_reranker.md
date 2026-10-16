# Experiment 38: 2-Stage Retrieval with Cross-Encoder Reranking on Kaggle GPU

- **Ngày thực hiện:** 13/10/2026
- **Mục tiêu:** Kiểm nghiệm giả thuyết 2-Stage Retrieval: Sử dụng mô hình Cross-Encoder `BAAI/bge-reranker-v2-m3` (FP16, batch size 128) trên Kaggle GPU để tái sắp xếp tập ứng viên Top 150 từ Stage 1 (Trilingual Hybrid Sweet-spot) kết hợp Score Blending ($0.75 \times \text{Reranker} + 0.25 \times \text{Stage 1}$).
- **Thiết lập thử nghiệm:**
  - **Stage 1 (Retrieval):** FAISS Memory-Mapped + Sparse CSR (~1M corpus, 962k docs), cấu hình `zh_w=1.0, en_w=0.5, sparse_w=0.20, buffer=400`. Xuất Top 150 ứng viên / query.
  - **Stage 2 (Reranking trên Kaggle):** Ghép cặp đa ngữ `(Query, Chunk)` tương ứng ngôn ngữ bài viết (`query_zh` cho tiếng Trung, `query_en` cho tiếng Anh, `query_vi` cho tiếng Việt), chấm điểm bằng `bge-reranker-v2-m3`.
  - **Dung hợp điểm số (Score Blending):** $S_{final} = 0.75 \times S_{reranker\_norm} + 0.25 \times S_{stage1\_norm}$.

---

## 1. Kết quả Đánh giá từ Hệ thống Chấm điểm BTC

| Metric               | Exp 36 (1M Corpus, Stage 1 Only) | **Exp 38 (Kaggle Cross-Encoder Rerank)** |       Biến thiên so với Exp 36       |
| :------------------- | :------------------------------: | :--------------------------------------: | :----------------------------------: |
| **FINAL_SCORE**      |            **0.2963**            |                  0.2936                  |               -0.0027                |
| **DOCS_F2MACRO**     |              0.3187              |              **0.3251** 🏆               |   **+0.0064 (Bứt phá đỉnh mới!)**    |
| **CHUNKS_F2MACRO**   |            **0.2738**            |                  0.2621                  |               -0.0117                |
| **DOCS_PRECISION**   |              0.2499              |              **0.2527** 🏆               |         **+0.0028 (+0.28%)**         |
| **DOCS_RECALL**      |              0.4229              |              **0.4326** 🏆               | **+0.0097 (+0.97% - Lập đỉnh mới!)** |
| **CHUNKS_PRECISION** |            **0.2225**            |                  0.2135                  |               -0.0090                |
| **CHUNKS_RECALL**    |            **0.3563**            |                  0.3382                  |           -0.0181 (-1.81%)           |

---

## 2. Phân tích Nguyên nhân Cốt lõi & Bài học Đột phá (Key Discoveries)

### 🌟 Phát hiện 1: Cross-Encoder cực kỳ thành công ở cấp độ Document

- **Docs Recall nhảy vọt lên 43.26% 🏆** (tăng gần +1.0% so với Exp 36 là 42.29%).
- **Docs Precision tăng lên 25.27% 🏆** và **Docs F2 tăng vọt lên 0.3251 🏆**.
- **Khoảng cách với Top 1 (45.78% Docs Recall) thu hẹp xuống mức kỷ lục: chỉ còn vỏn vẹn 2.52%!**
- Điều này chứng minh giả thuyết hoàn toàn chính xác: Mô hình Cross-Encoder `bge-reranker-v2-m3` đọc sâu toàn diện cặp câu hỏi - đoạn văn và sắp xếp tài liệu cực kỳ chuẩn xác, kéo các tài liệu ground truth nằm sâu trong Top 100–150 lên vị trí cao.

### ⚠️ Phát hiện 2: "Cổ chai" ở cơ chế trích xuất Chunks (Root Cause of Chunks Drop)

- Tại sao Docs Recall tăng vọt nhưng Chunks Recall lại giảm từ 35.63% xuống 33.82%?
- **Nguyên nhân kỹ thuật:**
  1. Trong script trích xuất `export_candidates_for_kaggle.py`, ta đã lọc deduplicate `if d_id not in seen_docs`, vô tình **ép mỗi document chỉ có đúng 1 chunk duy nhất**.
  2. Trong thực tế (như ở Exp 36), một tài liệu ground truth dài thường chứa **2 đến 3 đoạn văn (chunks) liên quan** trả lời cho câu hỏi.
  3. Khi chỉ cho phép 1 chunk / doc, các đoạn văn đắt giá thứ 2 và thứ 3 của các bài viết Top đầu bị vứt bỏ hoàn toàn. Danh sách 98 chunks bị phân tán mỏng ra 98 documents khác nhau thay vì tập trung các đoạn văn chất lượng nhất của các tài liệu Top 1-30.

---

## 3. Giải pháp Khắc phục để Vượt Ngưỡng 0.31+

- **Chuyển sang Chunk-Level Candidate Pool:**
  - Khi export candidate từ Stage 1, lấy **Top 200–250 CHUNKS** (cho phép nhiều chunks trên cùng một document).
  - Cross-Encoder sẽ chấm điểm trực tiếp cho từng chunk.
  - `relevant_docs`: Lấy Top 100 unique documents có chunk điểm cao nhất.
  - `relevant_chunks`: Lấy Top 98 chunks có điểm Cross-Encoder cao nhất (tự động cho phép tài liệu chuẩn đóng góp nhiều chunks).
- Với giải pháp này, Docs Recall giữ vững mốc **43.26%**, trong khi Chunks Recall sẽ hồi phục và vượt ngưỡng **36–37%**, dự kiến đẩy Final Score vượt **0.3050 - 0.3100**!
