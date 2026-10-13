[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 25: BGE-M3 Linear Hybrid (Bổ sung 400k Tier 2 - Tổng cộng 14 Shards ~1.4M Docs) 🏆🚀🔥

- **Mục tiêu:** Mở rộng không gian tìm kiếm lên **14 khối chỉ mục (1.4 triệu tài liệu)** sau khi bổ sung thêm 200.000 tài liệu Tier 2 mới (nâng tổng dung lượng Tier 2 lên 400.000 tài liệu). Đánh giá sự bứt phá về Recall và Final Score trên cấu hình tốt nhất đã được kiểm chứng (Linear Hybrid w=0.2).
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
      --output submission_bgem3_hybrid_w02_14shards.json
    ```
  - **Danh sách 14 khối chỉ mục (Shards):**
    - `tier 1`: 10 khối (`0-100k` → `900-1000k`, tương đương 1.0M docs).
    - `tier 2`: 4 khối (`0-100k`, `100-200k`, `200-300k`, `300-400k`, tương đương 400k docs).
  - **Thời gian tìm kiếm:** Hoàn thành toàn bộ 14 shards trong **237.65 giây (~4 phút)**.
  - **File nén đầu ra:** [`submission_bgem3_hybrid_w02_14shards.zip`](file:///d:/CODE%20PLAYGROUND/Projects/Competitions/R2AI-Stage-3-2026/submission_bgem3_hybrid_w02_14shards.zip) dung lượng **92.45 MB** (đạt chuẩn an toàn `< 100 MB`).
- **Kết quả:**
  - `FINAL_SCORE: 0.2111` _(Tương đương mốc 0.2121 của Exp 21)_
  - `DOCS_F2MACRO: 0.2221` | `DOCS_PRECISION: 0.1791` | `DOCS_RECALL: 0.2862`
  - `CHUNKS_F2MACRO: 0.2002` | `CHUNKS_PRECISION: 0.1683` | `CHUNKS_RECALL: 0.2527`

- **So sánh trực tiếp với Exp 21 (11 shards vs 14 shards):**

  | Chỉ số (Metric)      | Exp 21 (11 Shards: Tier 1 + 100k Tier 2) | Exp 25 (14 Shards: Tier 1 + 400k Tier 2) |  Chênh lệch (Delta)   |
  | :------------------- | :--------------------------------------: | :--------------------------------------: | :-------------------: |
  | **FINAL SCORE**      |                **0.2121**                |                  0.2111                  | -0.0010 (Tương đương) |
  | **DOCS RECALL**      |           **0.2875 (28.75%)**            |             0.2862 (28.62%)              | -0.13% (Dao động nhẹ) |
  | **DOCS PRECISION**   |           **0.1802 (18.02%)**            |             0.1791 (17.91%)              |        -0.11%         |
  | **DOCS F2 MACRO**    |                **0.2233**                |                  0.2221                  |        -0.0012        |
  | **CHUNKS RECALL**    |           **0.2536 (25.36%)**            |             0.2527 (25.27%)              |        -0.09%         |
  | **CHUNKS PRECISION** |           **0.1692 (16.92%)**            |             0.1683 (16.83%)              |        -0.09%         |
  | **CHUNKS F2 MACRO**  |                **0.2010**                |                  0.2002                  |        -0.0008        |

- **Phân tích Chuyên sâu (Key Insights & Chẩn đoán Nút thắt):**
  1. **Hiệu ứng "Bão hòa cụm Domain" (Domain Saturation):**
     - 4 khối của Tier 2 (`0-100k` đến `300-400k`) tập trung gần như toàn bộ vào 2 website Q&A: `www.120ask.com` (~480k URLs) và `www.cnkang.com` (~447k URLs).
     - Việc nạp thêm tài liệu từ cùng cụm domain này không làm tăng thêm Recall vì các câu hỏi trong bộ đề của BTC vốn có câu trả lời nằm ở `120ask` hay `cnkang` đã được trúng ngay từ khối 100k đầu tiên (ở Exp 21).
  2. **Các "Mảnh ghép Ground Truth" còn thiếu nằm ở đâu?**
     - Nhìn vào phân bố của tập còn thiếu (`remaining_urls.parquet`), các domain khổng lồ chưa được lập chỉ mục gồm:
       - `ask.39.net`: Thiếu **337.000 URLs** (Diễn đàn hỏi đáp bác sĩ lớn nhất Trung Quốc, thường là nguồn ground truth chính).
       - `nhathuoclongchau.com.vn`: Thiếu **78.000 URLs** (Nguồn dược lý & bệnh học tiếng Việt chuẩn).
       - `familydoctor.com.cn`: Thiếu **268.000 URLs**.
     - Đây chính là nơi ẩn giấu 15–20% Recall còn lại để bứt phá lên ngang hàng với Top 1 (~45% Recall)!
  3. **Nút thắt Top 100 Cut-off:**
     - Khi kho dữ liệu phình to lên 1.4 triệu tài liệu, việc chỉ lấy Top 100 docs per query khiến sự cạnh tranh điểm số gắt gao hơn. Thử nghiệm Exp 23 cho thấy nếu nới lên Top 200 docs, Recall nhảy vọt lên tận **35.47%**.

---

---
[← Exp 24](exp24_2stage_rerank.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 26 →](exp26_bge_m3_nhathuoclongchau.md)
