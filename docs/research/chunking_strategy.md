# Chiến lược Semantic Chunking cho Big Data (4.4 Triệu URLs)

Tài liệu này ghi chú lại các nghiên cứu mới nhất (2025-2026) về Chunking cho hệ thống Medical RAG và giải thích chiến lược Hybrid Chunking được áp dụng cho dự án R2AI Stage 3.

---

## 1. Cạm bẫy của Thuần Semantic Chunking (Embedding-based) trên Large Corpus

- **Lý thuyết:** Các hệ thống RAG thường dùng Embedding Model để nhúng từng câu, sau đó tính Cosine Similarity giữa 2 câu liền kề. Nếu điểm Similarity giảm đột ngột -> Cắt chunk (vì chủ đề thay đổi).
- **Thực tế:** Với 4.4 triệu bài báo (khoảng 200 triệu câu), việc gọi Embedding Model 200 triệu lần tốn lượng tính toán khổng lồ, có thể kéo dài nhiều tuần trên GPU. Đây là "cú lừa" khi cố gắng Scale up từ POC (Proof of Concept) lên hệ thống Big Data.

---

## 2. Chiến lược Tối ưu: Hybrid Chunking + Mới nhất từ Anthropic

Để đạt được hiệu năng ngữ nghĩa tương đương nhưng với tốc độ O(N) trên CPU, chúng ta kết hợp 3 kỹ thuật sau:

### A. Structure-Aware & Sentence-Based Recursive Chunking

Thay vì dùng Embedding, chúng ta tận dụng cấu trúc tự nhiên của ngôn ngữ:

- **Tầng 1 (Structure):** Ưu tiên cắt theo đoạn văn (dấu `\n\n`). Đoạn văn là vách ngăn chủ đề tự nhiên nhất do tác giả tạo ra.
- **Tầng 2 (Sentence):** Nếu đoạn văn quá giới hạn token, dùng `re`/`nltk` để cắt theo dấu câu (chấm, hỏi, than). Tuyệt đối không cắt ngang câu làm gãy ngữ nghĩa.
- **Tốc độ:** Chạy cực nhanh trên CPU, xử lý hàng triệu bài trong vài giờ (thông qua `batch_chunker.py`).

### B. Kỹ thuật "Small-to-Big" (Parent-Child Retrieval)

RAG y khoa cực kỳ nhạy cảm với ngữ cảnh (ví dụ: triệu chứng của bệnh hay tác dụng phụ của thuốc).

- **Tìm Nhỏ (High Precision):** Cắt chunk với kích thước rất nhỏ (256 tokens) để tạo mật độ từ khóa cao nhất, giúp thuật toán BM25 và Vector tìm kiếm cực kỳ chính xác.
- **Đọc To (High Context):** Gắn metadata `chunk_index`. Khi truy hồi được Chunk N, ta chủ động lấy thêm Chunk N-1 và Chunk N+1 để tạo thành đoạn văn 1024 tokens nạp cho LLM. LLM sẽ không bao giờ bị thiếu ngữ cảnh.

### C. Contextual Chunking (Kỹ thuật Anthropic - Cuối 2024)

- **Vấn đề:** Các chunk ở giữa bài thường chứa các đại từ nhân xưng ("Nó", "Thuốc này") khiến BM25 mù tịt vì mất Context.
- **Giải pháp (Contextual Injection):** Trích xuất tự động **đoạn văn đầu tiên (First Paragraph)** của bài viết (chứa chủ đề cốt lõi). Sau đó, tự động tiêm (inject) đoạn này vào đầu của tất cả các chunk con khác dưới dạng `[Context: ...]`.
- **Lợi ích:** Thuật toán Sparse Retrieval (BM25) sẽ bứt phá giới hạn vì mọi chunk đều mang theo từ khóa chủ đề của toàn bài báo!

---

## 3. Kiến trúc Code

- `src/preprocessing/chunker.py`: Cốt lõi của thuật toán cắt (Tích hợp Contextual Injection).
- `src/preprocessing/batch_chunker.py`: Kịch bản xử lý đa luồng (ProcessPoolExecutor) để "nhai" hàng triệu file Parquet. Mặc định dùng Chunk size = 256 tokens.
