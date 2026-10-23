# Phân tích URL crawl còn lại

## Merge/rebuild active index ngày 19/10/2026 — hai ZIP đã tích hợp

Đã kiểm tra và merge cùng một lượt:

- `5k_urls.zip`: 5.338 docs / 16.398 chunks; chính là 5.324 Pharmacity và 14 Iiyi mới cứu. Đầu vào notebook 7.044 rows, nhưng 1.706 rows bị dropped, không có vector để merge.
- `2k_urls.zip`: hai docs Gia Đình Online `103007`, `116642` / 7 chunks; đã nằm trong embedded registry từ lần trước nhưng chưa nằm trong active index.
- Cả hai artifact khớp ID–URL BTC và text registry, không trùng nhau hoặc với index cũ; metadata model cùng `BAAI/bge-m3` commit `5617a9f61b028005a4858fdac845db406aefb181`.

Kết quả hiện hành: active index **1.211.275 docs / 1.723.642 chunks**, 22 dense/chunk shards, 89 text shards. Embedded `1.205.937 → 1.211.275` (+5.338), unembedded `7.044 → 1.706`; không thêm trùng hai docs đã chuyển trước đó. Remaining 7.434 và excluded 183 không đổi cả hash. Bốn registry phân hoạch chính xác toàn corpus BTC; embedded IDs khớp chính xác tập IDs có trong index.

Đã rebuild FAISS FlatIP, sparse CSR `(1.723.642, 250.005)` / 310.383.182 nonzeros, `chunk_ids.npy` và global metadata trong staging rồi mới kích hoạt. Dùng streaming để tránh nạp toàn bộ FAISS/CSR vào RAM; định dạng FAISS được đối chiếu byte với serializer thư viện và SciPy đọc được CSR trong tests. Toàn bộ payload dense và các mảng CSR được đọc lại kiểm tra hash; native FAISS reader/reconstruct/search được thử trên mẫu giới hạn RAM. Không khẳng định đã nạp toàn bộ index nhiều GB bằng FAISS vào RAM trong bước kiểm tra này.

[Manifest](../data/audits/recovered_index_merge_20261019/manifest.json) lưu hash, số lượng, kết quả rebuild và đường dẫn backup. [Kiểm tra độc lập](../data/audits/recovered_index_merge_20261019/independent_verification.json) xác nhận payload FAISS và metadata cũ được giữ nguyên, toàn bộ vectors/text mới khớp hai ZIP, registry còn lại chỉ mất đúng các rows đã chuyển. Index cũ giữ tại `data/indices/new_dataset/index_backup_pre_recovered_merge_20261019T121718`; backup hai registry trong `data/audits/recovered_index_merge_20261019/backups/`. Bộ kiểm thử 27/27 pass, bao gồm rollback trước và sau commit registry. Cache retrieval/CE/submission cũ được giữ làm lịch sử, cần rerun hoặc kiểm tra fingerprint trước khi sử dụng với index mới.

Các phần dưới là lịch sử trước lần merge/rebuild này.

## Đồng bộ artifact `2k_urls.zip` ngày 19/10/2026

ZIP được tạo từ đầu vào cũ 1.708 docs, trước đợt cứu thêm 5.338 URLs. Kiểm tra CRC và các shard xác nhận chỉ **2 docs / 7 chunks** thực sự có dense/sparse vectors: IDs `103007` và `116642`. Cả hai khớp nguyên dạng ID–URL BTC và text trong registry (8.912 và 10.469 ký tự). Dense hữu hạn, không có vector zero, 1.024 chiều; CSR, các lookup tables, chunk IDs và span offsets khớp nhau.

- Đã chuyển đúng hai rows: embedded `1.205.935 → 1.205.937`, unembedded `7.046 → 7.044`.
- Giữ nguyên 1.706 rows bị dropped, cùng toàn bộ 5.338 rows mới cứu ở unembedded. Log ZIP ghi 1.703 quá ngắn, 3 nội dung lặp; đối chiếu đầu vào cũ xác nhận có 1.703/1.706 texts dưới 500 ký tự. Không đánh dấu những rows này là đã embed, cũng không tự xóa hoặc hạ ngưỡng chất lượng.
- Remaining `7.434`, excluded `183` không đổi cả SHA-256. Bốn registry vẫn tạo phân hoạch chính xác toàn corpus 1.220.598 ID–URL, không trùng ID/URL, không sai mapping.
- **Chưa merge/rebuild active index:** vẫn 1.205.935 docs / 1.707.237 chunks. Hai docs mới có vector trong ZIP nhưng chưa nằm trong search index; cần merge artifact này ở đợt rebuild tiếp theo.
- Ghi lại Parquet cũ bằng Arrow bị thiếu RAM trước commit, không thay đổi registry gốc. Đã dùng append trên bản staging; xác minh toàn bộ compressed payload và metadata các row groups cũ giữ nguyên, đồng thời đọc lại đúng hai rows mới trước thay file.

