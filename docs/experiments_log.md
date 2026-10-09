# Nhật ký Thử nghiệm & Benchmark (Experiment Logs)

Tài liệu này lưu trữ kết quả của các lần submit và thử nghiệm mô hình, nhằm theo dõi sự cải thiện (hoặc sụt giảm) hiệu năng qua từng thay đổi trong Pipeline. Chúng ta sẽ dùng điểm Baseline của BTC làm mốc đối chiếu (Mốc 0).

## 1. Bảng Xếp hạng Nội bộ (Leaderboard)

| Ngày       | Lần thử (Experiment)                                    | FINAL SCORE | DOCS F2    | CHUNKS F2  | DOCS P     | DOCS R     | CHUNKS P   | CHUNKS R   | Ghi chú                                                                                                                                                                                                                                                                |
| :--------- | :------------------------------------------------------ | :---------- | :--------- | :--------- | :--------- | :--------- | :--------- | :--------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-09-30 | **BM25 Baseline (BTC)**                                 | **0.3764**  | 0.5587     | 0.1941     | 0.8805     | 0.5146     | 0.3403     | 0.1755     | Baseline cơ bản chỉ sử dụng BM25 (Sparse Retrieval).                                                                                                                                                                                                                   |
| 2026-10-01 | **Exp 01: Format Error (String ID)**                    | **0.0000**  | 0.0000     | 0.0000     | 0.0000     | 0.0000     | 0.0000     | 0.0000     | Lỗi định dạng: `doc_id` kiểu string thay vì integer, server chấm 0 điểm toàn bộ.                                                                                                                                                                                       |
| 2026-10-02 | **Exp 02: BM25s (2.1M docs, top k=5)**                  | **0.0000**  | 0.0000     | 0.0000     | 0.0000     | 0.0000     | 0.0000     | 0.0000     | BM25s trên 2.1M docs, chỉ lấy top 5 docs. Quá hẹp, không trúng tài liệu nào.                                                                                                                                                                                           |
| 2026-10-02 | **Exp 03: BM25s (2.1M docs, top k=100)**                | **0.0683**  | 0.1366     | 0.0000     | 0.1048     | 0.1821     | 0.0000     | 0.0000     | Mở rộng top-100: Docs Recall lên 18.21%, Docs P 10.48%. Chunk chưa nộp/trúng (0.0).                                                                                                                                                                                    |
| 2026-10-02 | **Exp 04: BM25s (2.1M docs, top k=500)**                | **0.0594**  | 0.1188     | 0.0000     | 0.0408     | 0.3115     | 0.0000     | 0.0000     | Mở rộng top-500: Docs Recall tăng vọt lên 31.15% (+13%), Precision giảm, Chunk 0.0.                                                                                                                                                                                    |
| 2026-10-03 | **Exp 05: BM25s (Top 100) + BGE Reranker**              | **0.0232**  | 0.0464     | 0.0000     | 0.3491     | 0.0396     | 0.0000     | 0.0000     | Rerank top 100 từ BM25 bằng BGE-M3, nộp top 5. Precision tăng vọt (34.91%) nhưng Recall rớt thảm (3.96%).                                                                                                                                                              |
| 2026-10-03 | **Exp 06: Multi-BM25 + RRF + BGE Reranker**             | **0.0677**  | 0.1354     | 0.0000     | 0.1043     | 0.1804     | 0.0000     | 0.0000     | Dịch 3 ngôn ngữ, RRF(500), BGE rerank nộp 100. Điểm bằng Exp 03. BGE zero-shot thất bại trong phân loại.                                                                                                                                                               |
| 2026-10-04 | **Exp 07: BM25s Top 100 + Naive Chunks**                | **0.0842**  | 0.1366     | 0.0318     | 0.1048     | 0.1821     | 0.0252     | 0.0431     | Nộp 1200 ký tự đầu làm chunk cho các doc từ Exp 03. Điểm chunk cải thiện lên 0.0318, đẩy Final Score lên 0.0842.                                                                                                                                                       |
| 2026-10-04 | **Exp 08: Window 100-2500 chars (Naive)**               | **0.1182**  | 0.1366     | 0.0999     | 0.1048     | 0.1821     | 0.0790     | 0.1313     | Mở rộng giới hạn cắt chunk từ vị trí 100 tới 2500. CHUNKS F2 tăng vọt gấp 3 lần (0.0999), Final Score lên 0.1182.                                                                                                                                                      |
| 2026-10-04 | **Exp 09: Dynamic Window (2500 chars)**                 | **0.1206**  | 0.1366     | 0.1047     | 0.1048     | 0.1821     | 0.0826     | 0.1381     | Áp dụng thuật toán trượt cửa sổ động tìm mật độ từ khóa với win_chars=2500. Final Score vượt 0.12, file zip an toàn <100MB.                                                                                                                                            |
| 2026-10-04 | **Exp 10: Dynamic Window (3200 chars, k=70)**           | **0.1156**  | 0.1278     | 0.1034     | 0.1226     | 0.1553     | 0.1012     | 0.1254     | Tăng win_chars=3200 để lấy ngữ cảnh rộng nhưng giảm top_k=70 (để nén <100MB). Final Score tụt vì Docs Recall rớt mạnh.                                                                                                                                                 |
| 2026-10-05 | **Exp 11: Multi-BM25 + RRF(60) + NLLB**                 | **0.0679**  | 0.0803     | 0.0554     | 0.0570     | 0.1137     | 0.0403     | 0.0778     | Dịch bằng mô hình NLLB 600M, nén zip cắt bỏ 100 từ đầu để <100MB. Điểm Docs Recall giảm thảm hại (11.37%).                                                                                                                                                             |
| 2026-10-07 | **Exp 12: BGE-M3 Dense (400k docs, top 10)**            | **0.0621**  | 0.0717     | 0.0526     | 0.3250     | 0.0633     | 0.2506     | 0.0462     | Code Dense Retrieval trên 400k index BGE-M3. Điểm Recall thấp do code nộp nhầm giới hạn 10 docs (đáng lẽ phải 100 docs).                                                                                                                                               |
| 2026-10-07 | **Exp 13: BGE-M3 Dense (400k docs, top 100)**           | **0.1076**  | 0.1626     | 0.0526     | 0.1326     | 0.2079     | 0.2506     | 0.0462     | Cùng cấu hình Exp 12 nhưng sửa `relevant_docs` lên 100. Docs Recall vượt BM25 toàn tập dữ liệu dù chỉ search trên 400k docs!                                                                                                                                           |
| 2026-10-07 | **Exp 14: BGE-M3 Dense (400k docs, chunks=100)**        | **0.1557**  | 0.1626     | 0.1488     | 0.1326     | 0.2079     | 0.1279     | 0.1854     | Sửa lỗi hardcode giới hạn 10 chunks thành 100. Kỷ lục mới! Chunk Recall tăng vọt lên 18.54%, Final Score đạt 0.1557.                                                                                                                                                   |
| 2026-10-08 | **Exp 15: BGE-M3 Dense (700k docs, chunks=100)**        | **0.1570**  | 0.1646     | 0.1494     | 0.1348     | 0.2093     | 0.1287     | 0.1855     | Bổ sung thêm 300k vector (400k-700k docs). Kỷ lục mới! Docs F2 và Recall đều tăng, Final Score đạt 0.1570.                                                                                                                                                             |
| 2026-10-08 | **Exp 16: BGE-M3 Hybrid (Dense 1.0 + Sparse 0.3)**      | **0.1684**  | 0.1758     | 0.1610     | 0.1433     | 0.2228     | 0.1398     | 0.1979     | Hybrid: Dense(1.0) + Sparse(0.3) trên 700k docs. Kỷ lục mới 0.1684! Cả Recall và Precision đều bứt phá đồng loạt.                                                                                                                                                      |
| 2026-10-08 | **Exp 17: BGE-M3 Hybrid (Dense 1.0 + Sparse 0.5)**      | **0.1641**  | 0.1720     | 0.1562     | 0.1397     | 0.2181     | 0.1411     | 0.1890     | Tăng sparse lên 0.5. Chunk Precision tăng lên 0.1411 nhưng Recall giảm do query tiếng Việt không match Sparse tài liệu tiếng Trung.                                                                                                                                    |
| 2026-10-08 | **Exp 18: BGE-M3 RRF Fusion (w=0.8, k=60)**             | **0.1483**  | 0.1559     | 0.1408     | 0.1252     | 0.1996     | 0.1229     | 0.1730     | Thử nghiệm Reciprocal Rank Fusion (k=60) với Sparse weight 0.8. Điểm sụt giảm do RRF làm phẳng tín hiệu Cosine tương đối.                                                                                                                                              |
| 2026-10-08 | **Exp 19: BGE-M3 Hybrid (Dense 1.0 + Sparse 0.2)**      | **0.1686**  | 0.1763     | 0.1609     | 0.1441     | 0.2230     | 0.1399     | 0.1978     | Điểm ngọt Linear Hybrid: Sparse nhẹ 0.2 neo exact terms mà không dìm tài liệu tiếng Trung. DOCS_RECALL đạt 22.30%.                                                                                                                                                     |
| 2026-10-09 | **Exp 20: Pure BM25 SQLite FTS5 (1.35M docs)**          | **0.0677**  | 0.0736     | 0.0617     | 0.0589     | 0.0965     | 0.0512     | 0.0798     | Thử nghiệm "chỉ dùng BM25" trên 1.35M docs (SQLite FTS5, lỗi `tier_2`). Bác bỏ tin đồn "chỉ cần cào BM25 là 0.3x". Recall (9.65%) quá tệ do tokenization yếu và nhiễu stopword tiếng Việt.                                                                             |
| 2026-10-09 | **Exp 21: BGE-M3 Hybrid (Bổ sung Tier 2 - Trung Quốc)** | **0.2121**  | **0.2233** | **0.2010** | 0.1802     | **0.2875** | 0.1692     | **0.2536** | **Kỷ lục mới (All-Time High: 0.2121)!** Bổ sung Tier 2 (tài liệu tiếng Trung). Docs Recall tăng vọt lên 28.75% (+6.45%), Chunks Recall lên 25.36% (+5.58%), phá vỡ mốc 0.20!                                                                                           |
| 2026-10-09 | **Exp 22: BGE-M3 Hybrid (Thử nghiệm Top k=10)**         | **0.0731**  | 0.0825     | 0.0637     | **0.3582** | 0.0749     | **0.2912** | 0.0578     | Thử nghiệm nộp khắt khe top 10 docs & chunks. Docs Precision (35.82%) và Chunk Precision (29.12%) tăng vọt đỉnh điểm, nhưng Recall rớt thảm hại do bỏ sót tài liệu ngoài top 10, kéo Final Score sụt về 0.0731.                                                        |
| 2026-10-09 | **Exp 23: BGE-M3 Hybrid (Top 200 Docs, 100 Chunks)**    | **0.2110**  | 0.2205     | **0.2016** | 0.1183     | **0.3547** | 0.1675     | **0.2557** | **Kỷ lục Docs Recall mới (35.47%)!** Nới rộng top 200 docs: Docs Recall bứt phá từ 28.75% lên 35.47% (+6.72%), Chunks Recall lên 25.57%, Chunks F2 đạt đỉnh 0.2016. Docs Precision giảm do chia 200 docs giữ Final Score 0.2110.                                       |
| 2026-10-09 | **Exp 24: 2-Stage Rerank (Top 200 -> Top 100 Docs)**    | **0.1835**  | 0.2024     | 0.1646     | 0.1602     | 0.2616     | 0.1361     | 0.2086     | Thử nghiệm 2-Stage Retrieval dùng `bge-reranker-v2-m3` lọc Top 200 xuống 100 docs & 98 chunks. Zero-shot Reranker bị "negative transfer", đẩy trôi tài liệu ground truth làm Recall tụt từ 35.47% về 26.16%. Khẳng định cần dùng Score Fusion hoặc fine-tune Reranker. |

