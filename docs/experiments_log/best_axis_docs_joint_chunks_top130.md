# Best-axis recombination — joint docs + top130 chunks

Trạng thái: BTC-scored, promoted làm control mới. Không chạy model hoặc tune threshold mới; chỉ recombine hai axis đã được BTC chấm.

- `relevant_docs`: exact từ joint Qwen top130 + P2a owner-release, BTC Docs F2/P/R `0.3731/0.2261/0.5631`.
- `relevant_chunks`: exact từ P1 top130/Exp122, BTC Chunks F2/P/R `0.2565/0.1957/0.3427`.
- Đặc tả BTC tính Docs F2 và Chunks F2 độc lập rồi lấy trung bình; submission format không yêu cầu chunk owner thuộc `relevant_docs`.
- 1.200 queries; 183.703 query-docs; 130.108 chunks.
- 8.311 chunk-owner query-docs nằm ngoài `relevant_docs`; đây là axis decoupling có chủ đích, không phải lỗi source. Mọi chunk vẫn giữ nguyên `doc_id` nguồn và nguyên văn.
- Artifact: `submission_best_axes_docs_joint_chunks_top130.zip`, 99.314.397 bytes.
- SHA-256: `b6bc6b304a8ccf5d55ebffdfd55e49633ab6822c1736556be65d8438a1e5215d`.
- Manifest/streaming equality audit: `submission_best_axes_docs_joint_chunks_top130_manifest.json`; exact docs/chunks source hashes pass.

## Kết quả BTC

```json
{
  "FINAL_SCORE": 0.3148,
  "DOCS_F2MACRO": 0.3731,
  "CHUNKS_F2MACRO": 0.2565,
  "DOCS_PRECISION": 0.2261,
  "DOCS_RECALL": 0.5631,
  "CHUNKS_PRECISION": 0.1957,
  "CHUNKS_RECALL": 0.3427
}
```

Kết quả khớp chính xác công thức `(0.3731 + 0.2565) / 2 = 0.3148`, xác nhận hai axis độc lập trong evaluator hiện hành. Promote làm control mới. Docs fixed-cutoff/owner-release đã gần bão hòa; ưu tiên tiếp theo là scorer chunk khác BGE trên nguyên chunk control.
