[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 21: BGE-M3 Linear Hybrid Sweet-Spot + Bổ sung Tier 2 (Corpus Trung Quốc) 🏆🚀

- **Mục tiêu:** Đánh giá hiệu năng của pipeline Hybrid Retrieval (Dense 1.0 + Sparse 0.2) sau khi bổ sung các khối chỉ mục từ Tier 2 (chủ yếu là các bách khoa y học, từ điển dược liệu và các trang y tế tiếng Trung như `cnkang.com`, `a-hospital.com`, `zhongyibaodian.net`...).
- **Cấu hình Chi tiết (Configuration & Hyperparameters):**
  - **Lệnh thực thi:**
    ```bash
    python scripts/run_submission.py --mode hybrid --fusion linear --dense_weight 1.0 --sparse_weight 0.2 --top_docs 100 --top_chunks 98 --output submission_bgem3_hybrid_w02.json
    ```
  - **Retrieval Mode:** `hybrid` (Linear Fusion: $1.0 \times \text{Dense} + 0.2 \times \text{Sparse}$)
  - **Kho dữ liệu index:** Toàn bộ Tier 1 (~1.0M docs) + Tier 2 bổ sung (~1.1M docs). Tổng cộng 11 khối chỉ mục (shards).
  - **Đầu ra:** Top 100 relevant docs, Top 98 relevant chunks per query. File nén an toàn `< 100 MB`.
- **Kết quả Chi tiết & So sánh với Exp 19 (700k docs):**

  | Chỉ số (Metric)      | Exp 19 (700k docs) | Exp 21 (Bổ sung Tier 2) |   Chênh lệch (Delta)    |
  | :------------------- | :----------------: | :---------------------: | :---------------------: |
  | **FINAL SCORE**      |     **0.1686**     |       **0.2121**        | **+0.0435 (+25.8%)** 🚀 |
  | **DOCS F2 MACRO**    |       0.1763       |       **0.2233**        |       **+0.0470**       |
  | **CHUNKS F2 MACRO**  |       0.1609       |       **0.2010**        |       **+0.0401**       |
  | **DOCS RECALL**      |  0.2230 (22.30%)   |   **0.2875 (28.75%)**   |       **+6.45%**        |
  | **CHUNKS RECALL**    |  0.1978 (19.78%)   |   **0.2536 (25.36%)**   |       **+5.58%**        |
  | **DOCS PRECISION**   |  0.1441 (14.41%)   |   **0.1802 (18.02%)**   |       **+3.61%**        |
  | **CHUNKS PRECISION** |  0.1399 (13.99%)   |   **0.1692 (16.92%)**   |       **+2.93%**        |

- **Phân tích Đột phá (Key Insights):**
  1. **Cột mốc lịch sử (> 0.20):** Lần đầu tiên điểm số chính thức của đội vượt qua mốc 0.20, đạt đỉnh **0.2121** (+25.8% so với kỷ lục cũ).
  2. **Bằng chứng xác thực về vai trò của Corpus tiếng Trung:**
     - `DOCS_RECALL` nhảy vọt từ `22.30%` lên **`28.75%`** (+6.45%).
     - `CHUNKS_RECALL` tăng mạnh từ `19.78%` lên **`25.36%`** (+5.58%).
     - Điều này chứng minh một tỷ lệ lớn câu hỏi trong bộ đề kiểm thử của BTC có câu trả lời trực tiếp hoặc tài liệu tham chiếu gốc nằm ở các website y tế tiếng Trung (Tier 2). Việc bổ sung Tier 2 đã lập tức kích hoạt khả năng truy hồi liên ngôn ngữ (Cross-lingual Retrieval) của BGE-M3.
  3. **Precision tăng đồng đều (Không bị pha loãng):** Cả `DOCS_PRECISION` (lên 18.02%) và `CHUNKS_PRECISION` (lên 16.92%) đều tăng thêm ~3%. Điều này khẳng định tài liệu Tier 2 được bổ sung có chất lượng rất cao và sát với ngữ cảnh câu hỏi, không gây nhiễu cho không gian tìm kiếm.
  4. **Triển vọng tiến tới mốc 0.3x - 0.4x:** Việc chỉ bổ sung một phần Tier 2 đã mang lại mức tăng trưởng Recall +6.45%. Khi cào và lập chỉ mục đầy đủ các domain Q&A tiếng Trung còn thiếu (như `ask.39.net`, phần còn lại của `120ask.com` và `cnkang.com`), việc đẩy DOCS_RECALL lên mức 40-45% và bắt kịp điểm số của Top 1 (0.42+) hoàn toàn nằm trong tầm tay!

---

---
[← Exp 20](exp20_pure_bm25_sqlite_fts5.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 22 →](exp22_bge_m3_top10.md)