### Mục tiêu (Target) - Top 1 Leaderboard hiện tại (2026-10-08)

| Đội thi              | FINAL SCORE |  DOCS F2   | CHUNKS F2  |   DOCS P   |   DOCS R   |  CHUNKS P  |  CHUNKS R  |
| :------------------- | :---------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: |
| **Quýt đây đứng sợ** | **0.4214**  | **0.4183** | **0.4246** | **0.4690** | **0.4578** | **0.6281** | **0.4365** |

- **Phân tích khoảng cách (Gap Analysis):**
  - So với kỷ lục mới của chúng ta (Exp 21: `0.2121`), khoảng cách với Top 1 đã **thu hẹp xuống còn 2.0 lần** (trước đây là 2.5 lần).
  - **Recall:** Họ đạt Recall ~43-45%, trong khi ta vừa bứt phá từ ~22% lên **28.75%**. Khi lập chỉ mục (index) đủ 100% corpus (bao gồm các domain Q&A tiếng Trung & tiếng Việt lớn còn thiếu), Docs Recall hứa hẹn sẽ tiệm cận mức 40-45%.
  - **Precision:** Điểm Chunks Precision của họ lên tới **0.6281**, trong khi của ta đang ở mức **0.1692**. Sau khi index phủ kín dữ liệu, việc tích hợp mô hình Cross-encoder Reranker mạnh sẽ là chìa khóa then chốt để đẩy Precision lên và cạnh tranh ngôi vương.

---

## 2. Chi tiết các lần thử nghiệm (Experiment Details)

### Exp 00: BM25 Baseline (BTC cung cấp)

- **Phương pháp:** Thuật toán đếm tần suất từ khóa BM25 truyền thống, không dùng AI hay Vector Embedding.
- **Phân tích kết quả:**
  - **Truy hồi cấp Document (Tài liệu):** Điểm F2 đạt 0.5587. Precision rất cao (0.8805) nhưng Recall chỉ ở mức trung bình (0.5146).
    👉 _Nhận xét:_ Chữ nào giống chữ đó thì BM25 tìm rất trúng (Precision cao), nhưng nó bỏ sót một nửa số tài liệu liên quan (Recall thấp) vì không hiểu được từ đồng nghĩa hoặc các thuật ngữ y khoa tương đương.
  - **Truy hồi cấp Chunk (Đoạn văn):** Điểm F2 siêu thấp (0.1941), Recall cực kỳ tệ (0.1755).
    👉 _Nhận xét:_ BM25 gần như thất bại hoàn toàn trong việc trích xuất chính xác đoạn chứa thông tin "chốt". Thuật toán Chunking của Baseline khả năng cao đang cắt vỡ ngữ nghĩa hoặc chunk nộp lên không overlap đủ với Ground Truth.
- **Mục tiêu cho Pipeline R2AI của chúng ta:**
  1. Tăng vọt Recall bằng cách thêm Vector Embedding + Medical Ontology.
  2. Áp dụng Semantic Chunking khắt khe (< 1024 tokens) để cứu vãn điểm Chunks F2.

---

### Exp 01: Lỗi định dạng ID kiểu String (String ID Format Error)

- **Mục tiêu:** Thử nghiệm submission đầu tiên lên hệ thống.
- **Phương pháp:** Pipeline sinh file submission nhưng `doc_id` trong danh sách `relevant_docs` bị ép kiểu hoặc xuất ra dưới dạng chuỗi (`string`) thay vì số nguyên (`integer`).
- **Kết quả:**
  - `FINAL_SCORE: 0.0` (Tất cả các metric đều bằng 0.0).
- **Nguyên nhân & Bài học:**
  - Server chấm thi của BTC yêu cầu trường `doc_id` bắt buộc phải là kiểu **Integer (int)**.
  - Khi `doc_id` là kiểu String, hệ thống đối soát không match được với Ground Truth (hoặc parser trên server BTC reject).
  - 👉 **Quy tắc bất di bất dịch:** Toàn bộ pipeline xuất submission luôn phải ép kiểu `int(doc_id)` trước khi xuất file.

---

### Exp 02: BM25s trên 2.1 triệu tài liệu (Top k = 5)

- **Mục tiêu:** Kiểm tra khả năng truy hồi của thư viện BM25s siêu tốc trên toàn bộ kho corpus crawl được (~2.1M documents) với ngưỡng lựa chọn chặt chẽ ($k=5$).
- **Phương pháp:**
  - Sử dụng thư viện `bm25s` để index toàn bộ ~2.1 triệu tài liệu.
  - Chỉ lấy $k=5$ tài liệu có score cao nhất cho mỗi câu truy vấn.
- **Kết quả:**
  - `FINAL_SCORE: 0.0` (DOCS_F2 = 0.0, DOCS_RECALL = 0.0, CHUNKS_F2 = 0.0).
- **Phân tích kết quả:**
  - Trên không gian tìm kiếm cực lớn (2.1M tài liệu so với tập nhỏ của baseline), việc chỉ lấy top 5 là quá hẹp. BM25 thuần túy bị nhiễu bởi các tài liệu dài hoặc trùng lặp từ khóa ngẫu nhiên, khiến các tài liệu thực sự liên quan không lọt nổi vào top 5.
  - Dẫn đến Recall bằng 0 tuyệt đối.

---

