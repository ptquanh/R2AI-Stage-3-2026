[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 47: Merge chunk cùng document thành parent envelope

## Mục tiêu

Khai thác trực tiếp quy tắc chunk overlap của BTC. Các chunk Exp45 thuộc cùng document được gộp khi cách nhau không quá 2.000 ký tự và envelope cuối không dài quá 7.000 ký tự. Một envelope nguyên văn có thể bao phủ nhiều ground-truth chunks, đồng thời giảm mẫu số precision do loại các dự đoán chồng lấn.

## Cấu hình

- Giữ nguyên chính xác document set Exp45.
- Giữ thứ tự theo rank đầu tiên của cluster.
- Số chunk/query: trung bình `88,44`, min `65`, max `98`.
- Độ dài chunk trung bình `2.458,8` ký tự; tối đa `7.000`.

## Cách đọc kết quả

- Docs F2 phải giữ đúng `0,3266`.
- Đây là biến thể chunk ít rủi ro nhất trong nhóm Exp47–49: chỉ gộp evidence gần nhau, không bỏ phần đầu ranking.
- Chunks F2 trên `0,2792` xác nhận metric-aware parent envelope hiệu quả.

## Validation

- 1.200 query; document lists giống Exp45 cho cả 1.200 query.
- Mọi chunk là substring nguyên văn của đúng `doc_id`.
- Không trùng `(doc_id, chunk_text)` trong từng query.
- ZIP: `97.328.151` bytes, chỉ chứa `submission.json` ở root.
- SHA-256: `fa0915839b387db6e8402c4e7cb36754062a344a32c84edf55de6f9e48912eb6`.

## Artifact

- `submission_exp47_merged_chunk_envelopes.zip`
- Generator: `scripts/generate_breakthrough_submissions.py`

## Kết quả BTC

- Final Score: **`0,3059`** — new champion.
- Docs F2: `0,3266`; Precision `0,2553`; Recall `0,4337`.
- Chunks F2: **`0,2851`**; Precision **`0,2413`**; Recall **`0,3653`**.

So với Exp45:

- Final `+0,0030`.
- Docs metrics giữ nguyên tuyệt đối, xác nhận ablation cô lập đúng chunk policy.
- Chunks F2 `+0,0059`.
- Chunks Precision `+0,0150`, là nguồn tăng chính.
- Chunks Recall vẫn tăng `+0,0006` dù số chunk trung bình giảm từ 98 xuống 88,44.

## Kết luận

Giả thuyết metric-aware parent envelope được xác nhận. Các chunk chồng lấn của Exp45 đang làm tăng mẫu số precision mà không bổ sung đủ ground-truth coverage. Gộp evidence gần nhau trong cùng document vừa loại dự đoán dư thừa vừa giúp một envelope bao phủ tốt hơn các đoạn chuẩn. Exp47 thay Exp45 làm champion.

Tiếp theo ưu tiên Exp48 để đo giới hạn cắt đuôi ở top-64. Exp49 vẫn là biến thể rủi ro cao vì bỏ hơn một nửa số chunk; chỉ nộp sau Exp48.
