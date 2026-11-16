# Joint trial — Qwen top130 docs + P2a keep90 chunks

Trạng thái: BTC-scored, không promote theo Final. Đây là joint membership treatment.

- Base: Exp122, SHA-256 `8c7f221cfafa401dfb5435df7da06464999c4b60594e69bc7726bb4ffb379886`.
- Docs: Qwen4B top130 trên 216 docs/query, cộng các internal owners của **tập chunks sau P2a filtering**.
- Chunks: exact byte/order membership của `submission_p2a_bge_keep90_full.zip`, SHA-256 `5c81bb37ed361d198f7f5fca7f72cb3bda7b42fbc1c788429605ab8caab4d673`.
- Qwen full-score payload SHA-256 `bc36af1b525069c43927cf150cd04f3f6c636e692409c8ffcfdf86895ac650a4`.
- 1.200 queries; docs `259.200 → 183.703` (remove 75.497); chunks `130.108 → 117.661` (remove 12.447).
- So với top130 docs-only, joint candidate bỏ thêm 6.484 docs vì P2a đã loại toàn bộ evidence chunks khiến chúng không còn cần owner protection.
- 946 external owner query-docs đã tồn tại từ Exp122/P2a được giữ nguyên semantics; không tự ý thêm vào 216-doc pool.
- Artifact: `submission_joint_qwen_top130_p2a_keep90_v1.zip`, 88.961.424 bytes.
- SHA-256: `d1e618b33b4106ff832cabb2fd281a25b6abe44decead29199388c80294c7da0`.
- Independent validator: `data/audits/joint_qwen_top130_p2a_keep90_validation.json`, exact joint policy pass.

## Kết quả BTC

```json
{
  "FINAL_SCORE": 0.3141,
  "DOCS_F2MACRO": 0.3731,
  "CHUNKS_F2MACRO": 0.2551,
  "DOCS_PRECISION": 0.2261,
  "DOCS_RECALL": 0.5631,
  "CHUNKS_PRECISION": 0.2069,
  "CHUNKS_RECALL": 0.3319
}
```

So với top130 docs-only: Docs F2 `+0.0009` (P `+0.0046`, R `-0.0048`), nhưng Chunks F2 `-0.0014`; Final `-0.0002`. Không promote nguyên joint artifact. Tuy nhiên owner-release docs là docs axis tốt nhất hiện tại, còn original Exp122 chunks là chunk axis tốt nhất; hai trục được evaluator tính riêng theo đặc tả. Follow-up hợp lệ là recombine đúng hai axis đã chấm, không tune threshold mới.
