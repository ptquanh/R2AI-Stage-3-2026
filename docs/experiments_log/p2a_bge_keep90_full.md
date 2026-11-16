# P2a — BGE chunk filtering keep90

Kết quả BTC do người dùng báo, ghi nhận ngày 2026-10-26; không có timestamp chấm độc lập.

- Artifact: `submission_p2a_bge_keep90_full.zip`.
- SHA-256: `5c81bb37ed361d198f7f5fca7f72cb3bda7b42fbc1c788429605ab8caab4d673`.
- Control: P1 Qwen4B top195, Final 0.3107, Docs F2 0.3650, Chunks F2 0.2565.
- Policy: giữ ceil(90% số chunks) từng query theo max-window BGE score; docs/text còn lại không đổi.
- Loại 12.447/130.108 chunks; ZIP 89.169.813 bytes.

```json
{
  "FINAL_SCORE": 0.31,
  "DOCS_F2MACRO": 0.365,
  "CHUNKS_F2MACRO": 0.2551,
  "DOCS_PRECISION": 0.1922,
  "DOCS_RECALL": 0.6042,
  "CHUNKS_PRECISION": 0.2069,
  "CHUNKS_RECALL": 0.3319
}
```

Final giảm 0.0007; chunk precision tăng 0.0112 nhưng recall giảm 0.0108 và F2 giảm 0.0014.
Không promote; không sweep keep fraction. Kết quả không bác bỏ toàn bộ reranking/translation.
Thử tiếp P2b: chọn paragraph spans nguyên văn, khóa docs và số chunks/doc, chấm đúng input
được nộp, không truncation ngầm, fallback parent. Không dùng local scorer/qrels tự tạo.
