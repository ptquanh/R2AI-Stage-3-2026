[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 30: BGE-M3 Linear Hybrid (Áp dụng Bộ lọc Danh mục 1.19M URLs của BTC) 🏆🌟🚀

- **Bối cảnh & Mục tiêu:**
  - BTC công bố danh sách URL chính thức rút gọn còn **1.194.469 URLs** (`links_corpus_vi_en_zh.parquet`), loại bỏ hơn 2.5 triệu URL tiếng Trung đại trà và bổ sung 240.000 bài báo PubMed (tiếng Anh).
  - Phân tích của chúng ta phát hiện: trong 20 shards index hiện có (~1.98M tài liệu), có tới **78.0% (1.545.286 tài liệu)** là các bài viết tiếng Trung đã bị BTC loại khỏi cuộc thi. Các bài viết này chiếm chỗ trong Top 100 và 100% trở thành False Positives.
  - Mục tiêu: Tích hợp bộ lọc `--btc_links_file` trực tiếp vào pipeline tìm kiếm `run_submission.py`, loại bỏ hoàn toàn các tài liệu ngoài danh mục ở cấp độ shard (`chunks_map` và `texts_map`), đảm bảo 100% tài liệu trả về thuộc tập 1.19M của BTC.
- **Cấu hình Chi tiết:**
  - **Lệnh thực thi:**
    ```powershell
    python scripts/run_submission.py `
      --query_file data/raw/btc_provided/query.parquet `
      --mode hybrid `
      --fusion linear `
      --dense_weight 1.0 `
      --sparse_weight 0.2 `
      --top_docs 100 `
      --top_chunks 98 `
      --cand_pool 200 `
      --cand_buffer 400 `
      --btc_links_file data/raw/btc_provided/links_corpus_vi_en_zh.parquet `
      --output submission_bgem3_top100.json
    ```
  - **Bộ lọc Corpus:** Lọc tự động đối soát với 1.194.469 ID hợp lệ. Giữ lại **436.756 tài liệu hợp lệ**, loại bỏ 1.545.286 tài liệu rác.
  - **Dữ liệu quét:** 20 khối chỉ mục DUY NHẤT.
  - **File nén đầu ra:** [`submission_bgem3_top100.zip`](file:///d:/CODE%20PLAYGROUND/Projects/Competitions/R2AI-Stage-3-2026/submission_bgem3_top100.zip) dung lượng **95.03 MB** (đạt chuẩn an toàn `< 100 MB`).
- **Kết quả Thực tế (Chấm trên hệ thống BTC):**
  - **`FINAL_SCORE: 0.2499`** 🏆 **(ALL-TIME HIGH - TĂNG +0.0075 / +3.1% SO VỚI EXP 29)**
  - `DOCS_F2MACRO: 0.2667` (Kỷ lục mới, tăng +0.0075)
  - `CHUNKS_F2MACRO: 0.2332` (Kỷ lục mới, tăng +0.0077)
  - `DOCS_PRECISION: 0.2133` (Kỷ lục mới, tăng +0.0085)
  - `DOCS_RECALL: 0.3447` (Kỷ lục mới, tăng +0.0065 - đạt 34.47%)
  - `CHUNKS_PRECISION: 0.1933` (Kỷ lục mới, tăng +0.0080)
  - `CHUNKS_RECALL: 0.2958` (Kỷ lục mới, tăng +0.0078 - đạt 29.58%)

- **Bảng so sánh chuyên sâu (Exp 27 vs Exp 28 vs Exp 29 vs Exp 30):**

  | Chỉ số (Metric)      | Exp 27 (19 Shards) | Exp 28 (20 Shards) | Exp 29 (Buffer 400) | Exp 30 (BTC 1.19M Filter) | So với Exp 29  | So với Exp 27  |
  | :------------------- | :----------------: | :----------------: | :-----------------: | :-----------------------: | :------------: | :------------: |
  | **FINAL SCORE**      |       0.2441       |       0.2423       |       0.2424        |       **0.2499** 🏆       | **+0.0075** 🚀 | **+0.0058** 🚀 |
  | **DOCS RECALL**      |  0.3395 (33.95%)   |  0.3337 (33.37%)   |   0.3382 (33.82%)   |  **0.3447 (34.47%)** 🥇   | **+0.65%** 📈  | **+0.52%** 📈  |
  | **DOCS PRECISION**   |  0.2059 (20.59%)   |  0.2099 (20.99%)   |   0.2048 (20.48%)   |  **0.2133 (21.33%)** 🥇   | **+0.85%** 📈  | **+0.74%** 📈  |
  | **DOCS F2 MACRO**    |       0.2604       |       0.2582       |       0.2592        |       **0.2667** 🥇       | **+0.0075** 📈 | **+0.0063** 📈 |
  | **CHUNKS RECALL**    |  0.2913 (29.13%)   |  0.2888 (28.88%)   |   0.2880 (28.80%)   |  **0.2958 (29.58%)** 🥇   | **+0.78%** 📈  | **+0.45%** 📈  |
  | **CHUNKS PRECISION** |  0.1875 (18.75%)   |  0.1868 (18.68%)   |   0.1853 (18.53%)   |  **0.1933 (19.33%)** 🥇   | **+0.80%** 📈  | **+0.58%** 📈  |
  | **CHUNKS F2 MACRO**  |       0.2278       |       0.2265       |       0.2255        |       **0.2332** 🥇       | **+0.0077** 📈 | **+0.0054** 📈 |

- **Phân tích Chuyên sâu (Key Insights & Bước ngoặt Kỹ thuật):**
  1. **Đồng loạt bứt phá trên CẢ 6 CHỈ SỐ:**
     - Đây là thực nghiệm ĐẦU TIÊN trong toàn bộ cuộc thi mà **tất cả 6 chỉ số (Docs P, R, F2 và Chunks P, R, F2) đều đồng loạt thiết lập đỉnh cao nhất mọi thời đại**.
     - Không có hiện tượng "được cái này mất cái kia" (trade-off) như các đợt trước.
  2. **Lý giải hiện tượng RECALL TĂNG khi LOẠI BỎ TÀI LIỆU:**
     - Trước đây, 1.54M tài liệu tiếng Trung ngoài lề có điểm similarity cao ảo (do câu hỏi chung chung) đã chiếm chỗ trong Top 100, đẩy các tài liệu tiếng Việt / tiếng Trung thực sự liên quan rớt xuống hạng 101+.
     - Khi lọc sạch 1.54M tài liệu này, các tài liệu Ground Truth đích thực được đưa lên Top 100, giúp **Docs Recall tăng từ 33.82% lên 34.47%** và **Chunks Recall tăng từ 28.80% lên 29.58%**.
  3. **Lộ trình Tiếp tục Đẩy Điểm Số Lên 0.28 - 0.32+:**
     - **Ưu tiên 1 (Dynamic Thresholding - Ngưỡng 0.70 / 0.73 của BTC):** Cắt bỏ các tài liệu điểm thấp dưới 0.73 để giảm false positives, đẩy mạnh Precision từ 21.3% lên 30-40%+.
     - **Ưu tiên 2 (Lập chỉ mục 367.811 bài viết đã cào còn lại):** Nhúng ngay 30.474 bài viết Tier 1 Resume (21.3k Long Châu + 8.9k ask.39) và các bài viết Thanh Niên, Lao Động đã cào sẵn để nâng Docs Recall lên 38-42%+.

---

---
[← Exp 29](exp29_bge_m3_dedup_buffer400.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 31 →](exp31_bge_m3_vinmec_200k.md)