### Exp 03: BM25s trên 2.1 triệu tài liệu (Top k = 100)

- **Mục tiêu:** Nới rộng candidate pool lên top 100 để xem liệu BM25s có bắt được tài liệu liên quan không.
- **Phương pháp:**
  - BM25s trên ~2.1M tài liệu.
  - Lấy top $k=100$ tài liệu cho mỗi query.
- **Kết quả:**
  - `FINAL_SCORE: 0.0683`
  - `DOCS_F2MACRO: 0.1366` | `DOCS_PRECISION: 0.1048` | `DOCS_RECALL: 0.1821`
  - `CHUNKS_F2MACRO: 0.0` | `CHUNKS_PRECISION: 0.0` | `CHUNKS_RECALL: 0.0`
- **Phân tích kết quả:**
  - **Tài liệu (Docs):** Mở rộng từ $k=5$ lên $k=100$ ngay lập tức mở khóa Recall từ **0% lên 18.21%**! Precision đạt 10.48%.
  - **Đoạn văn (Chunks):** Điểm bằng 0.0 do chưa có mô-đun Semantic Chunking hoặc chưa submit chunks hợp lệ.
  - Chứng minh BM25s đã bắt đầu tìm thấy tài liệu liên quan, nhưng $k=100$ vẫn còn bỏ sót hơn 81% tài liệu ground truth.

---

### Exp 04: BM25s trên 2.1 triệu tài liệu (Top k = 500)

- **Mục tiêu:** Tiếp tục tăng ngưỡng $k$ lên 500 để tối đa hóa khả năng bao phủ (Recall) của Stage 1 BM25.
- **Phương pháp:**
  - BM25s trên ~2.1M tài liệu.
  - Lấy top $k=500$ tài liệu cho mỗi query.
- **Kết quả:**
  - `FINAL_SCORE: 0.0594`
  - `DOCS_F2MACRO: 0.1188` | `DOCS_PRECISION: 0.0408` | `DOCS_RECALL: 0.3115`
  - `CHUNKS_F2MACRO: 0.0` | `CHUNKS_PRECISION: 0.0` | `CHUNKS_RECALL: 0.0`
- **So sánh & Đúc kết quan trọng (Key Insights):**
  1. **Recall tăng vọt:** Khi tăng từ $k=100 \to 500$, **DOCS_RECALL tăng từ 18.21% lên 31.15%** (+12.94%). Điều này khẳng định gần 1/3 tài liệu liên quan nằm trong top 500 của BM25s.
  2. **Trade-off Precision vs Recall:** Nộp thẳng 500 tài liệu làm Precision tụt từ 10.48% xuống 4.08%, kéo DOCS_F2 giảm nhẹ từ 0.1366 xuống 0.1188.
  3. **Định hình kiến trúc 2-Stage:**
     - **Stage 1 (BM25s Candidate Generation):** Nên để $k=300 \sim 500$ để giữ Recall ở mức cao nhất có thể (~31%+).
     - **Stage 2 (Qwen Semantic Re-ranking):** Dùng mô hình Cross-Encoder / Qwen-8B re-rank lại 500 ứng viên này, lọc lấy top 10-20 tài liệu chất lượng nhất để đẩy Precision lên lại 80%+, đồng thời trích xuất Chunk chuẩn xác để giải quyết bài toán `CHUNKS_F2 = 0.0`.

---

### Exp 05: BM25s (Top 100) + BGE Reranker (Nộp top 5)

- **Mục tiêu:** Áp dụng mô hình Cross-Encoder (BAAI/bge-reranker-v2-m3) để re-rank các candidates do BM25 truy hồi, nhằm tăng Precision.
- **Phương pháp:**
  - Stage 1: BM25s lấy ra top $k=100$ candidates.
  - Stage 2: Truyền 100 văn bản này vào BGE-M3 Reranker.
  - Lấy top 5 kết quả sau khi rerank để nộp (không nộp chunks).
- **Kết quả:**
  - `FINAL_SCORE: 0.0232`
  - `DOCS_F2MACRO: 0.0464` | `DOCS_PRECISION: 0.3491` | `DOCS_RECALL: 0.0396`
  - `CHUNKS_F2MACRO: 0.0` | `CHUNKS_PRECISION: 0.0` | `CHUNKS_RECALL: 0.0`
- **Phân tích kết quả:**
  - **Precision tăng vọt:** BGE-M3 đã làm việc rất hiệu quả khi tăng Docs Precision lên **34.91%** (so với 4.08% của Exp 04 và 10.48% của Exp 03).
  - **Recall rớt thảm (Bottleneck):** Điểm yếu lớn nhất ở đây là Docs Recall chỉ đạt **3.96%**. Lý do:
    1. Đầu vào cho reranker chỉ là Top 100 từ BM25 (chỉ cover được 18.21% Recall tối đa theo Exp 03).
    2. Chỉ lấy top 5 để submit là quá khắt khe, gạt bỏ nhiều tài liệu ground truth khác nằm ngoài top 5. Chú ý điểm thi F2 Macro luôn ưu tiên Recall hơn Precision (trọng số Recall cao gấp 4 lần Precision).

---

### Exp 06: Multilingual BM25 + Query Expansion + RRF + BGE Reranker (Nộp top 100)

- **Mục tiêu:** Tối đa hóa Recall bằng cách mở rộng truy vấn (VI, EN, ZH) kết hợp RRF (lấy top 500) và dùng BGE-M3 Reranker để chọn ra top 100 nộp bài.
- **Phương pháp:**
  - Stage 1: Groq API Query Expansion (y khoa) -> Dịch sang 3 ngôn ngữ -> BM25s -> Reciprocal Rank Fusion (RRF $k=60$) lấy ra 500 candidates tốt nhất.
  - Stage 2: BGE-M3 Reranker đánh giá 500 ứng viên này và giữ lại Top 100 để nộp.
- **Kết quả:**
  - `FINAL_SCORE: 0.0677`
  - `DOCS_F2MACRO: 0.1354` | `DOCS_PRECISION: 0.1043` | `DOCS_RECALL: 0.1804`
  - `CHUNKS_F2MACRO: 0.0` | `CHUNKS_PRECISION: 0.0` | `CHUNKS_RECALL: 0.0`
- **Phân tích kết quả (Key Insights):**
  - **Điểm số gần như y hệt Exp 03 (BM25s chay top 100):** Kết quả này (Recall 18.04%, Precision 10.43%) gần như trùng khớp hoàn toàn với Exp 03 (Recall 18.21%, Precision 10.48%).
  - **Nút thắt ở Zero-shot Reranker (Out-of-domain):** Mặc dù Stage 1 có thể đã gom được Recall lên rất cao (>30% như Exp 04), nhưng mô hình BGE-M3 Reranker (vốn được train chung chung) đã không thể nhận diện chính xác độ liên quan trong ngữ cảnh y khoa tiếng Việt. Hậu quả là khi cắt lấy top 100 sau re-rank, nó đã đẩy nhiều tài liệu đúng xuống dưới và kéo Recall tụt trở lại mức 18%.
  - **Nhiễu từ Query Expansion:** Việc mở rộng truy vấn bằng LLM và dịch sang tiếng Anh/Trung có thể đã đưa vào top 500 quá nhiều tài liệu nhiễu (dài, chứa các từ khóa học thuật nhưng không có đáp án cụ thể cho câu hỏi), khiến reranker bị "đánh lừa".

---

### Exp 07: BM25s Top 100 + Nộp Naive Chunks (1200 chars đầu)

- **Mục tiêu:** Kiểm tra xem nếu trích xuất một đoạn text đơn giản (naive window: lấy 1200 ký tự đầu của mỗi tài liệu tìm được) thì điểm `CHUNKS_F2` sẽ thay đổi như thế nào, nhằm thoát khỏi cảnh điểm Chunk bị 0 liên tục.
- **Phương pháp:**
  - Vẫn giữ nguyên kết quả truy hồi tài liệu (Docs) giống y hệt Exp 03 (dùng `bm25s`, top 100).
  - Với mỗi tài liệu lọt vào top 100, cắt 1200 ký tự đầu tiên để nộp dưới dạng `relevant_chunks`.
- **Kết quả:**
  - `FINAL_SCORE: 0.0842` _(Tăng từ 0.0677)_
  - `DOCS_F2MACRO: 0.1366` | `DOCS_PRECISION: 0.1048` | `DOCS_RECALL: 0.1821`
  - `CHUNKS_F2MACRO: 0.0318` | `CHUNKS_PRECISION: 0.0252` | `CHUNKS_RECALL: 0.0431`
