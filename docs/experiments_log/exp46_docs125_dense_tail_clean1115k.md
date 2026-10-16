[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 46: Docs top-125 bằng dense tail trên clean index

## Mục tiêu

Kiểm tra liệu điểm tối ưu document F2 có nằm giữa top-100 của Exp45 và top-200 đã từng thử ở Exp23 hay không. Exp46 giữ nguyên toàn bộ 98 chunks của champion và chỉ thêm 25 document/query từ dense-VI top-500 cache của đúng clean index 1.115.733 documents.

## Giả thuyết và cách đọc kết quả

- Chunks F2 phải giữ đúng `0,2792`; nếu khác thì backend chấm không deterministic hoặc artifact tải lên không đúng.
- Nếu Docs F2 vượt `0,3266`, phần đuôi 101–125 còn đủ recall để bù precision.
- Nếu Docs F2 giảm, giữ top-100 và không mở rộng tiếp top-150.

## Validation

- 1.200 query, đúng 125 unique document IDs/query.
- Mọi document ID thuộc corpus chính thức.
- Chunks giống Exp45 ở mức JSON value cho cả 1.200 query và đều là substring nguyên văn.
- ZIP: `97.829.897` bytes, chỉ chứa `submission.json` ở root.
- SHA-256: `83be57201bed5cdb9638756dbf89eef377ffa5caec7afacac776ca7a5efea06a`.

## Artifact

- `submission_exp46_docs125_dense_tail_clean1115k.zip`
- Generator: `scripts/generate_breakthrough_submissions.py`

## Kết quả BTC

- Final Score: **`0,3064`** — new champion tại thời điểm nộp.
- Docs F2: **`0,3336`**; Precision `0,2294`; Recall **`0,4699`**.
- Chunks F2: `0,2792`; Precision `0,2263`; Recall `0,3647`.

So với Exp45:

- Final `+0,0035`.
- Docs F2 `+0,0070`.
- Docs Precision `-0,0259`, nhưng Docs Recall tăng mạnh `+0,0362` nên F2 vẫn thắng rõ ràng.
- Toàn bộ chunk metrics giữ nguyên tuyệt đối, đúng thiết kế docs-only ablation.

## Kết luận

Điểm tối ưu document output nằm cao hơn top-100: phần đuôi 101–125 chứa đủ ground truth để recall bù cho precision. Exp46 vượt Exp47 `0,0005` về Final nhưng hai cải tiến tác động lên hai trục độc lập, vì vậy cần kết hợp docs Exp46 với chunks Exp47 ở Exp50.
