# Exp 64 — Cached CE Consensus, Head-150 / Pool-300

## Mục tiêu

Kiểm tra lại tín hiệu document reranking của Exp38 mà không lặp confound làm Chunk F2 giảm. Exp38 dùng `BAAI/bge-reranker-v2-m3` và từng tăng Docs F2 từ `0,3187` lên `0,3251` (`+0,0064`), nhưng thay chunk output bằng một chunk/document. Exp64 chỉ dùng top-100 document ranking đã tính sẵn từ cross-encoder như một feature và giữ chunks champion Exp63 nguyên vẹn.

## Cấu hình

- Champion nền: Exp63, fixed top-216, chunks gap 2.000 / span 8.000.
- Khóa cứng ranks 1–150 của Exp63.
- Mở dense candidate pool hiện tại đến rank 300.
- Trong ranks 151–300, ưu tiên documents xuất hiện trong top-100 cross-encoder Exp38; các documents còn lại giữ thứ tự hiện tại.
- Xuất đúng 216 unique documents/query.
- Chunks giống Exp63 value-by-value.

Đây là cached cross-encoder consensus, không phải lần inference mới trên full index 1,205M. Mức can thiệp được giữ nhỏ để giảm rủi ro domain/index drift từ artifact Exp38 cũ.

## Mức thay đổi

- Queries thay đổi: `927/1.200`.
- Swaps/query min/mean/median/max: `0 / 3,399 / 3 / 21`.
- Original rank của docs được đưa vào: `217–300`, trung bình `250,67`, trung vị `247`.
- Top-150 không đổi trên toàn bộ 1.200 query.
- Chunk output không đổi trên toàn bộ 1.200 query.

## Audit

- Đủ 1.200 query, đúng 216 unique official IDs/query.
- Mọi document được thêm đều thuộc top-100 BGE cross-encoder Exp38 của cùng query.
- Top-150 khớp Exp63 value-by-value.
- Chunks khớp Exp63 value-by-value.
- ZIP chỉ chứa `submission.json`; CRC hợp lệ.
- Tests: `4 passed`.
- Kích thước ZIP: `98.171.758` bytes.
- SHA-256: `0f80b72990ec0b27cddf56348c1d48165ab2bc431015cf6d93f38b471cb9c771`.

## Kết quả BTC

| Metric | Exp64 | Exp63 | Chênh lệch |
| --- | ---: | ---: | ---: |
| FINAL_SCORE | 0.3166 | 0.3158 | +0.0008 |
| DOCS_F2MACRO | 0.3478 | 0.3461 | +0.0017 |
| CHUNKS_F2MACRO | 0.2855 | 0.2855 | 0.0000 |
| DOCS_PRECISION | 0.1772 | 0.1765 | +0.0007 |
| DOCS_RECALL | 0.5901 | 0.5869 | +0.0032 |
| CHUNKS_PRECISION | 0.2419 | 0.2419 | 0.0000 |
| CHUNKS_RECALL | 0.3654 | 0.3654 | 0.0000 |

## Kết luận

Exp64 là champion mới. Việc chỉ thay trung bình 3,40 documents/query bằng cached cross-encoder consensus cải thiện đồng thời precision và recall. Chunk metrics bất biến xác nhận ablation sạch và chứng minh regression của Exp38 đến từ cách xuất chunks, không phải từ tín hiệu document reranker. Bước kế tiếp: mở pool đến rank 400 với cùng frozen head và output count để đo phần CE consensus còn sót sâu hơn.