- **Phân tích kết quả (Key Insights):**
  1. **Tài liệu (Docs) ổn định:** Do không thay đổi thuật toán tìm tài liệu, điểm Docs F2 hoàn toàn giống Exp 03.
  2. **Thoát khỏi điểm Chunk 0:** Phương pháp "cắt thô" đã giúp điểm CHUNKS_F2 nhích lên 0.0318, qua đó kéo FINAL_SCORE lên 0.0842.
  3. **Tuy nhiên, 1200 ký tự đầu là chưa đủ tốt:**
     - Mặc dù Docs Recall là ~18.2%, nhưng Chunks Recall chỉ đạt 4.31%.
     - Điều này chứng tỏ trong số các tài liệu tìm đúng, chưa tới 1/4 có chứa đáp án thực sự trong 1200 ký tự đầu tiên.
     - Rất nhiều trang web chứa "boilerplate" (thanh điều hướng, footer, quảng cáo) hoặc đáp án nằm sâu ở bên dưới, nên việc lấy 1200 ký tự đầu tiên bị "trượt" khỏi tiêu chuẩn Overlap > 0.5 với Ground Truth Chunk.
  4. **Kết luận / Bước tiếp theo:** Để có điểm chunk cao thực sự (vượt qua 0.18), không thể cắt chuỗi thô mà bắt buộc phải dùng mô hình LLM / Cross-encoder để xác định chính xác vị trí đoạn văn chứa thông tin trả lời (Semantic Chunking & Reranking) hoặc loại bỏ boilerplate trước khi cắt chunk.

---

### Exp 08: Mở rộng cửa sổ Naive Chunk (từ 100 đến 2500)

- **Mục tiêu:** Kiểm chứng giả thuyết rằng cửa sổ 1200 ký tự là quá hẹp để bao phủ được câu trả lời.
- **Phương pháp:**
  - Vẫn giữ nguyên kết quả truy hồi tài liệu (Docs) giống Exp 03.
  - Cắt `[100:2500]` ký tự của văn bản thay vì `[:1200]`.
- **Kết quả:**
  - `FINAL_SCORE: 0.1182` _(Tăng từ 0.0842)_
  - `DOCS_F2MACRO: 0.1366` | `DOCS_PRECISION: 0.1048` | `DOCS_RECALL: 0.1821`
  - `CHUNKS_F2MACRO: 0.0999` | `CHUNKS_PRECISION: 0.079` | `CHUNKS_RECALL: 0.1313`
- **Phân tích kết quả:**
  - Đúng như phân tích từ file `06_CHUNK_1024_TOKEN_SPEC.md` trong plan `vibomir`, **độ rộng window là đòn bẩy số 1**.
  - Điểm Chunk F2 đã **tăng vọt gấp 3 lần** (từ 0.0318 lên 0.0999), kéo FINAL SCORE lên 0.1182.
  - Điều này chứng minh việc "nới lỏng" độ rộng cửa sổ mang lại lợi ích khổng lồ do không bị phạt thêm Precision.
  - **Bước tiếp theo:** Đổi sang cửa sổ trượt động (`Dynamic Sliding Window`) với ngân sách chuẩn 1024 Token (~3200 ký tự) kết hợp hàm tính điểm Keyword thay vì cắt fix cứng `[100:2500]` để đạt điểm cao hơn nữa.

---

### Exp 09: Dynamic Window (2500 chars, top k=100)

- **Mục tiêu:** Thử nghiệm hàm trượt cửa sổ động `select_best_window` ưu tiên mật độ từ khóa, đồng thời giữ `win_chars = 2500` (để không vượt quá giới hạn file size 100MB của BTC khi nén file json bằng chuẩn Deflated thông thường).
- **Phương pháp:**
  - Docs: Giữ nguyên truy hồi bằng BM25s lấy top $k=100$.
  - Chunks: Chạy thuật toán Sliding Window để tìm đoạn văn (tối đa 2500 ký tự) có chứa nhiều từ khóa từ câu hỏi nhất, thay vì cắt đoạn đầu `[100:2500]` cứng nhắc như Exp 08.
- **Kết quả:**
  - `FINAL_SCORE: 0.1206` _(Tăng từ 0.1182)_
  - `DOCS_F2MACRO: 0.1366` | `DOCS_PRECISION: 0.1048` | `DOCS_RECALL: 0.1821`
  - `CHUNKS_F2MACRO: 0.1047` | `CHUNKS_PRECISION: 0.0826` | `CHUNKS_RECALL: 0.1381`
- **Phân tích kết quả (Key Insights):**
  - **Chunk F2 tiếp tục tăng:** Việc trượt tìm đoạn chứa nhiều keyword đã giúp cắt đoạn chính xác hơn, nâng CHUNKS F2 từ 0.0999 lên 0.1047 (+4.8%).
  - Mốc `FINAL_SCORE` vượt 0.12 đầu tiên trong lịch sử log. Việc giữ Window Size = 2500 tỏ ra tối ưu, vượt qua bài test giới hạn 100MB cho phép nộp file thành công mà không phải đánh đổi Recall.

---

### Exp 10: Dynamic Window (3200 chars, top k=70)

- **Mục tiêu:** Khai thác tối đa giới hạn 1024 tokens chuẩn (tương đương 3200 ký tự) để lấy ngữ cảnh đầy đủ hơn, nâng điểm Chunk Recall. Tuy nhiên, vì 3200 ký tự $\times$ 100 docs vượt quá 100MB khi zip, ta buộc phải đánh đổi bằng cách giảm số lượng Docs nộp (giảm $k$ từ 100 xuống 70).
- **Phương pháp:**
  - Docs: Giảm số ứng viên lấy từ BM25s xuống top $k=70$ (thay vì 100).
  - Chunks: Sử dụng Dynamic Sliding Window với max size `win_chars = 3200`.
- **Kết quả:**
  - `FINAL_SCORE: 0.1156` _(Giảm từ 0.1206)_
  - `DOCS_F2MACRO: 0.1278` | `DOCS_PRECISION: 0.1226` | `DOCS_RECALL: 0.1553`
  - `CHUNKS_F2MACRO: 0.1034` | `CHUNKS_PRECISION: 0.1012` | `CHUNKS_RECALL: 0.1254`
- **Phân tích kết quả:**
  - **Đánh đổi Recall là sai lầm:** Khi giảm top $k=70$, DOCS RECALL đã rớt thẳng từ 18.21% xuống 15.53% (mất gần 3%). Kéo theo đó, mặc dù độ rộng Chunk 3200 ký tự giúp Docs Precision và Chunk Precision tăng lên cao nhất lịch sử (tương ứng 12.26% và 10.12%), nhưng công thức F2 Macro của BTC thiên vị Recall cực nặng (Recall trọng số 4 so với Precision trọng số 1).
  - **Kết luận:** **Tuyệt đối không giảm $k$ xuống dưới 100 (tốt nhất là giữ $k \ge 100$).** Việc hy sinh Document Recall để chừa dung lượng cho Chunk lớn hơn đem lại bất lợi ("lợi bất cập hại"). Lộ trình tốt nhất để tăng điểm lúc này là dùng $k=100$, ép `win_chars = 2500` như Exp 09 và tìm cách mở rộng truy vấn (Multilingual BM25) hoặc dùng mô hình phân giải để tăng Docs Recall từ 18% lên 30% thay vì can thiệp vào Chunk quá lớn gây phình dung lượng.

---

### Exp 11: Multilingual BM25 + RRF + NLLB Translation

- **Mục tiêu:** Áp dụng mô hình dịch thuật local (NLLB-200 600M) chạy trực tiếp trên GPU Kaggle để mở rộng truy vấn (VI -> EN, ZH) kết hợp với RRF (công thức $k=60$). Đánh giá tính khả thi và hiệu năng của mô hình dịch nhỏ gọn này trong ngữ cảnh y tế.
- **Phương pháp:**
  - Notebook: `09_baseline_bm25_chunk_submission.ipynb`.
  - Dịch Query: Dùng mô hình `facebook/nllb-200-distilled-600M` để dịch sang tiếng Anh và tiếng Trung.
  - Fusion: Chạy 3 luồng BM25s cho 3 ngôn ngữ (mỗi luồng lấy top 300 docs) và kết hợp điểm bằng RRF (công thức k=60), sau đó lấy ra top 100 docs cuối cùng.
  - Chunking: Lấy tối đa 2500 ký tự (sử dụng Sliding Window nếu có). Sau đó ở bước tạo file submission, tiến hành cắt bỏ 100 từ đầu tiên ở mỗi chunk để file zip nộp xuống dưới giới hạn 100MB của BTC (chỉ còn 73.9MB).
