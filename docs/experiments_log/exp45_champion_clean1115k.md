[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 45: Exp40 champion config trên clean index 1.115.733 docs

## Mục tiêu

Đo riêng tác động của clean rebuild và corpus coverage mới. Giữ nguyên thuật toán, query, weight và output policy của Exp40; chỉ thay index 1.056.901 docs cũ bằng index sạch 1.115.733 valid docs.

## Kết quả BTC

- Final Score: **`0,3029`** — new champion.
- Docs F2: **`0,3266`**; Precision `0,2553`; Recall `0,4337`.
- Chunks F2: **`0,2792`**; Precision `0,2263`; Recall `0,3647`.

So với Exp40:

- Final `+0,0038`.
- Docs F2 `+0,0043`; Precision `+0,0032`; Recall `+0,0052`.
- Chunks F2 `+0,0033`; Precision `+0,0025`; Recall `+0,0039`.

Cả 7 chỉ số cùng tăng. Clean rebuild và 99.448 valid docs mới cải thiện đồng thời precision lẫn recall; Exp45 thay Exp40 làm champion.

## Cấu hình

- Hybrid linear giống Exp40: dense `1,0` + sparse `0,2`.
- Sparse query fusion: VI + ZH × `1,0` + EN × `0,5`.
- Candidate generation giống champion: dense top-400, sparse rescoring trong pool đó.
- `cand_pool=150`, `top_docs=100`, `top_chunks=98`.
- Không dùng independent union, RRF mới, reranker hay threshold.
- Index: 1.115.733 valid docs, 1.590.459 chunks.

## Delta corpus

- Thêm 99.448 valid docs đã embed so với index Exp40.
- Loại 40.616 docs ngoài corpus.
- Net tăng 58.832 docs.
- 4.895 document output positions đến từ tập 99.448 docs mới, trải trên 1.044/1.200 query.
- 4.488 chunk output positions đến từ docs mới, trải trên 999/1.200 query.

## Mức thay đổi so với Exp40

- Document overlap trung bình: 95,8808/100; tức chỉ thay khoảng 4,12 docs/query.
- Chunk overlap trung bình: 93,7258/98; tức thay khoảng 4,27 chunks/query.
- Đây là thay đổi nhỏ, chủ yếu do corpus mới, không phải do fusion như Exp41.

## Validation

- 1.200 query.
- 1.191 query có 100 docs; 9 query có 90–99 docs, tương tự hành vi Exp40 do nhiều chunks trùng document trong `cand_pool=150`.
- 98 chunks/query.
- Không có duplicate document trong cùng query.
- 0 ID ngoài corpus.
- 78.090 source documents cần cho chunk đều load được; 0 chunk không phải substring nguyên văn.
- ZIP: 97.675.939 byte.
- SHA-256: `28f5534aafc8092bc0c5b1c68012500eb24f8709a3ead0eb77c499b6d3a2113a`.

## Artifact

- Submission: `submission_exp45_champion_clean1115k.zip`
- JSON: `submission_exp45_champion_clean1115k.json`
- Manifest: `submission_exp45_champion_clean1115k_manifest.json`

## Cách đọc kết quả

- [x] Docs/Chunks F2 cùng tăng: giữ index sạch và tiếp tục embed/crawl phần coverage còn thiếu.
- Nếu điểm ngang Exp40: 99.448 docs mới phần lớn redundant; ưu tiên reranker/chunk evidence.
- Nếu điểm giảm: kiểm tra 4,12 docs và 4,27 chunks bị thay trung bình; không quy lỗi cho clean filtering vì 40.616 docs bị loại không xuất hiện trong submission Exp40.
