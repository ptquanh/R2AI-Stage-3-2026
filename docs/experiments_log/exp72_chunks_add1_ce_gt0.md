# Exp 72 — Add One High-Confidence CE Chunk

## Mục tiêu

Tận dụng các evidence chunks đã được fresh cross-encoder chấm trong Exp67–71 để tăng chunk recall, nhưng không xóa bất kỳ evidence nào của chunk champion Exp63. Đây là chunk-only ablation đầu tiên sau khi document branch hội tụ ở Exp71.

## Cấu hình

- Documents: giữ nguyên Exp71 value-by-value.
- Chunks nền: giữ toàn bộ Exp71/Exp63 chunks theo đúng thứ tự.
- Với mỗi query, chỉ xét documents đã có trong `relevant_docs` Exp71 nhưng chưa có document nào đại diện trong `relevant_chunks`.
- Chọn evidence chunk có CE score cao nhất của document, sau đó chọn tối đa một chunk/query.
- Chỉ thêm khi raw BGE cross-encoder score `> 0`.
- Model tạo score: `BAAI/bge-reranker-v2-m3`; tái sử dụng caches Exp67/69/70/71, không inference mới.

## Mức thay đổi

- Queries có addition: `1.160/1.200`.
- Chunks thêm: `1.160`.
- Chunks/query min/mean/median/max: `66 / 89,187 / 90 / 99`.
- Chunk count trung bình tăng từ `88,220` lên `89,187` (`+1,10%`).
- CE score min/mean/median/max của additions: `0,006 / 3,398 / 3,313 / 9,359`.
- Độ dài additions min/mean/median/max: `136 / 1.544,85 / 1.106,5 / 3.481` ký tự.

## Audit

- Đủ 1.200 query; document lists khớp Exp71 value-by-value.
- Mọi Exp71 chunk được giữ nguyên value-by-value và theo đúng thứ tự.
- Mọi addition thuộc một Exp71-selected document chưa có chunk đại diện.
- Mọi chunk mới là substring nguyên văn của source document.
- Tất cả IDs thuộc official corpus; không trùng `(doc_id, chunk_text)` trong query.
- ZIP chỉ chứa `submission.json`; CRC hợp lệ và payload khớp byte-for-byte với JSON ngoài ZIP.
- Tests: `4 passed`.
- Kích thước ZIP: `99.104.871` bytes.
- JSON SHA-256: `451d910521741e2bccc6e003ea4ad86a8451fad70f444b0d8e5a348c77a981c4`.
- ZIP SHA-256: `b5ba2e89d022130b182b4605d293fba86d01deff85b6cbbfcc61faa8ce8cbbc4`.

## Kết quả BTC

- Final Score: `0,3212` (`+0,0005` so với Exp71).
- Docs F2/Precision/Recall: `0,3560 / 0,1808 / 0,6059` (không đổi).
- Chunks F2: `0,2863` (`+0,0008`).
- Chunks Precision: `0,2407` (`-0,0012`).
- Chunks Recall: `0,3675` (`+0,0021`).

Exp72 là champion mới. Việc cộng evidence làm giảm nhẹ precision nhưng recall tăng đủ để cải thiện Chunk F2 và Final Score; kết quả này ủng hộ thử một addition thứ hai với ngưỡng CE chặt hơn cho slot cuối.