- **Kết quả:**
  - `FINAL_SCORE: 0.0679` _(Giảm mạnh từ mốc 0.1206 của Exp 09)_
  - `DOCS_F2MACRO: 0.0803` | `DOCS_PRECISION: 0.0570` | `DOCS_RECALL: 0.1137`
  - `CHUNKS_F2MACRO: 0.0554` | `CHUNKS_PRECISION: 0.0403` | `CHUNKS_RECALL: 0.0778`
- **Phân tích kết quả:**
  - **Docs Recall rớt nghiêm trọng:** So với BM25s thuần (Exp 03, Recall 18.21%), việc dùng NLLB dịch truy vấn kết hợp RRF lại làm Recall tụt xuống 11.37%.
    - _Nguyên nhân:_ Mô hình NLLB-200 600M là mô hình nhỏ gọn nên chất lượng dịch thuật ngữ y khoa chuyên sâu từ tiếng Việt sang EN/ZH có khả năng chưa đủ tốt hoặc bị sai nghĩa. Điều này dẫn tới 2 luồng truy hồi EN và ZH bị nhiễu. Khi kết hợp RRF, những kết quả sai này đã vô tình đẩy các tài liệu chuẩn xác (từ luồng VI) rớt hạng xuống khỏi Top 100.
  - **Chunk F2 thấp do thủ thuật cắt từ:** Việc loại bỏ 100 từ đầu tiên (để "ép" dung lượng zip) thực chất lại gọt mất một lượng lớn thông tin then chốt (do nhiều bài báo trả lời trực tiếp câu hỏi ở phần tóm tắt đầu bài). Điều này trực tiếp kéo Chunk Recall xuống mức thấp (0.0778).
  - **Bài học rút ra:** Việc dịch tự động bằng translation model nhẹ không phải lúc nào cũng tối ưu cho độ chính xác cao. Lời đề nghị sử dụng chuẩn từ điển y khoa ICD-10 của user rất chính xác. Khâu Query Expansion nên ưu tiên dùng các bộ Map/Ontology y khoa chuẩn hóa thay vì RRF đa ngôn ngữ bằng mô hình dịch nhỏ. Kế đó, cần một chiến lược chunking thông minh hơn thay vì gọt xén bớt đầu đuôi.

---

### Exp 12: BGE-M3 Dense Search (400k docs, top 10)

- **Mục tiêu:** Thử nghiệm phương pháp tìm kiếm Dense Retrieval trực tiếp bằng model `BAAI/bge-m3` trên tập 400.000 tài liệu đầu tiên đã được lập chỉ mục (index).
- **Phương pháp:**
  - Embedding: Dùng BGE-M3 mã hóa query và đối chiếu (dot product) với index của 400k docs.
  - Ranking: Kết hợp điểm từ 4 khối 100k, lấy ra top các chunks.
  - Lỗi cấu hình: Do nhầm lẫn trong code `run_local_submission.py`, thuật toán đã giới hạn `relevant_docs` ở mức tối đa **10 docs** thay vì 100 docs (mức thực nghiệm cho thấy đem lại điểm Recall tốt).
- **Kết quả:**
  - `FINAL_SCORE: 0.0621`
  - `DOCS_F2MACRO: 0.0717` | `DOCS_PRECISION: 0.3250` | `DOCS_RECALL: 0.0633`
  - `CHUNKS_F2MACRO: 0.0526` | `CHUNKS_PRECISION: 0.2506` | `CHUNKS_RECALL: 0.0462`
- **Phân tích kết quả:**
  - **Precision tăng rất mạnh:** Docs Precision lên đến **32.50%** và Chunk Precision lên đến **25.06%**. Điều này cho thấy khả năng matching vector của BGE-M3 cực kỳ chính xác. Những tài liệu và đoạn trích mà nó đẩy lên đầu đa phần là rất đúng.
  - **Recall rớt thê thảm:** Do nộp tối đa có 10 docs, model bỏ sót phần lớn ground truth (Docs Recall chỉ đạt 6.33%). Vì công thức tính của Kaggle (F2 Macro) phạt rất nặng lỗi Recall thấp, nên Final Score bị kéo tụt xuống mức 0.0621.
  - **Hướng khắc phục:** Sửa lại code `run_local_submission.py` để nộp đủ **100 docs** (để tối đa hóa Recall theo kinh nghiệm) và **10 chunks** như quy định. Với Precision cao như vậy, khi mở rộng lên 100 docs, điểm số hứa hẹn sẽ tăng vọt. Kế hoạch tiếp theo là chạy nốt index cho phần còn lại của tập 2.1 triệu tài liệu.

---

### Exp 13: BGE-M3 Dense Search (400k docs, top 100)

- **Mục tiêu:** Kiểm tra lại điểm số sau khi fix code lấy đủ top 100 relevant docs (thay vì 10 docs như Exp 12) trên cùng tập 400.000 tài liệu đầu tiên.
- **Phương pháp:**
  - Tương tự Exp 12, nhưng tăng giới hạn xuất file từ 10 docs lên 100 docs.
- **Kết quả:**
  - `FINAL_SCORE: 0.1076`
  - `DOCS_F2MACRO: 0.1626` | `DOCS_PRECISION: 0.1326` | `DOCS_RECALL: 0.2079`
  - `CHUNKS_F2MACRO: 0.0526` | `CHUNKS_PRECISION: 0.2506` | `CHUNKS_RECALL: 0.0462`
- **Phân tích kết quả (Chiến thắng của Dense Retrieval):**
  - **Docs Recall bứt phá:** Chỉ với 400.000 tài liệu (tức là **chưa đến 20%** của toàn bộ 2.1 triệu tài liệu), mô hình Dense Retrieval đã đạt Recall **20.79%**!
  - So sánh với BM25 ở Exp 03 (chạy trên _toàn bộ_ 2.1 triệu tài liệu, top 100), BM25 chỉ đạt Recall **18.21%**.
  - Điều này chứng minh sức mạnh áp đảo của Embedding: nó tìm ra ground truth tốt hơn hẳn thuật toán từ khóa truyền thống. Việc điểm FINAL_SCORE vẫn ở mức 0.1076 (chưa vượt qua mốc 0.12) hoàn toàn là do **chưa đủ vector** (còn 1.7 triệu tài liệu chưa được index).
  - Điểm Chunk giữ nguyên so với Exp 12 vì giới hạn chunks vẫn là 10 và các chunk tốt nhất đều đã được đẩy lên đầu trong top 10, nên việc mở rộng danh sách docs lên 100 không làm thay đổi top 10 chunks.
  - **Bước tiếp theo:** Ưu tiên số 1 hiện tại là lập chỉ mục (index) toàn bộ 1.7 triệu tài liệu còn lại. Khi có đủ kho dữ liệu, Recall có thể sẽ bùng nổ lên mức rất cao!

---

### Exp 14: BGE-M3 Dense Search (400k docs, top 100 chunks)

- **Mục tiêu:** Cập nhật file nộp bài sau khi phát hiện và loại bỏ hardcode `len(relevant_chunks) < 10` trong `run_local_submission.py`. BTC không giới hạn số chunk nộp. Cho phép xuất tối đa 100 chunks.
- **Phương pháp:**
  - Giữ nguyên khối 400k docs. Cấu hình lấy `100` relevant docs và `100` relevant chunks (giới hạn 100).
- **Kết quả:**
  - `FINAL_SCORE: 0.1557` (Kỷ lục mới!)
  - `DOCS_F2MACRO: 0.1626` | `DOCS_PRECISION: 0.1326` | `DOCS_RECALL: 0.2079`
  - `CHUNKS_F2MACRO: 0.1488` | `CHUNKS_PRECISION: 0.1279` | `CHUNKS_RECALL: 0.1854`
- **Phân tích kết quả:**
  - **Kỷ lục mới bị phá vỡ:** Việc tăng chunk từ 10 lên 100 đã khiến **CHUNKS_RECALL nhảy vọt từ 4.62% lên 18.54%** (tăng gấp 4 lần)! Điều này đẩy điểm CHUNKS_F2MACRO lên 0.1488, qua đó kéo `FINAL_SCORE` lên mốc **0.1557** cao nhất từ đầu cuộc thi tới giờ.
  - Sức mạnh của Dense Retrieval: Điểm cao nhất trước đó là Exp 09 (0.1206) có được sau khi chạy thuật toán Sliding Window tinh xảo qua **2.1 triệu tài liệu**. Ở Exp 14 này, dù chỉ mới lấy **19% dữ liệu**, chúng ta đã vượt mốc 0.15.
  - **Bước tiếp theo (Bắt buộc):** Chạy tiếp index trên phần 1.7 triệu tài liệu còn lại. Khi 100% dữ liệu có vector, Final Score hứa hẹn sẽ bùng nổ vượt 0.2 hoặc cao hơn nữa.

