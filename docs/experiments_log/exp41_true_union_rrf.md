[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 41: Independent multilingual candidate union + weighted RRF

## Mục tiêu

Kiểm tra trực tiếp giả thuyết ở Gate 2: pipeline cũ chỉ lấy dense top-400 rồi chấm sparse trên chính tập đó, nên sparse và query translation không thể cứu candidate ngoài dense pool.

Exp41 tạo candidate độc lập trên toàn bộ 1.590.459 chunks của index sạch cho từng nhánh, sau đó mới union và fuse.

## Kết quả BTC

- Final Score: `0,2523`.
- Docs F2: `0,2747`; Precision `0,2121`; Recall `0,3696`.
- Chunks F2: `0,2298`; Precision `0,1869`; Recall `0,3019`.

So với Exp40, Final giảm `0,0468`; Docs F2 giảm `0,0476`; Chunks F2 giảm `0,0461`. Docs Recall và Chunks Recall cùng giảm đúng `0,0589`, trong khi precision cũng giảm. Đây là regression toàn diện, không phải trade-off precision/recall.

**Kết luận:** candidate độc lập có khả năng mở rộng coverage, nhưng weighted RRF hiện tại đã thay ranking quá mạnh: trung bình 35,97/100 docs bị thay so với Exp40. Các nhánh EN/ZH/sparse có trọng số đủ lớn để đẩy candidate tốt của champion ra khỏi top-100. Exp41 còn thay đồng thời bốn branch, fusion và chunk ranking, nên không dùng được để quy trách nhiệm cho riêng branch nào.

**Quyết định:** không dùng Exp41 làm champion. Giữ cache candidate để ablate mà không retrieval lại; lần kế tiếp phải giữ nguyên chunks Exp40 và chỉ thay document ranking, đồng thời giới hạn mức thay đổi khoảng 5–10 docs/query.

## Cấu hình submission chính

- Index: 1.115.733 documents hợp lệ, 1.590.459 chunks.
- Candidate mỗi nhánh: top 500.
- Dense retrieval độc lập: query VI, EN và ZH với BGE-M3.
- Sparse retrieval độc lập: BGE-M3 lexical VI + ZH × 1,0 + EN × 0,5, tìm trên toàn sparse index.
- Fusion: weighted RRF, `rrf_k=60`.
- Trọng số: dense VI `1,00`; sparse `0,90`; dense ZH `0,45`; dense EN `0,35`.
- Document fusion và chunk fusion được tính riêng. Mỗi branch collapse về document rank trước khi cộng RRF cho `relevant_docs`, tránh document có nhiều chunks được lợi không công bằng.
- Output trước đóng gói: 100 documents và 98 chunks/query. Bản ZIP cuối giữ 100 documents và 96 chunks/query để nằm dưới cả cách hiểu 100 MB hệ thập phân.
- Chunk là substring nguyên văn; dedup theo span và `(doc_id, chunk_text)`, không dedup text giữa các document khác nhau.

## Vì sao chưa trộn BM25 vào bản chính

Artifact `corpus_fts.db` hiện có không phải bản tái tạo đáng tin cậy của BM25 baseline BTC:

- Chứa 1.358.107 documents từ corpus cũ, không khớp index sạch hiện tại.
- Dùng SQLite FTS5 `unicode61` và OR-unigram.
- Exp20 với artifact này chỉ đạt Docs F2 `0,0736`.

Script vẫn hỗ trợ `--include-legacy-bm25` như một ablation document-level có cache, nhưng mặc định tắt để Exp41 đo đúng tác động của independent candidate union. BM25 đúng corpus/analyzer vẫn thuộc Gate 1 riêng.

## Kiểm tra trước khi nộp

- 1.200/1.200 query, đúng ID và thứ tự.
- 100 documents/query; không duplicate document.
- 96 chunks/query trong artifact cuối; không duplicate `(doc_id, chunk_text)` trong cùng document.
- Mọi `doc_id` đều thuộc 1.220.598 ID trong corpus chính thức.
- Mọi `chunk_text` đều là substring nguyên văn của source document.
- ZIP: khoảng 99,23 triệu byte (94,63 MiB), dưới giới hạn 100 MB theo cả hệ thập phân lẫn nhị phân.
- SHA-256 của ZIP: `693fe87edb3c844362b24cb313d97952403c9cf95b412363352d63f4349d092b`.
- Model: BGE-M3 open-weight, nằm trong giới hạn 15B của cuộc thi; không dùng closed-source API để tạo retrieval output.

## Mức thay đổi so với Exp40

- Trung bình 64,03/100 documents/query trùng bản `submission_bgem3_trilingual_105m_corpus`; tức 35,97 documents/query được thay mới.
- Cả 1.200 query đều thay đổi ranking.
- Trung bình 19,74/100 documents cuối không nằm trong dense-VI top-500, xác nhận sparse và bản dịch đã thực sự cứu candidate ngoài dense VI pool.
- Trong top-100 cuối, mức hiện diện trung bình theo candidate branch: dense VI 80,26; sparse 73,85; dense ZH 48,37; dense EN 45,69. Các tập có overlap nên tổng lớn hơn 100.

Đây chỉ là diagnostic về độ khác biệt ranking, không phải bằng chứng điểm tăng. Kết luận phải dựa trên điểm BTC.

## Artifact

- Generator: `scripts/generate_true_union_submission.py`
- Submission: `submission_exp41_true_union_rrf.zip`
- JSON: `submission_exp41_true_union_rrf.json`
- Manifest: `submission_exp41_true_union_rrf_manifest.json`
- Retrieval caches: `data/indices/new_dataset/index/.cache/exp41_true_union/`

## Quyết định sau khi có điểm BTC

- [x] Docs F2 không tăng: giảm/tắt từng nhánh EN, ZH, sparse bằng cách tái fuse cache hiện có; không cần chạy lại retrieval.
- [ ] Exp42: giữ nguyên chunks Exp40; chỉ thử document fusion giữa champion ranking, dense VI và sparse độc lập với mức thay 5–10 docs/query.
- [ ] Chỉ sau khi sparse docs-only có lợi mới thêm lần lượt ZH rồi EN; không bật cả hai cùng lúc.