[Manifest và hash](../data/audits/embedded_2k_zip_20261019_append/manifest.json); backup hai registry gốc trong `backups/` cùng thư mục. [Kiểm tra độc lập sau commit](../data/audits/embedded_2k_zip_20261019_append/independent_verification.json) xác nhận giữ nguyên 1.706 dropped + 5.338 recovered rows, chạy lại không chuyển thêm row nào và stats active index không đổi. Bộ kiểm thử `22/22` pass. Script [sync_embedded_zip_registry.py](../scripts/sync_embedded_zip_registry.py) mặc định dry-run, kiểm tra text/mapping/vector trước chuyển, chống concurrent edit, có rollback và không chuyển trùng khi chạy lại.

Các snapshot recovery dưới đây được giữ như lịch sử trước lần đồng bộ này.

## Recovery bổ sung ngày 19/10/2026 — thêm 5.338 URLs

Đầu vào đối chiếu là backup `data/audits/local_recovered_final_20261019/backups/remaining_urls.parquet` với 12.774 URLs. Hai bài Gia Đình Online đã được đồng bộ ở đợt audit trước; đợt này cứu thêm **5.324 bài Pharmacity + 14 bài Iiyi**. So với backup, tổng cộng đã xử lý thành công 5.340 URLs, còn 7.434 URLs chưa thu hồi được.

### Pharmacity: phục hồi qua API công khai của chính publisher

Kết luận trước đây rằng staging đóng cửa đồng nghĩa không còn cách lấy bài là chưa đầy đủ. Frontend chính dùng đường dẫn `https://www.pharmacity.vn/<slug>.htm`; JavaScript công khai của publisher khai báo `blogGetPost` là GET `https://api-gateway.pharmacity.vn/blog/posts`, `isAuth: false`.

- API nhận nhiều slug một lượt và trả dữ liệu WordPress gồm post ID, `link`, `slug`, `status`, title và `content.rendered`.
- Chỉ nhận record `publish`, **link trùng chính xác URL staging BTC** và slug khớp path; không remap bài khác chỉ vì cùng tiêu đề/chủ đề.
- Đã kiểm tra cả 5.333 URLs, thu hồi đúng nguồn 5.324 (`99,83%`). Chín URLs không có record chính xác vẫn ở remaining; không đánh dấu là đã bị xóa.
- Lưu JSON response gốc dạng gzip, SHA-256, source API URL, WordPress ID và nguồn từng row. Không lấy nội dung từ search snippets hoặc sinh lại bằng model.
- Pilot frontend phát hiện `robots.txt` yêu cầu Crawl-delay 20 giây, nên dừng tải hàng loạt website. Script frontend hiện tự đọc và tuân thủ delay; nhánh API công khai trả robots 404 và được gọi với tối đa một request/giây, có batch và dừng khi 403/429.
- Các candidates frontend chỉ khớp slug/canonical mà chưa có link nguồn chính xác được chuyển sang `review`, không đưa vào registry. Toàn bộ 5.324 bài đã sync có bằng chứng `wordpress_exact_official_link`.
- Kiểm tra lại toàn bộ JSON phát hiện HTML sai dấu nháy ở `img/span`; đã sửa parser, re-extract 409 texts bị ảnh hưởng và backup trước sửa. Tất cả 5.324 bài hiện được xác nhận có thân bài nguồn không rỗng; không để bản chỉ có tiêu đề do lỗi parser vào embedding.

Nguồn khám phá API: asset công khai `https://prod-cdn.pharmacity.io/assets/20261014/_next/static/chunks/782-b41fed6b2ffd4318.js`. Script [recover_pharmacity_api.py](../scripts/recover_pharmacity_api.py) có checkpoint/resume; có thể tiếp tục với các URLs mới bằng cùng quy trình kiểm chứng.

