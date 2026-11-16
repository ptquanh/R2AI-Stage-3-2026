# Exp138 — Sentence-aligned passages, fixed Exp122 docs

## Giả thuyết

Exp134/135 cho thấy thêm anchored windows theo count/width cố định làm chunk P/R giảm theo evaluator mới. Exp138 giữ nguyên documents và số chunks/query của Exp122, nhưng thay passage selection: chia source text theo ranh giới câu, gộp tối đa sáu câu liền kề thành đoạn tự nhiên (120–1.500 ký tự), xếp hạng lexical đoạn kết hợp dense rank của indexed chunk chứa đoạn. Mỗi document đóng góp tối đa một passage ở lượt đầu, tối đa hai nếu cần đủ count.

Giả thuyết ban đầu là sentence-aligned passage selection có thể nâng precision mà vẫn giữ recall. Kết quả BTC bên dưới bác bỏ treatment này; không tiếp tục sweep độ dài trên cùng thiết kế.

## Cấu hình

- Control: Exp122 re-evaluated, ZIP SHA-256 `8c7f221cfafa401dfb5435df7da06464999c4b60594e69bc7726bb4ffb379886`.
- Docs: khóa nguyên thứ tự và membership của Exp122 (216 unique docs/query).
- Chunk count: khóa theo Exp122 từng query (tổng 130.108).
- Passage builder: sentence boundary packing; min 120, max 1.500 ký tự, tối đa 6 câu; câu đơn vượt max bị bỏ khỏi candidate pool, không bị cắt giữa câu.
- Ranking: 65% RRF dense rank của source chunk, 35% RRF lexical rank trên passage query tiếng Việt gốc; `k=60`.
- Diversity: tối đa 1 passage/doc trước, sau đó tối đa 2; không chọn đoạn chồng lấn trong cùng doc. Không dùng translation, LLM hay API.
- Encoder/index: BAAI/bge-m3; model revision `5617a9f61b028005a4858fdac845db406aefb181`.

## Artifact và validation

- Builder: `scripts/generate_sentence_passage_submission.py`.
- Independent validator: `scripts/validate_sentence_passage_submission.py`.
- Tests: `tests/test_sentence_passage_submission.py` — 6 passed.
- ZIP: `submission_exp138_sentence_passages_fixed_docs.zip`, `19.986.265` bytes (<100 MB).
- SHA-256 ZIP: `f3b0736811a9d85f09485b85418d9bf85b662a3a15c1db9cd56188e4f71486fa`.
- SHA-256 JSON: `e1a8812c1d67f089ef2e1ca3f0e398f751c3c5f114f761c2bc4b1ee28f9a5f18`.
- 1.200 rows / 130.108 chunks; exact docs order and per-query chunk count match Exp122; every chunk belongs to a returned doc; zero fallback chunks; ZIP CRC passes.
- Selected passage lengths: min 120, median 554, p90 861, max 1.500 chars.

## Kết quả BTC

Người dùng báo kết quả ngày 23/10/2026; evaluator mới LCS hai phía:

```json
{"FINAL_SCORE":0.2031,"DOCS_F2MACRO":0.3586,"CHUNKS_F2MACRO":0.0477,"DOCS_PRECISION":0.1816,"DOCS_RECALL":0.6114,"CHUNKS_PRECISION":0.0365,"CHUNKS_RECALL":0.0644}
```

So với Exp122 (2): Final `-0.1044`, Chunks F2 `-0.2088`, Chunk precision `-0.1592`, recall `-0.2783`; Docs metrics giữ nguyên. **Loại Exp138, giữ control 0.3075.**

## Hậu kiểm sau kết quả — 2026-10-23

Đọc trực tiếp hai ZIP, so từng query bằng streaming JSON (không inference, không sửa artifact):

- 1.200/1.200 docs lists giữ nguyên, tổng chunks cùng 130.108; nhưng **1.200/1.200 chunk-owner sets thay đổi**.
- Bỏ 28.998 cặp query–doc evidence control và thêm 28.998 cặp khác; trung bình chỉ giữ `77.776%` owner set ban đầu.
- Median chars `3.933,5 → 554`. Chunks có >20% ký tự CJK vùng U+4E00–U+9FFF giảm `25.256 → 15.411`. Đây là heuristic script composition, không phải phân loại ngôn ngữ/relevance.
- AST-extracted `sentence_ranges`/`make_passages` tái hiện lỗi: chuỗi `医学文本。` lặp 400 lần (2.000 chars, có dấu câu, không khoảng trắng) tạo 1 sentence span và **0 passages**. Regex yêu cầu whitespace sau dấu câu; câu dài hơn 1.500 chars bị bỏ hoàn toàn.
- Passage rank kế thừa dense parent, không có passage cross-encoder. Lexical VI trên nguồn đa ngữ và rank tie theo input order có thể gây bias.
- Cần test/sửa mapping overlap: điều kiện đúng là `chunk_end > passage_start AND chunk_start < passage_end`; hiện searchsorted fallback so nhầm biên, cần kiểm tra tính đơn điệu ends và không gán chunk không giao.

Đây không phải ablation thuần span length: owners, segmentation, ranking và diversity policy cùng đổi. Chưa có nhãn hợp lệ để phân bổ mức giảm điểm cho từng yếu tố; không khẳng định chỉ sửa splitter sẽ phục hồi score. Validator cũ pass format/count, không chứng minh quality. Ưu tiên tiếp theo là verifier/relevance filtering trên nguyên evidence control; xem [kế hoạch hiện hành](../r2ai_score_improvement_plan.md).
