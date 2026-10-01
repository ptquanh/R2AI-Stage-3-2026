# Bài học từ các Nghiên cứu (Papers) Mới nhất 2025-2026 về Multilingual Medical RAG

Dựa trên việc rà soát các nghiên cứu mới nhất (trên arXiv và các hội nghị lớn năm 2025 - 2026), dưới đây là các xu hướng và bài học cốt lõi cần áp dụng vào kiến trúc hệ thống R2AI Stage 3.

---

## 1. Vấn đề "Language Drift" (Trôi dạt ngôn ngữ)

**Nghiên cứu:** _"Language Drift in Multilingual Retrieval-Augmented Generation: Characterization and Decoding-Time Mitigation" (2026)_

**Bài học rút ra:**
Khi triển khai RAG đa ngôn ngữ (tiếng Việt, tiếng Trung), các LLM (đặc biệt là model dưới 15B) thường bị hiện tượng "Language Drift" - tức là dù câu hỏi bằng tiếng Việt, và đoạn văn trích xuất (Context) bằng tiếng Việt, LLM vẫn có xu hướng trả lời bằng **tiếng Anh**. Điều này là do trọng số tiếng Anh trong pre-training data quá lớn.

**Chiến thuật cho dự án:**

- **Prompt Engineering chặt chẽ:** Ép buộc bằng system prompt cực kỳ gắt gao (ví dụ: `You MUST answer in the EXACT SAME LANGUAGE as the user's query. Failure to do so will result in a penalty.`).
- **Soft Constrained Decoding (SCD):** Đề xuất từ paper là can thiệp vào quá trình decoding (bước sinh token) để "phạt" (penalize) các token không thuộc bảng mã của ngôn ngữ mục tiêu. Khi code bước Generation (bằng `vllm`), ta có thể can thiệp vào `logit_processor` để giảm xác suất sinh ra từ tiếng Anh nếu câu hỏi là tiếng Việt.

## 2. Sự sụt giảm hiệu năng ở các ngôn ngữ Non-English (MMed-Bench-IR)

**Nghiên cứu:** _"MMed-Bench-IR: A Heterogeneous Benchmark for Multilingual Medical Information Retrieval" (2026)_

**Bài học rút ra:**
Các mô hình Embedding Y sinh tốt nhất hiện nay (thậm chí là các mô hình dense tốt) thường bị sụt giảm độ chính xác (Recall/NDCG) nghiêm trọng khi truy hồi các ngôn ngữ ngoài tiếng Anh (như tiếng Nhật, tiếng Việt).

**Chiến thuật cho dự án:**

- **Không đặt niềm tin 100% vào Vector Embedding (Dense Retrieval).** Bắt buộc phải kết hợp Sparse Retrieval (BM25) được tinh chỉnh riêng với bộ tách từ (Tokenizer) của từng ngôn ngữ (như `pyvi` hoặc `underthesea` cho tiếng Việt, `jieba` cho tiếng Trung).
- Áp dụng **Parallel Medical Knowledge**: Sử dụng cơ sở dữ liệu ánh xạ để dịch thuật từ khóa y khoa (Medical Concept Translation) trước khi tìm kiếm, giúp Vector DB nhận diện ngữ nghĩa tốt hơn.

## 3. Kiến trúc OntologyRAG

**Nghiên cứu:** _"OntologyRAG: better and faster biomedical code mapping with retrieval-augmented generation" (2025)_

**Bài học rút ra:**
Nghiên cứu này chứng minh hoàn toàn hướng đi của đội "7 Grass & 10 Wind" tại Viettel AI Race. Sử dụng cấu trúc dữ liệu đồ thị / bản thể học (Ontology) để gán nhãn (tagging) cho các đoạn văn bản y khoa không chỉ giúp tăng độ chính xác (Precision) mà còn làm giảm thời gian truy hồi.

**Chiến thuật cho dự án:**

- Ở pha Preprocessing (Tiền xử lý dữ liệu), mỗi chunk văn bản (của Pubmed hoặc bài viết URL) sẽ được chạy qua một bước **Entity Tagging**.
- Lưu các Tag này thành Metadata vào Qdrant/Chroma. Khi người dùng query, ta trích xuất Entity từ query và thực hiện **Metadata Filtering** (Lọc theo Tag) trước khi tính khoảng cách Vector, làm giảm đáng kể không gian tìm kiếm.

## 4. Grounding & Infrastructure

**Nghiên cứu:** _"From Fine-Tuning to Grounding: Retrieval-Augmented Generation for Biomedical LLMs in Research and Clinical Data Infrastructures" (2026)_

**Bài học rút ra:**
Trong lĩnh vực Y tế, tính chính xác và nguồn gốc của thông tin (Grounding & Provenance) quan trọng hơn sự trôi chảy của câu văn. Hệ thống phải đảm bảo mọi thông tin đưa ra đều có thể truy vết về nguồn.

**Chiến thuật cho dự án:**

- Đảm bảo đầu ra JSON của LLM phải chứa trường `citations`.
- Áp dụng cơ chế **Post-processing Validator**: Một script Python độc lập sẽ dò tìm các trích dẫn mà LLM sinh ra và đối chiếu chuỗi (String Matching) với Context ban đầu. Nếu LLM trích dẫn một đoạn không hề tồn tại trong Context, hệ thống sẽ tự động gỡ bỏ trích dẫn đó hoặc báo lỗi (Fail-safe).

---

**TỔNG KẾT:** Các nghiên cứu mới nhất năm 2025-2026 hoàn toàn củng cố cho proposal áp dụng _Ontology_ và _Multi-stage RAG_. Đặc biệt, chúng ta cần lưu tâm việc tinh chỉnh Logit (để tránh Language Drift) và Metadata Filtering (để cải thiện điểm yếu của Multilingual Embedding).
