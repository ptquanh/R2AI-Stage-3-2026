# Exp 124 — Exp121 + 21 CE-ranked missing-document parents

## Giả thuyết

Tăng từ 19 lên 21 additions/query trong cùng CE-ranked selected-document pool để dùng phần ZIP còn trống, vẫn giữ toàn bộ Exp121 parents.

## Artifact và audit

- File nộp: `submission_exp124_exp121_add21_ce_ranked_parents.zip`.
- ZIP: `99.995.774` bytes, method 14 (LZMA), chỉ một entry `submission.json`.
- Dưới decimal 100 MB đúng `4.226` bytes; đây là sát giới hạn nên Exp123 add19 có buffer an toàn hơn.
- 21 additions/query, tổng `25.200`, từ 23.328 source docs; tổng output 132.508 chunks.
- Giữ nguyên toàn bộ Exp121; candidate pool 31–60 CE-ranked docs/query.
- Parent bổ sung mean/median `3.467/2.850` ký tự; tổng `87.369.553` ký tự.
- CRC, source-substring, selected-doc membership, uniqueness và payload hash được validate.
- SHA-256 ZIP: `d44a00ff03c6f0af844a3b1422ca0bc1383ed5329632a9d0a06ac1232e76284a`.
- SHA-256 JSON: `490ff31f66824e14a4b0b2ed1206e22ef567fcf3b0fbc8334ba6c634c35c5df0`.

## Kết quả BTC

Chưa nộp; **tạm dừng sau kết quả Exp123** (`0,3501`, kém Exp122 `0,0015`). Không dành slot cho việc tăng count của policy CE vừa giảm cả precision và recall. Artifact vẫn được giữ để tái lập; không tự động coi là phương án tiếp theo.
