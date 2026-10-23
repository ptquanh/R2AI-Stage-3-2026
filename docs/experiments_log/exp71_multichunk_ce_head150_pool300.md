# Exp 71 — Multi-Chunk CE, Head-150 / Pool-300

## Mục tiêu

Kiểm tra boundary pressure phát hiện ở Exp70 bằng cách mở candidate end từ rank 260 lên 300, trong khi giữ top-150, output-216, multi-chunk aggregation và chunks không đổi. Đây là phép thử cuối của document branch trước khi chuyển sang chunk optimization.

## Cấu hình

- Champion: Exp70.
- Khóa cứng ranks 1–150 của Exp70.
- Candidate pool: source ranks 151–300, tổng 150 documents/query.
- Chọn 66 documents để xuất đúng 216 documents/query.
- Tái sử dụng toàn bộ multi-chunk scores ranks 151–260.
- Chấm mới ranks 261–300 với first chunk và tối đa hai diverse extra chunks/document.
- Extra spans overlap không quá `50%`.
- Document CE score: max trên tối đa ba chunks.
- Blend: `0,75 × minmax(multi-chunk CE) + 0,25 × minmax(-stage rank)`.
- Model: `BAAI/bge-reranker-v2-m3`, FP16, `max_length=384`.
- Output chunks giữ nguyên value-by-value từ Exp70.

## Candidate lineage

- Top-260 được neo trực tiếp vào source/cache đã tạo Exp67–70.
- FAISS top-3.000 chỉ dùng để append documents chưa xuất hiện và lấy evidence cho ranks 261–300.
- `1/1.200` query (ID 159) có tie-order khác khi tăng search-k từ 1.000 lên 3.000; cache anchoring bảo đảm top-260 không đổi.
- Ranks 261–300 chứa đúng 48.000 unique query–document pairs.

## Inference mới

- Tổng query–chunk pairs mới: `62.092`.
- First chunks: `48.000`.
- Extra chunks: `14.092`.
- Documents có extra evidence: `12.409`.
- Documents có hai extra chunks: `1.683`.
- Extra evidence thắng first chunk ở `4.368/12.409` documents (`35,2%`).
- Đủ `62.092/62.092` finite scores, không NaN; `11.867` score values khác nhau.

## Mức thay đổi so với Exp70

- Queries thay đổi: `1.196/1.200`.
- Tổng swaps: `7.732`.
- Swaps/query min/mean/median/max: `0 / 6,443 / 6 / 15`.
- Churn trung bình: `6,443/216 = 2,98%` output/query.
- Insertions đến từ ranks 261–300: `7.428/7.732` (`96,1%`).
- Trung bình/median documents ranks 261–300 được chọn: `6,19/6` mỗi query; min/max `0/15`.
- Rank nguồn của toàn bộ insertions có mean/median `276,80/276`; có `1.379` insertions từ ranks 291–300.

## Audit

- Đủ 1.200 query, đúng 216 unique official IDs/query.
- Mọi document tail đều thuộc candidate pool 151–300 của đúng query.
- Top-150 khớp Exp70 value-by-value.
- Chunks khớp Exp70 value-by-value.
- ZIP chỉ chứa `submission.json`; CRC hợp lệ và payload khớp byte-for-byte với JSON ngoài ZIP.
- Tests: `4 passed`.
- Kích thước ZIP: `98.169.692` bytes.
- JSON SHA-256: `90d1f1ed02a13795e97e28ba0ecdc9501e554b0d9577b1b59762d0d62c570738`.
- ZIP SHA-256: `5e97807646f2d38d35e1cf207f690687c83377bc2fe4df60af4faffb48dd186b`.

## Kết quả BTC

- `FINAL_SCORE`: `0,3207` (`+0,0008` so với Exp70).
- `DOCS_F2MACRO`: `0,3560` (`+0,0017`).
- `DOCS_PRECISION`: `0,1808` (`+0,0007`).
- `DOCS_RECALL`: `0,6059` (`+0,0045`).
- `CHUNKS_F2MACRO`: `0,2855` (không đổi).
- `CHUNKS_PRECISION`: `0,2419` (không đổi).
- `CHUNKS_RECALL`: `0,3654` (không đổi).

## Kết luận

Exp71 là champion mới và thắng rõ hơn Exp70. Pool 300 khai thác được boundary pressure còn lại, nhưng document branch dừng tại đây theo kế hoạch; hai slot cuối ngày chuyển sang chunk-only ablation để xử lý trục điểm đang tụt xa hơn.
