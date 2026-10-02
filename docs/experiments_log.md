# Nhật ký Thử nghiệm & Benchmark (Experiment Logs)

Tài liệu này lưu trữ kết quả của các lần submit và thử nghiệm mô hình, nhằm theo dõi sự cải thiện (hoặc sụt giảm) hiệu năng qua từng thay đổi trong Pipeline. Chúng ta sẽ dùng điểm Baseline của BTC làm mốc đối chiếu (Mốc 0).

## 1. Bảng Xếp hạng Nội bộ (Leaderboard)

| Ngày       | Lần thử (Experiment)                     | FINAL SCORE | DOCS F2 | CHUNKS F2 | DOCS P | DOCS R | CHUNKS P | CHUNKS R | Ghi chú                                                                             |
| :--------- | :--------------------------------------- | :---------- | :------ | :-------- | :----- | :----- | :------- | :------- | :---------------------------------------------------------------------------------- |
| 2026-09-30 | **BM25 Baseline (BTC)**                  | **0.3764**  | 0.5587  | 0.1941    | 0.8805 | 0.5146 | 0.3403   | 0.1755   | Baseline cơ bản chỉ sử dụng BM25 (Sparse Retrieval).                                |
| 2026-10-01 | **Exp 01: Format Error (String ID)**     | **0.0000**  | 0.0000  | 0.0000    | 0.0000 | 0.0000 | 0.0000   | 0.0000   | Lỗi định dạng: `doc_id` kiểu string thay vì integer, server chấm 0 điểm toàn bộ.    |
| 2026-10-02 | **Exp 02: BM25s (2.1M docs, top k=5)**   | **0.0000**  | 0.0000  | 0.0000    | 0.0000 | 0.0000 | 0.0000   | 0.0000   | BM25s trên 2.1M docs, chỉ lấy top 5 docs. Quá hẹp, không trúng tài liệu nào.        |
| 2026-10-02 | **Exp 03: BM25s (2.1M docs, top k=100)** | **0.0683**  | 0.1366  | 0.0000    | 0.1048 | 0.1821 | 0.0000   | 0.0000   | Mở rộng top-100: Docs Recall lên 18.21%, Docs P 10.48%. Chunk chưa nộp/trúng (0.0). |
| 2026-10-02 | **Exp 04: BM25s (2.1M docs, top k=500)** | **0.0594**  | 0.1188  | 0.0000    | 0.0408 | 0.3115 | 0.0000   | 0.0000   | Mở rộng top-500: Docs Recall tăng vọt lên 31.15% (+13%), Precision giảm, Chunk 0.0. |

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