---

### Exp 15: BGE-M3 Dense Search (700k docs, top 100 chunks)

- **Mục tiêu:** Cập nhật kết quả truy xuất Dense Retrieval sau khi có thêm 300k tài liệu mới (400-700k) được lập chỉ mục.
- **Phương pháp:**
  - Kho dữ liệu: 700,000 tài liệu.
  - Vẫn sử dụng `run_local_submission.py` để rút top 100 docs, top 100 chunks.
- **Kết quả:**
  - `FINAL_SCORE: 0.1570` (Kỷ lục mới!)
  - `DOCS_F2MACRO: 0.1646` | `DOCS_PRECISION: 0.1348` | `DOCS_RECALL: 0.2093`
  - `CHUNKS_F2MACRO: 0.1494` | `CHUNKS_PRECISION: 0.1287` | `CHUNKS_RECALL: 0.1855`
- **Phân tích kết quả:**
  - Điểm `FINAL_SCORE` tiếp tục nhích lên (0.1557 -> 0.1570).
  - Độ bao phủ (Recall) của Document và Chunk đều tăng nhẹ khi có thêm dữ liệu (DOCS_RECALL từ 0.2079 lên 0.2093, CHUNKS_RECALL từ 0.1854 lên 0.1855).
  - Điểm F2MACRO của Docs tăng từ 0.1626 lên 0.1646, cho thấy độ chính xác và tính đầy đủ của các tài liệu tìm được đang đi đúng hướng.
  - Việc `tier_1.parquet` vừa được tổng hợp đầy đủ lên mức ~1.19 triệu bài hứa hẹn khi cắm vào chạy nối tiếp (resume) sẽ bứt phá mạnh hơn nữa.

---

### Exp 16: BGE-M3 Hybrid Retrieval (Dense 1.0 + Sparse Lexical 0.3, 700k docs)

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

### Exp 17: BGE-M3 Hybrid Retrieval (Dense 1.0 + Sparse 0.5, 700k docs)

- **Mục tiêu:** Thử nghiệm đẩy mạnh trọng số Sparse Lexical từ `0.3` lên `0.5` theo khuyến nghị của tác giả BGE-M3 nhằm tối ưu hơn nữa khả năng neo từ khóa y khoa.
- **Cấu hình & Tham số:**
  - `dense_weight = 1.0` | `sparse_weight = 0.5`
  - File nộp: `submission_bgem3_hybrid_w05.zip` (96.88 MB, 100 docs, 92 chunks)
- **Kết quả:**
  - `FINAL_SCORE: 0.1641` _(Giảm nhẹ -0.0043 so với Exp 16: 0.1684)_
  - `DOCS_F2MACRO: 0.1720` | `DOCS_PRECISION: 0.1397` | `DOCS_RECALL: 0.2181`
  - `CHUNKS_F2MACRO: 0.1562` | `CHUNKS_PRECISION: 0.1411` | `CHUNKS_RECALL: 0.1890`
- **Phân tích Đột phá (Root Cause Analysis - Hiện tượng Lệch pha Ngôn ngữ trong Sparse Retrieval):**
  - **Điểm tích cực:** `CHUNKS_PRECISION` tiếp tục tăng lên mức cao kỷ lục mới **`0.1411`** (tăng từ 0.1398). Điều này khẳng định tăng trọng số từ vựng giúp các đoạn văn được chọn lọc vô cùng chuẩn xác.
  - **Lý do Recall và Final Score sụt giảm:**
    1. **Bản chất Corpus đa ngôn ngữ:** Tập dữ liệu của BTC chứa một tỷ lệ rất lớn tài liệu tiếng Trung (các domain hàng đầu như `120ask.com`, `youlai.cn`, `cnkang.com`, `zhongyibaodian.net`...).
    2. **Sparse Lexical chỉ match đồng ngôn ngữ:** Truy vấn của bài thi là **Tiếng Việt**. Mô hình Dense Vector (1024d) của BGE-M3 là mô hình liên ngôn ngữ (Cross-lingual continuous space), nên query tiếng Việt vẫn tìm được tài liệu tiếng Trung rất tốt. Tuy nhiên, ma trận Sparse Lexical dựa trên token vocabulary rời rạc (XLM-RoBERTa vocab): từ tiếng Việt (`tiểu đường`) và từ tiếng Trung (`糖尿病`) có token ID hoàn toàn khác nhau, dẫn tới điểm Sparse giữa query tiếng Việt và tài liệu tiếng Trung luôn bằng **0.0**!
    3. **Hiệu ứng dìm tài liệu tiếng Trung:**
       - Tài liệu tiếng Việt nhận: $1.0 \times \text{Dense} + 0.5 \times \text{Sparse}$.
       - Tài liệu tiếng Trung chỉ nhận: $1.0 \times \text{Dense} + 0.0 \times \text{Sparse}$.
         👉 Khi $w_s$ tăng từ $0.3 \rightarrow 0.5$, khoảng cách điểm này càng bị kéo giãn, khiến các tài liệu tiếng Trung chuẩn xác bị tài liệu tiếng Việt "chen hàng" đẩy văng khỏi Top 100 docs và Top chunks. Kéo theo `DOCS_RECALL` rớt từ `22.28%` xuống `21.81%`.
- **Chiến lược & Hướng giải quyết mới (Multilingual Query Translation):**
  - Không cần nộp phương án B (`w_s = 0.7`) vì sẽ càng dìm tài liệu tiếng Trung mạnh hơn.
  - Nghiên cứu mô hình dịch thuật mở (Open-source $\le 15\text{B}$, phát hành trước 01/08/2026) để dịch query tiếng Việt $\rightarrow$ Tiếng Trung & Tiếng Anh. Khi đó:
    $$Q_{\text{sparse}} = \text{Merge}\big(\text{Sparse}(Q_{\text{vi}}), \text{Sparse}(Q_{\text{zh}})\big)$$
    Cả tài liệu tiếng Trung và tiếng Việt đều sẽ nhận được trọn vẹn điểm thưởng Lexical Matching, hứa hẹn tạo nên bước nhảy vọt Recall chưa từng có!

---

### Exp 18: Reciprocal Rank Fusion (RRF) (Dense 1.0 + Sparse 0.8, k=60)

- **Mục tiêu:** Thử nghiệm thuật toán Reciprocal Rank Fusion (RRF) nhằm giải quyết sự khác biệt về biên độ phân phối điểm (score scale) giữa Dense Cosine Similarity và Sparse Lexical Dot-Product.
- **Cấu hình & Tham số:**
  - `fusion = rrf` | `dense_weight = 1.0` | `sparse_weight = 0.8` | `rrf_k = 60` | `cand_pool = 150`
  - File nộp: `submission_bgem3_rrf_w08.zip`
- **Kết quả:**
  - `FINAL_SCORE: 0.1483` _(Sụt giảm -0.0201 so với Exp 16: 0.1684)_
  - `DOCS_F2MACRO: 0.1559` | `DOCS_PRECISION: 0.1252` | `DOCS_RECALL: 0.1996`
  - `CHUNKS_F2MACRO: 0.1408` | `CHUNKS_PRECISION: 0.1229` | `CHUNKS_RECALL: 0.1730`
- **Phân tích nguyên nhân (Why RRF Underperformed):**
  1. **Triệt tiêu cường độ tín hiệu Cosine (Loss of Continuous Distance Confidence):** Dense Cosine Similarity phản ánh độ tin cậy liên tục rất nhạy (ví dụ cosine `0.88` so với `0.70` là một khoảng cách ngữ nghĩa cực kỳ lớn). Tuy nhiên công thức RRF $\frac{1}{60 + \text{rank}}$ chỉ quan tâm đến thứ hạng cục bộ, biến rank 1 thành $\approx 0.01639$ và rank 2 thành $\approx 0.01613$, triệt tiêu hoàn toàn ưu thế của những tài liệu có độ tin cậy ngữ nghĩa vượt trội.
  2. **Hiệu ứng phân mảnh đa phân mảnh (Multi-shard Partitioning Artifact):** Vì dữ liệu được chia theo từng shard (100k docs/shard) và chỉ giữ lại `cand_pool = 150` ứng viên mỗi shard trước khi RRF toàn cục, các tài liệu có điểm Dense rất cao ở một shard đơn lẻ dễ bị bất lợi so với các tài liệu xuất hiện rank trung bình ở nhiều phân mảnh.
  3. **Kết luận:** Linear Score Fusion vượt trội hơn hẳn RRF trong bài toán này nhờ giữ nguyên được độ tự tin khoảng cách (distance metric confidence).

