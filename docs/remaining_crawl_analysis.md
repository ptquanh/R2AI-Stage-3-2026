# Phân tích 12.774 URL còn lại

Cập nhật: 2026-10-16 (Asia/Bangkok)

## Kết quả sau vòng sửa crawler

- Trước phân tích: 12.828 URL trong `data/remaining_urls.parquet`.
- Thu hồi thêm: 41 tài liệu có nội dung.
  - PubMed: 30/30 bản ghi trước đây bị loại vì không có abstract; nay lấy full text hoặc metadata gốc từ Europe PMC.
  - `cnkang.com`: 6/6 qua mobile host chính thức `m.cnkang.com`.
  - `ask.39.net`: 4/4 qua URL canonical; bỏ rewrite cũ sang `wapask` gây HTTP 429.
  - `msdmanuals.cn`: 1/13 còn nội dung.
- Xác nhận và loại khỏi `remaining`: 13 URL HTTP 404 (12 MSD Manuals, 1 Youlai).
- Sau đồng bộ: 12.774 URL còn lại; partition với corpus BTC vẫn chính xác.

## Ma trận nguyên nhân hiện tại

| Domain | URL còn lại | Chẩn đoán | Có thể giải quyết chỉ bằng sửa parser? |
|---|---:|---|---|
| `zysjonline.com` | 6.591 | Cloudflare Managed Challenge trên request, Selenium headless, direct IP và proxy | Không |
| `pmc-ecm-healthblog.beta.pharmacity.io` | 5.333 | Staging Nginx trả HTTP 403; slug tương ứng trên site Pharmacity hiện tại trả 404 | Không |
| `article.iiyi.com` | 729 | TCP timeout tới cụm IP `219.239.89.30-32`, cả direct và proxy hiện có | Không |
| `pubmed.ncbi.nlm.nih.gov` | 104 | PMID không tồn tại trong Europe PMC; mẫu kiểm tra cũng không có kết quả nguồn khác | Không |
| `120ask.com` | 9 | Cùng cụm IP với Iiyi; TCP timeout direct và proxy | Không |
| `bingli.iiyi.com` | 5 | Cùng cụm IP với Iiyi; TCP timeout direct và proxy | Không |
| `giadinhonline.vn` | 2 | Một URL trả HTTP 500, một URL trả shell 31 byte không có nội dung | Không |
| `bachmai.gov.vn` | 1 | HTTP 200 soft-404/Next.js shell, không có article body | Không |

Tổng: 12.774 URL.

Trong báo cáo tự động, `No persisted result` không đồng nghĩa với chưa từng probe. Trước thay đổi này crawler cố ý không ghi `error` để URL luôn retryable. Từ vòng tiếp theo, lỗi tạm thời được lưu riêng dưới `local_recovered/errors` nhưng vẫn không tham gia logic skip hoặc sync.

## Những nguồn nội bộ đã kiểm tra

Không tìm thấy text cho 12.828 ID ban đầu trong:

- `data/raw/corpus_text/parts`: 440 parquet, khoảng 3,1 GB.
- `data/raw/corpus_text/recovered_remaining_urls`: 877 parquet, khoảng 0,9 GB.
- `data/raw/corpus_text/pubmed_recovered`: 24 parquet.
- Active index và toàn bộ index backup trong `data/indices/new_dataset`.

Các file `recovered_remaining_urls` chỉ chứa lịch sử lỗi/status cho các ID này, không chứa text có thể phục hồi.

## Archive và URL thay thế đã kiểm tra

- Common Crawl 2026: mẫu ZYS, staging Pharmacity, Iiyi, Gia Đình Online và Bạch Mai không có capture hoặc index trả lỗi gateway. Chưa có bằng chứng đủ để triển khai archive recovery hàng loạt.
- `pharmacity.vn/blog/<slug>` và `pharmacity.vn/<slug>`: HTTP 404 cho các mẫu staging.
- MSD Manuals: URL tiếng Trung cũ phần lớn 404. Bản tiếng Anh có thể còn sống nhưng không được gán vào doc ID tiếng Trung vì `chunk_text` phải lấy từ tài liệu nguồn tương ứng.
- `cnkang.com`: mobile host chứa đúng bài và đã được dùng thành công.

## Ràng buộc cuộc thi

Theo `docs/competition_information`:

- Chỉ ID trong corpus chính thức được tính là nhãn dương.
- Dữ liệu ngoài được phép nếu ghi rõ nguồn để BTC kiểm tra.
- `chunk_text` phải được trích xuất từ tài liệu nguồn, không được viết lại hoặc sinh mới.
- Không sử dụng closed-source LLM API trong pipeline chính thức.

Vì vậy không được biến slug URL thành “nội dung bài”, không dùng LLM sinh lại bài và không âm thầm gán bài mirror khác vào ID gốc.

## Điều kiện cần để giảm tiếp remaining

1. **ZYS (6.591):** cần một trong các điều kiện sau:
   - quyền truy cập/allowlist từ chủ website;
   - cookie Cloudflare hợp lệ có thể tái sử dụng hợp pháp;
   - archive HTML gốc có provenance rõ ràng.
2. **Staging Pharmacity (5.333):** cần export/crawl artifact từ origin staging trước khi server bị đóng, hoặc bản archive HTML gốc. Site production hiện không có các slug mẫu.
3. **Iiyi/120ask (743):** cần egress/proxy tại Trung Quốc có thể kết nối cụm `219.239.89.30-32`; proxy Việt Nam hiện tại không giải quyết được TCP timeout.
4. **PubMed (104):** cần BTC xác nhận các PMID không tồn tại hoặc cung cấp mapping nguồn đúng. Không nên tạo text giả cho các ID này.
5. **Ba URL Gia Đình Online/Bạch Mai:** chỉ có thể phục hồi từ backup/archive của nhà xuất bản.

## Thay đổi crawler đã triển khai

- Europe PMC full-text và metadata fallback cho bài PubMed không có abstract.
- Mobile-host adapter cho `cnkang.com`.
- Canonical-host adapter cho `ask.39.net`, tránh `wapask` 429.
- Safari fingerprint cho kiểm tra MSD Manuals.
- Giữ phân biệt giữa lỗi tạm thời, 404 thật và nguồn không tồn tại; không xóa URL chỉ vì timeout/403/429.
- Ghi error ledger riêng cho timeout/403/429 để phân tích lịch sử retry mà không làm mất URL.

## Nguyên tắc vận hành tiếp theo

- Chỉ đưa vào `unembedded_samples.parquet` khi có text nguồn không rỗng và đúng `(id, url)` chính thức.
- Chỉ chuyển sang `excluded_urls.parquet` khi có HTTP 404/410 xác nhận hoặc quyết định loại có ghi lý do.
- Timeout, Cloudflare, HTTP 403/429 và gateway lỗi vẫn phải ở trạng thái retryable/blocked, không được coi là 404.
- Mọi archive/external source phải lưu index, timestamp, URL archive và provenance để đáp ứng khả năng tái lập.
