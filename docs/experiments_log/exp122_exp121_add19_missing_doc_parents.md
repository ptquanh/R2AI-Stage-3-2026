# Exp 122 — Exp121 + 19 missing-document full parents

## Giả thuyết

Exp121 tăng Chunk F2 từ `0,2873` lên `0,3238` nhờ full-parent nhưng mới có evidence cho trung bình `89,42` query-docs, trong khi document output có 216 docs/query. Exp122 giữ nguyên toàn bộ Exp121 rồi thêm full-source parent cho 19 selected documents xếp hạng cao nhất chưa có chunk evidence ở mỗi query.

Đây là append-only experiment: mọi hit, parent và document của Exp121 được bảo toàn. Additions nhắm khoảng trống giữa Docs Recall `0,6114` và Chunks Recall `0,4174`.

## Artifact và audit

- File nộp: `submission_exp122_exp121_add19_missing_doc_parents.zip`.
- ZIP: `99.361.586` bytes, dưới giới hạn decimal 100 MB đúng `638.414` bytes.
- Compression: ZIP method 14 (LZMA), 7-Zip mx9, dictionary 64 MiB.
- 1.200 queries; document axis giống Exp121 tuyệt đối.
- Giữ nguyên byte-for-byte toàn bộ `107.308` Exp121 parents.
- Thêm đúng 19 parents/query, tổng `22.800`; output tổng `130.108` chunks.
- Additions thuộc selected documents, chưa từng có chunk evidence và là full-source substring nguyên văn.
- Added text: `86.783.082` ký tự; mean/median `3.806/3.583`, max `49.780`.
- CRC, entry duy nhất `submission.json`, payload hash và semantic prefix audit đều pass.
- SHA-256 ZIP: `8c7f221cfafa401dfb5435df7da06464999c4b60594e69bc7726bb4ffb379886`.
- SHA-256 JSON: `7539b64f0b6c48a2b72460533562fe558efc4534dd04624af094f855f72c23b7`.

Builder add25 tạo ZIP `104.319.110` bytes nên bị loại; JSON/ZIP add25 đã xóa để tránh nộp nhầm. Add19 là mức lớn nhất an toàn theo kích thước đo thực tế; add20 được dự báo sát/vượt trần nên không dùng.

## Kết quả BTC

- Final Score: `0,3516` (`+0,0104` so với Exp121).
- Docs F2 / Precision / Recall: `0,3586 / 0,1816 / 0,6114`, bất biến.
- Chunks F2: `0,3446` (`+0,0208`).
- Chunks Precision / Recall: `0,2512 / 0,4682` (`-0,0156 / +0,0508`).

19 additions/query tăng Chunk F2 rõ rệt nhưng precision tradeoff lớn hơn Exp121. Giữ Exp122 làm champion; kiểm tra thêm lựa chọn document/addition và tận dụng archive budget trước khi cố định số lượng additions tiếp theo.
