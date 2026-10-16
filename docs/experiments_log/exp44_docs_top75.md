[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 44: Docs top-75, giữ nguyên chunks Exp40

## Mục tiêu

Đo trực tiếp việc 25 documents cuối của top-100 Exp40 có đang làm loãng precision hay vẫn đóng góp đủ recall cho F2 hay không.

## Kết quả BTC

- Final Score: `0,2868`.
- Docs F2: `0,2977`; Precision `0,2777`; Recall `0,3707`.
- Chunks F2: `0,2759`; Precision `0,2238`; Recall `0,3608`.

So với Exp40, Docs Precision tăng `0,0256` nhưng Docs Recall giảm `0,0578`, làm Docs F2 giảm `0,0246` và Final giảm `0,0123`. Chunks giữ nguyên hoàn toàn.

**Kết luận:** F2 cần phần đuôi 76–100; giữ `top_docs=100`. Không thử top-50 vì recall loss đã quá rõ ở top-75.

## Cấu hình

- Ranking nguồn: Exp40 champion, không retrieval hoặc fusion lại.
- `relevant_docs`: lấy đúng top 75 thay vì top 100.
- `relevant_chunks`: giữ nguyên hoàn toàn 98 chunks/query của Exp40.
- Không thay model, candidate pool, score hoặc query translation.

## Validation

- 1.200 query, đúng 75 unique document IDs/query.
- Tất cả document IDs thuộc corpus chính thức.
- Chunks giống Exp40 ở mức JSON value.
- ZIP: 97.257.705 byte.
- SHA-256: `9a120dbc8f5e4e17bed74962468efecbd8680f874800aa6d456ef297723ada99`.

## Artifact

- Submission: `submission_exp44_docs_top75_chunks_exp40.zip`
- Generator: `scripts/generate_docs_topk_ablation.py`
- Manifest: `submission_exp44_docs_top75_chunks_exp40_manifest.json`

## Cách đọc kết quả

- Chunks F2 phải giữ đúng `0,2759`.
- [x] Docs F2 ≤ `0,3223`: top-100 vẫn là output policy tốt hơn; không cắt thêm top-50.
