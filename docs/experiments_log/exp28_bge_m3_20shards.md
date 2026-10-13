[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 28: BGE-M3 Linear Hybrid (Bổ sung Tier 1 1000-1100k: 120ask.com - Toàn diện 20 Shards ~2.0M Docs) 🚀🎯

- **Mục tiêu:** Mở rộng quy mô chỉ mục lên **trọn vẹn 20 Shards (2.0 triệu tài liệu)** bằng việc bổ sung khối `data/indices/tier 1/1000-1100k/index` (chứa 99,766 tài liệu hỏi đáp bác sĩ chuyên sâu từ `www.120ask.com`). Đánh giá sự tương tác giữa độ chính xác (Precision) và độ bao phủ (Recall) khi kho dữ liệu đạt ngưỡng 2 triệu docs.
- **Cấu hình Chi tiết:**
  - **Lệnh thực thi:**
    ```powershell
    python scripts/run_submission.py `
      --mode hybrid `
      --fusion linear `
      --dense_weight 1.0 `
      --sparse_weight 0.2 `
      --top_docs 100 `
      --top_chunks 98 `
      --output submission_bgem3_hybrid_w02_20shards.json
    ```
  - **Cải tiến kiến trúc mã nguồn (Memory Optimization):**
    - Chuyển đổi phép tính ma trận thưa từ $Q \cdot M^T$ sang $(M \cdot Q^T)^T$ để tránh cấp phát bản sao transpose của $M$ (nguyên nhân gây `ArrayMemoryError` trước đó).
    - Tự động prune danh sách ứng viên (giữ top 150) và gọi `gc.collect()` sau mỗi shard, giúp RAM duy trì ổn định ở mức an toàn < 2.5 GB trong suốt quá trình xử lý 20 shards.
  - **Dữ liệu quét:** Toàn bộ **20 khối chỉ mục (shards)** trong `data/indices` (14 khối Tier 1: `0-100k` $\to$ `1400k` và 6 khối Tier 2: `0-100k` $\to$ `600k`).
  - **Thời gian tìm kiếm:** **540.88 giây (~9 phút)**.
  - **File nén nộp bài:** [`submission_bgem3_hybrid_w02_20shards.zip`](file:///d:/CODE%20PLAYGROUND/Projects/Competitions/R2AI-Stage-3-2026/submission_bgem3_hybrid_w02_20shards.zip) (dung lượng **92.24 MB** đạt chuẩn an toàn `< 100 MB`).
- **Kết quả Thực tế (Chấm trên hệ thống BTC):**
  - **`FINAL_SCORE: 0.2423`**
  - `DOCS_F2MACRO: 0.2582` | `DOCS_PRECISION: 0.2099` (20.99% - **Kỷ lục Precision mới** 🥇) | `DOCS_RECALL: 0.3337` (33.37%)
  - `CHUNKS_F2MACRO: 0.2265` | `CHUNKS_PRECISION: 0.1868` | `CHUNKS_RECALL: 0.2888` (28.88%)

- **Bảng so sánh chuyên sâu (Exp 26 vs Exp 27 vs Exp 28):**

  | Chỉ số (Metric)      | Exp 26 (14 Shards) | Exp 27 (19 Shards: +1300-1400k) | Exp 28 (20 Shards: +1000-1100k) | So với Exp 27 |
  | :------------------- | :----------------: | :-----------------------------: | :-----------------------------: | :-----------: |
  | **FINAL SCORE**      |       0.2146       |          **0.2441** 🏆          |             0.2423              |    -0.0018    |
  | **DOCS RECALL**      |  0.2904 (29.04%)   |     **0.3395 (33.95%)** 🥇      |         0.3337 (33.37%)         |    -0.58%     |
  | **DOCS PRECISION**   |  0.1815 (18.15%)   |         0.2059 (20.59%)         |     **0.2099 (20.99%)** 🥇      | **+0.40%** 📈 |
  | **DOCS F2 MACRO**    |       0.2252       |          **0.2604** 🥇          |             0.2582              |    -0.0022    |
  | **CHUNKS RECALL**    |  0.2578 (25.78%)   |     **0.2913 (29.13%)** 🥇      |         0.2888 (28.88%)         |    -0.25%     |
  | **CHUNKS PRECISION** |  0.1714 (17.14%)   |     **0.1875 (18.75%)** 🥇      |         0.1868 (18.68%)         |    -0.07%     |
  | **CHUNKS F2 MACRO**  |       0.2041       |          **0.2278** 🥇          |             0.2265              |    -0.0013    |

- **Phân tích Chuyên sâu (Key Insights & Trade-off Analysis):**
  1. **Kỷ lục mới về Document Precision (20.99%):**
     - Shard `1000-1100k` chứa 100% là các bài viết hỏi đáp từ `120ask.com`. Độ liên quan câu hỏi - câu trả lời của nguồn này rất sắc nét, giúp đẩy tỷ lệ tài liệu trúng đích trong Top 100 lên mốc cao nhất từ trước đến nay (gần 21%).
  2. **Hiệu ứng cạnh tranh vị trí Top 100 Cut-off (Slot Competition):**
     - Giới hạn cứng của hệ thống là `top_docs = 100`. Khi nạp thêm gần 100,000 bài viết Q&A từ `120ask.com`, một số bài viết tiếng Trung này có điểm tương đồng lexical/dense cao đã chiếm chỗ trong Top 100, vô tình đẩy một vài tài liệu Ground Truth tiếng Việt (từ Long Châu / YouMed) xuống vị trí ngoài Top 100 (vị trí 101–150).
     - Do công thức tính $F_2$-Macro ưu tiên Recall gấp đôi so với Precision ($\beta = 2$), nên việc Recall giảm 0.58% làm tổng điểm $F_2$ hạ nhẹ 0.0018 điểm dù Precision tăng.
  3. **Chiến lược tối ưu hóa tiếp theo:**
     - **Tăng cường nạp nguồn tiếng Việt (Tier 1 nội địa):** Các nguồn dược lý tiếng Việt như `nhathuoclongchau` hay `youmed` mang lại Ground Truth trực tiếp mà không bị cạnh tranh lệch ngôn ngữ.
     - **Điều chỉnh trọng số sparse tiếng Trung (`--zh_weight`):** Cân nhắc giảm nhẹ trọng số sparse cho tiếng Trung (ví dụ `--zh_weight 0.8` hoặc `0.7`) để các tài liệu tiếng Việt có ưu thế điểm số hơn trong top 100 cut-off.

---

---
[← Exp 27](exp27_bge_m3_19shards.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 29 →](exp29_bge_m3_dedup_buffer400.md)
