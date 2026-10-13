[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 24: 2-Stage Retrieval + Cross-Encoder Reranker (`bge-reranker-v2-m3`) 🚀🔥

- **Mục tiêu:** Hiện thực hóa kiến trúc **2-Stage Retrieval** nhằm giải quyết triệt để bài toán mâu thuẫn giữa Recall và Precision (vấn đề của Exp 22 và Exp 23):
  - **Stage 1:** Sử dụng BGE-M3 Dense + Sparse Hybrid (RRF) quét toàn bộ 11 shards (`data/indices`) để lấy **Top 200 Candidate Docs** mỗi query (đảm bảo Recall thô $\ge 35\%$).
  - **Stage 2:** Sử dụng mô hình Cross-Encoder đa ngữ đỉnh cao **`BAAI/bge-reranker-v2-m3`** (FP16) với cơ chế tự động định tuyến ngôn ngữ (Cross-Lingual Query Routing: ghép `query_zh` khi chunk là tiếng Trung, giữ `query` gốc khi chunk tiếng Việt) để tính điểm cross-attention sâu giữa câu hỏi và đoạn văn bản.
  - **Output Filter:** Sắp xếp lại danh sách ứng viên theo điểm Reranker, sau đó cắt lọc lấy **Top 100 Docs** và **Top 98 Chunks** tốt nhất.
- **Cấu hình & Siêu tham số:**
  - Lệnh thực thi:
    ```powershell
    python scripts/run_submission.py `
      --mode hybrid `
      --fusion rrf `
      --dense_weight 1.0 `
      --sparse_weight 0.2 `
      --rerank `
      --rerank_cand_docs 200 `
      --top_docs 100 `
      --top_chunks 98 `
      --output submission_bgem3_rerank_cand200_top100.json
    ```
  - Reranker: `BAAI/bge-reranker-v2-m3` (FP16, batch_size=64, max_length=512).
  - VRAM Management: Tự động giải phóng `model` BGE-M3 và dọn bộ nhớ cache (`torch.cuda.empty_cache()`) trước khi tải Reranker, đảm bảo hoạt động an toàn tuyệt đối trên RTX 3050 Ti 4GB VRAM.
  - File ZIP sinh ra: [`submission_bgem3_rerank_cand200_top100.zip`](file:///d:/CODE%20PLAYGROUND/Projects/Competitions/R2AI-Stage-3-2026/submission_bgem3_rerank_cand200_top100.zip) dung lượng **82.78 MB** (đạt chuẩn an toàn `< 100 MB`).
- **Kết quả:**
  - `FINAL_SCORE: 0.1835` _(Giảm từ mốc 0.2121 của Exp 21 và 0.2110 của Exp 23)_
  - `DOCS_F2MACRO: 0.2024` | `DOCS_PRECISION: 0.1602` | `DOCS_RECALL: 0.2616`
  - `CHUNKS_F2MACRO: 0.1646` | `CHUNKS_PRECISION: 0.1361` | `CHUNKS_RECALL: 0.2086`

- **So sánh trực tiếp với Exp 21 và Exp 23:**

  | Chỉ số (Metric)      | Exp 21 (Linear Top 100) | Exp 23 (Linear Top 200) | Exp 24 (2-Stage Rerank: Top 200 $\to$ 100) | So với Exp 21 | So với Exp 23 |
  | :------------------- | :---------------------: | :---------------------: | :----------------------------------------: | :-----------: | :-----------: |
  | **FINAL SCORE**      |       **0.2121**        |         0.2110          |                   0.1835                   |  **-0.0286**  |  **-0.0275**  |
  | **DOCS RECALL**      |     0.2875 (28.75%)     | **0.3547 (35.47%)** 🥇  |              0.2616 (26.16%)               | **-2.59%** 🔻 | **-9.31%** 🔻 |
  | **DOCS PRECISION**   |   **0.1802 (18.02%)**   |     0.1183 (11.83%)     |              0.1602 (16.02%)               |    -2.00%     | **+4.19%** 🚀 |
  | **DOCS F2 MACRO**    |       **0.2233**        |         0.2205          |                   0.2024                   |    -0.0209    |    -0.0181    |
  | **CHUNKS RECALL**    |     0.2536 (25.36%)     | **0.2557 (25.57%)** 🥇  |              0.2086 (20.86%)               | **-4.50%** 🔻 | **-4.71%** 🔻 |
  | **CHUNKS PRECISION** |   **0.1692 (16.92%)**   |     0.1675 (16.75%)     |              0.1361 (13.61%)               |    -3.31%     |    -3.14%     |
  | **CHUNKS F2 MACRO**  |         0.2010          |      **0.2016** 🥇      |                   0.1646                   |    -0.0364    |    -0.0370    |

- **Phân tích Chuyên sâu (Key Insights & Root Cause Analysis):**
  1. **Hiện tượng "Negative Transfer" của Zero-shot Cross-Encoder:**
     - Mô hình `BAAI/bge-reranker-v2-m3` là một mô hình tổng quát (General-domain), chưa được tinh chỉnh (fine-tune) trên tập câu hỏi - đáp y khoa chuyên sâu của cuộc thi.
     - Khi cho Cross-Encoder chấm điểm thuần túy và sắp xếp lại, mô hình có xu hướng chấm điểm cao cho các văn bản chứa các từ vựng trùng lặp bề mặt (lexical overlap) hoặc bài viết sức khỏe đời sống chung chung, trong khi các tài liệu chuyên ngành thực sự (Ground Truth) lại bị đẩy tụt xuống sau vị trí 100.
     - Hậu quả: **DOCS_RECALL bị rơi từ 35.47% (Exp 23) xuống chỉ còn 26.16%** (thậm chí thấp hơn cả 28.75% của Exp 21 không dùng reranker).
  2. **Sai lầm khi loại bỏ hoàn toàn điểm số Stage 1 (Hard Replacement vs. Score Interpolation):**
     - Hiện tại trong Exp 24, thứ hạng cuối cùng được quyết định **100% bởi điểm Reranker**. Điều này làm mất đi hoàn toàn "mỏ neo" ngữ nghĩa toàn cục và điểm số lexical matching cực chuẩn mà BGE-M3 (Dense + Sparse) đã tính toán.
     - Trong Information Retrieval chuẩn công nghiệp, không bao giờ dùng Reranker thay thế hoàn toàn điểm Stage 1 nếu Reranker chưa được fine-tune in-domain. Giải pháp chuẩn là **kết hợp trọng số (Interpolation / Fusion)**:
       $$\text{Score}_{\text{final}} = \text{Score}_{\text{Stage1}} + \alpha \cdot \text{Score}_{\text{Reranker}}$$
       hoặc dùng Reciprocal Rank Fusion (RRF) kết hợp Rank Stage 1 và Rank Reranker.
  3. **Yếu tố Fusion (RRF vs. Linear) ở Stage 1:**
     - Cấu hình đỉnh cao ở Exp 21 dùng `--fusion linear --dense_weight 1.0 --sparse_weight 0.2` (cộng tuyến tính dot product giữa Dense và Sparse).
     - Ở Exp 24, script lại dùng `--fusion rrf`, vốn dựa vào thứ hạng nghịch đảo $1 / (60 + rank)$, khiến cho tập ứng viên 200 tài liệu ban đầu bị biến đổi so với Exp 21.
  4. **Kết luận Chiến lược:**
     - Tạm thời **không dùng Zero-shot Cross-Encoder thay thế hoàn toàn điểm số**.
     - Nếu muốn tiếp tục tăng điểm ngay lập tức:
       - **Phương án 1 (Ổn định nhất):** Quay về kiến trúc **Linear Hybrid (w=0.2)** của Exp 21 / Exp 23.
       - **Phương án 2 (Ensemble / Interpolation):** Giữ Stage 1 là Linear Hybrid (Exp 21/23), nếu dùng Reranker thì phải kết hợp điểm số $\text{Score}_{\text{Stage1}} + \alpha \cdot \text{Score}_{\text{Rerank}}$ thay vì ghi đè hoàn toàn.
       - **Phương án 3 (Mở rộng Corpus - Lõi cốt tử):** Tiếp tục lập chỉ mục (index) các khối Tier 2 còn thiếu (như `ask.39.net`, `120ask.com`) vì dữ liệu thực tế chứng minh mỗi khi nạp thêm dữ liệu cào được, Recall tăng vọt từ 20% lên 28% và 35%.

---

---
[← Exp 23](exp23_bge_m3_top200.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 25 →](exp25_bge_m3_14shards.md)
