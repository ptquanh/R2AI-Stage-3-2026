# Exp 67 — Fresh Cross-Encoder, Head-180 / Pool-260

## Mục tiêu

Thoát khỏi tín hiệu cross-encoder cache cũ đã gần bão hòa ở Exp66 bằng cách chạy inference mới trên full index hiện tại, nhưng chỉ thay đổi vùng sát cutoff document để giới hạn rủi ro.

## Cấu hình

- Champion nguồn: Exp66.
- Khóa cứng ranks 1–180 của Exp66.
- Candidate pool: ranks 181–260, tổng cộng 80 documents/query.
- Evidence: best dense chunk hiện tại của từng candidate document.
- Model: `BAAI/bge-reranker-v2-m3`, FP16, `max_length=384`.
- Tổng inference: 96.000 query–document pairs cho 1.200 queries.
- Điểm cuối: `0,75 × minmax(fresh CE) + 0,25 × minmax(-stage rank)` theo từng query.
- Chọn 36 documents từ pool để xuất đúng 216 documents/query.
- Chunks giữ nguyên value-by-value từ Exp66/Exp63.

## Mức thay đổi

So với Exp66:

- Queries thay đổi: `1.199/1.200`.
- Tổng swaps: `15.644`.
- Swaps/query min/mean/median/max: `0 / 13,037 / 13 / 26`.
- Rank gốc của documents được thêm: `217–260`, trung bình `234,36`, trung vị `233`.
- Rank Exp66 của documents bị loại: `181–216`, trung bình `201,07`, trung vị `202`.
- Churn trung bình là `13/216 = 6,0%` documents/query; top-180 không đổi.

## Kiểm tra score

- Đủ `96.000/96.000` finite scores, không có NaN.
- Có `13.589` giá trị score khác nhau.
- Median per-query standard deviation: `1,806`.
- Chỉ query `159` có score range bằng 0; với query này, thành phần stage-rank tự giữ thứ tự cũ nên không phát sinh swap.

## Audit

- Đủ 1.200 query, đúng 216 unique official IDs/query.
- Mọi document được chọn ở tail đều thuộc candidate ranks 181–260 của đúng query.
- Top-180 khớp Exp66 value-by-value.
- Chunks khớp Exp66 value-by-value.
- ZIP chỉ chứa `submission.json`; CRC hợp lệ và payload khớp byte-for-byte với JSON ngoài ZIP.
- Tests: `4 passed`.
- Kích thước ZIP: `98.170.486` bytes.
- JSON SHA-256: `b2ba20a1881f5790dbcf795891c9b976fa6cd64c6df8f79319ea0e1a114b79b0`.
- ZIP SHA-256: `a524992863b7b71462357e6a03c4d4cc3c1488c0306d8aa84234b99b4e85d889`.

## Kết quả BTC

- `FINAL_SCORE`: `0,3193` (`+0,0020` so với Exp66).
- `DOCS_F2MACRO`: `0,3532` (`+0,0042`).
- `DOCS_PRECISION`: `0,1796` (`+0,0019`).
- `DOCS_RECALL`: `0,6001` (`+0,0074`).
- `CHUNKS_F2MACRO`: `0,2855` (không đổi).
- `CHUNKS_PRECISION`: `0,2419` (không đổi).
- `CHUNKS_RECALL`: `0,3654` (không đổi).

## Kết luận

Exp67 là champion mới. Fresh cross-encoder cải thiện đồng thời document precision và recall, còn toàn bộ Chunk metrics giữ nguyên đúng như thiết kế ablation. Điều này xác nhận mức tăng đến từ document membership mới chứ không phải nhiễu ở nhánh chunk.

Sensitivity trên cùng score cache cho thấy tăng CE weight từ `0,75` lên `0,85` chỉ thay thêm trung bình `2,95` docs/query so với Exp67; pure CE `1,0` thay thêm `6,64`. Vì vậy bước kế tiếp ưu tiên weight `0,85`, chưa cần chạy lại inference.