---

### Exp 19: BGE-M3 Linear Hybrid Sweet-Spot (Dense 1.0 + Sparse 0.2, 700k docs) 🏆

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

### Exp 20: Pure BM25 via SQLite FTS5 (1.35M docs)

- **Mục tiêu:** Kiểm chứng giả thuyết (tin đồn từ Top 1) rằng "chỉ cần cào hết data và chạy BM25 là điểm sẽ > 0.3x".
- **Phương pháp:**
  - Lập chỉ mục bằng **SQLite FTS5** trên `tier_1_resume.parquet` và `tier_other.parquet` (tổng cộng **1.358.107 bài viết**). Chú ý: file `tier_2.parquet` (254k docs) bị lỗi I/O nên không được nạp.
  - Tokenization: Dùng `unicode61` mặc định của SQLite (bỏ dấu tiếng Việt).
  - Search: Nối các từ trong query bằng `OR` (`MATCH 'từ1 OR từ2'`).
  - Chunking: Hàm `sliding_window_extract` tìm đoạn 2500 ký tự chứa nhiều keyword nhất.
- **Kết quả:**
  - `FINAL_SCORE: 0.0677` _(Rất thấp, ngang ngửa với Exp 06)_
  - `DOCS_F2MACRO: 0.0736` | `DOCS_PRECISION: 0.0589` | `DOCS_RECALL: 0.0965`
  - `CHUNKS_F2MACRO: 0.0617` | `CHUNKS_PRECISION: 0.0512` | `CHUNKS_RECALL: 0.0798`
- **Phân tích Đột phá (Bác bỏ giả thuyết "Chỉ cần BM25 là 0.3x"):**
  1. **Điểm số quá tệ:** Document Recall chỉ đạt **9.65%**, thấp hơn rất nhiều so với phương pháp Dense Hybrid (Recall 22.3% trên 700k docs) dù kho dữ liệu lớn gần gấp đôi (1.35M docs).
  2. **Nguyên nhân cốt lõi từ SQLite FTS5:**
     - _Diacritic Stripping:_ FTS5 mặc định bỏ dấu tiếng Việt (ví dụ `đường` -> `duong`), gây nhiễu loạn ngữ nghĩa nghiêm trọng.
     - _Nhiễu Stopword:_ Không có bước loại bỏ stopword ("của", "và", "những"). Khi query bằng toán tử `OR`, các tài liệu chứa nhiều từ nối (nhưng không liên quan đến bệnh) sẽ bị đẩy rank lên rất cao.
     - _Unigram Matching:_ Tiếng Việt đa phần là từ ghép (bi-gram). BM25 dựa trên unigram không thể phân biệt "bệnh viện" với các tài liệu có từ "bệnh" và từ "viện" nằm rải rác.
  3. **Tác động từ việc mất `tier_2`:** Việc hụt mất 250k tài liệu chắc chắn làm giảm Recall, nhưng không đủ để giải thích mức sụt giảm khổng lồ từ mốc "tin đồn" 0.3x xuống tận 0.06x.
- **Kết luận (Next Steps):**
  - Giả thuyết "Chỉ cần BM25 là 0.3x" bị bác bỏ (ít nhất là với cách implement BM25 thô sơ này). Rất có thể Top 1 đã ám chỉ "BM25 có bộ Analyzer/Tokenizer tiếng Việt chuẩn (như Elasticsearch + VnCoreNLP) kết hợp hybrid", hoặc pipeline của họ xịn hơn rất nhiều.
  - Hướng đi đúng đắn nhất của đội chúng ta vẫn là **Hybrid Retrieval (BGE-M3 Dense + Sparse)**. Việc cần làm ngay bây giờ là tạo vector embedding cho toàn bộ 1.35M docs này thay vì dùng BM25 thuần túy.

---

### Exp 21: BGE-M3 Linear Hybrid Sweet-Spot + Bổ sung Tier 2 (Corpus Trung Quốc) 🏆🚀

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

### Exp 22: BGE-M3 Linear Hybrid Khắt khe (Top k = 10 Docs & Chunks)

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

### Exp 23: BGE-M3 Linear Hybrid (Top 200 Docs & 100 Chunks) 🚀

- **Mục tiêu:** Mở rộng số lượng tài liệu truy hồi lên gấp đôi (`top_docs = 200`) để kiểm chứng khả năng tối đa hóa Docs Recall, đồng thời giữ nguyên ngân sách đoạn văn tối đa cho phép (`top_chunks = 100`) với cơ chế nén bảo vệ dung lượng ZIP < 98 MB.
- **Cấu hình & Siêu tham số:**
  - Lệnh: `python scripts/run_submission.py --mode hybrid --fusion linear --dense_weight 1.0 --sparse_weight 0.2 --top_docs 200 --top_chunks 100 --output submission_bgem3_top200_docs.json`
  - Nộp: 200 docs và 100 chunks per query. File ZIP nặng 94.11 MB (an toàn dưới ngưỡng 100 MB).
- **Kết quả:**
  - `FINAL_SCORE: 0.2110` _(Tương đương mốc đỉnh 0.2121 của Exp 21)_
  - `DOCS_F2MACRO: 0.2205` | `DOCS_PRECISION: 0.1183` | **`DOCS_RECALL: 0.3547`** 🥇 _(Kỷ lục Recall cao nhất lịch sử!)_
  - **`CHUNKS_F2MACRO: 0.2016`** 🥇 | `CHUNKS_PRECISION: 0.1675` | **`CHUNKS_RECALL: 0.2557`**
- **So sánh trực tiếp với Exp 21 (Top 100 Docs, 98 Chunks):**

  | Chỉ số (Metric)      | Exp 21 (Top 100 Docs) | Exp 23 (Top 200 Docs)  |      Chênh lệch (Delta)      |
  | :------------------- | :-------------------: | :--------------------: | :--------------------------: |
  | **FINAL SCORE**      |      **0.2121**       |         0.2110         |      -0.0011 (Cân bằng)      |
  | **DOCS RECALL**      |    0.2875 (28.75%)    | **0.3547 (35.47%)** 🥇 |    **+6.72% (+23.4%)** 🚀    |
  | **CHUNKS RECALL**    |    0.2536 (25.36%)    | **0.2557 (25.57%)** 🥇 |          **+0.21%**          |
  | **CHUNKS F2 MACRO**  |        0.2010         |     **0.2016** 🥇      |    **+0.0006 (Đỉnh mới)**    |
  | **CHUNKS PRECISION** |      **0.1692**       |         0.1675         |           -0.0017            |
  | **DOCS PRECISION**   |      **0.1802**       |         0.1183         | -0.0619 (Do chia mẫu số 200) |
  | **DOCS F2 MACRO**    |      **0.2233**       |         0.2205         |           -0.0028            |

- **Phân tích Đột phá (Key Insights):**
  1. **Bước nhảy vọt lịch sử về Recall (35.47%):**
     - Khi mở rộng từ 100 lên 200 docs, **DOCS_RECALL tăng vọt thêm +6.72%** (từ 28.75% lên 35.47%, tăng tương đối +23.4%).
     - Điều này chứng minh hơn **1/3 tổng số tài liệu Ground Truth của bài thi** đã nằm trong Top 200 ứng viên của mô hình BGE-M3!
     - Khoảng cách Recall với đội Top 1 (`45.78%`) đã được thu hẹp đáng kể (từ 17% xuống chỉ còn ~10%).
  2. **Bài toán Trade-off Precision vs. Recall:**
     - Do nộp 200 docs, mẫu số tính Docs Precision tăng gấp đôi, làm Docs Precision giảm từ 18.02% xuống 11.83%. Mức giảm Precision này đã kìm giữ Docs F2 ở mức 0.2205 (giảm nhẹ 0.0028) dù Recall tăng rất mạnh.
     - Về phía Chunk, do vẫn giữ nguyên `top_chunks = 100`, cả Chunks Recall và Chunks F2 đều đạt kỷ lục mới (**CHUNKS_F2 = 0.2016**).
  3. **Kết luận & Hướng tối ưu cho Stage 2 (Reranking):**
     - Thử nghiệm này khẳng định: **Stage 1 Candidate Pool với $k=200$ là cực kỳ hoàn hảo vì đã gom được tới 35.5% Recall**.
     - Để bứt phá lên Top 1 (0.42+), bước tiếp theo không phải là mò mẫm cắt tỉa Top-K thô, mà là **huấn luyện hoặc áp dụng một Cross-Encoder Reranker** (ví dụ Qwen2.5-7B/14B Reranker hoặc BGE Reranker fine-tuned) để re-rank lại 200 ứng viên này: lọc lấy Top 100–120 tài liệu chất lượng nhất để vừa giữ nguyên Recall ~35%+, vừa đẩy Docs Precision trở lại mức > 30%, đưa FINAL_SCORE nhảy vọt qua mốc **0.30 – 0.35+**!

