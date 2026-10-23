# Exp 123 — Exp121 + 19 CE-ranked missing-document parents

## Giả thuyết

Exp122 tăng Chunk F2 lên `0,3446` bằng 19 full-source parents/query nhưng chọn additions theo thứ tự document rank. Exp123 giữ nguyên số lượng và toàn bộ Exp121, sau đó chọn 19 missing selected docs/query theo điểm BGE cross-encoder đã cache trong Exp75. Đây là ablation về cách chọn document với output count tương đương Exp122.

## Artifact và audit

- File nộp: `submission_exp123_exp121_add19_ce_ranked_parents.zip`.
- ZIP: `98.423.366` bytes, method 14 (LZMA), CRC pass, một `submission.json` ở root.
- 60.076 CE candidates giao với selected docs chưa có chunk evidence; mỗi query có 31–60 candidates (mean `50,06`).
- 19 additions/query, tổng `22.800`, từ 21.245 source docs.
- Giữ nguyên toàn bộ Exp121; docs và số chunks giống Exp122.
- Parent bổ sung mean/median `3.458/2.849` ký tự; tổng `78.846.567` ký tự.
- SHA-256 ZIP: `ba6ead9d7f5703980ce39eba7161b7d99964fc560377cf2effe7062c63bfaaee`.
- SHA-256 JSON: `d96493bc5071c64f240934cc2044060b7a707a99cf80e1f585e9d4c1df2e040e`.

## Kết quả BTC

Kết quả do người dùng cung cấp ngày 21/10/2026:

```json
{
  "FINAL_SCORE": 0.3501,
  "DOCS_F2MACRO": 0.3586,
  "CHUNKS_F2MACRO": 0.3417,
  "DOCS_PRECISION": 0.1816,
  "DOCS_RECALL": 0.6114,
  "CHUNKS_PRECISION": 0.2504,
  "CHUNKS_RECALL": 0.4627
}
```

So với Exp122: Final `-0,0015`, Chunk F2 `-0,0029`, Chunk Precision `-0,0008`, Chunk Recall `-0,0055`. Giữ **Exp122 (0,3516)** làm champion; dừng ladder Exp124 CE add21.

## Diễn giải sau audit

Không coi đây là ablation thuần ranking: Exp123 dùng pool CE của Exp75, còn Exp122 được chọn theo document rank từ tập missing docs hiện tại. Trung bình `4,4792/19` additions Exp122 nằm ngoài pool CE, nên Exp123 không thể chọn lại chúng; hai tập additions giao trung bình `11,3342/19`. Đồng thời CE chỉ nhìn một passage tối đa 500 ký tự, trong khi output là full parent. Kết quả bác bỏ policy cụ thể này, chưa bác bỏ reranking trên cùng pool với nhiều passages.

Audit tái lập: `python scripts/audit_query_architecture.py`; kết quả tại `data/audits/query_architecture_post_exp123.json`. Xem kế hoạch kiến trúc mới trong mục 15 của `docs/r2ai_score_improvement_plan.md`.
