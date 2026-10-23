# Exp 55 — BM25F + ICD Soft Adaptive 5–15

## Cấu hình

- BM25F document-level trên đúng `1.205.935` official documents.
- Field weights: title `8`, lead `3`, body `1`, Chinese bigram `1`.
- Query VI/EN/ZH, IDF pruning, weighted RRF và ICD-10 soft boost.
- Adaptive cutoff: giữ document có score ít nhất `95%` top score, clamp `5–15` documents/query.
- Phân bố thực tế: min `5`, median `8`, mean `6,865`, max `12` documents/query.
- Chunks giữ nguyên value-by-value từ Exp51.

## Kết quả BTC

| Metric | Score | So với Exp51 |
| --- | ---: | ---: |
| FINAL_SCORE | 0.1558 | -0.1540 |
| DOCS_F2MACRO | 0.0263 | -0.3080 |
| CHUNKS_F2MACRO | 0.2853 | 0.0000 |
| DOCS_PRECISION | 0.1281 | -0.1017 |
| DOCS_RECALL | 0.0237 | -0.4473 |
| CHUNKS_PRECISION | 0.2414 | 0.0000 |
| CHUNKS_RECALL | 0.3653 | 0.0000 |

## Chẩn đoán hậu nghiệm

- `97,4%` documents được chọn chỉ xuất hiện trong đúng một language branch; RRF gần như chỉ interleave thay vì tạo đồng thuận đa ngôn ngữ.
- Output gồm `4.344` VI-only và `3.679` ZH-only documents; nhánh EN gần như biến mất do trọng số `0,5`.
- BM25 VI top-500 vẫn chứa trung bình `40,194/125` documents của Exp51; union ba branch chứa trung bình `45,847/125`. Candidate recall có tồn tại ở rank sâu nhưng top lexical ranking không đủ tốt.
- Output top bị nghiêng về `120ask.com`, `ask.39.net` và các domain Trung; PubMed, YouMed và Tâm Anh bị thiếu so với dense champion.
- ICD chapter-level quá rộng để sửa lỗi ranking ở mức document; không có bằng chứng cho hard filter.

## Quyết định

1. Không nộp pure-BM25 top-1/top-3 còn lại vì recall sẽ thấp hơn hoặc tương đương Exp55.
2. Không dùng BM25/ICD ranking để thay thế document champion.
3. Giữ BM25 làm candidate generator sâu (đặc biệt VI top-500), sau đó dense-score/rerank và chỉ cho phép thay một lượng nhỏ documents của Exp51.
4. Tách ablation ICD khỏi ablation BM25; chỉ giữ ICD nếu scorer BTC chứng minh có lợi trên cùng một dense candidate pool.
