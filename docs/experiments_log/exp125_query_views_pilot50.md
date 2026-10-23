# Exp125 — Query-view RRF pilot (50 rows)

## Mục tiêu

Kiểm tra liệu query understanding đã sinh trước đó có cải thiện document retrieval, giữ Exp122 làm control và không đổi nhánh chunks.

## Cấu hình

- Control: `submission_exp122_exp121_add19_missing_doc_parents.zip` (Final `0,3516`).
- Input views: `query_views_20a36c979a30e5b5.zip`, Qwen3-8B NF4, run fingerprint `20a36c979a30e5b5`.
- ZIP nguồn có 63 rows hoàn tất, nhưng thử đúng 50 rows đầu: 30 `ok`, 20 `needs_review`; trong nhóm sau có 18 JSON parse được và 2 lỗi parse.
- 48 parsed views được dùng, bao gồm cả 18 view `needs_review` theo mục tiêu thử nghiệm; 2 query lỗi parse giữ nguyên control.
- BGE-M3 dense retrieval trên gốc + canonical/aliases VI + EN + ZH; document-level weighted RRF với weights `1.00/0.60/0.35/0.35`, `rrf_k=60`, `dense_k=4096`.
- Khóa top-150 docs của Exp122; điền 66 vị trí tail bằng thứ hạng RRF. Tất cả chunks và 1.152 queries còn lại giữ nguyên.
- Artifacts: `submission_exp125_query_views_pilot50.zip` (`99.359.954` bytes; dưới giới hạn decimal 100 MB), JSON `741.723.763` bytes. CRC/schema/count/unique-doc validation pass. SHA-256 ZIP `8996bd70f6a8ae6aa92b423acd6f73ced4bc4f675f93d9bcd236f981e5077bd8`; JSON `2d10c3cb070c1268e4bd1346c72997b321d73da155b45d069d45d318dda6527a`.

## Kết quả BTC

```json
{
  "FINAL_SCORE": 0.3513,
  "DOCS_F2MACRO": 0.3579,
  "CHUNKS_F2MACRO": 0.3446,
  "DOCS_PRECISION": 0.1813,
  "DOCS_RECALL": 0.6104,
  "CHUNKS_PRECISION": 0.2512,
  "CHUNKS_RECALL": 0.4682
}
```

So với Exp122:

- Final `-0,0003` (`0,3516 → 0,3513`).
- Docs F2 `-0,0007`; Docs Precision `-0,0003`; Docs Recall `-0,0010`.
- Chunks F2/Precision/Recall bất biến ở `0,3446/0,2512/0,4682`, đúng với thiết kế docs-only.

## Kết luận

Exp122 tiếp tục là champion. Dừng đúng recipe query-view RRF này; không tăng trọng số hoặc mở rộng count. Kết quả âm nhẹ không đủ chứng minh query rewriting nói chung có hại: chỉ 48/1.200 queries đổi, trong đó 18 view bị validator gắn `needs_review`; việc này kiểm tra đồng thời chất lượng view và retrieval recipe, chưa tách được hai yếu tố. Pilot sau chỉ nên dùng view đã qua semantic review/validator tốt hơn và đánh giá candidate recall/overlap offline trước khi dùng slot BTC.
