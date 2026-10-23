# Exp 63 — Docs-216 + Chunk Span 8.000

## Mục tiêu

Dùng slot cuối ngày cho một chunk-only ablation bảo thủ; chưa thực hiện rerank document tail. Giữ nguyên champion Exp61 ở document axis và kiểm tra liệu envelope dài hơn một chút có cải thiện Chunk F2 hay không.

## Cấu hình

- Documents: giống hệt Exp61, fixed top-216.
- Merge gap: giữ nguyên `2.000` ký tự.
- Max envelope span: tăng từ `7.000` lên `8.000` ký tự.
- Không thay đổi index, query translation hoặc document ranking.

## Phân tích offline

Các mức chỉ tăng gap trong khi giữ span 7.000 gần như không tạo khác biệt: gap 2.250/2.500/2.750/3.000 chỉ merge thêm lần lượt 2/4/6/15 chunks. Tăng span lên 8.000 với gap giữ 2.000 tạo tác động rõ hơn nhưng vẫn bảo thủ:

- Chunks Exp61: `106.182`.
- Chunks Exp63: `105.864`.
- Giảm: `318` chunks (`0,30%`).
- Tổng số ký tự chỉ tăng `1.658` do phần lớn envelopes mới nối các span gần nhau.
- Mean chunks/query: `88,485→88,220`.

## Audit

- Đủ `1.200` query; document lists giống Exp61 value-by-value.
- Tất cả document IDs thuộc official corpus và không trùng trong query.
- Mọi chunk Exp61 là substring nguyên vẹn của một chunk Exp63 cùng `doc_id`.
- Tất cả chunks Exp63 là substring nguyên văn của source document.
- ZIP chỉ chứa `submission.json`; CRC hợp lệ.
- Tests: `4 passed`.
- Kích thước ZIP: `98.172.133` bytes.
- SHA-256: `f809a669aadeaf34e085f2da10392c2c02dd5a768501c2571fea4662f505f703`.

## Kết quả BTC

| Metric | Exp63 | Exp61 | Chênh lệch |
| --- | ---: | ---: | ---: |
| FINAL_SCORE | 0.3158 | 0.3157 | +0.0001 |
| DOCS_F2MACRO | 0.3461 | 0.3461 | 0.0000 |
| CHUNKS_F2MACRO | 0.2855 | 0.2853 | +0.0002 |
| DOCS_PRECISION | 0.1765 | 0.1765 | 0.0000 |
| DOCS_RECALL | 0.5869 | 0.5869 | 0.0000 |
| CHUNKS_PRECISION | 0.2419 | 0.2414 | +0.0005 |
| CHUNKS_RECALL | 0.3654 | 0.3653 | +0.0001 |

## Kết luận

Exp63 là champion mới. Envelope span 8.000 cải thiện đồng thời chunk precision và recall trong khi document axis bất biến. Giữ policy này làm chunk baseline cho các thử nghiệm rerank ngày mai; không nới span tiếp khi chưa có thêm slot và phân tích offline.
