# Đề xuất Cấu trúc Codebase cho Dự án R2AI Stage 3

Dựa trên việc tham khảo mã nguồn của các đội đạt giải cao trong Stage 1 (Truy hồi Pháp luật) và Stage 2 (Text-to-Pandas) – tiêu biểu như đội **MSCAI**, **Nguyễn Văn Nghiêm**, và **KINGPRO** – kết hợp với yêu cầu thực tế của Stage 3 (Truy hồi Y sinh Đa ngôn ngữ), dưới đây là đề xuất cấu trúc mã nguồn (Codebase) tối ưu cho dự án này.

---

## 1. Phân tích các Pattern từ các Team Top

1. **Tách biệt rõ ràng các Phase (Modular Pipeline):**
   Đội Nguyễn Văn Nghiêm chia rất nhỏ các module: `query_decomposition.py`, `retrieval_dense.py`, `retrieval_bm25s.py`, `rerank.py`. Điều này giúp họ dễ dàng A/B testing từng khâu mà không ảnh hưởng toàn hệ thống.
2. **Quản lý Configuration tập trung:**
   Đội MSCAI dùng file `config.yaml` làm nguồn cấu hình duy nhất thay vì rải rác các file `.env` khó kiểm soát.
3. **Thư mục Scripts độc lập:**
   Hầu hết các team tách riêng một thư mục `scripts/` để chạy các tác vụ ETL (Extract, Transform, Load), Đánh giá (Evaluation), hoặc Pipeline End-to-End.
4. **Cô lập Dữ liệu (Data Isolation):**
   Dữ liệu (raw, cache, indices) luôn được tách biệt khỏi mã nguồn và được khai báo trong `.gitignore` để tránh tràn bộ nhớ Git (ví dụ lỗi LFS tải dữ liệu nặng như ta đã thấy).

---

## 2. Đề xuất Cấu trúc Thư mục (Directory Structure)

Cho dự án R2AI Stage 3 (Truy hồi Y khoa Đa ngôn ngữ: Việt - Anh - Trung), một pipeline chuẩn xác và dễ bảo trì nên được tổ chức như sau:

```text
R2AI-Stage-3-2026/
├── data/                       # Chứa dữ liệu (TUYỆT ĐỐI ĐƯA VÀO .gitignore)
│   ├── raw/                    # Dữ liệu crawl gốc (PubMed XML, HTML bài viết)
│   ├── processed/              # Dữ liệu đã làm sạch và phân đoạn (chunks)
│   ├── indices/                # Vector store (FAISS, Qdrant) & Sparse (BM25)
│   └── test/                   # Tập dữ liệu câu hỏi kiểm thử (test queries)
│
├── configs/                    # Các file cấu hình YAML/JSON
│   ├── models.yaml             # Cấu hình LLM & Embedding models (endpoint, params)
│   └── pipeline.yaml           # Các tham số chunk_size, top_k, logit_gap
│
├── src/                        # Thư mục mã nguồn chính (Core)
│   ├── data_collection/        # Logic gọi API PubMed, Europe PMC, Cào dữ liệu
│   │   ├── pubmed_client.py
│   │   └── web_scraper.py
│   ├── preprocessing/          # Làm sạch text, xử lý đặc thù ngôn ngữ (Vi/En/Zh)
│   │   ├── cleaner.py
│   │   └── chunker.py          # Thuật toán cắt chunk y khoa (Semantic chunking)
│   ├── retrieval/              # Các phương pháp truy hồi
│   │   ├── bm25_retriever.py   # Sparse Search
│   │   ├── dense_retriever.py  # Vector Search
│   │   └── fusion.py           # Kết hợp điểm (vd: Reciprocal Rank Fusion - RRF)
│   ├── reranking/              # Chấm điểm lại (Cross-encoder hoặc LLM)
│   │   ├── cross_encoder.py
│   │   └── llm_reranker.py
│   ├── pipeline/               # Orchestrator ghép nối chuỗi query -> answer
│   │   └── rag_pipeline.py
│   └── utils/                  # Helper functions
│       ├── logger.py
│       └── metrics.py          # Tính Precision, Recall, F2 macro
│
├── scripts/                    # Scripts chạy thực thi độc lập
│   ├── 01_crawl_data.py        # Tải dữ liệu từ BTC / API
│   ├── 02_build_indices.py     # Nhúng (embed) và tạo index cho BM25 + Vector DB
│   ├── 03_run_evaluation.py    # Chạy tập kiểm thử và tính điểm F2
│   └── 04_build_submission.py  # Chạy format đầu ra .json đúng chuẩn để nộp bài
│
├── notebooks/                  # Chứa Jupyter Notebooks
│   ├── EDA_queries.ipynb       # Phân tích tập câu hỏi
│   └── Evaluate_retrievers.ipynb # Chạy test trực quan các chiến lược truy hồi
│
├── tests/                      # Unit tests & Integration tests
│   └── test_chunker.py
│
├── .gitignore
├── requirements.txt            # Thư viện Python (vllm, transformers, faiss, v.v.)
└── README.md                   # Hướng dẫn setup và tái lập kết quả
```

---

## 3. Lộ trình Triển khai Codebase (Implementation Plan)

Nếu bạn đồng ý với cấu trúc này, chúng ta có thể tiến hành theo các bước sau:

**Bước 1: Khởi tạo Project (Setup)**

- Tạo các thư mục tương ứng.
- Khởi tạo file `.gitignore` để tránh commit nhầm dữ liệu nặng.
- Tạo `requirements.txt` với các thư viện cần thiết (`numpy`, `pandas`, `requests`, `transformers`, `sentence-transformers`, `faiss-cpu`, `vllm`).

**Bước 2: Phát triển Data Collector & Preprocessor (Tuần 1)**

- Viết script `pubmed_client.py` để sử dụng NCBI/PubTator API lấy bài viết tiếng Anh.
- Viết script cào nội dung URL cho tiếng Việt và tiếng Trung.
- Xây dựng `chunker.py` để chia nhỏ văn bản, giới hạn max 1024 tokens như quy định BTC.

**Bước 3: Xây dựng Retrieval Pipeline (Tuần 2)**

- Triển khai BM25 cho Sparse Retrieval (có tokenizer riêng cho tiếng Việt và tiếng Trung).
- Triển khai Dense Retrieval dùng `bge-m3` và `FAISS`.
- Kết hợp 2 luồng (RRF) để tối ưu điểm số sơ bộ.

**Bước 4: Tích hợp Reranking và Submission (Tuần 3)**

- Thêm Cross-encoder hoặc LLM (`Qwen`) để rerank top 50 văn bản.
- Xây dựng script export file `.json` đúng định dạng nộp bài của BTC.

Bạn có muốn tôi bắt đầu tạo các thư mục và file khởi tạo (Bước 1) ngay bây giờ không?
