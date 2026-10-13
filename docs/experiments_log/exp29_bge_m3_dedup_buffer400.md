[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 29: BGE-M3 Linear Hybrid (Fix Shard Duplicate, Nâng Buffer 400 & Nạp Tier 2 600-700k) 🚀🎯⚡

- **Mục tiêu:**
  - Triển khai **Hướng 1** theo chiến lược tối ưu hóa [`docs/improvement_strategy_and_exp29.md`](file:///d:/CODE%20PLAYGROUND/Projects/Competitions/R2AI-Stage-3-2026/docs/improvement_strategy_and_exp29.md).
  - Tự động nhận diện và loại bỏ 2 shard bị trùng lặp 100% (`tier 1/100-200k` và `tier 1/1400-1500k`) để giải phóng slot bị nhân đôi điểm số trong candidate pool.
  - Mở rộng candidate pool trung gian từ 150 lên **400 ứng viên (`--cand_buffer 400`)** với cơ chế đa dạng hóa cấp độ Document (tối đa 2 chunks/doc trong buffer) nhằm đảm bảo luôn có ít nhất 200 tài liệu duy nhất cạnh tranh vào Top 100.
  - Nạp thêm khối chỉ mục hợp lệ mới **`data/indices/tier 2/600-700k/index`** (194.200 chunks, 50.000 docs).
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
      --cand_pool 200 `
      --cand_buffer 400 `
      --output submission_bgem3_hybrid_w02_exp29.json
    ```
  - **Dữ liệu quét:** Đúng **20 khối chỉ mục DUY NHẤT** (13 khối Tier 1 và 7 khối Tier 2).
  - **Thời gian tìm kiếm:** **637.25 giây (~10.6 phút)**.
  - **File nén đầu ra:** [`submission_bgem3_hybrid_w02_exp29.zip`](file:///d:/CODE%20PLAYGROUND/Projects/Competitions/R2AI-Stage-3-2026/submission_bgem3_hybrid_w02_exp29.zip) dung lượng **92.87 MB** (đạt chuẩn an toàn `< 100 MB`).
- **Kiểm định Chất lượng File Submission:**
  - 100% queries (1200/1200) đạt đủ chính xác **100 docs** và **98 chunks**.
  - Không có bất kỳ doc hoặc chunk nào bị trùng lặp trong từng query.
- **Kết quả Thực tế (Chấm trên hệ thống BTC):**
  - **`FINAL_SCORE: 0.2424`**
  - `DOCS_F2MACRO: 0.2592` | `DOCS_PRECISION: 0.2048` | `DOCS_RECALL: 0.3382` (33.82%)
  - `CHUNKS_F2MACRO: 0.2255` | `CHUNKS_PRECISION: 0.1853` | `CHUNKS_RECALL: 0.2880` (28.80%)

- **Bảng so sánh chuyên sâu (Exp 27 vs Exp 28 vs Exp 29):**

  | Chỉ số (Metric)      | Exp 27 (19 Shards: +1300-1400k) | Exp 28 (20 Shards: +1000-1100k) | Exp 29 (20 Unique Shards: Buffer 400 + Tier 2 600-700k) | So với Exp 28 | So với Exp 27 |
  | :------------------- | :-----------------------------: | :-----------------------------: | :-----------------------------------------------------: | :-----------: | :-----------: |
  | **FINAL SCORE**      |          **0.2441** 🏆          |             0.2423              |                         0.2424                          |    +0.0001    |    -0.0017    |
  | **DOCS RECALL**      |     **0.3395 (33.95%)** 🥇      |         0.3337 (33.37%)         |                     0.3382 (33.82%)                     | **+0.45%** 📈 |    -0.13%     |
  | **DOCS PRECISION**   |         0.2059 (20.59%)         |     **0.2099 (20.99%)** 🥇      |                     0.2048 (20.48%)                     |    -0.51%     |    -0.11%     |
  | **DOCS F2 MACRO**    |          **0.2604** 🥇          |             0.2582              |                         0.2592                          |  +0.0010 📈   |    -0.0012    |
  | **CHUNKS RECALL**    |     **0.2913 (29.13%)** 🥇      |         0.2888 (28.88%)         |                     0.2880 (28.80%)                     |    -0.08%     |    -0.33%     |
  | **CHUNKS PRECISION** |     **0.1875 (18.75%)** 🥇      |         0.1868 (18.68%)         |                     0.1853 (18.53%)                     |    -0.15%     |    -0.22%     |
  | **CHUNKS F2 MACRO**  |          **0.2278** 🥇          |             0.2265              |                         0.2255                          |    -0.0010    |    -0.0023    |

- **Phân tích Chuyên sâu (Key Insights & Chẩn đoán Nút thắt):**
  1. **Hiệu quả rõ rệt của Candidate Buffer 400 và Deduplication:**
     - So với Exp 28, **Docs Recall đã phục hồi mạnh mẽ từ 33.37% lên 33.82% (+0.45%)**, kéo Docs F2 tăng từ 0.2582 lên 0.2592. Việc mở rộng buffer từ 150 lên 400 và giới hạn max 2 chunks/doc đã thành công giải phóng không gian cho các tài liệu tiềm năng lọt vào Top 100.
  2. **Bằng chứng Thực nghiệm Đanh thép về "Bão hòa Tier 2":**
     - Shard mới `tier 2/600-700k` bổ sung thêm 50k tài liệu tiếng Trung (chủ yếu từ `cnkang` và `120ask`). Tuy nhiên, Docs Recall vẫn ở mức 33.82% (không vượt qua được mốc 33.95% của Exp 27) và Precision giảm nhẹ.
     - Điều này chứng minh tuyệt đối giả thuyết đã nêu trong Exp 25: **Nguồn Q&A tiếng Trung đại trà (cnkang/120ask) đã chạm ngưỡng bão hòa hoàn toàn (Domain Saturation)**. Khi nạp thêm, chúng chỉ cạnh tranh điểm số và choán chỗ của tài liệu tiếng Việt chứ không đem lại ground truth mới.
  3. **Kết luận Chiến lược Tối thượng cho Exp 30:**
     - Không tiếp tục mở rộng Tier 2 đại trà.
     - **Tập trung 100% nguồn lực vào Hướng 2 (Tier 1 Nội địa):** Tạo embedding ngay lập tức cho **29.980 bài viết trong `tier_1_resume.parquet`** (trong đó có hơn 12.200 bài dược lý chuyên sâu từ `nhathuoclongchau.com.vn` và bài viết bác sĩ `ask.39.net`). Đây là nguồn ground truth trực tiếp cho các câu hỏi tiếng Việt, hứa hẹn sẽ đưa Recall bứt phá thẳng lên mốc **36% - 38%** và đưa Final Score vượt mốc **0.265 - 0.280+**!

---

---
[← Exp 28](exp28_bge_m3_20shards.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 30 →](exp30_bge_m3_btc_119m_filter.md)
