[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 32: BGE-M3 Linear Hybrid (Bổ sung 200k Tài liệu Báo chí Y tế & Dược phẩm Mới) 🏆🌟🚀

- **Bối cảnh & Mục tiêu:**
  - Tiếp nối đà tăng trưởng của Exp 31, chúng ta tiến hành lập chỉ mục và hợp nhất **200.000 bài viết y tế mới** từ `data/indices/new_dataset` (`0-100k` và `100-200k`) vào kho chỉ mục chung `ViBioMIR_Consolidated_Index` (`data/indices/new_dataset/index`).
  - Nguồn dữ liệu mới bổ sung mật độ bài viết phong phú từ các trang báo sức khỏe và cổng y tế uy tín: `thanhnien.vn` (48.6k bài), `phunusuckhoe.giadinhonline.vn` (23.8k bài), `nhathuoclongchau.com.vn` (21.3k bài), `baohaiphong.vn` (15.8k), `baonghean.vn` (15.0k), `baodanang.vn` (14.2k), `giadinhonline.vn` (14.2k), `khoahocphothong.vn`...
  - Tổng quy mô chỉ mục tăng từ **462.882 docs (759.578 chunks)** lên **662.844 docs (1.049.370 chunks)**, chính thức vượt mốc 1 triệu chunks.
  - Chạy thực nghiệm với Module CLI mới được tái cấu trúc theo chuẩn OOP/SOLID (`python -m src.submit.cli`) kết hợp thuật toán Linear Hybrid ($1.0 \times \text{Dense} + 0.2 \times \text{Sparse}$), Candidate buffer 400.

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
  - **Quy mô Corpus:** 662.844 tài liệu y khoa hợp lệ, 1.049.370 chunks vector hóa (Dense 1024-d fp16 + Sparse CSR 250k).
  - **Phương pháp Fusion:** Linear Hybrid ($1.0 \times \text{Dense} + 0.2 \times \text{Sparse}$), Candidate buffer 400, top 100 docs & 98 chunks.

- **Kết quả Thực tế (Chấm trên hệ thống BTC):**
  - **`FINAL_SCORE: 0.2846`** 🏆 **(ALL-TIME HIGH - TĂNG VỌT +0.0267 / +10.35% SO VỚI EXP 31, TIỆM CẬN MỐC 0.29!)**
  - `DOCS_F2MACRO: 0.3069` (Kỷ lục mới, lần đầu vượt mốc 0.30! Tăng +0.0296 / +10.68%)
  - `CHUNKS_F2MACRO: 0.2624` (Kỷ lục mới, tăng +0.0239 / +10.02%)
  - `DOCS_PRECISION: 0.2409` (Kỷ lục mới, tăng +0.0213 / +9.70%)
  - `DOCS_RECALL: 0.4047` (Kỷ lục mới - **LẦN ĐẦU TIÊN VƯỢT NGƯỠNG 40%, ĐẠT 40.47%! Tăng +4.40% so với Exp 31!**)
  - `CHUNKS_PRECISION: 0.2139` (Kỷ lục mới, tăng +0.0173 / +8.80%)
  - `CHUNKS_RECALL: 0.3394` (Kỷ lục mới - **CHẠM 33.94%, tăng +3.53% so với Exp 31!**)

- **Bảng so sánh chuyên sâu (Exp 29 vs Exp 30 vs Exp 31 vs Exp 32):**

  | Chỉ số (Metric)      | Exp 29 (Buffer 400) | Exp 30 (BTC 1.19M Filter) | Exp 31 (+200k Vinmec) | Exp 32 (+200k Báo chí & Dược) | So với Exp 31  | So với Baseline BTC |
  | :------------------- | :-----------------: | :-----------------------: | :-------------------: | :---------------------------: | :------------: | :-----------------: |
  | **FINAL SCORE**      |       0.2424        |          0.2499           |        0.2579         |         **0.2846** 🏆         | **+0.0267** 🚀 |     **-0.0918**     |
  | **DOCS RECALL**      |   0.3382 (33.82%)   |      0.3447 (34.47%)      |    0.3607 (36.07%)    |    **0.4047 (40.47%)** 🥇     | **+4.40%** 📈  |    Top 1: 45.78%    |
  | **DOCS PRECISION**   |   0.2048 (20.48%)   |      0.2133 (21.33%)      |    0.2196 (21.96%)    |    **0.2409 (24.09%)** 🥇     | **+2.13%** 📈  |     **+3.10%**      |
  | **DOCS F2 MACRO**    |       0.2592        |          0.2667           |        0.2773         |         **0.3069** 🥇         | **+0.0296** 📈 |     **+0.0487**     |
  | **CHUNKS RECALL**    |   0.2880 (28.80%)   |      0.2958 (29.58%)      |    0.3041 (30.41%)    |    **0.3394 (33.94%)** 🥇     | **+3.53%** 📈  |     **+5.14%**      |
  | **CHUNKS PRECISION** |   0.1853 (18.53%)   |      0.1933 (19.33%)      |    0.1966 (19.66%)    |    **0.2139 (21.39%)** 🥇     | **+1.73%** 📈  |     **+2.71%**      |
  | **CHUNKS F2 MACRO**  |       0.2255        |          0.2332           |        0.2385         |         **0.2624** 🥇         | **+0.0239** 📈 |     **+0.0369**     |

- **Phân tích Chuyên sâu (Key Insights & Động lực Tăng trưởng):**
  1. **Bước nhảy vọt lịch sử về Document Recall (Bứt phá qua mốc 40%):**
     - Docs Recall tăng vọt từ 36.07% lên **40.47%** (+4.40%). Đây là mức tăng trưởng theo lượt nộp ấn tượng nhất từ trước đến nay.
     - Khoảng cách Docs Recall so với Top 1 Leaderboard ("Quýt đây đứng sợ" - 45.78%) giờ đây chỉ còn vỏn vẹn **5.31%**!
  2. **Tăng trưởng toàn diện mà không bị pha loãng (Zero Dilution):**
     - Cả Docs Precision (24.09%) lẫn Chunks Precision (21.39%) đều đồng loạt lập kỷ lục mới, chứng minh các tài liệu báo chí y tế và dược phẩm thêm vào có độ tương thích từ khóa và ngữ nghĩa cực kỳ cao với bộ câu hỏi test.
     - Pipeline CLI mới và cơ chế deduplication đã giữ cho candidate buffer 400 hoạt động tối ưu, không để lọt rác vào top 100.
  3. **Chunks Recall và F2 bứt phá ngoạn mục:**
     - Chunks Recall nhảy từ 30.41% lên **33.94%** (+3.53%), đẩy Chunks F2 lên **0.2624**.
     - Ngưỡng cắt đoạn văn ngữ cảnh tự nhiên 2500 ký tự hoạt động hiệu quả khi kho văn bản gốc bao phủ đúng bài viết ground truth.
  4. **Lộ trình công phá Top 1 Leaderboard:**
     - Kho tài liệu quốc tế **PubMed (239.741 bài)** vừa hoàn tất cào xong và đang nằm sẵn trong `data/unembedded_samples.parquet`.
     - Cùng với ~59k URLs còn lại đang được cào tiếp ở background, việc nhúng nốt toàn bộ kho dữ liệu này hứa hẹn sẽ đưa Docs Recall vượt qua mốc **45 - 48%**, mở toang cánh cửa vươn lên Top 1 giải đấu!

---

[← Exp 31](exp31_bge_m3_vinmec_200k.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md)
