# Báo cáo Nghiên cứu Kỹ thuật và Chiến thuật từ các Đội Top (R2AI Stage 1 & 2)

Dựa trên mã nguồn và tài liệu kỹ thuật (README) của các đội top đầu trong hai cuộc thi R2AI Stage 1 (Truy hồi & Hỏi đáp Pháp luật) và R2AI Stage 2 (Text-to-Pandas Báo cáo tài chính), dưới đây là tổng hợp các mô hình, kỹ thuật và chiến thuật cốt lõi đã giúp họ đạt được vị trí cao.

---

## 1. R2AI Stage 1: Legal AI Assistant (Truy hồi & Hỏi đáp Pháp luật)

Bài toán yêu cầu truy hồi chính xác các Điều luật từ tập tài liệu quy phạm pháp luật và sinh câu trả lời có trích dẫn nguồn.

### Đội MSCAI (Giải Nhất)

- **Chiến thuật cốt lõi:** Pure RAG (Không Fine-tuning). Tập trung vào kiến trúc hệ thống ổn định và prompt engineering thay vì fine-tune phức tạp.
- **Mô hình (LLM & Embedding):**
  - LLM: **Qwen3.5-9B** (phiên bản custom `qwen-vbpl` để mở rộng context window lên 16k tokens, phù hợp với RAG). Phục vụ qua Ollama.
  - Embedding: **bge-m3** (1024-dim, đa ngôn ngữ hỗ trợ tiếng Việt tốt).
- **Pipeline Truy hồi (Retrieval):**
  - Hybrid Search: Kết hợp Vector Search (Dùng Qdrant/Chroma embedded) và Sparse Search (BM25).
  - Lọc dữ liệu nghiêm ngặt: Chỉ lấy tập văn bản thuộc phạm vi Doanh nghiệp / SME để giảm nhiễu (noise) trong vector space.
- **Kỹ thuật sinh (Generation):**
  - Prompt ép LLM bắt buộc phải trích dẫn theo format `[Điều X, Khoản Y, Tên văn bản]`.
  - Tắt reasoning chain (đặt `reasoning_effort=none`) để tăng tốc độ và tránh model sinh lan man.

### Đội Nguyễn Văn Nghiêm (Giải Ba - Điển hình về Kỹ thuật tối ưu)

- **Chiến thuật cốt lõi:** Pipeline Multi-stage phức tạp giúp làm sạch dữ liệu qua từng tầng. "Reranker chỉ hiệu quả khi input sạch".
- **Mô hình (Toàn bộ dưới 14B parameter):**
  - LLM: **Qwen3-8B-AWQ**.
  - Embedding: **Vietnamese_Embedding_v2** (568M) kết hợp FAISS.
  - Reranker: **Vietnamese_Reranker fine-tuned** (trên tập hard negatives).
  - Classifier: **Qwen3-1.7B-Base + LoRA** để làm bộ lọc hậu xử lý (Post-processing).
- **Kỹ thuật RAG nâng cao:**
  - **Query Decomposition:** Dùng LLM tách câu hỏi phức tạp thành 1-3 sub-queries.
  - **HyDE (Hypothetical Document Embeddings):** LLM sinh ra một "Điều luật giả định" để query vào Vector DB thay vì query trực tiếp.
  - **Intersection Pool:** Lấy giao tập (Intersection) của Dense Candidates (từ HyDE) và Sparse Candidates (từ BM25S có kết hợp Synthetic QA) để giảm 70% noise trước khi đưa vào Reranker.
- **Hậu xử lý (Post-processing Classifier):**
  - Dùng mô hình 1.7B (LoRA) chấm điểm độc lập từng Điều luật được truy hồi: loại bỏ các False Positives và thêm vào các đoạn có high-confidence.
- **Anti-hallucination:** Tách riêng System/User prompt, yêu cầu LLM "chỉ trích dẫn từ context" và chốt lại bằng "Căn cứ pháp lý".

---

## 2. R2AI Stage 2: Financial Text-to-Pandas

Bài toán yêu cầu truy hồi các bảng dữ liệu báo cáo tài chính và sinh mã Python (Pandas) để tự động tính toán ra câu trả lời cuối cùng.

### Đội LASTDANCE (Giải Nhất)

- **Chiến thuật cốt lõi:** End-to-end execution. Mọi câu trả lời phải được sinh ra từ việc thực thi một Pandas Script trong môi trường hộp cát (sandbox).
- **Mô hình sử dụng:**
  - Planner/Reranker: **Qwen2.5-14B-Instruct**.
  - Critic (Kiểm định): **DeepSeek-R1-Distill-Qwen-14B**.
  - Tiebreak/Critic: **Qwen3-14B**.
