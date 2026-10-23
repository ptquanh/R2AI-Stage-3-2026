# Exp 69 — Multi-Chunk Cross-Encoder Evidence

## Mục tiêu

Khắc phục giới hạn của Exp67 khi mỗi candidate document chỉ được đại diện bởi một dense chunk. Exp69 bổ sung tối đa hai chunk khác biệt cho mỗi document, nhưng giữ nguyên candidate pool, blend và output policy để đo riêng tác động của multi-chunk evidence.

## Cấu hình

- Champion: Exp67.
- Khóa cứng ranks 1–180 của Exp67.
- Candidate pool: cùng pool ranks 181–260 đã dùng để tạo Exp67 (source ranking Exp66), chọn 36 documents để xuất tổng 216.
- Tái sử dụng toàn bộ `96.000` first-chunk scores của Exp67.
- Tìm chunk bổ sung trong dense top-2.000; tối đa hai chunk/document.
- Span bổ sung phải overlap không quá `50%` với các span đã chọn.
- Chấm thêm `26.277` query–chunk pairs bằng `BAAI/bge-reranker-v2-m3`, FP16, `max_length=384`.
- Document CE score: `max(first chunk, extra chunk 2, extra chunk 3)`.
- Blend giữ nguyên Exp67: `0,75 × minmax(multi-chunk CE) + 0,25 × minmax(-stage rank)`.
- Output chunks giữ nguyên value-by-value từ Exp67.

## Độ phủ evidence bổ sung

- Documents có ít nhất một chunk bổ sung: `23.311`.
- Documents có đủ hai chunk bổ sung: `2.966`.
- Queries có evidence bổ sung: `1.189/1.200`.
- Documents được chunk phụ nâng CE score: `8.647/23.311` (`37,1%`).
- Với nhóm được nâng score, median/mean uplift là `+0,935/+1,217` raw logit.

## Mức thay đổi so với Exp67

- Queries thay đổi: `916/1.200`.
- Tổng swaps: `2.051`.
- Swaps/query min/mean/median/max: `0 / 1,709 / 1 / 9`.
- `1.994/2.051` insertions (`97,2%`) là documents được extra chunk nâng score trực tiếp.
- `57/2.051` insertions còn lại là thay đổi gián tiếp do per-query min-max được hiệu chỉnh lại.
- Trong 1.994 insertions trực tiếp, chunk thứ hai tạo best score cho `1.825`, chunk thứ ba cho `169`.
- Median/mean raw-logit uplift của các insertions trực tiếp: `+1,830/+2,072`.

## Audit

- Đủ 1.200 query, đúng 216 unique official IDs/query.
- Top-180 khớp Exp67 value-by-value.
- Chunks khớp Exp67 value-by-value.
- ZIP chỉ chứa `submission.json`; CRC hợp lệ và payload khớp byte-for-byte với JSON ngoài ZIP.
- Tests: `4 passed`.
- Kích thước ZIP: `98.170.112` bytes.
- JSON SHA-256: `7a92aa38b100eef32015899d1d58d1136884fc31d76681cb36aebacd413cafdd`.
- ZIP SHA-256: `62cc6d5c70fe35b38d6adee82b8809de6fd28a0e3c99ae15cca498674713eaf5`.

## Ghi chú tái lập

JSON Exp67 từng không còn ở root trong lúc build Exp69. Nó đã được tái tạo từ cache gốc và top-180/chunks của Exp68; JSON tái tạo có đúng SHA-256 cũ `b2ba20a1881f5790dbcf795891c9b976fa6cd64c6df8f79319ea0e1a114b79b0`, xác nhận byte-identical với artifact Exp67 đã nộp.

## Kết quả BTC

- `FINAL_SCORE`: `0,3197` (`+0,0004` so với Exp67).
- `DOCS_F2MACRO`: `0,3540` (`+0,0008`).
- `DOCS_PRECISION`: `0,1799` (`+0,0003`).
- `DOCS_RECALL`: `0,6012` (`+0,0011`).
- `CHUNKS_F2MACRO`: `0,2855` (không đổi).
- `CHUNKS_PRECISION`: `0,2419` (không đổi).
- `CHUNKS_RECALL`: `0,3654` (không đổi).

## Kết luận

Exp69 là champion mới. Multi-chunk evidence cải thiện đồng thời document precision và recall với churn chỉ `1,709` docs/query; Chunk metrics giữ nguyên đúng như thiết kế ablation. Tín hiệu thắng nhưng lợi ích biên nhỏ, nên bước tiếp theo mở vùng fresh multi-chunk CE lên ranks 151–260 và khóa top-150, thay vì tiếp tục tăng số chunk trên cùng pool.
