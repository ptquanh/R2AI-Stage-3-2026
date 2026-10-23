# Exp 74 — Refresh Exp73 trên active index 1,212M documents

## Mục tiêu

Đo tác động của đợt embedding `1k_urls.zip` trên document retrieval mà không đổi chunk axis đã thắng của Exp73. Đây là active index gần đầy đủ, không gọi là coverage 100% corpus BTC: sau merge vẫn còn 560 tài liệu trong `unembedded`, 7.434 URL trong `remaining` và 183 URL trong `excluded`.

## Merge/rebuild

- Artifact: `data/indices/new_dataset/1k_urls.zip`.
- SHA-256: `6dc5a9fd0c0fb306491427c6335ba4f73c84264216ef7c698a9d7beab484aea4`.
- Artifact hợp lệ: 1.146 documents / 1.156 chunks; không có ID ngoài corpus hoặc overlap active index.
- Active index: 1.211.275 → 1.212.421 documents; 1.723.642 → 1.724.798 chunks.
- Registry: chuyển đúng 1.146 hàng `unembedded → embedded`; `unembedded` còn 560. `remaining` 7.434 và `excluded` 183 không đổi.
- Backup index trước merge: `data/indices/new_dataset/index_backup_pre_recovered_merge_20261019T130400`.
- Manifest: `data/audits/1k_index_merge_20261019/manifest.json`.

## Cấu hình submission

- Control/chunk source: Exp73.
- Khóa nguyên lineage ranks 1–260 đã tạo Exp73; chỉ dựng lại dense ranks 261–300 trên active index mới.
- Rerank lại pool ranks 151–300, giữ protected head 1–150.
- Tái dùng BGE cross-encoder scores cũ chỉ cho đúng cặp `(query_id, doc_id)` đã chấm.
- Chấm mới 7.628 spans thuộc 3.792 cặp query/document chưa có cache bằng `BAAI/bge-reranker-v2-m3`, `max_length=384`.
- Rerank pool bằng `0,75 × normalized CE + 0,25 × normalized stage rank`; chọn 66 tail documents để xuất 216 documents/query.
- Giữ `relevant_chunks` Exp73 value-by-value để cô lập document axis.

## Mức thay đổi so với Exp73

- 760/1.200 queries đổi document tail.
- 1.723 document occurrences được thay, trung bình 1,436/query, median 1, max 11.
- Riêng docs thuộc artifact `1k_urls.zip` được chọn 46 lần trên 41 queries, tối đa 3/query. Các thay đổi tail khác cũng bao gồm docs từ các đợt merge trước Exp73 chưa được refresh retrieval.
- Chunks không đổi.

## Artifact và audit

- JSON: `submission_exp74_full1212k_exp73_refresh.json`.
- ZIP: `submission_exp74_full1212k_exp73_refresh.zip`.
- ZIP: 99.553.338 bytes; còn 446.662 bytes dưới giới hạn decimal 100.000.000 bytes.
- ZIP SHA-256: `8758acbb1cace20aa14dcd92922c17d59efc8b263766595c3f285d3996672161`.
- JSON SHA-256: `8ef4ee746d5f09a63b026739df84f116fd094ea9faea7f47a95a31551881a752`.
- Đủ 1.200 query, đúng 216 docs/query, không duplicate docs hoặc duplicate `(doc_id, chunk_text)`, chỉ official IDs.
- ZIP chỉ có `submission.json`, CRC hợp lệ và payload khớp JSON ngoài ZIP.
- Bốn query có cùng `chunk_text` ở các `doc_id` khác nhau; đây không phải duplicate `(doc_id, chunk_text)` và được kế thừa nguyên vẹn từ Exp73.
- Test suite cấp dự án: 27/27 passed.

## Kết quả BTC — nhận ngày 19/10/2026

- FINAL_SCORE: `0,3221` (`+0,0007` so với Exp73).
- DOCS_F2MACRO: `0,3574` (`+0,0014`).
- CHUNKS_F2MACRO: `0,2868` (không đổi).
- DOCS_PRECISION: `0,1813` (`+0,0005`).
- DOCS_RECALL: `0,6086` (`+0,0027`).
- CHUNKS_PRECISION / CHUNKS_RECALL: `0,2401 / 0,3685` (không đổi).

Exp74 là champion nội bộ mới. Refresh document tail tăng đồng thời Docs precision và recall; chunk metrics khớp Exp73 đúng thiết kế. Kết quả phản ánh cả các batch merge trước đó và pool refresh, chưa tách được gain riêng của `1k_urls.zip` hoặc filter mới. Ranks 1–260 và chunks vẫn kế thừa lịch sử, nên đây chưa phải rerun toàn bộ retrieval/evidence trên index mới.

Còn thiếu `0,0543` để bằng baseline BTC `0,3764` và `0,0579` để đạt `0,38`. Ưu tiên tiếp theo là evidence coverage theo mục 13 của kế hoạch: dùng Docs Exp74 làm control, thử phủ khoảng 140 documents/query trong ZIP target ≤95 MB. Gán dự kiến Exp75 cho nhánh này; Exp74 đã dùng cho refresh index.
