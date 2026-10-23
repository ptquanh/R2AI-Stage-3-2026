# Exp 121 — Full parent cho toàn bộ represented query-docs

## Mục tiêu

Giữ nguyên document axis Exp114 và giữ nguyên tập `doc_id` đã có chunk ở từng query. Với mỗi `(query, doc_id)`, gộp toàn bộ chunks cũ thành đúng một parent nguyên văn chứa tất cả chúng. Khác Exp115, không loại tail document-evidence nào.

Theo đặc tả BTC, nếu chunk cũ hit một reference thì parent chứa chunk cũ vẫn đạt ít nhất cùng LCS overlap; mỗi reference được tính found nếu tồn tại một prediction hit. Do đó policy này bảo toàn mọi hit cũ theo metric công khai và có thể tìm thêm reference chunks từ context mở rộng.

## Artifact

- File nộp: `submission_exp121_all_doc_full_parents_lzma_mx9.zip`.
- ZIP: `83.800.114` bytes, method 14 (LZMA), một entry `submission.json` ở root.
- JSON giải nén: `619.295.721` bytes.
- SHA-256 ZIP: `e8e98f42e2be1a58569cba9c47e96fa942de6a5938e15ca3e8a54673c5575b22`.
- SHA-256 payload: `75bd505c58e045cc706e2444a60bb1a17707334d53a2d9f4346a9698fd059860`.

## Audit

- 1.200 queries; documents giống Exp114 tuyệt đối.
- Chunks `108.438 → 107.308`; chỉ gộp 1.130 duplicate same-query-doc chunks.
- Tập represented chunk-docs giống Exp114 tuyệt đối ở cả 1.200 queries.
- Tổng chunk characters `263.684.609 → 447.257.132`; parent mean/median `4.168 / 3.991` ký tự.
- Mọi parent là source substring và chứa tất cả chunks cũ của cùng query-doc.
- Python `zipfile` đọc được method 14, CRC pass và payload hash trong ZIP khớp JSON ngoài ZIP.

Portal compatibility là rủi ro duy nhất: thể lệ yêu cầu ZIP nhưng không quy định compression method. Nếu portal nhận file, nộp Exp121 trước các artifact Exp118–120. Nếu portal từ chối giải nén, lỗi upload không phải kết quả metric; không đổi sang file vượt 100 MB.

## Kết quả BTC

- Final Score: `0,3412` (`+0,0183` so với Exp114 và `+0,0208` so với Exp115).
- Docs F2 / Precision / Recall: `0,3586 / 0,1816 / 0,6114`, giữ nguyên đúng control.
- Chunks F2: `0,3238` (`+0,0365` so với Exp114).
- Chunks Precision: `0,2668` (`+0,0279`).
- Chunks Recall: `0,4174` (`+0,0478`).

Đây là bước nhảy lớn nhất kể từ khi hoàn thiện corpus và xác nhận full-parent cùng việc bảo toàn evidence coverage là hướng đúng. Tiếp tục bằng append-only full-parent cho selected documents xếp hạng cao nhưng chưa có chunk evidence; không quay lại cắt tail hoặc thay span cũ.
