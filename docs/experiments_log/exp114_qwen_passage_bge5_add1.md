# Exp 114 — Qwen passage retrieval + BGE CE≥5 add-one

Trạng thái: đã được BTC chấm; chunk axis tăng nhẹ, champion control mới.

- Documents giữ nguyên Exp110 để cô lập chunk axis.
- Chỉ tìm passage trong 216 documents đã được chọn của mỗi query.
- Qwen3-Embedding-0.6B xếp hạng passage; passage đã được output hoặc phủ bởi chunk hiện tại bị loại.
- `BAAI/bge-reranker-v2-m3` chấm lại 17.924 passage chưa được phủ.
- Append tối đa một passage/query và chỉ khi raw BGE CE score `≥ 5,0`.

## Chẩn đoán artifact

- 96 queries được thêm passage; tổng 96 chunks.
- BGE CE: min `5,0`, mean `5,8918`, median `5,7676`, max `8,8906`.
- Qwen cosine: mean `0,7435`, median `0,7422`.
- Độ dài passage: mean `2.350`, median `2.930` ký tự.
- Documents khớp Exp110 và toàn bộ chunks cũ được giữ nguyên theo đúng thứ tự.
- ZIP `99.854.787` bytes, CRC hợp lệ và dưới giới hạn 100 MB thập phân.

Mục tiêu của Exp114 là kiểm tra candidate diversity của Qwen ở cấp passage mà không lặp lại thay document membership đã thất bại ở Exp111.

## Kết quả BTC

```json
{"FINAL_SCORE":0.3229,"DOCS_F2MACRO":0.3586,"CHUNKS_F2MACRO":0.2873,"DOCS_PRECISION":0.1816,"DOCS_RECALL":0.6114,"CHUNKS_PRECISION":0.2389,"CHUNKS_RECALL":0.3696}
```

So với Exp110, Docs bất biến; Chunk recall tăng `0,0002`, Chunk F2 tăng `0,0001`, Final hòa sau làm tròn. Tín hiệu dương nhưng add-one không đủ để tiến tới `0,38`; chuyển sang long-envelope reallocation ở Exp115–117.

