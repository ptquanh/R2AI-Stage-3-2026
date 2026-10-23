# Exp 51 — Full 1.205M Docs + Exp50 Policies

## Cấu hình

- Active index sau khi merge artifact cuối: `1.205.935` documents.
- Document output: top `125` theo cấu hình document champion.
- Chunk output: merged envelopes kế thừa Exp47/Exp50.

## Kết quả BTC

| Metric | Score |
| --- | ---: |
| FINAL_SCORE | 0.3098 |
| DOCS_F2MACRO | 0.3343 |
| CHUNKS_F2MACRO | 0.2853 |
| DOCS_PRECISION | 0.2298 |
| DOCS_RECALL | 0.4710 |
| CHUNKS_PRECISION | 0.2414 |
| CHUNKS_RECALL | 0.3653 |

## Kết luận

Coverage mới tạo cải thiện nhỏ nhưng nhất quán so với Exp50: Docs F2 `+0.0007`, Docs Recall `+0.0011`, Final `+0.0005`. Exp51 là champion hiện tại và là baseline an toàn cho mọi ablation tiếp theo.