### Iiyi: đọc bản WARC nguyên gốc từ Common Crawl

API CDX của Common Crawl trả 503/504, nhưng file chỉ mục và WARC công khai vẫn truy cập được. Đã triển khai tìm bằng HTTP Range trên `cluster.idx` và các block CDX nén, thay vì phụ thuộc API đang lỗi hoặc tải toàn index.

- Đã khảo sát các collections được chọn từ 2017–2026; tìm 14 HTTP-200 captures trùng URLs Iiyi cần cứu, trong các snapshots 2018/2019/2021/2022/2024.
- Tải đúng byte range WARC; kiểm tra `WARC-Type=response`, `WARC-Target-URI` tương ứng source URL BTC và HTTP status trong bản chụp là 200; sau đó extract article body, loại challenge pages.
- Mỗi row lưu collection, timestamp, original URL, WARC target URI, filename, offset, length và hash bản WARC gốc. Không dùng bài tương tự ở domain khác làm nguồn thay thế.
- Kiểm tra control `example.com` đọc được 280 URLs từ index, giúp xác nhận kết quả không có capture ở các nhánh khác không phải do lookup luôn trả rỗng.
- Chỉ các collections và target URLs đã khảo sát mới được kết luận; chưa chứng minh không có thêm capture trong mọi snapshot khác.

Scripts: [probe_commoncrawl_shards.py](../scripts/probe_commoncrawl_shards.py), [recover_commoncrawl_hits.py](../scripts/recover_commoncrawl_hits.py). Bằng chứng chỉ mục nằm trong `data/audits/recovery_commoncrawl_20261019/`, WARC nằm trong `data/raw/corpus_text/recovery_sources/commoncrawl_20261019/`.

### Registry và khả năng khôi phục sau đợt recovery

- Embedded: `1.205.935`, không đổi.
- Unembedded: `1.708 → 7.046` (`+5.338`); tất cả IDs mới chỉ đang chờ embedding.
- Remaining active: `12.772 → 7.434` (`-5.338`). Backup 12.774 URLs người dùng chỉ định được giữ nguyên.
- Excluded: `183`, không thêm URL lỗi nào.
- Đã kiểm tra độc lập: bốn registry tạo phân hoạch chính xác toàn corpus `1.220.598` ID–URL, không trùng hoặc sai mapping; giữ nguyên toàn bộ 1.708 unembedded rows trước recovery.

Manifests và backup:

- [Đợt sync Pharmacity](../data/audits/publisher_rescue_20261019/applied_summary.json); backup registry tại thư mục `backups/` cùng cấp.
- [Kiểm tra nguồn và sửa text](../data/audits/publisher_rescue_20261019/text_verification/verification.json); backup text trước sửa và các recovery ledgers nằm cùng thư mục.
- [Đợt sync WARC](../data/audits/archive_rescue_20261019/applied_summary.json); backup trước append archive nằm trong `backups/` cùng cấp.
- [Kiểm tra độc lập cuối cùng](../data/audits/archive_rescue_20261019/final_independent_verification.json): đối chiếu toàn bộ 5.324 texts với JSON nguồn, 14 texts với WARC, xác nhận backup đầu vào không đổi và chỉ các IDs phục hồi bị loại khỏi remaining. `15/15` tests pass.
- [Audit script](../scripts/audit_local_recovered_final.py) bảo toàn cả `source_file` (raw payload) và `ledger_file` (recovery record), kiểm tra concurrent changes trước commit.

### Phần còn lại và giới hạn đã kiểm tra

- `zysjonline.com`: 6.591 URLs; origin/www challenge 403, mobile host không resolve, host ZYS cũ không kết nối. Chưa tìm được capture exact-source trong các snapshots ZYS đã kiểm tra. Không gán nội dung sách từ mirror chưa xác minh vào ID gốc.
- `article.iiyi.com`: còn 715; `bingli.iiyi.com`: 5; `120ask.com`: 9. Các route desktop/mobile vẫn timeout; DNS công khai khớp DNS local, không phải lỗi cache DNS. Hai cấu hình proxy hiện có cũng không kết nối trong probes. Các archives đã khảo sát chưa có capture cho phần còn lại.
- PubMed: 104; origin/BioC/ID-conversion bị chặn NCBI, Europe PMC vẫn không có record. Không dùng trang challenge làm article text.
- Pharmacity: 9; chưa có exact source record. Bản `/benh/dau-lung/` khác path với `/dau-lung/` BTC nên không tự remap.
- Bạch Mai: 1; HTML hiện không cung cấp body. Tìm được bài cùng tiêu đề trên website chuyên khoa của Bạch Mai nhưng chưa xác minh cùng document identity, nên không sync thay thế.
- Wayback CDX timeout, availability API trả 429 nên không tiếp tục dồn request. Arquivo.pt không có capture cho các mẫu ZYS/Iiyi đã thử.

