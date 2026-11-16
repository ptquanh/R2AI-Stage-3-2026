# P1 follow-up — Qwen4B top130 docs-only

Trạng thái: BTC-scored, promoted làm control mới. Chỉ một breakpoint sâu hơn được chọn sau khi top160 thắng top195; không sweep các cutoff lân cận.

- Control source: Exp122 ZIP, SHA-256 `8c7f221cfafa401dfb5435df7da06464999c4b60594e69bc7726bb4ffb379886`.
- Current BTC control for comparison: P1 top160, Final `0.3138`, Docs F2/P/R `0.3711/0.2085/0.5867`.
- Scorer: `Qwen/Qwen3-Reranker-4B`; full score payload SHA-256 `bc36af1b525069c43927cf150cd04f3f6c636e692409c8ffcfdf86895ac650a4`.
- Policy: giữ Qwen top130 trong 216 docs/query và bắt buộc giữ mọi chunk-owning doc.
- 1.200/1.200 queries thay đổi; loại 69.013/259.200 query-docs (26,63%); còn 190.187 (mean 158,49/query).
- 34.187 chunk-owner docs nằm ngoài top130 được bảo vệ.
- `relevant_chunks` byte-identical với Exp122/top160; không đổi chunk membership, text, order hay count.
- Artifact: `submission_p1_qwen4b_top130_full.zip`, 99.338.819 bytes.
- SHA-256: `ec32de34c32aca79b8a9986962291162cdc3042a267c2ef7fa26db369ebf6d27`.
- Independent validation: `data/audits/p1_full_qwen4b_merged/submission_p1_qwen4b_top130_validation.json`.
- Structural comparison: `data/audits/p1_full_qwen4b_merged/policy_impact_deeper_breakpoints.json`.

## Kết quả BTC

```json
{
  "FINAL_SCORE": 0.3143,
  "DOCS_F2MACRO": 0.3722,
  "CHUNKS_F2MACRO": 0.2565,
  "DOCS_PRECISION": 0.2215,
  "DOCS_RECALL": 0.5679,
  "CHUNKS_PRECISION": 0.1957,
  "CHUNKS_RECALL": 0.3427
}
```

So với top160: Final `+0.0005`, Docs F2 `+0.0011`, Docs Precision `+0.0130`, Docs Recall `-0.0188`; chunks bất biến. Promote top130 làm control mới nhưng dừng fixed-cutoff ladder vì gain đã giảm mạnh và thấp hơn ngưỡng ưu tiên nguồn lực.
