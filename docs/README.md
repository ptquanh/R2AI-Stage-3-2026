# Tài liệu Dự án R2AI Stage 3

Thư mục `docs/` chứa toàn bộ tài liệu từ quy định cuộc thi, nghiên cứu ban đầu cho tới các thiết kế kiến trúc hệ thống của dự án.

## Cấu trúc Tài liệu

### 1. Thông tin Cuộc thi (`competition_information/`)

Các tài liệu gốc quy định về cuộc thi R2AI Stage 3 (Truy hồi Y sinh đa ngôn ngữ).

- `1_overview.md`: Bối cảnh, mục tiêu và phạm vi bài toán.
- `2_evaluation.md`: Phương pháp đánh giá (F2 Score, độ chính xác của trích dẫn).
- `3_submission_instructions.md`: Hướng dẫn nộp bài (đóng gói mã nguồn, format JSON).
- `4_data.md`: Cấu trúc và thông tin về bộ dữ liệu (Training, Corpus).
- `5_policy_and_rules.md`: Thể lệ, quy định về sử dụng model (<= 15B) và gian lận.

### 2. Nghiên cứu & Phân tích (`research/`)

Các tài liệu tổng hợp và đúc kết kinh nghiệm để xây dựng chiến thuật.

- `top_teams_research_report.md`: Báo cáo phân tích kỹ thuật, pipeline và mã nguồn từ các đội đạt giải cao ở Stage 1 & 2.
- `models_research.md`: Danh sách phân loại và đánh giá các LLM <= 15B phù hợp để triển khai cho dự án.

### 3. Kiến trúc Hệ thống (`architecture/`)

Thiết kế kỹ thuật và lộ trình xây dựng dự án.

- `codebase_proposal.md`: Đề xuất cấu trúc thư mục codebase (Module hóa, tách biệt logic Data/Retrieval/Reranking) và kế hoạch triển khai.

---

_Lưu ý: Luôn đọc các tài liệu này để đảm bảo implementation bám sát luật của BTC và kế thừa các chiến thuật hiệu quả nhất._
