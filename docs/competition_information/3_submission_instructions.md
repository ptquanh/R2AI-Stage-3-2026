# 3. Submission instructions

## Dashboard kết quả

Các đội thi nộp kết quả dự đoán trực tiếp trên hệ thống Dashboard chính thức của cuộc thi. Mỗi lần nộp bài cần đảm bảo các yêu cầu sau:

- **Định dạng file:** kết quả được nộp dưới dạng file chuẩn theo mẫu do Ban Tổ chức quy định, với cấu trúc trường dữ liệu tuân thủ đúng đặc tả.
- **Nội dung file:** bao gồm kết quả trả lời cho toàn bộ câu hỏi trong bộ dữ liệu kiểm thử. Bài nộp bị thiếu câu hoặc không đúng định dạng sẽ không được đánh giá.
- **Số lần nộp:** mỗi đội được giới hạn số lần nộp bài mỗi ngày nhằm đảm bảo tính công bằng và tránh hiện tượng dò đáp án.

## Định dạng nộp bài

Thí sinh phải nộp file kết quả truy hồi ở định dạng `.json`. File phải tuân theo cấu trúc sau:

```json
[
  {
    "id": <integer>,
    "relevant_docs": ["<id_tài_liệu>"],
    "relevant_chunks": [
      {
        "doc_id": "<id_tài_liệu>",
        "chunk_text": "<nội_dung_chunk>"
      }
    ]
  },
  ...
]
```

Trong đó:

- `id`: Mã định danh của câu hỏi, kiểu số nguyên (integer).
- `relevant_docs`: Danh sách mã định danh của các tài liệu được dự đoán là liên quan.
- `relevant_chunks`: Danh sách các đoạn nội dung được dự đoán là liên quan. Mỗi đoạn cần chỉ rõ tài liệu nguồn qua `doc_id` và nội dung của đoạn qua `chunk_text`.
- `doc_id`: Mã định danh của tài liệu gốc chứa đoạn nội dung được truy hồi. Đối với tài liệu tiếng Việt và tiếng Trung, `doc_id` là mã id tương ứng trong tệp nguồn do Ban Tổ chức cung cấp. Đối với tài liệu tiếng Anh, nguồn dữ liệu sử dụng là PubMed và PMID được dùng làm `doc_id`.
- `chunk_text`: Nội dung của đoạn văn bản được hệ thống truy hồi từ tài liệu tương ứng với `doc_id`. `chunk_text` phải là nội dung được trích xuất từ tài liệu gốc, không phải nội dung được viết lại hoặc sinh mới bởi hệ thống.

**Ví dụ bài nộp:**

```json
[
  {
    "id": 1,
    "relevant_docs": ["doc_id1", "doc_id2"],
    "relevant_chunks": [
      {
        "doc_id": "doc_id1",
        "chunk_text": "Đoạn nội dung liên quan thứ nhất được trích từ tài liệu doc_id1."
      },
      {
        "doc_id": "doc_id1",
        "chunk_text": "Đoạn nội dung liên quan thứ hai được trích từ một vị trí khác trong tài liệu doc_id1."
      },
      {
        "doc_id": "doc_id2",
        "chunk_text": "Đoạn nội dung liên quan được trích từ tài liệu doc_id2."
      }
    ]
  }
]
```

Nếu hệ thống không dự đoán được kết quả ở một mức, thí sinh vẫn phải cung cấp trường tương ứng với danh sách rỗng.
Sau đó nén file `.json` lại, vào mục My Submissions trên [http://leaderboard.aiguru.com.vn/](http://leaderboard.aiguru.com.vn/), và tải lên file đã nén.

**Lưu ý:**

- Tất cả các file kết quả phải được nén trong một file ZIP, chỉ chứa duy nhất một file (không nằm trong thư mục con).
- Xin lưu ý rằng các bài nộp bị thiếu file hoặc thiếu câu sẽ không được đánh giá và sẽ không bị tính vào số lần nộp tối đa cho phép.

## Quy định nộp bài

- Mỗi đội được phép nộp tối đa **10 bài mỗi ngày**.
- Số bài nộp tối đa cho mỗi người dùng trong Vòng riêng (Private Phase) là **5 bài tổng cộng**. Vì vậy, hãy chọn lựa các bài nộp ở Vòng riêng một cách cẩn thận.
- Mỗi đội cần có một tên người dùng đại diện.
- Kết quả cuối cùng sẽ không được xem là chính thức cho đến khi một bài báo mô tả phương pháp (working notes paper) với mô tả đầy đủ về các phương pháp được nộp.
- Ban Tổ chức Cuộc thi có toàn quyền, theo quyết định riêng của mình, loại bất kỳ thí sinh nào có bài nộp không tuân thủ tất cả các yêu cầu.
