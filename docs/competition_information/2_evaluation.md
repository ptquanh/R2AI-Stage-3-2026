# 2. Evaluation (Phương pháp Đánh giá)

Hiệu suất hệ thống trên nhiệm vụ truy hồi được đánh giá ở hai cấp độ: **tài liệu (document)** và **đoạn nội dung (chunk)**, bằng các chỉ số Độ chính xác (**Precision**), Độ bao phủ (**Recall**) và **F2**. Các chỉ số được tính riêng cho từng truy vấn, sau đó lấy trung bình trên toàn bộ tập câu hỏi (**macro-average**).

---

## 1. Truy hồi Tài liệu (Cấp Document)

Với mỗi truy vấn, gọi $D$ là tập tài liệu được đội thi truy hồi (`relevant_docs`) và $G$ là tập tài liệu liên quan theo nhãn tham chiếu (Ground Truth):

$$\text{Precision}_{\text{doc}} = \frac{|D \cap G|}{|D|}$$

$$\text{Recall}_{\text{doc}} = \frac{|D \cap G|}{|G|}$$

- **Lưu ý:** `doc_id` bắt buộc phải là số nguyên (**int**).

---

## 2. Quy tắc Xác định một Đoạn Văn bản Được Truy hồi Đúng (Cấp Chunk)

Mỗi chunk $c$ đội thi nộp được đối chiếu với các đoạn tham chiếu $g$ **thuộc cùng câu hỏi và cùng `doc_id`**.

### 2.1. Tiền xử lý & Chuẩn hóa Văn bản (Normalization Pipeline)

Trước khi đối chiếu, văn bản cả hai phía ($c$ và $g$) bắt buộc phải qua 2 bước chuẩn hóa:

1. **Chuẩn hóa Unicode:** Áp dụng chuẩn **NFKC** (`unicodedata.normalize('NFKC', text)`).
2. **Làm sạch văn bản:**
   - Giải mã HTML entity (`html.unescape`).
   - Chuyển toàn bộ về chữ thường (`.lower()`).
   - Gộp các khoảng trắng liên tiếp thành 1 khoảng trắng (`re.sub(r'\s+', ' ', text)`).
   - Xóa bỏ khoảng trắng ở đầu và cuối chuỗi (`.strip()`).

### 2.2. Công thức Độ trùng khớp (Overlap)

Gọi $c$ là chunk nộp và $g$ là chunk tham chiếu sau chuẩn hóa:

$$\text{overlap}(c, g) = \frac{\text{LCS}_{\text{tokens}}(c, g)}{|g|}$$

Trong đó:

- $\text{LCS}_{\text{tokens}}(c, g)$: Độ dài của **dãy token con chung dài nhất** (Longest Common Subsequence) giữa $c$ và $g$ (giữ nguyên thứ tự từ trái qua phải, không bắt buộc các token phải đứng liền kề nhau).
- $|g|$: Tổng số lượng tokens của chunk tham chiếu $g$.

### 2.3. Điều kiện Tính là Đúng (Hit Threshold)

> Một chunk $c$ được tính là **ĐÚNG** nếu tồn tại ít nhất một chunk tham chiếu $g$ (cùng câu hỏi và cùng `doc_id`) sao cho:
> $$\text{overlap}(c, g) \ge 40\% \quad (0.4)$$

---

## 3. Đánh giá ở Cấp Đoạn Nội dung (Cấp Chunk)

$$\text{Precision}_{\text{chunk}} = \frac{\text{Số chunk nộp được tính là đúng}}{\text{Tổng số chunk đội thi nộp}}$$

$$\text{Recall}_{\text{chunk}} = \frac{\text{Số chunk tham chiếu đã được tìm thấy}}{\text{Tổng số chunk tham chiếu}}$$

_(Một chunk tham chiếu được tính là "đã tìm thấy" nếu có ít nhất 1 chunk nộp đạt overlap $\ge 40\%$ với nó)._

---

## 4. Điểm F2 và Điểm Tổng kết (Final Score)

### 4.1. Điểm F2 ở từng cấp

Ở mỗi cấp đánh giá (Docs và Chunks), với từng câu hỏi, điểm F2 được tính từ Precision và Recall (F2 ưu tiên Recall gấp đôi Precision):

$$F_2 = \frac{5 \times \text{Precision} \times \text{Recall}}{4 \times \text{Precision} + \text{Recall}}$$

Precision, Recall và F2 cuối cùng ở mỗi cấp đánh giá được tính bằng **trung bình cộng (macro-average)** trên toàn bộ tập câu hỏi test:

- $\text{DOCS\_F2MACRO}$
- $\text{CHUNKS\_F2MACRO}$

### 4.2. Điểm Xếp hạng Chung cuộc (Final Score)

Điểm số chính thức hiển thị trên Bảng xếp hạng (Leaderboard) được tính bằng trung bình cộng của 2 cấp độ:

$$\text{FINAL\_SCORE} = \frac{\text{DOCS\_F2MACRO} + \text{CHUNKS\_F2MACRO}}{2}$$

---

## 5. Đúc kết Kỹ thuật & Chiến lược Tối ưu

1. **Chuẩn hóa đồng bộ:** Module tiền xử lý chunking của chúng ta phải áp dụng đúng quy trình: NFKC + unescape HTML + lowercase + whitespace strip để tránh mất điểm overlap một cách lãng phí.
2. **Bản chất mẫu số $|g|$:** Mẫu số của độ đo overlap là độ dài của ground truth $|g|$. Điều này có nghĩa nếu chunk nộp $c$ bao phủ được câu chốt của $g$, $c$ có thể dài hơn một chút để đảm bảo an toàn nhưng không được nộp lan man vì sẽ làm giảm mạnh $\text{Precision}_{\text{chunk}}$.
3. **Cùng `doc_id`:** Chunk chỉ được tính điểm nếu trúng tài liệu (`doc_id`). Do đó, nếu Stage 1 chọn sai tài liệu thì Stage 2 dù chunk hay đến đâu cũng sẽ bị 0 điểm chunk.
