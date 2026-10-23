# Exp 61 — Full 1.205M Docs Top-216

## Giả thuyết

Sweep top-k đã tạo một khoảng chứa đỉnh:

- Top-200: Docs F2 `0,3455`.
- Top-225: Docs F2 `0,3459`.
- Top-250: Docs F2 `0,3437`.

Nội suy bậc hai trên ba mốc đặt cực đại xấp xỉ tại `216,35` docs/query. Exp61 thử cutoff nguyên gần nhất là `216`, thay vì tiếp tục mở rộng sau khi top-250 đã giảm.

## Cấu hình

- Giữ đúng 216 documents đầu trong ranking của Exp59.
- Chunks giống hệt Exp59 value-by-value.
- Không thay đổi index, query translation, ranking hay chunk policy.

## Kết quả BTC

| Metric | Exp61 | Exp59 | Chênh lệch |
| --- | ---: | ---: | ---: |
| FINAL_SCORE | 0.3157 | 0.3156 | +0.0001 |
| DOCS_F2MACRO | 0.3461 | 0.3459 | +0.0002 |
| CHUNKS_F2MACRO | 0.2853 | 0.2853 | 0.0000 |
| DOCS_PRECISION | 0.1765 | 0.1727 | +0.0038 |
| DOCS_RECALL | 0.5869 | 0.5965 | -0.0096 |
| CHUNKS_PRECISION | 0.2414 | 0.2414 | 0.0000 |
| CHUNKS_RECALL | 0.3653 | 0.3653 | 0.0000 |

## Audit artifact

- `1.200` query IDs duy nhất.
- Đúng `216` unique official document IDs/query.
- Toàn bộ document list là prefix 216 của Exp59.
- Chunks khớp hoàn toàn Exp59.
- ZIP chỉ chứa `submission.json`; CRC hợp lệ.
- Kích thước ZIP: `98.193.097` bytes.
- SHA-256: `c803486927cb28931e97769ff3384189c35ea567d2a2d46ec3376e00c24e07e5`.

## Trạng thái

Exp61 là champion mới với Final `0,3157`. Cutoff 216 cân bằng precision/recall tốt hơn top-225 và xác nhận đỉnh nội suy. Dừng sweep fixed-k; chuyển sang cải thiện ranking hoặc adaptive-k theo query.
