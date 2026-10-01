# Data Ingestion Pipeline Architecture

Sơ đồ dưới đây mô tả luồng thu thập và xử lý dữ liệu (Data Ingestion) của hệ thống, bao gồm cả luồng xử lý chính (bắt buộc để lấy điểm) và các luồng phụ (dành cho việc tạo dữ liệu huấn luyện, fine-tune mô hình).

```mermaid
flowchart TD
    %% Define Data Sources
    subgraph Nguồn_Dữ_Liệu
        LCP[("links_corpus.parquet\n(4.4 Triệu URLs)"):::mandatory]
        PM["PubMed / NCBI\n(Tài liệu Y khoa Tiếng Anh)"]:::optional
        QA["Vinmec / AloBacsi\n(Hỏi đáp Bác sĩ)"]:::optional
    end

    %% Define Data Collection Pipeline
    subgraph Data_Collection_Pipeline
        WS["Async Web Scraper\n(aiohttp + trafilatura)"]:::mandatory
        PC["PubMed Client\n(pubmed_client.py)"]:::optional
        QC["Q&A Crawler\n(Thu thập Hỏi/Đáp)"]:::optional

        LCP --> |"Phân lô (Batching)"| WS
        PM -.-> |"E-utilities API"| PC
        QA -.-> |"Scrape cặp Hỏi/Đáp"| QC
    end

    %% Define Raw Storage
    subgraph Raw_Storage
        RP[("Kho Text Tiếng Việt/Trung\n(.parquet file)"):::mandatory]
        RP_ENG[("Kho Text Tiếng Anh\n(.json file)")]:::optional
        RQA[("Kho Q&A Thô\n(Người bệnh - Bác sĩ)")]:::optional

        WS --> |"Lọc quảng cáo,\nlấy Main Text"| RP
        PC -.-> RP_ENG
        QC -.-> RQA
    end

    %% Define Data Processing & Synthetic Generation
    subgraph Processing_&_Augmentation
        CH["Semantic Chunker\n(Giới hạn < 1024 tokens)"]:::mandatory
        LLM1["LLM Synthetic Generator\n(Qwen / GPT)"]:::optional
        LLM2["LLM Reformulator\n(Trích xuất thuật ngữ)"]:::optional

        RP --> CH
        CH -.-> |"Lấy mẫu ngẫu nhiên"| LLM1
        RQA -.-> LLM2
    end

    %% Define Final Outputs
    subgraph Final_Artifacts_Cho_RAG
        KB[("Knowledge Base\n(Sẵn sàng nạp vào Vector DB)"):::mandatory]
        SFT1[("Synthetic Q-A Dataset\n(Dùng để Fine-tune Reranker)")]:::optional
        SFT2[("Query Reformulation Dataset\n(Dùng để Fine-tune LLM Dịch câu hỏi)")]:::optional

        CH --> KB
        LLM1 -.-> |"Tự sinh câu hỏi từ Text"| SFT1
        LLM2 -.-> |"Ánh xạ: Bệnh nhân -> Y khoa"| SFT2
    end

    %% Styling
    classDef mandatory fill:#2563eb,stroke:#1e40af,color:white,stroke-width:2px;
    classDef optional fill:#059669,stroke:#047857,color:white,stroke-dasharray: 5 5;
```

## Chú thích các luồng

1. **Khối Màu Xanh Dương (Nét liền) - Luồng Sống Còn (Mandatory):**
   - Đây là quy trình thu thập và xử lý bắt buộc để xây dựng hệ thống Retrieval theo yêu cầu của BTC.
   - Bắt đầu từ 4.4 triệu links, đi qua **Web Scraper** bất đồng bộ (`aiohttp` + `trafilatura`) để trích xuất văn bản sạch.
   - Văn bản thô được lưu thành các file Parquet nhỏ, sau đó đưa qua **Semantic Chunker** (cắt đoạn văn) để tạo thành Cơ sở tri thức (Knowledge Base) đưa vào Vector DB.

2. **Khối Màu Xanh Lá (Nét đứt) - Luồng Đào tạo & Tăng cường (Optional / Training):**
   - **Nhánh PubMed:** Dùng `pubmed_client.py` lấy tài liệu chuẩn tiếng Anh về làm giàu tri thức y khoa (để dạy Cross-Encoder).
   - **Nhánh Sinh dữ liệu (Synthetic Q-A):** Dùng LLM đọc văn bản của BTC để tự đẻ ra câu hỏi, làm tập test nội bộ.
   - **Nhánh Query Reformulation:** Cào các trang hỏi đáp y tế đời thực, dùng LLM chắt lọc thành bộ từ điển biến "Câu hỏi của bệnh nhân" thành "Câu truy vấn của chuyên gia" nhằm triệt tiêu Vocabulary Gap.
