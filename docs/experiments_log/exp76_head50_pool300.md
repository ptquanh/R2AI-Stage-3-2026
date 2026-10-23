# Exp 76 — Fresh BGE head rerank, top-50 protected / pool-300

## Mục tiêu

Sau Exp75 regression, quay chính xác về chunks Exp74 và chỉ thay document axis. Mở vùng từng bị khóa ranks 51–150 bằng fresh cross-encoder scores, ghép với scores ranks 151–300 đã có, rồi rerank pool 51–300.

## Cấu hình và inference

- Baseline/control: Exp74; 216 docs/query và chunks Exp74 giữ nguyên value-by-value.
- Khóa top-50; rerank ranks 51–300 bằng blend `0,75` CE + `0,25` stage rank.
- Ranks 51–150: `120.000` query/document pairs, tối đa ba lexical spans/document; sau khử model-input trùng có `242.019` passages, trung bình `2,0168` spans/doc.
- Model `BAAI/bge-reranker-v2-m3`, revision `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e`, FP16, context 384 tokens.
- Parquet được đọc theo batches 1.024 để giữ RAM bounded. Pilot 2.048 pairs đạt `86,61 pairs/s`; full run resume ở batch 8 sau một lỗi CUBLAS tại checkpoint 18.432 và hoàn tất đủ scores, không NaN/non-finite.
- Tail scores gồm caches Exp67–71 và delta cache Exp74; provenance gap này được audit và bổ sung trước build.

## Churn và artifacts

Natural outsiders trước cap: mean/median/max `11,64 / 11 / 33` docs/query.

- Cap 10: mean swaps `9,046`, cap bind 677 queries; ZIP 99.551.804 bytes.
- Cap 20: mean swaps `11,493`, cap bind 49 queries; ZIP 99.551.265 bytes.
- Cap 30: mean swaps `11,638`, cap bind 1 query; ZIP 99.551.214 bytes.

Khuyến nghị nộp cap 30 trước vì nó gần như ranking tự nhiên; cap 10 làm méo selection trên hơn nửa queries. Cap 30 SHA-256 `b7dd4262cbbaaca0da6776134bf3d13eec8fa9b400b183ffb02188bbdaafee68`.

Audit builder: 1.200 queries; chỉ official IDs; 216 unique docs/query; top-50 bằng Exp74; chunks bằng Exp74; scores đầy đủ hữu hạn; ZIP một `submission.json` ở root và dưới 100 MB.

## Kết quả BTC

- Final: `0,3225`.
- Docs F2/P/R: `0,3581 / 0,1816 / 0,6092`.
- Chunks F2/P/R: `0,2868 / 0,2401 / 0,3685`, giữ nguyên Exp74 đúng control.

So với Exp74, Docs F2 tăng `0,0007`, precision tăng `0,0003`, recall tăng `0,0006`; Final tăng `0,0004`. Exp76 cap 30 là champion mới. Gain chưa đạt gate `+0,005` cho cutoff sweep nên không ưu tiên 175/200. Bước tiếp theo là Exp81 kết hợp Docs Exp76 với chunks Exp78, sau đó dùng hai slots để đo cap 20/10 và slot cuối ghép chunk axis với cap Docs tốt nhất.
