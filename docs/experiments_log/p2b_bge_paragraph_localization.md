# P2b — BGE paragraph localization (full)

Kết quả BTC do người dùng báo ngày 2026-10-26. Candidate chỉ thay chunk text bằng paragraph group nguyên văn được chọn bên trong chunk parent; docs, owner và số lượng chunks/query giữ nguyên.

- Artifact: `submission_p2b_localized_full.zip`.
- SHA-256: `7b0eccc8c8ec83f951cb8a2e9f3871b0e52bf12df95cfdbd3c646646307a8189`.
- BGE reranker revision: `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e`.
- 40.429/130.108 chunks được localize; structural/source audit pass.
- Control P1 top195: Final 0.3107, Docs F2 0.3650, Chunks F2 0.2565.
- P2a keep90: Final 0.3100, Docs F2 0.3650, Chunks F2 0.2551.

```json
{
  "FINAL_SCORE": 0.2641,
  "DOCS_F2MACRO": 0.365,
  "CHUNKS_F2MACRO": 0.1632,
  "DOCS_PRECISION": 0.1922,
  "DOCS_RECALL": 0.6042,
  "CHUNKS_PRECISION": 0.1202,
  "CHUNKS_RECALL": 0.2269
}
```

Docs metrics are unchanged. Versus P1 top195, Final falls 0.0466 and Chunks F2 falls 0.0933; versus P2a, Final falls 0.0459 and Chunks F2 falls 0.0919. Chunk precision and recall both regress substantially. Reject this policy; do not promote or tune its raw-logit/margin thresholds. The outcome shows these BGE-selected short paragraph groups are poor submission evidence under BTC matching; it does **not** isolate whether the cause is span length, paragraph relevance, or the uncalibrated scoring policy. Restore P1 top195 as control.
