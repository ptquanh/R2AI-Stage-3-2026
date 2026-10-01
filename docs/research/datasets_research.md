# Báo cáo Đánh giá & Chiến lược Dữ liệu (Datasets)

Dựa trên tài liệu quy định ở `4_data.md`, dưới đây là đánh giá các nguồn dữ liệu mà BTC gợi ý. Nhìn chung, dữ liệu BTC cung cấp **ĐỦ TỐT để làm cơ sở tri thức (Knowledge Base / Corpus)**, nhưng **RẤT THIẾU để làm dữ liệu huấn luyện và đánh giá (Training/Evaluation Dataset)**.

Dưới đây là phân tích chi tiết và đề xuất bổ sung:

## 1. Đánh giá nguồn dữ liệu của BTC (Dành cho Corpus Truy hồi)

- **Tiếng Việt & Tiếng Trung (Danh sách URLs):** Đây là dữ liệu bắt buộc (Mandatory) của BTC. Câu trả lời chắc chắn nằm trong các nguồn này. Việc của chúng ta là viết web scraper thật tốt để cào sạch văn bản, giữ lại cấu trúc (tiêu đề, nội dung).
- **Tiếng Anh (PubMed thông qua API NCBI/PubTator):** Rất chuẩn mực. PubMed là kho tàng khổng lồ. Tuy nhiên, nó là một đại dương thông tin, bắt buộc chúng ta phải có API script linh hoạt để Query -> Fetch Metadata -> Fetch Fulltext. Dùng PubTator là một gợi ý tuyệt vời từ BTC vì nó trả về JSON dễ đọc thay vì XML phức tạp.
  👉 **Kết luận về Corpus:** Không cần (và không nên) nhét thêm các nguồn web rác hay Wikipedia vào Corpus truy hồi. Điều này dễ dẫn đến "nhiễu" vector và sai lệch nguồn gốc trích dẫn (Provenance).

## 2. Sự thiếu hụt & Các Dataset cần tìm thêm

**Vấn đề lớn nhất:** BTC không cung cấp tập Labeled Training (Cặp Query - Document) mà chỉ cho tập Test. Nếu chúng ta chỉ dùng mô hình Retriever/Reranker gốc (như `bge-m3`), nó có thể hiểu sai các thuật ngữ y khoa chuyên sâu hoặc bị lệch phẫu hệ ngôn ngữ.

**Đề xuất tìm kiếm thêm các Datasets mở (Legal & Open-source):** Để test độ chính xác (F2 Score nội bộ) hoặc Fine-tune Cross-Encoder Reranker, chúng ta CẦN các Medical QA Datasets sau:

- **Cho Tiếng Anh:**
  - **PubMedQA / BioASQ:** Chứa hàng chục ngàn cặp câu hỏi - câu trả lời kèm context chuẩn y khoa. Rất tốt để benchmark thuật toán Reranking.
  - **MedQA (USMLE):** Dữ liệu từ đề thi bác sĩ Mỹ, tốt cho reasoning.
  - **PubMed / NCBI E-utilities (Dữ liệu cũ BTC đề xuất):** Ở phiên bản thể lệ cũ, BTC gợi ý dùng NCBI Entrez E-utilities, Europe PMC API, PubTator API để lấy tài liệu PubMed. Dù luật mới quy định PubMed không được dùng để tính điểm đánh giá (chỉ chấm link trong `links_corpus.parquet`), chúng ta vẫn CÓ THỂ dùng script `pubmed_client.py` để kéo data về làm dữ liệu huấn luyện (Training Data) nhằm tăng khả năng hiểu Medical Ontology tiếng Anh, sau đó ánh xạ (cross-lingual) về tiếng Việt.
- **Cho Tiếng Việt:**
  - **ViHealthQA** hoặc **ViMedQA:** Các bộ dữ liệu QA y tế tiếng Việt mã nguồn mở. Mặc dù văn phong có thể hướng tới người dùng phổ thông, nhưng nó giúp mô hình làm quen với từ vựng y tế tiếng Việt.
- **Cho Tiếng Trung:**
  - **CMeQA** hoặc **cMedQA2:** Dữ liệu hỏi đáp y tế tiếng Trung chất lượng cao.
