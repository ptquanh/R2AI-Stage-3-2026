[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 23: BGE-M3 Linear Hybrid (Top 200 Docs & 100 Chunks) 🚀

- **Mục tiêu:** Mở rộng số lượng tài liệu truy hồi lên gấp đôi (`top_docs = 200`) để kiểm chứng khả năng tối đa hóa Docs Recall, đồng thời giữ nguyên ngân sách đoạn văn tối đa cho phép (`top_chunks = 100`) với cơ chế nén bảo vệ dung lượng ZIP < 98 MB.
- **Cấu hình & Siêu tham số:**
  - Lệnh: `python scripts/run_submission.py --mode hybrid --fusion linear --dense_weight 1.0 --sparse_weight 0.2 --top_docs 200 --top_chunks 100 --output submission_bgem3_top200_docs.json`
  - Nộp: 200 docs và 100 chunks per query. File ZIP nặng 94.11 MB (an toàn dưới ngưỡng 100 MB).
- **Kết quả:**
  - `FINAL_SCORE: 0.2110` _(Tương đương mốc đỉnh 0.2121 của Exp 21)_
  - `DOCS_F2MACRO: 0.2205` | `DOCS_PRECISION: 0.1183` | **`DOCS_RECALL: 0.3547`** 🥇 _(Kỷ lục Recall cao nhất lịch sử!)_
  - **`CHUNKS_F2MACRO: 0.2016`** 🥇 | `CHUNKS_PRECISION: 0.1675` | **`CHUNKS_RECALL: 0.2557`**
- **So sánh trực tiếp với Exp 21 (Top 100 Docs, 98 Chunks):**

  | Chỉ số (Metric)      | Exp 21 (Top 100 Docs) | Exp 23 (Top 200 Docs)  |      Chênh lệch (Delta)      |
  | :------------------- | :-------------------: | :--------------------: | :--------------------------: |
  | **FINAL SCORE**      |      **0.2121**       |         0.2110         |      -0.0011 (Cân bằng)      |
  | **DOCS RECALL**      |    0.2875 (28.75%)    | **0.3547 (35.47%)** 🥇 |    **+6.72% (+23.4%)** 🚀    |
  | **CHUNKS RECALL**    |    0.2536 (25.36%)    | **0.2557 (25.57%)** 🥇 |          **+0.21%**          |
  | **CHUNKS F2 MACRO**  |        0.2010         |     **0.2016** 🥇      |    **+0.0006 (Đỉnh mới)**    |
  | **CHUNKS PRECISION** |      **0.1692**       |         0.1675         |           -0.0017            |
  | **DOCS PRECISION**   |      **0.1802**       |         0.1183         | -0.0619 (Do chia mẫu số 200) |
  | **DOCS F2 MACRO**    |      **0.2233**       |         0.2205         |           -0.0028            |

- **Phân tích Đột phá (Key Insights):**
  1. **Bước nhảy vọt lịch sử về Recall (35.47%):**
     - Khi mở rộng từ 100 lên 200 docs, **DOCS_RECALL tăng vọt thêm +6.72%** (từ 28.75% lên 35.47%, tăng tương đối +23.4%).
     - Điều này chứng minh hơn **1/3 tổng số tài liệu Ground Truth của bài thi** đã nằm trong Top 200 ứng viên của mô hình BGE-M3!
     - Khoảng cách Recall với đội Top 1 (`45.78%`) đã được thu hẹp đáng kể (từ 17% xuống chỉ còn ~10%).
  2. **Bài toán Trade-off Precision vs. Recall:**
     - Do nộp 200 docs, mẫu số tính Docs Precision tăng gấp đôi, làm Docs Precision giảm từ 18.02% xuống 11.83%. Mức giảm Precision này đã kìm giữ Docs F2 ở mức 0.2205 (giảm nhẹ 0.0028) dù Recall tăng rất mạnh.
     - Về phía Chunk, do vẫn giữ nguyên `top_chunks = 100`, cả Chunks Recall và Chunks F2 đều đạt kỷ lục mới (**CHUNKS_F2 = 0.2016**).
  3. **Kết luận & Hướng tối ưu cho Stage 2 (Reranking):**
     - Thử nghiệm này khẳng định: **Stage 1 Candidate Pool với $k=200$ là cực kỳ hoàn hảo vì đã gom được tới 35.5% Recall**.
     - Để bứt phá lên Top 1 (0.42+), bước tiếp theo không phải là mò mẫm cắt tỉa Top-K thô, mà là **huấn luyện hoặc áp dụng một Cross-Encoder Reranker** (ví dụ Qwen2.5-7B/14B Reranker hoặc BGE Reranker fine-tuned) để re-rank lại 200 ứng viên này: lọc lấy Top 100–120 tài liệu chất lượng nhất để vừa giữ nguyên Recall ~35%+, vừa đẩy Docs Precision trở lại mức > 30%, đưa FINAL_SCORE nhảy vọt qua mốc **0.30 – 0.35+**!

---

---
[← Exp 22](exp22_bge_m3_top10.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 24 →](exp24_2stage_rerank.md)
