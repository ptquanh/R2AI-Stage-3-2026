# Exp 89 — Qwen3-Reranker-0.6B trên dense pool 51–300

Trạng thái: cap3 đã được BTC chấm và giảm điểm; dừng cap5/cap10.

Sau khi Exp88 bác bỏ BM25-only rescue, Exp89 giữ nguyên candidate pool của Exp76/Exp87 và chỉ thay scorer từ BGE sang `Qwen/Qwen3-Reranker-0.6B`. Top-50 và chunks Exp87 được giữ nguyên ở local builder; Kaggle chỉ tạo scores, không tạo submission.

## Model và luật

- Model: `Qwen/Qwen3-Reranker-0.6B`, 0,6B tham số, Apache-2.0.
- Revision pin: `e61197ed45024b0ed8a2d74b80b4d909f1255473`.
- Model đã phát hành trước cutoff BTC `01/08/2026` và dưới giới hạn 15B/model.
- Scoring dùng xác suất token `yes` so với `no` theo model card chính thức.
- Instruction tiếng Anh cố định: `Given a multilingual medical question, retrieve passages that contain information needed to answer the question.`

## Inference pack

- `300.000` query/document rows: đúng 250 docs/query, rank 51–300.
- Một passage/query/document, chọn bằng BGE score cao nhất từ cache hiện có để cố định passage preselection.
- 101 cached pairs chỉ có passage rỗng được fallback sang lexical span nguyên văn từ active source text.
- Parquet: `184.617.902` bytes.
- SHA-256: `4101aa0a741326240724793fdb95176ccdf3e7d94e9504e0514fee6194f47872`.
- Không chứa labels, chunks submission hoặc dữ liệu ngoài candidate pool.

## Kaggle và build local

- Notebook: `notebooks/11_qwen3_reranker_exp89_kaggle.ipynb`.
- Hai subprocess độc lập cho T4×2; checkpoint `.npy` theo shard và resume được.
- FP16, max length 512, batch mặc định 32/GPU; hạ xuống 16 nếu OOM.
- Notebook xuất `exp89_qwen_scores.npy`, score table, manifest và ZIP tải về.
- Local builder `scripts/build_exp89_from_qwen_scores.py` kiểm tra fingerprint rồi tạo cap3/5/10, bảo vệ top-50 và chunks Exp87.

Dataset Kaggle phải để Private. Chưa chọn cap nộp cho đến khi có churn diagnostics từ scores thật.

## Kết quả inference và audit ngày 20/10

- Đủ `300.000` scores float32; `1.200 × 250` rows, rank 51–300.
- Không NaN/Inf, không duplicate `(query_id, doc_id)`; NPY và Parquet khớp từng row.
- Score min/mean/max: `0,0000223865 / 0,3279613 / 0,9999747`.
- Input SHA-256 khớp pack: `4101aa0a741326240724793fdb95176ccdf3e7d94e9504e0514fee6194f47872`.
- Scores SHA-256: `63d801ca501f043b360a1f4e8fa550b01d97585f09da34e9b2af0017d0f7a7a8`.

Qwen ranking tự nhiên muốn đưa trung bình `45,41` outsiders/query (median 45, max 82) vào phần sau protected top-50. Đây là churn quá lớn cho lần nộp đầu, vì vậy cả ba cap đều bind ở đủ 1.200 queries:

- cap3: đúng 3 swaps/query, 3.600 tổng; ZIP `99.628.991` bytes; SHA-256 `5853b08423f8b9695261c1ead79d05841113963843eae460ea531b35cb4d1469`.
- cap5: đúng 5 swaps/query, 6.000 tổng; ZIP `99.629.121` bytes; SHA-256 `6e794d86b24fe5641d5b546dfefda022dbe76a82c896dea65265963db8444a47`.
- cap10: đúng 10 swaps/query, 12.000 tổng; ZIP `99.630.209` bytes; SHA-256 `0dcea4694ee644158eb23337a8835046d98310a37030cd7305028ba033f473c5`.

Independent streaming validation xác nhận mỗi ZIP chỉ có `submission.json`, CRC hợp lệ, đủ 1.200 queries, 216 unique official documents/query, top-50 và toàn bộ chunks giống Exp87. Nộp cap3 trước để đo direction của scorer mới; chỉ mở cap5/10 nếu Docs F2/Recall có tín hiệu dương.

## Điểm BTC — cap3

```json
{
  "FINAL_SCORE": 0.3221,
  "DOCS_F2MACRO": 0.3572,
  "CHUNKS_F2MACRO": 0.2870,
  "DOCS_PRECISION": 0.1813,
  "DOCS_RECALL": 0.6075,
  "CHUNKS_PRECISION": 0.2396,
  "CHUNKS_RECALL": 0.3688
}
```

So với champion Exp87, Final giảm `0,0005`, Docs F2 giảm `0,0011`, Docs Precision giảm `0,0005`, Docs Recall giảm `0,0023`; chunk axis tái hiện đúng vì được giữ bất biến. Cap3 chỉ thay 3 docs/query mà đã giảm, trong khi natural Qwen ranking muốn thay trung bình 45,41 docs/query. Vì vậy dừng cap5/cap10 và không nâng lên reranker 4B trên cùng thiết kế passage/membership này. Score cache vẫn hữu ích cho phân tích đồng thuận hoặc feature phụ, nhưng không dùng độc lập để thay candidates.
