[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 31: BGE-M3 Linear Hybrid (Bổ sung 200k Tài liệu Y khoa Nội địa Vinmec) 🏆🌟🚀

- **Bối cảnh & Mục tiêu:**
  - Sau thành công của Exp 30 với bộ lọc BTC 1.19M URLs (Final Score 0.2499), chúng ta tiến hành lập chỉ mục cho **200.000 bài viết y khoa chất lượng cao từ Vinmec** (chia làm 2 khối: `0-100k` với 99.962 docs và `100-200k` với 100.000 docs).
  - Tổng quy mô chỉ mục tăng trưởng từ **462.882 docs (759.578 chunks)** lên **662.844 docs (1.049.370 chunks)**, chính thức vượt mốc 1 triệu chunks.
  - Mục tiêu: Kiểm chứng sức mạnh của nguồn dữ liệu bệnh học, chẩn đoán và điều trị tiếng Việt nội địa (Vinmec) trong việc bao phủ các câu hỏi lâm sàng tiếng Việt của BTC.
- **Cấu hình Chi tiết:**
  - **Lệnh thực thi:**
    ```powershell
    python -m src.submit.cli `
      --query_file data/raw/btc_provided/query.parquet `
      --mode hybrid `
      --fusion linear `
      --dense_weight 1.0 `
      --sparse_weight 0.2 `
      --top_docs 100 `
      --top_chunks 98 `
      --cand_pool 200 `
      --cand_buffer 400 `
      --index_base data/indices/new_dataset `
      --btc_links_file data/raw/btc_provided/links_corpus_vi_en_zh.parquet `
      --output submission_bgem3_top100.json
    ```
  - **Quy mô Corpus:** 662.844 tài liệu hợp lệ, 1.049.370 chunks vector hóa (Dense 1024-d fp16 + Sparse CSR 250k).
  - **Phương pháp Fusion:** Linear Hybrid ($1.0 \times \text{Dense} + 0.2 \times \text{Sparse}$), Candidate buffer 400.
- **Kết quả Thực tế (Chấm trên hệ thống BTC):**
  - **`FINAL_SCORE: 0.2579`** 🏆 **(ALL-TIME HIGH - TĂNG +0.0080 / +3.2% SO VỚI EXP 30, TIỆM CẬN MỐC 0.26)**
  - `DOCS_F2MACRO: 0.2773` (Kỷ lục mới, tăng +0.0106 / +4.0%)
  - `CHUNKS_F2MACRO: 0.2385` (Kỷ lục mới, tăng +0.0053)
  - `DOCS_PRECISION: 0.2196` (Kỷ lục mới, tăng +0.0063 / +3.0%)
  - `DOCS_RECALL: 0.3607` (Kỷ lục mới, tăng +0.0160 - **bứt phá ngoạn mục lên 36.07%**)
  - `CHUNKS_PRECISION: 0.1966` (Kỷ lục mới, tăng +0.0033)
  - `CHUNKS_RECALL: 0.3041` (Kỷ lục mới, tăng +0.0083 - **lần đầu tiên Chunks Recall vượt mốc 30%**)

- **Bảng so sánh chuyên sâu (Exp 28 vs Exp 29 vs Exp 30 vs Exp 31):**

  | Chỉ số (Metric)      | Exp 28 (20 Shards) | Exp 29 (Buffer 400) | Exp 30 (BTC 1.19M Filter) | Exp 31 (+200k Docs Vinmec) | So với Exp 30  | So với Exp 29  |
  | :------------------- | :----------------: | :-----------------: | :-----------------------: | :------------------------: | :------------: | :------------: |
  | **FINAL SCORE**      |       0.2423       |       0.2424        |          0.2499           |       **0.2579** 🏆        | **+0.0080** 🚀 | **+0.0155** 🚀 |
  | **DOCS RECALL**      |  0.3337 (33.37%)   |   0.3382 (33.82%)   |      0.3447 (34.47%)      |   **0.3607 (36.07%)** 🥇   | **+1.60%** 📈  | **+2.25%** 📈  |
  | **DOCS PRECISION**   |  0.2099 (20.99%)   |   0.2048 (20.48%)   |      0.2133 (21.33%)      |   **0.2196 (21.96%)** 🥇   | **+0.63%** 📈  | **+1.48%** 📈  |
  | **DOCS F2 MACRO**    |       0.2582       |       0.2592        |          0.2667           |       **0.2773** 🥇        | **+0.0106** 📈 | **+0.0181** 📈 |
  | **CHUNKS RECALL**    |  0.2888 (28.88%)   |   0.2880 (28.80%)   |      0.2958 (29.58%)      |   **0.3041 (30.41%)** 🥇   | **+0.83%** 📈  | **+1.61%** 📈  |
  | **CHUNKS PRECISION** |  0.1868 (18.68%)   |   0.1853 (18.53%)   |      0.1933 (19.33%)      |   **0.1966 (19.66%)** 🥇   | **+0.33%** 📈  | **+1.13%** 📈  |
  | **CHUNKS F2 MACRO**  |       0.2265       |       0.2255        |          0.2332           |       **0.2385** 🥇        | **+0.0053** 📈 | **+0.0130** 📈 |

- **Phân tích Chuyên sâu (Key Insights & Động lực Tăng trưởng):**
  1. **Động cơ tăng trưởng mạnh nhất đến từ Tài liệu Nội địa (Vinmec):**
     - Docs Recall tăng vọt **+1.60% (từ 34.47% lên 36.07%)**, chứng minh tài liệu Vinmec chứa mật độ ground truth cực kỳ cao cho các câu truy vấn thực tế.
     - Đồng thời, Docs Precision cũng tăng từ **21.33% lên 21.96%**, chứng minh tài liệu mới không hề gây loãng (noise) mà trực tiếp gia tăng độ chính xác của Top 100.
  2. **Chunks Recall lần đầu vượt ngưỡng 30% (30.41%):**
     - Trước đây, Chunks Recall luôn giậm chân tại chỗ ở mức 28.8% - 29.5%. Việc bổ sung các bài viết giải phẫu và điều trị của Vinmec đã giúp hệ thống tìm trúng đoạn văn đích, kéo Chunks F2 lên **0.2385**.
  3. **Bước đệm hoàn hảo để công phá mốc 0.28 - 0.30+:**
     - Hiện tại chúng ta vừa hoàn thành cào thêm **239.741 bài báo y khoa quốc tế PubMed** (đã đồng bộ vào `unembedded_samples.parquet`, nâng tổng kho sẵn sàng lên **1.08 triệu tài liệu**).
     - Khi tiến hành nhúng tiếp PubMed và các tài liệu còn lại, Docs Recall được dự báo sẽ vượt ngưỡng **40 - 43%**, đưa Final Score bứt phá mạnh mẽ về đích!

---

[← Exp 30](exp30_bge_m3_btc_119m_filter.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 32 →](exp32_bge_m3_200k_new_dataset.md)