- **Dữ liệu từ Viettel AI Race 2026 (Track 1):** Cực kỳ giá trị nếu tìm lại được, vì nó chứa sẵn bộ Ontology và dữ liệu y khoa tiếng Việt.

## 3. Chiến lược cốt lõi: Tự tạo Dữ liệu Tổng hợp (Synthetic Data)

Thay vì chỉ đi tìm dataset ngoài (có thể khác văn phong của BTC), chúng ta nên kế thừa chiến thuật đỉnh cao của đội top Stage 1 (Nguyễn Văn Nghiêm):

- **Bước 1:** Sau khi crawl xong danh sách URL tiếng Việt/Trung của BTC.
- **Bước 2:** Dùng một LLM (ví dụ `Qwen3-14B`) đọc từng đoạn văn bản và tự sinh ra các câu hỏi (Synthetic Queries).
- **Bước 3:** Sử dụng cặp _(Câu hỏi sinh ra - Đoạn văn gốc)_ làm tập Training cực chuẩn để Fine-tune Reranker hoặc làm bộ Benchmark nội bộ.

## 4. Dữ liệu Thu hẹp khoảng cách từ vựng (Query Reformulation Datasets)

Để xử lý nghịch lý giữa văn phong hỏi bệnh của bệnh nhân và từ vựng của tạp chí khoa học (như đã phân tích ở phần CHIR), việc tìm hoặc tạo các bộ dataset "Dịch câu hỏi người bệnh sang thuật ngữ y khoa" là cực kỳ cần thiết.

**Tình hình Dataset hiện có:**

- **Tiếng Anh:** Đã có một số bộ dataset nổi tiếng như **HealthSearchQA** (thuộc MultiMedQA của Google - chứa 3,173 câu hỏi phổ thông), **CHQ-Sum** (Consumer Health Questions Summarization - 1,507 câu), và **GARD Dataset** (từ điển mapping thuật ngữ).
- **Tiếng Trung:** Rất phong phú, điển hình là benchmark **CBLUE** (Chinese Biomedical Language Understanding Evaluation) chứa các task như **KUAKE-QQR** (Query-Query Relevance) và **CHIP-CDN** (Clinical Term Normalization) chuyên để chuẩn hóa ngôn ngữ tự nhiên sang mã ICD.
- **Tiếng Việt:** **Hoàn toàn vắng bóng!** Hiện tại không có bất kỳ bộ dataset tiêu chuẩn (Gold Standard) nào dạng _(Câu hỏi đời thường -> Keyword Y khoa hàn lâm)_ cho tiếng Việt mã nguồn mở.

**Chiến lược bứt phá - "Tự tạo và Open Source":**
Bởi vì không có sẵn dữ liệu tiếng Việt, đây chính là **khoảng trống vàng** để chúng ta tạo ra bộ dataset riêng và thậm chí Public (Open-source) nó lên Hugging Face.

- **Cách làm:** Chúng ta sẽ crawl các cặp Hỏi - Đáp từ các trang tư vấn y khoa (như Vinmec, AloBacsi), dùng GPT-4o / Qwen3 trích xuất "Câu hỏi gốc của bệnh nhân" (Layperson Query) và "Từ khóa/Chẩn đoán của bác sĩ" (Professional Term).
- **Lợi ích:**
  1. Dùng bộ dữ liệu này để Fine-tune (SFT) hoặc Few-shot Prompting cho các mô hình chuyên làm nhiệm vụ **Query Rewriter**. Dù tốc độ (latency) không phải là yếu tố sống còn của cuộc thi, việc Fine-tune sẽ giúp mô hình "bắt bài" chính xác văn phong y tế Việt Nam và chuẩn hóa thuật ngữ (Ontology) nhất quán, chuẩn xác hơn rất nhiều so với dùng LLM Zero-shot chung chung.
  2. Nếu hệ thống của ta có module "Dịch thuật câu hỏi" này, điểm Recall của ta sẽ vượt trội hoàn toàn so với các team khác chỉ biết cắm đầu dùng BM25/Vector Search truyền thống.
