# Exp137 — Translation-driven chunks with fixed Exp122 docs

## Mục tiêu và giả thuyết

Sau regression Exp136, cố định hoàn toàn `relevant_docs` theo Exp122 để không lặp lại việc chunks trỏ đến document bị loại khỏi danh sách docs. Dùng query VI và các bản EN/ZH đã qua audit để xếp hạng dense passages BGE-M3 **chỉ trong chunks thuộc 216 docs Exp122 của từng query**.

## Cấu hình

- Control: `submission_exp122_exp121_add19_miss.zip`, SHA-256 `8c7f221cfafa401dfb5435df7da06464999c4b60594e69bc7726bb4ffb379886`.
- Encoder/index: BGE-M3; exact dense scoring trên vectors active index, chỉ trong docs đã khóa.
- Chunk ranking: weighted RRF, `k=60`, VI/EN/ZH weights `1.0/0.35/0.35`; EN/ZH chỉ bật khi status audit là `ok`.
- `relevant_docs` giữ nguyên byte/giá trị theo Exp122; số chunks/query cũng giữ nguyên (83–121; tổng 130.108).
- Chunk text là verbatim source spans lấy theo chunk metadata của active index. **Khác với Exp122, cách chọn span/độ dài chunk vì vậy cũng thay đổi**; thí nghiệm cố định trục document nhưng không cô lập riêng tác động của bản dịch khỏi segmentation policy.

## Artifact và kiểm định

- Generator: `scripts/generate_translation_chunks_fixed_docs.py`.
- ZIP: `submission_exp137_translation_chunks_fixed_docs.zip`, **60.164.751 bytes**, dưới decimal 100 MB.
- JSON: `submission_exp137_translation_chunks_fixed_docs.json`.
- SHA-256 ZIP: `95b9ae25e7b303d5b45d846eae9be9faa83a9506d152432440b06e7b01b02412`.
- SHA-256 JSON: `5c4026db415dc2944cc152fca6187036e5270854c65ad69f223949b7a7a06fae`.
- 1.200 query; 130.108 chunks. Independent streaming check: all docs identical to Exp122; every chunk belongs to a returned doc; ZIP payload equals JSON and CRC passes.
- Production translation ZIP SHA-256: `31d9e5f8cc6f53d3d081103002803491c1c625de09fe3657f842f31a3049f8c2`.

## Kết quả BTC

```json
{"FINAL_SCORE":0.294,"DOCS_F2MACRO":0.3586,"CHUNKS_F2MACRO":0.2295,"DOCS_PRECISION":0.1816,"DOCS_RECALL":0.6114,"CHUNKS_PRECISION":0.1766,"CHUNKS_RECALL":0.306}
```

Docs metrics trùng Exp122 vì document IDs giữ nguyên. Không dùng delta so với điểm legacy Exp122 để kết luận regression khi evaluator có thể đã đổi. Nếu Exp137 dùng rule mới như control Exp122 (2), delta Final là `-0.0135`, Chunks F2 `-0.0270`, Chunk precision `-0.0191`, recall `-0.0367`; cần xác nhận metadata evaluator trước coi đây là so sánh cùng phiên bản.

## Hậu kiểm artifact

- Exp122 median chunk length `3.934` ký tự, p90 `7.193`; Exp137 median `1.867`, p90 `3.367`.
- Exact `(doc_id, chunk_text)` overlap trung bình chỉ `29.1%` theo query; chunk-owning-doc overlap là `71.2%`.
- Vì vậy Exp137 vừa đổi passage selection bằng VI/EN/ZH, vừa đổi segmentation/độ dài mạnh. Các đoạn ngắn hơn có thể không đạt ngưỡng overlap LCS `0.4` với chunk tham chiếu; đồng thời passage selection có thể kém phù hợp. Kết quả không đủ để quy regression cho translation riêng lẻ.

## Kết luận

Exp137 loại bỏ rủi ro doc/chunk membership mismatch của Exp136 và giữ nguyên Docs axis, nhưng chunk treatment regression mạnh. Không promote. Kết quả ủng hộ việc sửa passage construction/coverage trước; cần A/B VI-only vs VI+translation trên cùng candidate chunk pool và cùng segmentation mới có thể kết luận dịch giúp hay hại.

## Evaluator version status

Điểm được báo trước lần re-eval Exp122 nhưng không vì vậy mà mặc định là rule cũ; phiên bản evaluator chưa có execution metadata xác nhận. Không ưu tiên dùng slot nộp lại treatment nhiều biến này. Kiểm tra timestamp nếu có; đầu tư A/B cùng candidate pool, owners và segmentation để xác định riêng tác động dịch.
