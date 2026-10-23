# Exp 62 — Adaptive-k Normalized Score Curve

## Mục tiêu

Thay cutoff cố định 216 của Exp61 bằng số lượng documents theo từng query, nhưng giữ nguyên ranking và chunks để cô lập tác động của adaptive-k.

## Rule

1. Tạo cùng dense ranking đến rank 250 như Exp60.
2. Với từng query, lấy cosine score tại rank 175 và 250 làm hai anchor.
3. Chuẩn hóa score curve trong khoảng này để loại score offset giữa query và ngôn ngữ.
4. Chọn cutoff tại mức suy giảm chuẩn hóa `0,6018531621`.
5. Mức này được hiệu chỉnh không nhãn sao cho số documents trung bình bằng champion fixed-k: `216`.
6. Giữ nguyên toàn bộ chunk predictions của Exp61.

Không sử dụng ground truth, nhãn ẩn hay phản hồi leaderboard theo từng query.

## Phương án đã loại trước khi nộp

Ngưỡng cosine tuyệt đối `0,62697217` cũng cho mean-k 216 nhưng tạo phân phối hai cực:

- `497/1.200` query ở k=175.
- `608/1.200` query ở k=250.
- Chỉ một query ở k=216.

Điều này phản ánh score cosine không được calibrate xuyên query, nên phương án bị loại mà không dùng slot nộp.

## Phân phối artifact

- Queries: `1.200`.
- K nhỏ nhất/trung bình/trung vị/lớn nhất: `193 / 216 / 216 / 250`.
- Độ lệch chuẩn: `4,7069`.
- p05/p25/p75/p95: `209 / 213 / 219 / 224`.
- Có `33` giá trị k khác nhau; `103` query giữ đúng k=216.
- 90% query nằm trong khoảng 209–224.

## Audit

- Tất cả document IDs thuộc official corpus và không trùng trong query.
- Mỗi document list là prefix của đúng ranking Exp60 top-250.
- Chunks giống hệt Exp61 value-by-value và là substring nguyên văn.
- ZIP chỉ chứa `submission.json`; CRC hợp lệ.
- Kích thước ZIP: `98.191.840` bytes.
- SHA-256: `c5c96302e652dbda7f61b22fd6f66b841aa46e769a65e9eb79579f89c374d30a`.

## Kết quả BTC

| Metric | Exp62 | Exp61 | Chênh lệch |
| --- | ---: | ---: | ---: |
| FINAL_SCORE | 0.3156 | 0.3157 | -0.0001 |
| DOCS_F2MACRO | 0.3458 | 0.3461 | -0.0003 |
| CHUNKS_F2MACRO | 0.2853 | 0.2853 | 0.0000 |
| DOCS_PRECISION | 0.1765 | 0.1765 | 0.0000 |
| DOCS_RECALL | 0.5862 | 0.5869 | -0.0007 |
| CHUNKS_PRECISION | 0.2414 | 0.2414 | 0.0000 |
| CHUNKS_RECALL | 0.3653 | 0.3653 | 0.0000 |

## Kết luận

Adaptive-k giảm nhẹ Docs F2. Precision không đổi ở độ phân giải báo cáo, trong khi recall giảm, cho thấy score-curve shape chưa dự đoán đúng query nào cần mở rộng hoặc thu hẹp. Giữ Exp61 fixed top-216 làm champion, dừng tuning cutoff trên ranking hiện tại và chuyển sang rerank tail.