Crawler `crawl_local_fast.py` đã sửa: staging không còn bị drop theo tên miền; Europe PMC miss được giữ retryable và có fallback origin; chỉ exact reason HTTP 404/410 mới bị xem là permanent; cookie/NCBI challenge không còn được nhận nhầm là nội dung. History cũ được giữ để truy vết.

## Rà soát cuối ngày 19/10/2026 (Asia/Bangkok)

Đã rà toàn bộ **47 Parquet / 42.114 bản ghi** trong `data/raw/corpus_text/local_recovered`, gồm cả thư mục `errors`, ứng với 12.774 IDs có trong remaining trước đợt này. Hai bản ghi success đã được xác minh đúng ID–URL chính thức và có nội dung bài, đồng thời origin hiện trả HTTP 200:

- `103007`: `https://giadinhonline.vn/an-mi-tom-co-hai-cho-suc-khoe-khong-d69905.html` — text nguồn 8.912 ký tự.
- `116642`: `https://giadinhonline.vn/tuoi-tho-toi-da-cua-con-nguoi-la-bao-nhieu-d196963.html` — text nguồn 10.469 ký tự.

Hai bài đã được thêm vào `unembedded_samples.parquet`, chưa đánh dấu embedded; đã loại đúng hai IDs này khỏi remaining. Nội dung giữ nguyên từ recovery artifact, có phần related-news/footer ở cuối; nên parser evidence tập trung article body, không xem độ dài text là độ dài bài chính.

Trạng thái sau đồng bộ:

- Embedded: `1.205.935`, không thay đổi.
- Unembedded: `1.706 → 1.708`.
- Remaining: `12.774 → 12.772`.
- Excluded: `183`, không thêm URL lỗi nào.
- Bốn registry tạo **phân hoạch chính xác toàn bộ 1.220.598 cặp ID–URL BTC**, không trùng ID/URL hoặc sai mapping. Con số 183 trước đây trông như thiếu coverage registry chính là excluded đã được quản lý, không phải dữ liệu thất lạc.

### Kết luận về URL thất bại

**Chưa đủ bằng chứng để loại vĩnh viễn thêm URL nào.** Rà lịch sử toàn bộ không đồng nghĩa đã GET mới từng URL. Đợt này probe trực tiếp **35 URLs**, gồm toàn bộ các nhóm nhỏ trừ PubMed và mẫu rải đều ở nhóm lớn; kiểm tra thêm toàn bộ **104 PMIDs** qua 5 batch Europe PMC, không có lỗi API và không tìm thấy record.

- ZYS: 6.591 URLs; 5/5 mẫu mới HTTP 403/challenge. Giữ trạng thái blocked, không suy ra bài đã bị xóa.
- Staging Pharmacity: 5.333 URLs; 5/5 mẫu mới HTTP 403. Nhãn `Server Staging/Beta Shut Down` hiện đến từ nhánh hard-code theo tên miền trong crawler, không phải 5.333 lần xác minh origin không tồn tại. Không dùng nhãn này làm căn cứ loại.
- Iiyi/120ask: 729 + 5 + 9 = 743 URLs; probe 5 Article Iiyi, toàn bộ 5 Bingli và 9 120ask đều timeout. Đây là vấn đề truy cập, không chứng minh URL chết.
- PubMed: 104 URLs đều không có trên Europe PMC, nhưng 3 origin probes mới trả HTTP 203 cùng challenge `Cookies must be enabled`. Probe ESummary ban đầu cũng redirect sang trang NCBI blocked diagnostic. Chưa xác minh được deletion từ nguồn PubMed; giữ toàn bộ 104 URLs.
- Bạch Mai: 1 URL HTTP 200, Next.js/RSC shell không có article body trong HTML tĩnh. Tiếp tục giữ là source/parser chưa xác minh, không tự kết luận soft-404 từ text rỗng.
- Gia Đình Online: 2/2 origin HTTP 200, đã đồng bộ success như trên.

