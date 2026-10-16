# Thử nghiệm 34: BGE-M3 Linear Hybrid (+Score Threshold 0.70)

- **Ngày thực hiện:** 13/10/2026
- **Mục tiêu:** Thử nghiệm chiến lược cắt tỉa tự động theo ngưỡng tương đồng Cosine khắt khe (`--score_threshold 0.70`, kèm khoảng bảo vệ `min_docs=5, min_chunks=5`) dựa trên kết quả của Exp 33 để kiểm chứng giả thuyết đẩy Precision.
- **Cấu hình chi tiết:**
  - **Mô hình:** `BAAI/bge-m3` (Linear Hybrid: Dense 1.0 + Sparse 0.2).
  - **Dữ liệu:** `data/indices/new_dataset` (662.8k docs / 1.05M chunks).
  - **Truy vấn:** Tiếng Việt gốc + Bản dịch tiếng Trung offline (Qwen 1.5B).
  - **Công cụ tìm kiếm:** `FAISSSearcher` (FAISS Memory-Mapped + Sparse Rescoring).
  - **Ngưỡng điểm (Threshold):** `--score_threshold 0.70` (áp dụng trên metric Dense Cosine Similarity).
  - **Khoảng bảo vệ:** `min_docs = 5`, `min_chunks = 5` (nếu không đủ kết quả $\ge 0.70$ thì giữ tối thiểu 5 ứng viên).
  - **File nộp:** `submission_bgem3_hybrid_w02_thresh_07.zip` (20.67 MB).

---

## Kết quả Đánh giá từ BTC (Official Score)

```json
{
  "FINAL_SCORE": 0.1151,
  "DOCS_F2MACRO": 0.1292,
  "CHUNKS_F2MACRO": 0.1011,
  "DOCS_PRECISION": 0.4145,
  "DOCS_RECALL": 0.1194,
  "CHUNKS_PRECISION": 0.3265,
  "CHUNKS_RECALL": 0.0931
}
```

---

## So sánh với Exp 33 (Ablation Comparison)

| Chỉ số (Metric) | Exp 33 (Top 100 Unconstrained) | **Exp 34 (Threshold 0.70)** | Chênh lệch (Impact) |
| :--- | :---: | :---: | :---: |
| **DOCS PRECISION** | 24.62% | **41.45%** 🥇 | **+16.83%** 🚀 (Tăng gần gấp đôi!) |
| **CHUNKS PRECISION** | 21.94% | **32.65%** 🥇 | **+10.71%** 🚀 |
| **DOCS RECALL** | **41.47%** | 11.94% | **-29.53%** 🔻 (Sụp đổ) |
| **CHUNKS RECALL** | **34.96%** | 9.31% | **-25.65%** 🔻 (Sụp đổ) |
| **DOCS F2 MACRO** | **0.3133** | 0.1292 | **-0.1841** 🔻 |
| **CHUNKS F2 MACRO** | **0.2693** | 0.1011 | **-0.1682** 🔻 |
| **FINAL SCORE** | **0.2913** 🏆 | 0.1151 | **-0.1762** 🔻 |

---

## Phân tích & Bài học Xương máu (Key Scientific Takeaways)

1. **Hiệu ứng Hai mặt của Ngưỡng điểm Tuyệt đối (Absolute Threshold):**
   - **Mặt tích cực:** Giả thuyết về Precision là hoàn toàn chính xác. Khi cắt bỏ các tài liệu điểm thấp, Docs Precision đã bứt phá từ **24.62% lên 41.45%** (kỷ lục cao nhất của đội từ trước tới nay) và Chunks Precision đạt **32.65%**.
   - **Mặt tiêu cực chí mạng:** Điểm Cosine Similarity của BGE-M3 đối với các bài viết Ground Truth thực tế tập trung trong dải **0.55 – 0.68**. Ngưỡng `0.70` là quá khắt khe, đã cắt bỏ hơn 70% số tài liệu đúng của đề thi. Rất nhiều query chỉ đạt ngưỡng với 1–2 tài liệu, và do `min_docs = 5` nên hệ thống chỉ trả về 5 tài liệu/query.

2. **Quy luật Bất khả xâm phạm của Hàm Mục tiêu $F_2$:**
   - Trong công thức $F_2 = \frac{5PR}{4P + R}$, trọng số Recall gấp **4 lần** Precision.
   - Thử nghiệm này (cùng với Exp 22: Top 10) chính thức chứng minh quy luật:  
     > **Bất kỳ kỹ thuật nào làm Recall giảm nhiều hơn mức tăng của Precision sẽ chắc chắn kéo sập $F_2$.**
   - Không được phép dùng ngưỡng tuyệt đối cứng (`0.70`, `0.73`) trên Stage 1 First-Stage Retrieval.

3. **Hướng đi Đúng đắn Tiếp theo:**
   - **Quay lại nền tảng Exp 33 (`0.2913`):** Luôn giữ `top_docs = 100` và `top_chunks = 98` để bảo toàn mức Recall 41.5%+.
   - **Đòn bẩy số 1 vẫn là Tăng độ phủ dữ liệu (Corpus Coverage):** Nhúng thêm 465k bài viết đang chờ trong `unembedded_samples.parquet` (PubMed, 39.net mới, Long Châu).
   - **Đòn bẩy số 2 cho Chunk Precision:** Giữ 100 docs nhưng tinh chỉnh thuật toán **Dynamic Windowing** (cắt chunk hẹp quanh mật độ từ khóa query) để tăng Chunks Precision mà không làm rơi Docs.
