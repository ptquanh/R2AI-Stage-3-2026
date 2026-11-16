# P1 follow-up — Qwen4B top160 docs-only

Trạng thái: BTC-scored, promoted làm control mới. Đây là một cardinality trial đã có trong policy curve trước kết quả P1 top195; không phải threshold được calibration bằng BTC qrels.

- Control source: Exp122 ZIP, SHA-256 `8c7f221cfafa401dfb5435df7da06464999c4b60594e69bc7726bb4ffb379886`.
- Scorer: `Qwen/Qwen3-Reranker-4B`, full scores đã audit; payload SHA-256 `bc36af1b525069c43927cf150cd04f3f6c636e692409c8ffcfdf86895ac650a4`.
- Policy: giữ Qwen top160 trong 216 docs/query và bắt buộc giữ mọi chunk-owning doc.
- 1.200/1.200 queries thay đổi; loại 47.176/259.200 query-docs (18,20%); còn 212.024.
- 20.024 chunk-owner docs nằm ngoài top160 được bảo vệ.
- `relevant_chunks` byte-identical với control; không đổi chunk membership, text, order hay count.
- Artifact: `submission_p1_qwen4b_top160_full.zip`, 99.421.900 bytes.
- Artifact SHA-256: `a88feb29279cba04fb7c7caf6eed8499ac6e415678ef050cf3c82f6062b27f40`.
- Independent validation: `data/audits/p1_full_qwen4b_merged/submission_p1_qwen4b_top160_validation.json`.
- Structural impact: `data/audits/p1_full_qwen4b_merged/policy_impact_top160.json`.

## Kết quả BTC

```json
{
  "FINAL_SCORE": 0.3138,
  "DOCS_F2MACRO": 0.3711,
  "CHUNKS_F2MACRO": 0.2565,
  "DOCS_PRECISION": 0.2085,
  "DOCS_RECALL": 0.5867,
  "CHUNKS_PRECISION": 0.1957,
  "CHUNKS_RECALL": 0.3427
}
```

So với P1 top195: Final `+0.0031`, Docs F2 `+0.0061`, Docs Precision `+0.0163`, Docs Recall `-0.0175`; toàn bộ chunk metrics bất biến đúng thiết kế. Promote top160 làm control mới. Tín hiệu xác nhận tail docs do Qwen4B xếp thấp có tỷ lệ false positive cao, nhưng không chứng minh mọi cutoff sâu hơn tiếp tục tốt.
