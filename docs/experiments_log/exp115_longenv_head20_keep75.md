# Exp 115 — Metric-aware long envelopes, head20 / keep75

Trạng thái: đã nộp; regression trên Chunk F2.

- Baseline: Exp114; documents giữ nguyên tuyệt đối.
- Với unique document xuất hiện trong 20 chunk đầu, thay mọi chunk của document đó bằng một parent envelope nguyên văn chứa toàn bộ các chunk cũ; gần như toàn bộ source được dùng, giới hạn mục tiêu 32.000 ký tự.
- Giữ prefix 75 chunks trước khi hợp nhất; phần tail yếu hơn bị loại để giữ ZIP dưới 100 MB.
- Parent dài hơn không thể làm mất overlap cũ theo công thức `LCS(c,g)/|g|`, trong khi có thể tìm thêm nhiều reference chunks cùng document.

## Chẩn đoán artifact

- Chunks/query: `90,365 → 74,444`.
- 23.812 query-document pairs được mở rộng, trung bình `19,84`/query.
- Parent length mean/median: `4.530 / 4.400` ký tự.
- Tổng chunk characters gần như giữ nguyên: `263.684.609 → 262.279.349`.
- ZIP `97.356.130` bytes, CRC hợp lệ.

Đây là biến thể có cường độ đủ lớn để kiểm tra giả thuyết đội 0,407 dùng một passage rất rộng cho mỗi document: ở dòng tham chiếu, Docs P/R `0,2317/0,5706` và Chunks P/R `0,2286/0,5725` gần như trùng nhau.

## Kết quả BTC

- Final Score: `0,3204` (`-0,0025` so với Exp114).
- Docs F2 / Precision / Recall: `0,3586 / 0,1816 / 0,6114`, bất biến đúng thiết kế.
- Chunks F2: `0,2822` (`-0,0051`).
- Chunks Precision: `0,2608` (`+0,0219`).
- Chunks Recall: `0,3492` (`-0,0204`).

Parent rộng có tín hiệu precision rõ, nhưng bỏ trung bình `15,921` tail chunks/query làm mất quá nhiều ground-truth coverage. Không nộp tiếp Exp116/117 theo ladder cũ: chúng vẫn đánh đổi context lấy tail, chỉ khác cường độ. Follow-up phải giữ nguyên tập query-document đã có evidence rồi mới mở parent.

