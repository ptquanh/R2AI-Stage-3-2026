# Exp 68 — Fresh Cross-Encoder Weight 0,85

## Mục tiêu

Kiểm tra liệu tín hiệu fresh cross-encoder đã thắng ở Exp67 còn được khai thác chưa đủ hay không. Chỉ tăng CE weight từ `0,75` lên `0,85`; mọi thành phần còn lại giữ nguyên.

## Cấu hình

- Champion tham chiếu: Exp67.
- Candidate/source: cùng 96.000 scores đã inference cho Exp67; không chạy lại model.
- Khóa cứng ranks 1–180 của Exp66.
- Candidate pool: ranks 181–260, chọn 36 documents để xuất tổng 216.
- Blend: `0,85 × minmax(fresh CE) + 0,15 × minmax(-stage rank)` theo từng query.
- Model tạo score: `BAAI/bge-reranker-v2-m3`, FP16, `max_length=384`.
- Chunks giữ nguyên value-by-value từ Exp67/Exp66/Exp63.

## Mức thay đổi

So với Exp67:

- Queries thay đổi: `1.186/1.200`.
- Tổng swaps: `3.536`.
- Swaps/query min/mean/median/max: `0 / 2,947 / 3 / 8`.
- Top-180 không đổi; chỉ membership của 36 vị trí tail thay đổi.

So với Exp66:

- Queries thay đổi: `1.199/1.200`.
- Swaps/query min/mean/median/max: `0 / 15,827 / 16 / 29`.

## Audit

- Đủ 1.200 query, đúng 216 unique official IDs/query.
- Top-180 khớp Exp67/Exp66 value-by-value.
- Chunks khớp Exp67 value-by-value.
- ZIP chỉ chứa `submission.json`; CRC hợp lệ và payload khớp byte-for-byte với JSON ngoài ZIP.
- Tests: `4 passed`.
- Kích thước ZIP: `98.170.602` bytes.
- JSON SHA-256: `9674d0e26bbe44bf12aca8b5512a98ec2193add50b24c0ffa40964a6c887d440`.
- ZIP SHA-256: `d8a9866d72439a7d7af3bc5354b6f3bffe8e942fc40fe495107121eb94187f76`.

## Kết quả BTC

- `FINAL_SCORE`: `0,3193` (không đổi ở độ phân giải báo cáo).
- `DOCS_F2MACRO`: `0,3532` (không đổi ở độ phân giải báo cáo).
- `DOCS_PRECISION`: `0,1795` (`-0,0001` so với Exp67).
- `DOCS_RECALL`: `0,5997` (`-0,0004`).
- `CHUNKS_F2MACRO`: `0,2855` (không đổi).
- `CHUNKS_PRECISION`: `0,2419` (không đổi).
- `CHUNKS_RECALL`: `0,3654` (không đổi).

## Kết luận

Exp68 hòa Final và Docs F2 với Exp67 sau làm tròn, nhưng cả document precision và recall đều giảm nhẹ. Exp67 tiếp tục là champion; CE weight `0,75` tốt hơn `0,85`. Dừng sweep weight và chuyển sang cải thiện chất lượng evidence bằng nhiều candidate chunks/document.
