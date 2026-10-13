[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 16: BGE-M3 Hybrid Retrieval (Dense 1.0 + Sparse Lexical 0.3, 700k docs)

- **Mục tiêu:** Kiểm tra hiệu năng của phương pháp kết hợp Hybrid giữa Dense Vector Semantic Embedding và Sparse Lexical Weights từ mô hình BGE-M3 trên toàn bộ 700.000 tài liệu đã index.
- **Cấu hình Chi tiết (Configuration & Hyperparameters):**
  - **Lệnh thực thi (CLI Command):**
    ```bash
    python scripts/run_submission.py --mode hybrid --dense_weight 1.0 --sparse_weight 0.3 --top_docs 100 --top_chunks 98
    ```
  - **Bảng thông số cấu hình:**
    | Tham số | Giá trị | Giải thích |
    | :--- | :--- | :--- |
    | **Mô hình Embedding** | `BAAI/bge-m3` (FP16) | Đa ngữ, hỗ trợ đồng thời Dense (1024d) và Sparse Lexical (Vocab 250k) |
    | **Retrieval Mode** | `hybrid` | Kết hợp tuyến tính (Score Fusion) giữa Dense và Sparse |
    | **Dense Weight ($w_d$)** | **`1.0`** | Trọng số ngữ nghĩa (Cosine Similarity trên vector 1024 chiều) |
    | **Sparse Weight ($w_s$)** | **`0.3`** | Trọng số từ vựng (Dot product qua `scipy.sparse.csr_matrix` SpMM) |
    | **Công thức Fusion** | $\text{Score} = 1.0 \times S_{\text{dense}} + 0.3 \times S_{\text{sparse}}$ | Điểm tổng hợp cho từng cặp (Query, Doc/Chunk) |
    | **Độ phủ Corpus** | **700,000 tài liệu** | 7 index chunks (từ chunk 0 đến chunk 700k trong `data/indices`) |
    | **Top Documents ($k_{\text{docs}}$)** | **100** | Lấy tối đa 100 tài liệu có điểm Hybrid cao nhất per query |
    | **Top Chunks ($k_{\text{chunks}}$)** | **98** | Lấy tối đa 98 chunks cao nhất per query (tối ưu file ZIP < 100MB) |
    | **Serialization** | `separators=(',', ':')` | JSON nén tối đa không khoảng trắng thừa, file ZIP đạt 98.86 MB |

- **Kết quả Chi tiết & So sánh với Exp 15 (Dense-only):**

  | Chỉ số (Metric)      | Exp 15 (Dense Only) | Exp 16 (Hybrid 1.0 + 0.3) |   Chênh lệch (Delta)    |
  | :------------------- | :-----------------: | :-----------------------: | :---------------------: |
  | **FINAL SCORE**      |     **0.1570**      |        **0.1684**         | **+0.0114 (+7.26%)** 🚀 |
  | **DOCS F2 MACRO**    |       0.1646        |        **0.1758**         |       **+0.0112**       |
  | **CHUNKS F2 MACRO**  |       0.1494        |        **0.1610**         |       **+0.0116**       |
  | **DOCS RECALL**      |   0.2093 (20.93%)   |    **0.2228 (22.28%)**    |       **+1.35%**        |
  | **CHUNKS RECALL**    |   0.1855 (18.55%)   |    **0.1979 (19.79%)**    |       **+1.24%**        |
  | **DOCS PRECISION**   |   0.1348 (13.48%)   |    **0.1433 (14.33%)**    |       **+0.85%**        |
  | **CHUNKS PRECISION** |   0.1287 (12.87%)   |    **0.1398 (13.98%)**    |       **+1.11%**        |

- **Phân tích kết quả:**
  - **Chiến thắng toàn diện của Hybrid Retrieval:** Khi bổ sung Sparse Lexical Weights với trọng số 0.3, toàn bộ 7 chỉ số đánh giá của BTC đều tăng vọt đồng loạt:
    - `DOCS_RECALL` tăng từ `20.93%` $\rightarrow$ **`22.28%`** (+1.35%).
    - `CHUNKS_RECALL` tăng từ `18.55%` $\rightarrow$ **`19.79%`** (+1.24%).
    - `DOCS_PRECISION` tăng từ `13.48%` $\rightarrow$ **`14.33%`** (+0.85%).
    - `CHUNKS_PRECISION` tăng từ `12.87%` $\rightarrow$ **`13.98%`** (+1.11%).
    - `DOCS_F2MACRO` tăng từ `0.1646` $\rightarrow$ **`0.1758`** (+0.0112).
    - `CHUNKS_F2MACRO` tăng từ `0.1494` $\rightarrow$ **`0.1610`** (+0.0116).
  - **Lý giải nguyên nhân:**
    1. **Neo chính xác thuật ngữ y khoa (Lexical Anchor):** Dense Retrieval hiểu rất tốt ngữ cảnh tương đồng nhưng dễ bị "semantic drift" với các từ viết tắt chuyên ngành (`HbA1c`, `CA125`, `ALT`, `AST`, `HP`, `HBV-DNA`) hoặc tên bệnh hiếm. Thành phần Sparse Lexical của BGE-M3 đã neo chặt các exact terms này, giúp tài liệu chứa đúng từ khóa chuyên môn được ưu tiên nhảy lên đầu bảng xếp hạng.
    2. **Đồng thời nâng cao Precision:** Sparse weights đóng vai trò như một bộ lọc tự nhiên, phạt nặng các đoạn văn có embedding nhìn "na ná" nhưng thực chất là sai căn bệnh / sai chỉ số y khoa.
  - **Ý nghĩa & Hướng phát triển:**
    - Cấu hình **Hybrid Dense 1.0 + Sparse 0.3** chính thức trở thành **Baseline chuẩn** cho toàn bộ pipeline của đội thi từ thời điểm này.
    - Tiềm năng khi phủ sóng 100% corpus (~1.24M URLs Tier 1 và các Tier khác) sẽ hứa hẹn đưa FINAL_SCORE vượt mốc **0.25 – 0.30+**.

---

---
[← Exp 15](exp15_bge_m3_dense_700k.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 17 →](exp17_bge_m3_hybrid_sparse05.md)
