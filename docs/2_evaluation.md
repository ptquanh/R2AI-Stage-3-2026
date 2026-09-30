# 2. Evaluation

## Phương pháp đánh giá

Hiệu suất hệ thống trên nhiệm vụ truy hồi được đánh giá ở hai cấp độ: tài liệu và đoạn nội dung, bằng các chỉ số Độ chính xác (Precision), Độ bao phủ (Recall) và F2. Các chỉ số được tính riêng cho từng truy vấn, sau đó lấy trung bình trên toàn bộ tập truy vấn (macro-average).

### 2.1 Truy hồi tài liệu (Cấp Document)

Với mỗi truy vấn, gọi D là tập tài liệu được truy hồi và G là tập tài liệu liên quan theo nhãn tham chiếu.

- Precision = `|D ∩ G| / |D|`
- Recall = `|D ∩ G| / |G|`

### 2.2 Truy hồi đoạn nội dung (Cấp Chunk)

Với mỗi truy vấn, gọi C là tập chunk_text được truy hồi và I là tập các phần thông tin cần thiết trong những tài liệu liên quan.

Một chunk_text được tính là relevant nếu chứa nội dung tương ứng hoặc overlap đủ với ít nhất một phần thông tin cần thiết trong I.

- Precision = `Số chunk relevant / Tổng số chunk được truy hồi`
- Recall = `Số phần thông tin cần thiết được bao phủ / Tổng số phần thông tin cần thiết`

Độ dài mỗi chunk_text được khuyến nghị không quá khoảng 1.024 tokens.

### 2.3 Độ đo F2 macro

Với mỗi truy vấn, điểm F2 được tính từ Precision và Recall của truy vấn đó:

- F2 = `(5 × Precision × Recall) / (4 × Precision + Recall)`

Điểm F2 macro được tính bằng trung bình cộng điểm F2 của tất cả các truy vấn.