---

### Exp 24: 2-Stage Retrieval + Cross-Encoder Reranker (`bge-reranker-v2-m3`) 🚀🔥

- **Mục tiêu:** Hiện thực hóa kiến trúc **2-Stage Retrieval** nhằm giải quyết triệt để bài toán mâu thuẫn giữa Recall và Precision (vấn đề của Exp 22 và Exp 23):
  - **Stage 1:** Sử dụng BGE-M3 Dense + Sparse Hybrid (RRF) quét toàn bộ 11 shards (`data/indices`) để lấy **Top 200 Candidate Docs** mỗi query (đảm bảo Recall thô $\ge 35\%$).
  - **Stage 2:** Sử dụng mô hình Cross-Encoder đa ngữ đỉnh cao **`BAAI/bge-reranker-v2-m3`** (FP16) với cơ chế tự động định tuyến ngôn ngữ (Cross-Lingual Query Routing: ghép `query_zh` khi chunk là tiếng Trung, giữ `query` gốc khi chunk tiếng Việt) để tính điểm cross-attention sâu giữa câu hỏi và đoạn văn bản.
  - **Output Filter:** Sắp xếp lại danh sách ứng viên theo điểm Reranker, sau đó cắt lọc lấy **Top 100 Docs** và **Top 98 Chunks** tốt nhất.
- **Cấu hình & Siêu tham số:**
  - Lệnh thực thi:
    ```powershell
    python scripts/run_submission.py `
      --mode hybrid `
      --fusion rrf `
      --dense_weight 1.0 `
      --sparse_weight 0.2 `
      --rerank `
      --rerank_cand_docs 200 `
      --top_docs 100 `
      --top_chunks 98 `
      --output submission_bgem3_rerank_cand200_top100.json
    ```
  - Reranker: `BAAI/bge-reranker-v2-m3` (FP16, batch_size=64, max_length=512).
  - VRAM Management: Tự động giải phóng `model` BGE-M3 và dọn bộ nhớ cache (`torch.cuda.empty_cache()`) trước khi tải Reranker, đảm bảo hoạt động an toàn tuyệt đối trên RTX 3050 Ti 4GB VRAM.
  - File ZIP sinh ra: [`submission_bgem3_rerank_cand200_top100.zip`](file:///d:/CODE%20PLAYGROUND/Projects/Competitions/R2AI-Stage-3-2026/submission_bgem3_rerank_cand200_top100.zip) dung lượng **82.78 MB** (đạt chuẩn an toàn `< 100 MB`).
- **Kết quả:**
  - `FINAL_SCORE: 0.1835` _(Giảm từ mốc 0.2121 của Exp 21 và 0.2110 của Exp 23)_
  - `DOCS_F2MACRO: 0.2024` | `DOCS_PRECISION: 0.1602` | `DOCS_RECALL: 0.2616`
  - `CHUNKS_F2MACRO: 0.1646` | `CHUNKS_PRECISION: 0.1361` | `CHUNKS_RECALL: 0.2086`

- **So sánh trực tiếp với Exp 21 và Exp 23:**

  | Chỉ số (Metric)      | Exp 21 (Linear Top 100) | Exp 23 (Linear Top 200) | Exp 24 (2-Stage Rerank: Top 200 $\to$ 100) | So với Exp 21 | So với Exp 23 |
  | :------------------- | :---------------------: | :---------------------: | :----------------------------------------: | :-----------: | :-----------: |
  | **FINAL SCORE**      |       **0.2121**        |         0.2110          |                   0.1835                   |  **-0.0286**  |  **-0.0275**  |
  | **DOCS RECALL**      |     0.2875 (28.75%)     | **0.3547 (35.47%)** 🥇  |              0.2616 (26.16%)               | **-2.59%** 🔻 | **-9.31%** 🔻 |
  | **DOCS PRECISION**   |   **0.1802 (18.02%)**   |     0.1183 (11.83%)     |              0.1602 (16.02%)               |    -2.00%     | **+4.19%** 🚀 |
  | **DOCS F2 MACRO**    |       **0.2233**        |         0.2205          |                   0.2024                   |    -0.0209    |    -0.0181    |
  | **CHUNKS RECALL**    |     0.2536 (25.36%)     | **0.2557 (25.57%)** 🥇  |              0.2086 (20.86%)               | **-4.50%** 🔻 | **-4.71%** 🔻 |
  | **CHUNKS PRECISION** |   **0.1692 (16.92%)**   |     0.1675 (16.75%)     |              0.1361 (13.61%)               |    -3.31%     |    -3.14%     |
  | **CHUNKS F2 MACRO**  |         0.2010          |      **0.2016** 🥇      |                   0.1646                   |    -0.0364    |    -0.0370    |

- **Phân tích Chuyên sâu (Key Insights & Root Cause Analysis):**
  1. **Hiện tượng "Negative Transfer" của Zero-shot Cross-Encoder:**
     - Mô hình `BAAI/bge-reranker-v2-m3` là một mô hình tổng quát (General-domain), chưa được tinh chỉnh (fine-tune) trên tập câu hỏi - đáp y khoa chuyên sâu của cuộc thi.
     - Khi cho Cross-Encoder chấm điểm thuần túy và sắp xếp lại, mô hình có xu hướng chấm điểm cao cho các văn bản chứa các từ vựng trùng lặp bề mặt (lexical overlap) hoặc bài viết sức khỏe đời sống chung chung, trong khi các tài liệu chuyên ngành thực sự (Ground Truth) lại bị đẩy tụt xuống sau vị trí 100.
     - Hậu quả: **DOCS_RECALL bị rơi từ 35.47% (Exp 23) xuống chỉ còn 26.16%** (thậm chí thấp hơn cả 28.75% của Exp 21 không dùng reranker).
  2. **Sai lầm khi loại bỏ hoàn toàn điểm số Stage 1 (Hard Replacement vs. Score Interpolation):**
     - Hiện tại trong Exp 24, thứ hạng cuối cùng được quyết định **100% bởi điểm Reranker**. Điều này làm mất đi hoàn toàn "mỏ neo" ngữ nghĩa toàn cục và điểm số lexical matching cực chuẩn mà BGE-M3 (Dense + Sparse) đã tính toán.
     - Trong Information Retrieval chuẩn công nghiệp, không bao giờ dùng Reranker thay thế hoàn toàn điểm Stage 1 nếu Reranker chưa được fine-tune in-domain. Giải pháp chuẩn là **kết hợp trọng số (Interpolation / Fusion)**:
       $$\text{Score}_{\text{final}} = \text{Score}_{\text{Stage1}} + \alpha \cdot \text{Score}_{\text{Reranker}}$$
       hoặc dùng Reciprocal Rank Fusion (RRF) kết hợp Rank Stage 1 và Rank Reranker.
  3. **Yếu tố Fusion (RRF vs. Linear) ở Stage 1:**
     - Cấu hình đỉnh cao ở Exp 21 dùng `--fusion linear --dense_weight 1.0 --sparse_weight 0.2` (cộng tuyến tính dot product giữa Dense và Sparse).
     - Ở Exp 24, script lại dùng `--fusion rrf`, vốn dựa vào thứ hạng nghịch đảo $1 / (60 + rank)$, khiến cho tập ứng viên 200 tài liệu ban đầu bị biến đổi so với Exp 21.
  4. **Kết luận Chiến lược:**
     - Tạm thời **không dùng Zero-shot Cross-Encoder thay thế hoàn toàn điểm số**.
     - Nếu muốn tiếp tục tăng điểm ngay lập tức:
       - **Phương án 1 (Ổn định nhất):** Quay về kiến trúc **Linear Hybrid (w=0.2)** của Exp 21 / Exp 23.
       - **Phương án 2 (Ensemble / Interpolation):** Giữ Stage 1 là Linear Hybrid (Exp 21/23), nếu dùng Reranker thì phải kết hợp điểm số $\text{Score}_{\text{Stage1}} + \alpha \cdot \text{Score}_{\text{Rerank}}$ thay vì ghi đè hoàn toàn.
       - **Phương án 3 (Mở rộng Corpus - Lõi cốt tử):** Tiếp tục lập chỉ mục (index) các khối Tier 2 còn thiếu (như `ask.39.net`, `120ask.com`) vì dữ liệu thực tế chứng minh mỗi khi nạp thêm dữ liệu cào được, Recall tăng vọt từ 20% lên 28% và 35%.
