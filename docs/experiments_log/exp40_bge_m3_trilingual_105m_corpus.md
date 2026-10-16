# Experiment 40: BGE-M3 Trilingual Retrieval on 1.05M Consolidated Corpus (+100k Unembedded Samples)

- **Ngày thực hiện:** 16/10/2026
- **Mục tiêu:** Kiểm nghiệm tác động của việc mở rộng quy mô dữ liệu vượt mốc 1 triệu tài liệu — từ 962,326 tài liệu (1,381,239 chunks) lên **1,056,901 tài liệu (1,500,940 chunks)** (+94,575 docs, +119,701 chunks mới từ khối `index_backup_unembedded_samples_0-100_2`) kết hợp cấu hình Best Config Trilingual Linear Hybrid.
- **Thiết lập thử nghiệm (Best Configuration):**
  - Chế độ: Hybrid Dense + Sparse (`mode=hybrid`, `fusion=linear`)
  - Trọng số Linear: `dense_weight=1.0`, `sparse_weight=0.2`
  - Truy vấn tam ngữ (Trilingual Query Expansion):
    $$W_{fused}(t) = \max\Big(W_{vi}(t),\, W_{zh}(t) \cdot 1.0,\, W_{en}(t) \cdot 0.5\Big)$$
    với bản dịch `query_zh` và `query_en` được tạo bởi mô hình offline `Qwen/Qwen2.5-1.5B-Instruct` (FP16).
  - Bộ lọc BTC: Bật lọc tự động theo 1,220,598 URL hợp lệ của BTC (`links_corpus_vi_en_zh.parquet`).
  - Candidate Buffer: `cand_buffer=400`
  - Giới hạn xuất: Top 100 documents, Top 98 chunks / query (không cắt tỉa score threshold để bảo toàn Recall F2).
  - Quy mô kho dữ liệu: **1,056,901 docs, 1,500,940 chunks** (16 emb parts, 16 chunk parts, 70 text parts).

---

## 1. Dữ liệu và Phương pháp

- **Tập truy vấn:** `data/raw/btc_provided/query_translated.parquet` (1,200 câu hỏi với đầy đủ các trường `query`, `query_zh`, `query_en`).
- **Kho dữ liệu tìm kiếm:** `data/indices/new_dataset/index`:
  - `faiss_index_flat_ip.bin`: 5,863.0 MB (~5.72 GB, 1,500,940 vectors dim 1024).
  - `sparse_csr.npz`: 1,013.8 MB (1,500,940 x 250,005 dims, 268,826,324 non-zeros).
  - `chunks_metadata.parquet`: 15.6 MB (1,500,940 rows).
- **Bộ máy tìm kiếm:** `FAISSSearcher` (Memory-Mapped).
- **Tập tin nộp:**
  - JSON: `submission_bgem3_trilingual_105m_corpus.json`
  - ZIP: `submission_bgem3_trilingual_105m_corpus.zip` (Kích thước: 92.90 MB < 100 MB an toàn).

---

## 2. Kết quả đánh giá trên hệ thống chấm điểm BTC

- **Kết quả chính thức:**
  - `FINAL_SCORE`: **0.2991** 🏆 (Lập đỉnh All-Time High mới! Tăng **+0.0027** so với Exp 39, áp sát ngưỡng **0.3000**!)
  - `DOCS_F2MACRO`: **0.3223** (Tăng mạnh **+0.0035** so với Exp 39)
  - `CHUNKS_F2MACRO`: **0.2759** (Tăng **+0.0020** so với Exp 39)
  - `DOCS_PRECISION`: **0.2521** (Tăng **+0.0021**, đạt đỉnh cao nhất lịch sử)
  - `DOCS_RECALL`: **0.4285** (Tăng vọt **+0.54%**, rút ngắn khoảng cách với Top 1 xuống **2.93%**)
  - `CHUNKS_PRECISION`: **0.2238** (Tăng **+0.0013**)
  - `CHUNKS_RECALL`: **0.3608** (Tăng **+0.44%**, lần đầu tiên vượt mốc 36%)

### Bảng So sánh Tiến trình Bứt phá Điểm số

| Metric | Exp 36 (962k docs) | Exp 39 (962k docs Eval) | **Exp 40 (1.05M docs)** | Tăng trưởng so với Exp 39 |
| :--- | :---: | :---: | :---: | :---: |
| **FINAL_SCORE** | 0.2963 | 0.2964 | **0.2991** 🏆 | **+0.0027** |
| **DOCS_F2MACRO** | 0.3187 | 0.3188 | **0.3223** 🏆 | **+0.0035** |
| **CHUNKS_F2MACRO** | 0.2738 | 0.2739 | **0.2759** 🏆 | **+0.0020** |
| **DOCS_RECALL** | 0.4229 | 0.4231 | **0.4285** 🏆 | **+0.0054 (+0.54%)** |
| **CHUNKS_RECALL** | 0.3563 | 0.3564 | **0.3608** 🏆 | **+0.0044 (+0.44%)** |
| **DOCS_PRECISION** | 0.2499 | 0.2500 | **0.2521** 🏆 | **+0.0021** |
| **CHUNKS_PRECISION** | 0.2225 | 0.2225 | **0.2238** 🏆 | **+0.0013** |

---

## 3. Phân tích & Đánh giá (Insights)

1. **Hiệu ứng Mở rộng Dữ liệu (Corpus Scaling Law) tiếp tục bứt phá:**
   - Việc bổ sung 94,575 tài liệu y khoa chất lượng từ khối `unembedded_0-100_2` đã ngay lập tức giúp Docs Recall tăng thêm **+0.54%** (từ 42.31% lên **42.85%**).
   - Đáng chú ý, **cả 7/7 chỉ số đồng loạt tăng trưởng**, khẳng định 94.5k docs được thêm vào hoàn toàn là dữ liệu giá trị cao, không hề gây loãng hay nhiễu kho chỉ mục.
2. **Khoảng cách với Top 1 ("Quýt đây đứng sợ" - 0.4214 / Docs Recall 45.78%):**
   - Docs Recall của đối thủ là 45.78%, hiện tại chúng ta đã đạt **42.85%** (khoảng cách giờ đây chỉ còn vỏn vẹn **2.93%**!).
   - Hiện trong `data/unembedded_samples.parquet` vẫn còn **16,931 bài viết** chưa nhúng, và `data/remaining_urls.parquet` còn **14,591 URLs** đang chờ cào tiếp. Khi hoàn tất 100%, chúng ta hoàn toàn có thể san bằng độ phủ Recall với Top 1!
3. **Đòn bẩy quyết định để vượt mốc 0.35+ và 0.40+:**
   - Khi Docs Recall đã đạt 42.85%, mấu chốt để đạt điểm số vô địch (0.42+) nằm ở **Chunks Precision**: Top 1 đạt Chunks Precision **0.6281**, trong khi chúng ta đang là **0.2238**.
   - Việc triển khai **Cross-Encoder Reranker** ở cấp độ chunk (chấm điểm nhiều chunk/doc trên GPU Kaggle) sẽ là chìa khóa then chốt để nhân đôi Chunks Precision và đưa điểm số tổng thể vượt qua đối thủ.
