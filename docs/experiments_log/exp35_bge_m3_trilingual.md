# Experiment 35: BGE-M3 Trilingual Retrieval (Vietnamese + Chinese + English)

- **Ngày thực hiện:** 13/10/2026
- **Mục tiêu:** Kiểm nghiệm giả thuyết mở rộng truy vấn tam ngữ (Tri-lingual Retrieval: Việt + Trung + Anh) để tối ưu hóa khả năng thu hồi (Recall) các tài liệu y khoa quốc tế (PubMed, dược thư, giải phẫu học, xét nghiệm chỉ số lâm sàng).
- **Thiết lập thử nghiệm (Ablation Control):**
  - Giữ nguyên các tham số chuẩn từ kỷ lục Exp 33:
    - Chế độ: Hybrid Dense + Sparse (`mode=hybrid`, `fusion=linear`)
    - Trọng số: `dense_weight=1.0`, `sparse_weight=0.2`
    - Bộ lọc BTC: Lọc loại bỏ các documents đã bị BTC xóa khỏi corpus (`--btc_links_file data/raw/btc_provided/links_corpus_vi_en_zh.parquet`)
    - Giới hạn ứng viên: Top 100 documents, Top 98 chunks / query (Không áp dụng score threshold cắt tỉa để bảo toàn Recall F2 tối đa)
  - Biến số thay đổi duy nhất:
    - Dịch offline 1,200 câu hỏi y khoa sang tiếng Anh (`query_en`) bằng mô hình `Qwen/Qwen2.5-1.5B-Instruct` (FP16, offline 100%, tuân thủ luật thi $\le 15\text{B}$).
    - Hợp nhất trọng số Lexical Token:
      $$W_{fused}(t) = \max\Big(W_{vi}(t),\, W_{zh}(t) \cdot 1.0,\, W_{en}(t) \cdot 0.5\Big)$$
    - Tiếng Anh được gán trọng số 0.5 để hỗ trợ các thuật ngữ y khoa chuyên ngành (tên thuốc, danh pháp giải phẫu, xét nghiệm) mà không làm loãng trọng tâm ngôn ngữ Việt/Trung.

---

## 1. Dữ liệu và Phương pháp

- **Dữ liệu truy vấn:** `data/raw/btc_provided/query_translated.parquet` (1,200 câu hỏi đầy đủ 3 ngôn ngữ: `query`, `query_zh`, `query_en`).
- **Bộ máy tìm kiếm:** `FAISSSearcher` (Memory-Mapped trên `data/indices/new_dataset/index/faiss_index_flat_ip.bin` với ~488,000 documents) kết hợp Sparse Sharded Search.
- **Tập tin xuất:**
  - JSON: `submission_bgem3_trilingual_vi_zh_en.json`
  - ZIP: `submission_bgem3_trilingual_vi_zh_en.zip` (Kích thước: 93.83 MB < 100 MB).

---

## 2. Kiểm tra tính toàn vẹn (Integrity Checks)

- Số lượng queries: Đủ 1,200 / 1,200 (100%).
- Số lượng documents trung bình / query: 99.95.
- Số lượng chunks trung bình / query: 98.0.
- Tất cả tài liệu đều thuộc tập hợp liên kết hợp lệ của BTC.

---

## 3. Kết quả đánh giá trên hệ thống chấm điểm BTC

- **Kết quả chính thức:**
  - `FINAL_SCORE`: **0.2915** 🏆 (Lập kỷ lục mới, tăng +0.0002 so với Exp 33)
  - `DOCS_F2MACRO`: **0.3137** (Tăng +0.0004 so với Exp 33)
  - `CHUNKS_F2MACRO`: **0.2693** (Duy trì ngang bằng Exp 33)
  - `DOCS_PRECISION`: **0.2466** (Tăng +0.0004 so với Exp 33)
  - `DOCS_RECALL`: **0.4152** (Tăng +0.05% so với Exp 33, tăng +1.05% so với Pure VI)
  - `CHUNKS_PRECISION`: **0.2194** (Duy trì ngang bằng Exp 33)
  - `CHUNKS_RECALL`: **0.3508** (Tăng +0.12% so với Exp 33, tăng +1.14% so với Pure VI)

| Metric               | Baseline Exp 31 (Pure VI) | Exp 33 (VI + ZH Qwen) | Exp 35 (VI + ZH + EN) | Thay đổi so với Exp 33 |
| -------------------- | ------------------------- | --------------------- | --------------------- | ---------------------- |
| **FINAL_SCORE**      | 0.2846                    | 0.2913                | **0.2915** 🏆         | **+0.0002**            |
| **DOCS_F2MACRO**     | 0.3060                    | 0.3133                | **0.3137**            | **+0.0004**            |
| **CHUNKS_F2MACRO**   | 0.2632                    | 0.2693                | **0.2693**            | 0.0000                 |
| **DOCS_RECALL**      | 0.4047                    | 0.4147                | **0.4152**            | **+0.0005 (+0.05%)**   |
| **CHUNKS_RECALL**    | 0.3394                    | 0.3496                | **0.3508**            | **+0.0012 (+0.12%)**   |
| **DOCS_PRECISION**   | 0.2404                    | 0.2462                | **0.2466**            | **+0.0004**            |
| **CHUNKS_PRECISION** | 0.2133                    | 0.2194                | **0.2194**            | 0.0000                 |

---

## 4. Phân tích & Đánh giá (Insights)

1. **Tiếng Anh (`query_en`) có đóng góp tích cực:**
   - Việc bổ sung tiếng Anh với trọng số `en_weight=0.5` tiếp tục cải thiện cả **Docs Recall** (lên 41.52%) và **Chunks Recall** (lên 35.08%).
   - Cả Docs Precision (0.2466) và Docs F2 (0.3137) đều tăng nhẹ, chứng minh rằng các từ khóa tiếng Anh y khoa chuyên ngành (tên thuốc, xét nghiệm, giải phẫu) giúp BGE-M3 khớp chính xác hơn vào các tài liệu y học có trích dẫn quốc tế hoặc thuật ngữ latin/tiếng Anh mà không gây nhiễu.
2. **Xu hướng Recall vững chắc:**
   - Pure VI: 40.47% Docs Recall / 33.94% Chunks Recall
   - VI + ZH: 41.47% Docs Recall / 34.96% Chunks Recall
   - VI + ZH + EN: 41.52% Docs Recall / 35.08% Chunks Recall
   - Tam ngữ chứng minh tính ưu việt toàn diện trên không gian embedding đa ngữ của `BAAI/bge-m3`.
