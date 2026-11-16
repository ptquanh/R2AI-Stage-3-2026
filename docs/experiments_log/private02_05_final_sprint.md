# Private02–05 — bốn treatment cuối, 04/11/2026

Control: `submission_private01_exp143_replay.zip` đã nộp; private **không hiện điểm trước hạn**. Người dùng xác nhận ngày 04/11 đã nộp cả Private02–05. Chưa có ID/receipt portal để đối chiếu độc lập và chưa có điểm BTC. SHA256 dưới đây là checksum của ZIP local, không phải mã portal. Không gọi một treatment là “winner” chỉ vì audit đạt.

1. `submission_private02_bm25_consensus_add2.zip`: chỉ thêm doc cho QuerySpec `status=ok`, BM25 VI đa góc nhìn rank<=150, `view_hits>=3`, tối đa 2 doc chưa có/query. +666 docs trên 337 query; chunks Exp143 giữ nguyên. 94.480.687 bytes; SHA256 `0362027da58364c43965f509ab84e51c85e97e87f38d1e2dca323e9b779e4652`.
2. `submission_private03_p2a_add5.zip`: dùng lại Exp143 source-span selection nhưng top5 thay top3/query; +2.053 chunk nguyên văn trên 1.055 query; docs giữ nguyên. Hash/offset của từng source window đã kiểm tra. 94.584.201 bytes; SHA256 `ba6e0862c23b6815b883f2994404229d112d0388e7ab8905d97b0c44cef554d3`.
3. `submission_private04_combined.zip`: ghép docs của Private02 với chunks của Private03 theo đúng query ID; +666 docs, +2.053 chunks. 94.584.631 bytes; SHA256 `fd8a5c8982cf77dd78bae41322be22c53be1aafb4b68195ee97814be6a58023d`.
4. `submission_private05_bm25_broad_add5.zip`: chỉ thêm docs, QuerySpec `status=ok`, BM25 VI rank<=150, `view_hits>=2`, tối đa 5 doc chưa có/query. +1.997 docs trên 400 query; chunks Exp143 giữ nguyên. 94.489.072 bytes; SHA256 `7d20236ec5cd653f08b58c53ae4d283e11de7049b10927395cb141a91cd8428d`.

Lệnh kiểm tra độc lập `python -m scripts.audit_private_four` đã PASS: 1.200 query/file, ZIP CRC, dung lượng <100 MB, mọi doc/chunk `doc_id` trong corpus, không duplicate, không xóa dự đoán control. BTC chỉ yêu cầu chunk `doc_id` là tài liệu nguồn; không bắt buộc chunk owner phải nằm trong `relevant_docs`. Source-hash/offset của P2A đã được builder Private03 kiểm tra trước đóng gói.

Lưu ý: Docs append-only có thể tăng recall nhưng giảm precision; chunk append-only có thể tăng recall nhưng giảm precision. Không có qrels đáng tin hoặc điểm private để khẳng định hướng nào tăng Final. Chỉ người dùng nộp qua portal; xác nhận của người dùng là bằng chứng trạng thái hiện có, chưa thay cho receipt portal.
