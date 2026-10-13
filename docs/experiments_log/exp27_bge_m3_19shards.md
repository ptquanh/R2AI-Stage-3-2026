[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 27: BGE-M3 Linear Hybrid (Bổ sung Tier 1 1300-1400k: Long Châu, YouMed, Vinmec, ask.39) 🚀🏆🔥

- **Mục tiêu:** Kiểm chứng tác động của việc bổ sung khối chỉ mục mới `data/indices/tier 1/1300-1400k/index` (chứa hơn 50.000 tài liệu y khoa chất lượng cao: Long Châu, YouMed, Sức Khỏe Cộng Đồng, ask.39.net, YouLai, Vinmec, HelloBacsi,...). Đánh giá bước nhảy vọt toàn diện về Recall và Precision khi mở rộng lên 19 Shards (~1.8 triệu docs).
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
      --output submission_bgem3_hybrid_w02_19shards.json
    ```
  - **Mô hình:** `BAAI/bge-m3` (FP16) kết hợp song ngữ Việt - Trung (`query_zh`) với Max-pooling Lexical Weights.
  - **Dữ liệu quét:** Toàn bộ **19 khối chỉ mục (shards)** trong `data/indices` (13 khối Tier 1 và 6 khối Tier 2).
  - **File nén nộp bài:** [`submission_bgem3_hybrid_w02_19shards.zip`](file:///d:/CODE%20PLAYGROUND/Projects/Competitions/R2AI-Stage-3-2026/submission_bgem3_hybrid_w02_19shards.zip) (dung lượng **92.85 MB** đạt chuẩn an toàn `< 100 MB`).
- **Kết quả Thực tế (Chấm trên hệ thống BTC):**
  - **`FINAL_SCORE: 0.2441`** 🥇 (Thiết lập kỷ lục mới ALL-TIME HIGH, bứt phá ngoạn mục từ 0.2146 của Exp 26)
  - `DOCS_F2MACRO: 0.2604` | `DOCS_PRECISION: 0.2059` | `DOCS_RECALL: 0.3395` (33.95%)
  - `CHUNKS_F2MACRO: 0.2278` | `CHUNKS_PRECISION: 0.1875` | `CHUNKS_RECALL: 0.2913` (29.13%)

- **Bảng so sánh bước nhảy vọt (Exp 25 vs Exp 26 vs Exp 27):**

  | Chỉ số (Metric)      | Exp 25 (14 Shards) | Exp 26 (+ Long Châu thô) | Exp 27 (+ Tier 1 1300-1400k: 19 Shards) |   Tăng so với Exp 26    |
  | :------------------- | :----------------: | :----------------------: | :-------------------------------------: | :---------------------: |
  | **FINAL SCORE**      |       0.2111       |          0.2146          |              **0.2441** 🏆              | **+0.0295 (+13.7%)** 🚀 |
  | **DOCS RECALL**      |  0.2862 (28.62%)   |     0.2904 (29.04%)      |         **0.3395 (33.95%)** 🥇          |      **+4.91%** 📈      |
  | **DOCS PRECISION**   |  0.1791 (17.91%)   |     0.1815 (18.15%)      |         **0.2059 (20.59%)** 🥇          |      **+2.44%** 📈      |
  | **DOCS F2 MACRO**    |       0.2221       |          0.2252          |              **0.2604** 🥇              | **+0.0352 (+15.6%)** 🚀 |
  | **CHUNKS RECALL**    |  0.2527 (25.27%)   |     0.2578 (25.78%)      |         **0.2913 (29.13%)** 🥇          |      **+3.35%** 📈      |
  | **CHUNKS PRECISION** |  0.1683 (16.83%)   |     0.1714 (17.14%)      |         **0.1875 (18.75%)** 🥇          |      **+1.61%** 📈      |
  | **CHUNKS F2 MACRO**  |       0.2002       |          0.2041          |              **0.2278** 🥇              | **+0.0237 (+11.6%)** 🚀 |

- **Phân tích Chuyên sâu (Key Insights):**
  1. **Khẳng định tuyệt đối về "Chất lượng vàng của Corpus Tier 1 nội địa & chuyên sâu":**
     - Khối `tier 1/1300-1400k` chứa các nguồn bách khoa dược lý & hỏi đáp lâm sàng đầu ngành như: `nhathuoclongchau.com.vn` (7.1k docs), `tiemchunglongchau.com.vn` (3.5k docs), `youmed.vn` (1.6k docs), `suckhoecongdongonline.vn` (1.2k docs), và `ask.39.net` (991 docs).
     - Việc đưa các nguồn này vào đã giải quyết dứt điểm điểm mù của hệ thống đối với các câu hỏi thực chứng bằng tiếng Việt: Cả **Docs Recall** vọt từ 29% lên gần **34%** và **Docs Precision** vượt ngưỡng 20%.
  2. **Tương quan đồng thuận giữa Recall và Precision:**
     - Thông thường khi thêm nhiều tài liệu (kho dữ liệu lớn hơn), Precision dễ bị pha loãng (giảm). Nhưng ở Exp 27, **cả Precision và Recall đều tăng mạnh đồng thời**, chứng minh các tài liệu mới trúng thẳng vào Ground Truth của đề thi, đẩy văng các tài liệu nhiễu ra khỏi top 100.
  3. **Định hướng chiến lược tiếp theo:**
     - Tiếp tục index các phần cào được mới của Long Châu, YouMed và `ask.39.net`.
     - Hiện tại Docs Recall đã tiệm cận 34%, Chunks Recall đạt 29.13%. Nếu tiếp tục bổ sung thêm ~100k-200k docs từ cụm `ask.39.net` và `nhathuoclongchau`, mục tiêu **FINAL_SCORE > 0.27 - 0.30** là hoàn toàn khả thi!

---

---
[← Exp 26](exp26_bge_m3_nhathuoclongchau.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 28 →](exp28_bge_m3_20shards.md)
