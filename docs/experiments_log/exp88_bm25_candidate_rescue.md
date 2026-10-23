# Exp 88 — BM25-only candidate rescue + BGE rerank

Trạng thái: đã có điểm BTC; regression, dừng nhánh.

Exp88 là document-only ablation trên Exp87. Bảo vệ top-50, giữ 166 tài liệu còn lại làm control pool, thêm 50 candidates/query lấy từ multilingual BM25 nhưng loại toàn bộ tài liệu đã xuất hiện trong dense pool rank 1–300. Candidates mới được chấm tối đa ba lexical source windows bằng đúng `BAAI/bge-reranker-v2-m3` revision `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e`; chunks giữ byte-for-byte từ Exp87.

## Dữ liệu và inference

- 60.000 BM25-only query/document pairs, đủ 50/query.
- 100.727 passages sau khi loại 2.087 model inputs trùng; mọi document có ít nhất một passage.
- Max pair context đúng 384 tokens; không có empty pair, source thiếu, NaN hoặc score vô hạn.
- BM25 index có 1.205.935 docs, thiếu 6.486 docs mới nhất so với active index 1.212.421 (`0,54%`). Giữ snapshot này để phép thử độc lập; chỉ rebuild BM25 full nếu nhánh thắng.
- Blend `0,90` normalized BGE CE + `0,10` prior rank. Natural rerank muốn đưa trung bình `21,5883` BM25 docs/query vào top-216, vì vậy không dùng output tự nhiên.

## Artifact được chọn

Chọn cap 3 để giới hạn rủi ro từ lexical candidates sau thất bại pure-BM25 Exp55:

- ZIP: `submission_exp88_bm25rescue_cap3.zip`.
- Kích thước: `99.629.531` bytes.
- SHA-256: `def521f683196240d22a87521141cc10c4ce2a9e9f1749b92c3d7b495f443a11`.
- 3.592 replacements tổng cộng; mean/median/max `2,9933 / 3 / 3`.
- 1.199/1.200 queries thay đổi; cap bind trên 1.189 queries.
- Preflight: đúng 1.200 query IDs; 216 unique official docs/query; top-50 bằng Exp87; chunks bằng Exp87; ZIP chỉ có `submission.json` ở root; CRC pass; dưới giới hạn decimal 100 MB.

Cap 5 và cap 10 đã build offline nhưng không nộp trước kết quả cap 3. Nếu Docs F2 tăng, thử cap 5; nếu giảm hoặc hòa, dừng ladder BM25 này và chuyển sang signal/reranker khác.

## Kết quả BTC

- Final: `0,3221`.
- Docs F2/P/R: `0,3572 / 0,1809 / 0,6095`.
- Chunks F2/P/R: `0,2870 / 0,2396 / 0,3688`, đúng control Exp87.

So với Exp87, Docs F2 giảm `0,0011`, precision giảm `0,0009`, recall giảm `0,0003`; Final giảm `0,0005`. Vì chunks bất biến, regression thuộc document membership từ BM25-only candidates. Không nộp cap5/cap10 và không rebuild BM25 full cho ladder này. Kết quả không chứng minh BM25 vô dụng cho mọi kiến trúc, nhưng bác bỏ chính sách đưa BM25-only candidates ngoài dense top-300 vào output bằng BGE blend hiện tại.
