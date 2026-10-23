# Exp 70 — Multi-Chunk CE, Head-150 / Pool-260

## Mục tiêu

Mở rộng fresh multi-chunk reranking đã thắng ở Exp69 lên vùng ranks 151–180, nơi trước đó vẫn bị khóa. Exp70 kiểm tra liệu fresh CE có thể thay một phần documents ở vùng này bằng candidates tốt hơn từ ranks 181–260 hay không.

## Cấu hình

- Champion: Exp69.
- Khóa cứng ranks 1–150 của Exp69.
- Candidate pool: source ranks 151–260, tổng cộng 110 documents/query.
- Chọn 66 documents từ pool để xuất đúng 216 documents/query.
- Ranks 181–260 tái sử dụng toàn bộ first/extra scores của Exp67/69.
- Ranks 151–180 được chấm mới first chunk và tối đa hai diverse extra chunks/document.
- Extra spans overlap không quá `50%`.
- Document CE score: max trên tối đa ba chunks.
- Blend giữ nguyên: `0,75 × minmax(multi-chunk CE) + 0,25 × minmax(-stage rank)`.
- Model: `BAAI/bge-reranker-v2-m3`, FP16, `max_length=384`.
- Output chunks giữ nguyên value-by-value từ Exp69.

## Inference mới

- Documents mới được chấm: `36.000`.
- Tổng query–chunk pairs mới: `47.551`.
- First chunks: `36.000`.
- Extra chunks: `11.551`.
- Documents có ít nhất một extra chunk: `10.239`.
- Documents có hai extra chunks: `1.312`.
- Extra evidence thắng first chunk ở `3.176/10.239` documents (`31,0%`).
- Đủ `47.551/47.551` finite scores, không NaN; `11.939` score values khác nhau.

## Mức thay đổi so với Exp69

- Queries thay đổi: `1.179/1.200`.
- Tổng swaps: `4.385`.
- Swaps/query min/mean/median/max: `0 / 3,654 / 4 / 12`.
- Trung bình giữ lại `26,81/30` documents gốc ở ranks 151–180; min/median/max `18/27/30`.
- Rank nguồn của documents được thêm: `181–260`, mean/median `233,69/237`.
- Vị trí Exp69 của documents bị loại: `151–216`, mean/median `177,15/174`.
- Churn trung bình là `3,654/216 = 1,69%` output/query.

## Audit

- Đủ 1.200 query, đúng 216 unique official IDs/query.
- Mọi document tail đều thuộc candidate pool 151–260 của đúng query.
- Top-150 khớp Exp69 value-by-value.
- Chunks khớp Exp69 value-by-value.
- ZIP chỉ chứa `submission.json`; CRC hợp lệ và payload khớp byte-for-byte với JSON ngoài ZIP.
- Tests: `4 passed`.
- Kích thước ZIP: `98.170.272` bytes.
- JSON SHA-256: `dcdde9e382c790394e4999b74c325f06f868e6750bddb518ec200ac50ca365d7`.
- ZIP SHA-256: `e196f5a1dece2ea749c82bd9daa3424690105882eb61b4f79c8315876bfbd687`.

## Kết quả BTC

- `FINAL_SCORE`: `0,3199` (`+0,0002` so với Exp69).
- `DOCS_F2MACRO`: `0,3543` (`+0,0003`).
- `DOCS_PRECISION`: `0,1801` (`+0,0002`).
- `DOCS_RECALL`: `0,6014` (`+0,0002`).
- `CHUNKS_F2MACRO`: `0,2855` (không đổi).
- `CHUNKS_PRECISION`: `0,2419` (không đổi).
- `CHUNKS_RECALL`: `0,3654` (không đổi).

## Chẩn đoán biên candidate pool

- `1.896/4.385` insertions (`43,24%`) đến từ ranks 241–260.
- `985/4.385` insertions (`22,46%`) đến từ 10 ranks cuối 251–260.
- `465/4.385` insertions (`10,60%`) đến từ 5 ranks cuối 256–260.

Mật độ insertions tăng mạnh sát rank 260 cho thấy candidate pool vẫn bị truncate. Điều này ủng hộ mở candidate end lên 300 thay vì tiếp tục hạ frozen head.

## Kết luận

Exp70 là champion mới, nhưng lợi ích biên đã nhỏ. Chạy thêm một Exp71 giữ top-150 và mở fresh multi-chunk pool tới rank 300 để xử lý dấu hiệu boundary pressure; sau đó dừng document sweep và chuyển sang tối ưu chunk branch.
