# Exp126 — Query views `status=ok` only

## Giả thuyết

Exp125 dùng 48 parsed views trong 50 rows, gồm 18 views mang cờ `needs_review`, và giảm Final `0,0003` so với Exp122. Exp126 kiểm tra một gate đơn giản: chỉ giữ query-view treatment cho 30 rows `status=ok`; 18 rows `needs_review` và 2 lỗi parse quay về document list Exp122.

## Cấu hình/artifact

- Control: Exp122 (`submission_exp122_exp121_add19_missing_doc_parents.zip`, Final `0,3516`).
- Treatment rows: 30 IDs có `status=ok` trong 50 rows đầu của `query_views_20a36c979a30e5b5.zip`; lấy đúng document list của các query tương ứng từ Exp125.
- Các query khác trả về nguyên document list Exp122. Toàn bộ chunks giữ nguyên Exp122.
- Vì tái sử dụng Exp125, encoder, weighted RRF và retrieval candidates không chạy lại; biến duy nhất so với Exp125 là fallback các query `needs_review` về control.
- ZIP: `submission_exp126_query_views_ok_only.zip`, `99.361.386` bytes, một `submission.json`, CRC pass, dưới decimal 100 MB.
- Validator: 1.200 queries, đúng 216 unique docs/query, không có duplicate doc IDs; ZIP CRC/entry pass. Validator tổng quát đếm 369 query có chunk text trùng nhau, bằng tình trạng baseline do chunks giữ nguyên.
- SHA-256 ZIP: `cc7041d7cd23cbffa69c35cc193890a147bd744ab718ca4a15e48c9a667e7b37`; SHA-256 JSON: `1a70e21da56b1923fc98439aab0978eb09dd322bcaf7222ac1e42b26e06c5704`.

## Kết quả BTC

Chưa có — artifact sẵn sàng để người dùng nộp thủ công. Không upload tự động.

## Quyết định

Exp122 tiếp tục là champion tới khi nhận được kết quả chính thức. Exp126 là phép kiểm tra cuối trong ngày về tác động của validator gate; không suy luận trước rằng 30 view `ok` chắc chắn giúp tăng điểm.
