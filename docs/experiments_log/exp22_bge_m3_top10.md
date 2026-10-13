[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 22: BGE-M3 Linear Hybrid Khắt khe (Top k = 10 Docs & Chunks)

- **Mục tiêu:** Kiểm nghiệm giả thuyết liệu việc thu hẹp số lượng nộp xuống mức rất khắt khe ($k=10$) có giúp tăng mạnh Precision để bù đắp điểm số tổng thể hay không.
- **Cấu hình:**
  - Lệnh: `python scripts/run_submission.py --mode hybrid --fusion linear --dense_weight 1.0 --sparse_weight 0.2 --top_docs 10 --top_chunks 10 --output submission_bgem3_top10.json`
  - Nộp: Đúng 10 docs và 10 chunks per query. File ZIP chỉ nặng 9.95 MB.
- **Kết quả:**
  - `FINAL_SCORE: 0.0731` _(Giảm mạnh từ 0.2121 của Exp 21)_
  - `DOCS_F2MACRO: 0.0825` | `DOCS_PRECISION: 0.3582` | `DOCS_RECALL: 0.0749`
  - `CHUNKS_F2MACRO: 0.0637` | `CHUNKS_PRECISION: 0.2912` | `CHUNKS_RECALL: 0.0578`
- **So sánh trực tiếp với Exp 21 (Top k=100):**

  | Chỉ số (Metric)      |  Exp 21 (Top 100)   |   Exp 22 (Top 10)   |    Chênh lệch (Delta)     |
  | :------------------- | :-----------------: | :-----------------: | :-----------------------: |
  | **FINAL SCORE**      |     **0.2121**      |     **0.0731**      |  **-0.1390 (-65.5%)** 🔻  |
  | **DOCS PRECISION**   |   0.1802 (18.02%)   | **0.3582 (35.82%)** | **+17.80% (Gấp đôi!)** 🚀 |
  | **CHUNKS PRECISION** |   0.1692 (16.92%)   | **0.2912 (29.12%)** |      **+12.20%** 🚀       |
  | **DOCS RECALL**      | **0.2875 (28.75%)** |   0.0749 (7.49%)    |      **-21.26%** 🔻       |
  | **CHUNKS RECALL**    | **0.2536 (25.36%)** |   0.0578 (5.78%)    |      **-19.58%** 🔻       |

- **Phân tích Đột phá (Key Insights):**
  1. **Khẳng định quy luật F2:** Công thức $F_2$ phạt Recall cực nặng (trọng số Recall gấp 4 lần Precision). Mặc dù Precision tăng vọt lên mức kỷ lục toàn giải (**35.82%** đối với Docs và **29.12%** đối với Chunks), nhưng việc Recall bị bóp nghẹt xuống 7.49% đã kéo toàn bộ điểm F2 sụp đổ.
  2. **Bài học chiến lược bất di bất dịch:** **Tuyệt đối không giảm số lượng nộp xuống dưới 100.** Trái lại, để tối đa hóa $F_2$, cần mở rộng số lượng docs nộp lên **150 – 200 docs** nhằm bao phủ tối đa Recall (chấp nhận Precision giảm nhẹ), đồng thời giữ số chunks ở mức 98–100 để file ZIP an toàn dưới 100 MB.

---

---
[← Exp 21](exp21_bge_m3_tier2.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 23 →](exp23_bge_m3_top200.md)
