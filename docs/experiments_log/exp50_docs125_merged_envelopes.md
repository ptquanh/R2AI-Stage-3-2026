[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 50: Docs top-125 + merged chunk envelopes

## Mục tiêu

Kết hợp hai cải tiến đã được BTC xác nhận và hoàn toàn trực giao:

- Document predictions lấy nguyên vẹn từ Exp46, đạt Docs F2 `0,3336`.
- Chunk predictions lấy nguyên vẹn từ Exp47, đạt Chunks F2 `0,2851`.

Scorer tính document và chunk độc lập rồi lấy trung bình hai F2, nên đây là phép hợp nhất không cần retrieval hay tuning mới.

## Điểm kỳ vọng

- Docs F2: `0,3336`.
- Chunks F2: `0,2851`.
- Final: `(0,3336 + 0,2851) / 2 = 0,30935`, dự kiến hiển thị `0,3094` nếu làm tròn bốn chữ số.

Nếu một trong hai metric khác nguồn tương ứng thì đó là tín hiệu artifact tải lên sai hoặc backend không deterministic.

## Validation

- 1.200 query.
- Đúng 125 unique document IDs/query, giống Exp46 ở mức JSON value.
- Chunk predictions giống Exp47 ở mức JSON value: trung bình `88,44` chunks/query, min `65`, max `98`.
- Mọi ID thuộc corpus chính thức; không có duplicate document/chunk trong query.
- Chunk Exp47 đã được xác minh là substring nguyên văn của source document.
- ZIP: `97.481.113` bytes, chỉ chứa `submission.json` ở root.
- SHA-256: `f822458d66d5cf7d78b3dec378eee73a8fb4d5d6472d226afbc58bc3d27118bb`.

## Artifact

- `submission_exp50_docs125_merged_envelopes.zip`
- Generator: `scripts/combine_submission_axes.py`

## Kết quả BTC

- Final Score: **`0,3093`** — new champion.
- Docs F2: **`0,3336`**; Precision `0,2294`; Recall **`0,4699`**.
- Chunks F2: **`0,2851`**; Precision **`0,2413`**; Recall **`0,3653`**.

Kết quả khớp chính xác các metric thành phần của Exp46 và Exp47. Final BTC hiển thị `0,3093`, tương ứng với giá trị chưa làm tròn nội bộ của hai F2; chênh `0,00005` so với phép tính từ các số đã hiển thị bốn chữ số không phải regression.

## Kết luận

Exp50 là champion cuối ngày 16/10/2026. Thử nghiệm xác nhận document predictions và chunk predictions có thể tối ưu độc lập rồi ghép lại mà không tạo tương tác bất lợi:

- Top-125 là output policy tốt hơn top-100 cho document F2.
- Merge các evidence gần nhau trong cùng document là output policy tốt hơn 98 chunks rời cho chunk F2.
- Không cắt chunk tail xuống top-64/top-48 vì recall loss lớn hơn precision gain.