- **Kỹ thuật thực thi:**
  - Xây dựng kho dữ liệu (Warehouse) dưới dạng SQLite + FTS5.
  - Trích xuất _Evidence CSV_ từ các bảng dữ liệu gốc. Sau đó, LLM sinh ra _Pandas Query_ để chạy trực tiếp trên file CSV này thay vì bắt LLM tự tính toán.
  - _Schema + Replay + Provenance validation:_ Các lệnh sinh ra đều được check AST (Abstract Syntax Tree) để đảm bảo an toàn và được "chạy lại" (replay) để xác minh tính chính xác trước khi nộp.

### Đội ARCANE (Giải Nhì)

- **Chiến thuật cốt lõi:** Pipeline rẽ nhánh với Reranker qua cặp tài liệu (candidate pairs) và Fusion.
- **Mô hình sử dụng:**
  - Embedding: **Qwen3-Embedding-4B** (Offline dense index).
  - Reranker: **Qwen3-Reranker-8B** (Table-pair reranking).
  - Generator: **Qwen3.5-9B**.
- **Kỹ thuật truy hồi:**
  - Áp dụng "Document Gate" (chốt lọc cứng theo Công ty/Năm/Phạm vi báo cáo) trước khi search.
  - Kết hợp RRF (Reciprocal Rank Fusion) để gộp điểm từ BM25 và Dense Search.
  - Adaptive Table Selection: Thuật toán chọn số lượng bảng linh hoạt dựa trên khoảng cách Logit (Logit Gap = 3) thay vì chọn Top-K cứng nhắc.

### Đội KINGPRO (Giải Ba)

- **Chiến thuật cốt lõi:** Tập trung vào kỹ nghệ phần mềm (Software Engineering), Parser ngữ nghĩa và An toàn (Safety sandbox).
- **Kỹ thuật & Pipeline:**
  - Trích xuất HTML thành CSV, giữ nguyên mapping tọa độ (report*id|line) để đảm bảo tính \_Provenance* (dẫn nguồn tuyệt đối).
  - Xây dựng hệ thống _Compiler source-bound_: Tách biệt logic truy hồi công ty/năm/kỳ báo cáo bằng các rule chặt chẽ thay vì phó mặc hoàn toàn cho LLM.
  - Sandbox Pandas 1.1.5: Cô lập mã độc hại (AST check) trước khi chạy code Pandas.
  - Cơ chế Fallback / Refusal Gate: Nếu LLM sinh code lỗi hoặc truy hồi không đủ độ tin cậy, hệ thống sẽ từ chối trả lời (Fail-closed) thay vì bịa số liệu.
- **Mô hình sử dụng:** **Qwen2.5-Coder-14B** (chuyên dụng để sinh code).

---

## 3. Bài học & Kế thừa cho Stage 3

Dựa trên phân tích các đội top, để đạt thành tích cao ở Stage 3 (Truy hồi y khoa đa ngôn ngữ Việt - Anh - Trung), chúng ta nên áp dụng các chiến thuật sau:

1. **Lựa chọn Mô hình (Dưới 15B theo Rule):**
   - Ưu tiên các dòng LLM mạnh về đa ngôn ngữ và tiếng Việt: **Qwen2.5 / Qwen3 (7B-14B)**. Dòng Qwen được hầu hết các đội top sử dụng vì khả năng tiếng Việt tốt và kích thước vừa vặn.
   - Mô hình Embedding: **bge-m3** là ứng viên sáng giá nhất vì hỗ trợ tốt đa ngôn ngữ (Multilingual), xử lý tốt văn bản dài và có tích hợp cả Dense lẫn Sparse.

2. **Kiến trúc Pipeline (Kế thừa từ Stage 1):**
   - **Multi-stage Retrieval:** Đừng phụ thuộc vào 1 Vector Search duy nhất. Hãy dùng: `Dense (bge-m3) + Sparse (BM25) -> RRF/Intersection Fusion -> Cross-Encoder Reranker -> LLM Generation`.
   - **HyDE & Query Decomposition:** Đối với lĩnh vực Y khoa phức tạp, việc dùng LLM tách câu hỏi hoặc sinh câu trả lời giả định trước khi đi tìm kiếm sẽ mang lại Recall rất cao.

3. **Xử lý Dữ liệu Y khoa & Đa ngôn ngữ:**
   - Nên thiết lập cơ sở dữ liệu có _Metadata cứng_ (như `language`, `source`, `doc_id`) để dùng "Gate filter" (lọc cứng bằng DB) trước khi vector search.
   - Cần có bước _Chunking_ thông minh (chia đoạn theo ngữ nghĩa thay vì cắt theo ký tự).

4. **Kỹ thuật Post-processing (Hậu xử lý):**
   - Kế thừa ý tưởng từ đội KINGPRO và NguyenVanNghiem: Đừng tin hoàn toàn vào LLM sinh ra. Cần có một script chạy bằng luật (Regex, Metadata check) để đảm bảo các chunk_text trả về thực sự khớp 100% với tài liệu gốc (không bị hallucinate/thay đổi từ ngữ).