Tổng probes mới: 19 timeout, 10 HTTP 403, 3 HTTP 203 challenge, 3 HTTP 200; **0 HTTP 404/410**. Không suy kết quả mẫu thành bằng chứng riêng cho từng URL trong domain lớn. Chỉ chuyển một URL sang excluded khi có xác minh cụ thể đáng tin cho chính URL đó, hoặc quyết định loại có chủ đích từ người dùng.

### Cảnh báo về cách retry hiện tại

`scripts/crawl_local_fast.py` có hai nhánh cần lưu ý trước lần retry sau:

1. `fetch_one_sync` trả `dropped` cho beta Pharmacity chỉ dựa tên miền, không request origin; trả `dropped` khi Europe PMC không có PMID.
2. `get_already_crawled_ids` coi reason chứa `not found` hoặc `staging/beta shut down` là đã xử lý. Vì vậy 5.437 URLs trên có thể bị skip mặc dù vẫn có trong remaining.

Đợt này chỉ audit và đồng bộ registry; chưa sửa crawler hoặc xóa lịch sử lỗi. Nếu chạy lại crawler nguyên trạng, không được diễn giải việc không có success mới là một lượt xác minh mới cho 5.437 URLs đó. Cần sửa cách phân loại/skip hoặc có kênh truy cập origin khác trước lần retry có ý nghĩa.

### Bằng chứng, khả năng khôi phục và tái lập

- Script: [audit_local_recovered_final.py](../scripts/audit_local_recovered_final.py), dry-run mặc định; kiểm tra network và apply được tách riêng.
- [Manifest đã áp dụng](../data/audits/local_recovered_final_20261019/applied_summary.json) chứa hashes trước/sau, số lượng và kiểm tra partition.
- [Ma trận quyết định của 12.774 URLs đầu vào](../data/audits/local_recovered_final_20261019/remaining_decisions.parquet).
- [Origin probes từng URL](../data/audits/local_recovered_final_20261019/origin_probes.parquet), [kết quả Europe PMC](../data/audits/local_recovered_final_20261019/europe_pmc_checks.json).
- Backup đầy đủ hai registry đã đổi trong `data/audits/local_recovered_final_20261019/backups/`; có thể khôi phục trạng thái trước sync. Embedded/excluded có hash trước/sau giống nhau.
- Audit độc lập sau ghi xác nhận giữ nguyên toàn bộ 1.706 rows unembedded cũ và text hai bài khớp recovery artifact; chỉ hai success IDs bị loại khỏi remaining. `9/9` tests pass, gồm bảo vệ trước 403/API miss/redirect, ưu tiên success, partition và staging/backup Parquet.

## Lịch sử ngày 16/10/2026 — snapshot 12.774 URLs

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

| Domain                                  | URL còn lại | Chẩn đoán                                                                          | Có thể giải quyết chỉ bằng sửa parser? |
| --------------------------------------- | ----------: | ---------------------------------------------------------------------------------- | -------------------------------------- |
| `zysjonline.com`                        |       6.591 | Cloudflare Managed Challenge trên request, Selenium headless, direct IP và proxy   | Không                                  |
| `pmc-ecm-healthblog.beta.pharmacity.io` |       5.333 | Staging Nginx trả HTTP 403; slug tương ứng trên site Pharmacity hiện tại trả 404   | Không                                  |
| `article.iiyi.com`                      |         729 | TCP timeout tới cụm IP `219.239.89.30-32`, cả direct và proxy hiện có              | Không                                  |
| `pubmed.ncbi.nlm.nih.gov`               |         104 | PMID không tồn tại trong Europe PMC; mẫu kiểm tra cũng không có kết quả nguồn khác | Không                                  |
| `120ask.com`                            |           9 | Cùng cụm IP với Iiyi; TCP timeout direct và proxy                                  | Không                                  |
| `bingli.iiyi.com`                       |           5 | Cùng cụm IP với Iiyi; TCP timeout direct và proxy                                  | Không                                  |
| `giadinhonline.vn`                      |           2 | Một URL trả HTTP 500, một URL trả shell 31 byte không có nội dung                  | Không                                  |
| `bachmai.gov.vn`                        |           1 | HTTP 200 soft-404/Next.js shell, không có article body                             | Không                                  |

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
