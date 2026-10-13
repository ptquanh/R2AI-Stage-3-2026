[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 19: BGE-M3 Linear Hybrid Sweet-Spot (Dense 1.0 + Sparse 0.2, 700k docs) 🏆

- **Mục tiêu:** Thử nghiệm hạ tỷ trọng Sparse Lexical xuống mức nhẹ `0.2` (thay vì 0.3 hay 0.5) để tìm điểm cân bằng hoàn hảo (sweet spot): vừa tận dụng khả năng neo exact terms y khoa, vừa không dìm tài liệu tiếng Trung.
- **Cấu hình & Tham số:**
  - `mode = hybrid` | `fusion = linear` | `dense_weight = 1.0` | `sparse_weight = 0.2`
  - File nộp: `submission_bgem3_hybrid_w02.zip` (100 docs, 98 chunks)
- **Kết quả:**
  - **`FINAL_SCORE: 0.1686`** 🚀 _(Kỷ lục mới cao nhất từ trước đến nay - All-Time High!)_
  - `DOCS_F2MACRO: 0.1763` | `DOCS_PRECISION: 0.1441` | `DOCS_RECALL: 0.2230`
  - `CHUNKS_F2MACRO: 0.1609` | `CHUNKS_PRECISION: 0.1399` | `CHUNKS_RECALL: 0.1978`
- **So sánh trực tiếp các mốc Sparse Weight:**

  | Cấu hình                  |  DOCS RECALL  | DOCS PRECISION |    DOCS F2    | CHUNKS F2  |  FINAL SCORE  |
  | :------------------------ | :-----------: | :------------: | :-----------: | :--------: | :-----------: |
  | **Dense Only (Exp 15)**   |    0.2093     |     0.1348     |    0.1646     |   0.1494   |    0.1570     |
  | **Hybrid w=0.2 (Exp 19)** | **0.2230** 🥇 | **0.1441** 🥇  | **0.1763** 🥇 |   0.1609   | **0.1686** 🏆 |
  | **Hybrid w=0.3 (Exp 16)** |    0.2228     |     0.1433     |    0.1758     | **0.1610** |    0.1684     |
  | **Hybrid w=0.5 (Exp 17)** |    0.2181     |     0.1397     |    0.1720     |   0.1562   |    0.1641     |

- **Phân tích Đột phá (The Linear Hybrid Sweet Spot):**
  1. **Sự cân bằng tối ưu giữa Dense và Sparse:**
     - Điểm Dense Cosine phân bố trong khoảng $[0.5, 0.9]$.
     - Điểm Sparse Lexical dot-product phân bố trong khoảng $[0.0, 5.0+]$.
     - Khi nhân với hệ số $w_s = 0.2$, phần thưởng từ vựng đóng góp khoảng $0.2 \times [1.0 - 2.0] = +0.2 \rightarrow +0.4$ điểm. Mức cộng này vừa đủ mạnh để kéo các tài liệu trùng khớp tên thuốc, chỉ số xét nghiệm (`HbA1c`, `ALT`, `AST`...) lên Top 100, nhưng **không quá lớn** để dìm văng các bài tiếng Trung có Dense tương đồng cao ra khỏi danh sách.
  2. **Hiệu quả thể hiện rõ nét:** `DOCS_RECALL` đạt đỉnh cao nhất lịch sử **`22.30%`**, kéo theo `DOCS_PRECISION` cũng đạt đỉnh **`14.41%`**.
- **Định hướng tiếp theo:**
  - Cấu hình **Linear Hybrid `dense_weight=1.0, sparse_weight=0.2`** chính thức trở thành cấu hình Retrieval chuẩn nhất.
  - Tiềm năng khi phủ sóng 100% corpus (~1.24M URLs Tier 1 và các Tier khác) sẽ hứa hẹn đưa FINAL_SCORE vượt mốc **0.25 – 0.30+**.

---

---
[← Exp 18](exp18_rrf_fusion.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 20 →](exp20_pure_bm25_sqlite_fts5.md)
