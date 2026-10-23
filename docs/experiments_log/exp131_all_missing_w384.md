# Exp131 — Evidence cho toàn bộ selected docs bằng anchored window 384 ký tự

## Giả thuyết

Exp122 chỉ có chunk evidence cho khoảng 108/216 selected documents mỗi query. Exp131 giữ nguyên toàn bộ full parents của Exp121, sau đó thêm đúng một cửa sổ nguyên văn tối đa 384 ký tự cho mọi selected document chưa có evidence. Mục tiêu là đưa Chunk Recall tiến gần Docs Recall trong giới hạn ZIP 100 MB; đây là phép thử breadth cực đại, không thay document axis.

Vị trí cửa sổ được neo lần lượt bằng scored span Exp75, passage Qwen Exp114, best stage-1 dense chunk, rồi mới fallback về đầu source. Không có nội dung sinh lại và không dùng nhãn leaderboard.

## Artifact và audit

- ZIP: `submission_exp131_all_missing_w384.zip` — `99.683.844` bytes.
- SHA-256: `77cc4f70c52ec96254e0505c9558a802f06c07aa548abb32e5f993e678d9ece2`.
- 1.200 query; documents giống Exp121 tuyệt đối.
- Giữ nguyên byte-for-byte toàn bộ `107.308` Exp121 parents.
- Thêm `153.719` windows, tương ứng toàn bộ `115–152` missing selected docs/query; tổng `261.027` chunk predictions.
- Added windows dài trung bình `379,92`, tối đa `384` ký tự; tất cả là substring nguyên văn của source.
- Anchor sources: `71.367` offset-cache, `32.116` stage-1 chunk, `50.236` source-head fallback.
- Một `submission.json` ở root, ZIP-LZMA method 14, CRC pass và dưới giới hạn decimal 100 MB.

## Kết quả BTC

Hai biến thể đã được BTC chấm:

| Biến thể | Final | Docs F2 | Chunks F2 | Docs P | Docs R | Chunks P | Chunks R |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Exp131, width 384 | 0,3079 | 0,3586 | 0,2572 | 0,1816 | 0,6114 | 0,1249 | 0,4622 |
| Exp131, width 512 | 0,3047 | 0,3586 | 0,2509 | 0,1816 | 0,6114 | 0,1213 | 0,4531 |

So với champion Exp122 (`0,3516 / 0,3586 / 0,3446`), width 384 giảm Final `0,0437`, Chunks F2 `0,0874`, Chunks Precision `0,1263` và Chunks Recall `0,0060`. Width 512 còn kém hơn: Final giảm `0,0469`, Chunks F2 giảm `0,0937`, Precision giảm `0,1299`, Recall giảm `0,0151`.

## Kết luận

Giả thuyết breadth cực đại bị bác bỏ. Việc thêm evidence cho hầu hết selected docs không đưa recall vượt Exp122; ngược lại, các cửa sổ ngắn/anchor yếu tạo rất nhiều false-positive chunks và làm precision sụp mạnh. Width 384 tốt hơn 512 nhưng vẫn thua control rõ rệt. Không tiếp tục tăng breadth hoặc tune width quanh cấu hình này.
