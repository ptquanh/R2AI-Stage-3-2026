# Exp 111 — Qwen candidate rescue + BGE cross-encoder, cap2

Trạng thái: đã được BTC chấm; regression nhẹ, không dùng làm champion.

- Baseline: Exp110; giữ nguyên top-150 documents và toàn bộ chunks.
- Candidate: document trong Qwen-VI top-50 nhưng chưa có trong 216 documents của Exp110.
- Tái sử dụng điểm `BAAI/bge-reranker-v2-m3` lịch sử; 10.154 cặp mới được chấm trên tối đa hai passage không trùng lặp mạnh.
- Chỉ loại document ở tail Exp110 nếu chính document đó đã có CE score; document chưa được chấm không bị loại.
- Một swap chỉ được chấp nhận khi CE score của Qwen candidate cao hơn document bị loại ít nhất `0,50`; tối đa 2 swaps/query.

## Chẩn đoán artifact

- 1.094/1.200 queries thay đổi; tổng 2.041 swaps, trung bình `1,70`/query.
- CE margin thực tế: mean `3,1265`, median `2,8525`, min `0,5022`.
- Qwen rank của document được nhận: median `41`, p90 `49`, phạm vi `19–50`.
- ZIP `99.772.875` bytes; chỉ chứa `submission.json`, CRC hợp lệ và dưới 100 MB thập phân.

## Giả thuyết

Exp108/110 chứng minh Qwen full-corpus có recall dương nhưng raw RRF làm precision giảm. Exp111 dùng Qwen làm candidate generator và cross-encoder đã thắng ở Exp67–71 làm cổng chất lượng, nhằm giữ phần recall mới nhưng loại dense false positives.

## Kết quả BTC

```json
{"FINAL_SCORE":0.3227,"DOCS_F2MACRO":0.3583,"CHUNKS_F2MACRO":0.2872,"DOCS_PRECISION":0.1814,"DOCS_RECALL":0.6112,"CHUNKS_PRECISION":0.2389,"CHUNKS_RECALL":0.3694}
```

So với Exp110, Final giảm `0,0002`, Docs F2 giảm `0,0003`, precision giảm `0,0002` và recall giảm `0,0002`. Offline CE margin lớn không tương quan đủ tốt với hidden labels ở Qwen rank 19–50. Dừng Exp112/113 vì chúng chỉ tăng exposure của cùng policy.

