# Exp136 — Production translation dense-RRF, docs-only

## Giả thuyết

Các bản dịch production đã qua audit có thể cải thiện phần tail của danh sách docs khi kết hợp với truy vấn gốc, trong khi giữ nguyên champion evidence của Exp122. Thử nghiệm chỉ thay 66 docs tail/query; giữ khóa 150 docs đầu và toàn bộ chunks Exp122.

## Cấu hình

- Control: `submission_exp122_exp121_add19_miss.zip`, SHA-256 `8c7f221cfafa401dfb5435df7da06464999c4b60594e69bc7726bb4ffb379886`.
- Query views: query VI gốc cho 1.200 câu; EN translation status `ok` cho 1.097 câu; ZH status `ok` cho 715 câu. Các view `needs_review` bị loại và fallback tự nhiên về query gốc.
- Encoder/index: BGE-M3, exact dense retrieval trên active index.
- Mỗi view lấy top 4.096 chunk hits; deduplicate theo doc rồi weighted RRF, `k=60`, weights VI/EN/ZH `1.0/0.35/0.35`.
- Giữ 150 docs đầu của Exp122; thay tail bằng 66 unique docs đứng đầu RRF. Tất cả chunks được copy nguyên trạng từ Exp122.

## Artifact và kiểm định

- ZIP: `submission_exp136_translation_production_v1.zip`, **99.319.388 bytes**, dưới ngưỡng decimal 100 MB.
- JSON: `submission_exp136_translation_production_v1.json`, 741.723.821 bytes.
- SHA-256 ZIP: `db6f79b0318a5aaa02d0698d922bc4eec6af7931a27c9092a20fb2e393d09bb4`.
- SHA-256 JSON: `16094688b3aa2b51a5e946e06fc27da75692a4e7efc0d558fd75b9f1cb37b2e9`.
- Có đủ 1.200 query, mỗi query đúng 216 unique docs; 150 docs đầu giữ nguyên; 79.200 tail slots được thay; toàn bộ **130.108 chunks** bằng Exp122.
- ZIP chỉ chứa root `submission.json`; CRC, payload/JSON hash, official document IDs và so sánh chunks pass.
- Manifest đầy đủ: `submission_exp136_translation_production_v1_manifest.json`.

## Kết quả

```json
{"FINAL_SCORE":0.2813,"DOCS_F2MACRO":0.3061,"CHUNKS_F2MACRO":0.2565,"DOCS_PRECISION":0.152,"DOCS_RECALL":0.5334,"CHUNKS_PRECISION":0.1957,"CHUNKS_RECALL":0.3427}
```

Docs F2 giảm `0.0525` so với Exp122. Đây **không phải best config nguyên vẹn**: Exp136 dùng Exp122 làm scaffold, giữ 150/216 docs đầu/query rồi thay 66 docs tail ở toàn bộ 1.200 query. Các delta Final `-0.0703` / Chunks F2 `-0.0881` từng ghi so với Exp122 legacy không được coi là regression retrieval vì evaluator có thể đã đổi.

## Hậu kiểm

So sánh artifact cho thấy overlap docs giữa Exp122 và Exp136 trung bình chỉ `150.002/216`; mọi query đều có thay đổi membership (tổng `79.198` docs bị bỏ và thêm). Dù chunk list được copy nguyên trạng, `6.955` query-doc chunk pairs trong `1.149` query trỏ tới docs không còn nằm trong Exp136 `relevant_docs`.

**Đính chính sau re-eval Exp122:** cả ba chunk metrics Exp136 trùng Exp122 (2): `0.2565 / 0.1957 / 0.3427`. Điều này rất phù hợp với việc Exp136 đã được chấm bằng rule mới. Rút lại nhận định mismatch là “giả thuyết mạnh giải thích chunk regression”: số liệu hiện có không hỗ trợ quy kết đó. Mismatch vẫn cần tránh để output nhất quán; docs tail replacement thực sự làm Docs P/R/F2 giảm.

**Bài học / quyết định:** không promote Exp136. Với lần thử tiếp theo, docs và chunks phải được xử lý như một cặp nhất quán: nếu thay document membership thì chỉ thêm chunks thuộc docs mới theo cùng candidate policy, hoặc giữ danh sách docs của champion tuyệt đối cố định để cô lập chunk treatment. Không dùng “chunks giữ nguyên” như bằng chứng rằng trục chunks không đổi khi docs bị thay.

## Evaluator version status

Chưa có execution metadata xác nhận evaluator. Việc điểm được báo trước lần re-eval Exp122 không đồng nghĩa dùng rule cũ. Nếu cùng rule mới, Final thấp hơn control `0.0262`, chunks không đổi ở độ chính xác đã báo. Không ưu tiên nộp lại treatment này; kiểm tra timestamp nếu có và ưu tiên A/B mới cô lập retrieval/translation.
