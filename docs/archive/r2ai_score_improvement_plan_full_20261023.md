# R2AI Stage 3 — Kế hoạch cải thiện điểm

> Cập nhật: 23/10/2026 (Asia/Bangkok). Champion control hiện tại vẫn là Exp122, Final `0,3516`, Docs F2 `0,3586`, Chunks F2 `0,3446`. Exp131–135 xác nhận chiến lược phủ nhiều selected docs bằng anchored windows ngắn làm Chunks Precision sụp nhưng không tăng Recall; biến thể tốt nhất Exp135 chỉ đạt `0,3326`. Benchmark dịch đã hoàn tất: VinAI Translate v2 thắng rõ cho EN; Qwen3-14B-AWQ được chọn cho ZH sau audit định tính. Mục tiêu baseline BTC `0,3764` còn cách `0,0248`; mục tiêu `0,38` còn cách `0,0284`. ZIP submission bắt buộc dưới `100.000.000` bytes. Các mốc đối thủ do người dùng báo cáo chỉ là tham chiếu, không khẳng định thứ hạng hiện tại.

## 1. Kết luận điều hành

**Trạng thái mới nhất (23/10):** Exp122 là champion `0,3516` (Docs/Chunks F2 `0,3586/0,3446`), còn thiếu `0,0248` để bằng baseline BTC `0,3764`. Exp131–135 giữ Docs axis bất biến nhưng Chunks F2 chỉ đạt `0,2509–0,3065`; kể cả Exp135 tốt nhất vẫn thấp hơn champion `0,0381` ở Chunks F2. Dừng sweep anchored short-window. Benchmark dịch chọn VinAI Translate v2 cho EN và Qwen3-14B-AWQ cho ZH; bước tiếp theo là chạy đủ 1.200 query, rebuild cache riêng và chỉ nộp translation-repair ablation nếu docs membership thực sự thay đổi. Mọi thí nghiệm tiếp theo dùng Exp122 làm control cho tới khi có champion mới.

1. Sau merge/rebuild thêm `1k_urls.zip` ngày 19/10, active index có `1.212.421` documents / `1.724.798` chunks; embedded registry khớp chính xác `1.212.421` IDs. Unembedded còn `560`, remaining `7.434`, excluded `183`. Batch mới bổ sung `1.146` docs / `1.156` chunks, không trùng hoặc ngoài corpus. Coverage trên danh sách URL thô là `99,3301%`, không phải coverage nhãn chấm điểm. Exp74 chỉ refresh tail ranks 261–300 và giữ chunks Exp73, chưa rerun toàn bộ retrieval/evidence.
2. Audit JSON Exp73: mỗi query có 216 documents nhưng chỉ trung bình `88,788` documents có chunk; `127,213` documents đã chọn chưa có evidence. Đây là khoảng trống đầu ra có thể xử lý trước khi embedding mới tới, không phải khẳng định những docs này đều relevant.
3. CE hiện dùng context `384` tokens và bảo vệ top-150 documents. Cần kiểm tra mất evidence do truncation và chất lượng head thay vì chỉ mở tail tiếp.
4. Exp55 thất bại khi đồng thời dùng BM25/RRF/ICD và cutoff quá nhỏ. Chưa có bằng chứng ICD độc lập cải thiện điểm; không đưa hard filter hoặc ngưỡng `0,73` sang score domain khác.

Ưu tiên: dùng model signal mới để thoát vùng bão hòa của sweep BGE, nhưng không tiếp tục scale một nhánh đã giảm điểm. Exp89 cho thấy Qwen-0.6B passage reranker không nên thay membership độc lập trong pool hiện có; Qwen secondary index vẫn đo một giả thuyết khác là tìm candidates ngoài pool BGE. Mở rộng span chỉ dùng dung lượng còn trống, không tạo artifact >100 MB. Vector BGE bổ sung vẫn được tích hợp riêng khi artifact tới.

Mục 2–3 lưu lịch sử clean rebuild ngày 16/10, không mô tả quy mô index hiện tại.

## 2. Audit index và nguồn sai lệch

### 2.1 Trạng thái trước rebuild

Nguồn kiểm tra:

- `data/raw/btc_provided/links_corpus_vi_en_zh.parquet`
- `data/indices/new_dataset/index/chunks_metadata.parquet`
- `data/indices/new_dataset/index/emb_dense/`
- `data/indices/new_dataset/index/faiss_index_flat_ip.bin`
- `data/indices/new_dataset/index/stats.json`

Kết quả:

| Thành phần                                  |  Số lượng |
| ------------------------------------------- | --------: |
| Document duy nhất trong index               | 1.056.901 |
| Document thuộc danh sách BTC hiện tại       | 1.016.285 |
| Document không thuộc danh sách BTC hiện tại |    40.616 |
| Coverage hợp lệ hiện tại                    |    83,26% |
| Chunks trong metadata                       | 1.500.940 |
| Dense vectors trong các shard               | 1.500.940 |
| Vectors trong FAISS                         | 1.500.940 |

Các lớp `chunks_metadata`, dense shards, `chunk_ids.npy` và FAISS cũ khớp đủ `1.500.940` chunks. Sai lệch không phải do FAISS bị thiếu vector so với metadata; nó đến từ dữ liệu đầu vào đã được merge.

### 2.2 Trạng thái sau rebuild

| Thành phần                         |   Kết quả đã xác minh |
| ---------------------------------- | --------------------: |
| Document hợp lệ trong active index |             1.115.733 |
| Document không thuộc danh sách BTC |                     0 |
| Coverage corpus chính thức         |            91,408719% |
| Chunks metadata                    |             1.590.459 |
| Dense vectors / FAISS `ntotal`     |             1.590.459 |
| Sparse matrix                      |   1.590.459 × 250.005 |
| Text rows / unique document IDs    | 1.115.733 / 1.115.733 |

Active index: `data/indices/new_dataset/index`

Backup có thể phục hồi: `data/indices/new_dataset/index_backup_pre_clean_rebuild_20261016T155529`

Manifest: `data/indices/new_dataset/index/rebuild_manifest.json`

### 2.3 Artifact đã gây ra 40.616 document không hợp lệ

Sai lệch được khoanh vùng chính xác tới:

`data/indices/new_dataset/index_backup_unembedded_samples_0-100_2.zip`

Artifact này chứa:

- `94.575` document tổng cộng.
- `53.959` document thuộc danh sách BTC hiện hành.
- `40.616` document không thuộc danh sách BTC hiện hành.

Toàn bộ `40.616` document không hợp lệ trong index hiện tại đều đến từ artifact này. Các artifact `0-100k`, `100-200k`, `0-100k-2`, `200-300k`, `300-400k` và artifact 99.448 docs được kiểm tra đều chứa 100% ID hợp lệ theo danh sách hiện hành.

Dấu hiệu cho thấy đây là artifact từ bộ URL cũ:

- Toàn bộ ID không hợp lệ nằm trong khoảng `1.705.850–4.161.614`, thuộc dải ID của bộ khoảng 4,4 triệu URL trước đây.
- `40.358/40.616` URL lỗi thuộc `cnkang.com`.
- Không URL nào trong 40.616 URL này xuất hiện nguyên dạng trong danh sách BTC hiện hành dưới một ID khác, nên không thể sửa đơn giản bằng remap ID.
- `stats.json` xác nhận index ngày 16/10 được tạo bằng cách merge `previous 962k + unembedded_0-100_2 (94.575 docs)`.

Kết luận: giả thuyết tải hoặc merge nhầm artifact của bộ 4,4 triệu URL là đúng với độ tin cậy rất cao. Điều được chứng minh trực tiếp là toàn bộ contamination đến từ một artifact cụ thể; provenance xa hơn của artifact không còn manifest gốc trong workspace để chứng minh tuyệt đối.

### 2.4 Cách xử lý đã thực hiện

Các document hợp lệ và không hợp lệ bị trộn trong cùng shard embedding. Việc chỉ lọc `chunks_metadata` sẽ làm mapping giữa FAISS row, sparse row và chunk ID sai lệch.

Clean rebuild đã tái sử dụng các vector sẵn có và thực hiện đồng bộ:

1. Tạo mask theo `doc_id ∈ official_ids`.
2. Giữ lại dense vector, sparse row, chunk span và text tương ứng.
3. Đánh lại `chunk_id` liên tục.
4. Rebuild FAISS, sparse CSR, `chunk_ids.npy` và `chunks_metadata.parquet` cùng một lần.
5. Kiểm tra mọi `doc_id` trong index mới đều thuộc danh sách BTC.

Không cần embed lại `53.959` docs hợp lệ nằm chung artifact; chỉ cần lọc và rebuild mapping.

## 3. Artifact 99.448 document đã được merge

Artifact:

`data/indices/new_dataset/index_backup_unembedded_samples_0-100-20261014T033450Z-1-001.zip`

Kết quả kiểm tra:

| Kiểm tra                                            |       Kết quả |
| --------------------------------------------------- | ------------: |
| Documents trong artifact                            |        99.448 |
| Chunks trong artifact                               |       146.128 |
| Documents hợp lệ theo BTC hiện hành                 |        99.448 |
| Documents đã có trong index hiện hành               |             0 |
| Documents khớp tập hợp “embedded nhưng thiếu index” | 99.448/99.448 |

Artifact có đủ:

- `emb_dense/vec_*.npy`
- `emb_dense/ids_*.npy`
- `emb_dense/sp_*.npz`
- chunk metadata
- document/text parquet

Kết luận đã xác nhận: `99.448` document này **đã được embed** nhưng trước rebuild chưa nằm trong consolidated FAISS index. Artifact hiện đã được merge đầy đủ vào active index.

Sau clean rebuild và merge artifact, coverage hợp lệ đã tăng từ:

`1.016.285 / 1.220.598 = 83,26%`

lên:

`1.115.733 / 1.220.598 = 91,41%`

## 4. Trạng thái corpus

**Snapshot hiện hành 19/10/2026 sau merge/rebuild hai ZIP:** active index và embedded registry cùng `1.211.275` docs; index có `1.723.642` chunks, 22 dense/chunk shards và 89 text shards. `5k_urls.zip` có đúng 5.338 docs / 16.398 chunks (5.324 Pharmacity + 14 Iiyi); `2k_urls.zip` bổ sung hai bài Gia Đình Online / 7 chunks. Đã chuyển 5.338 rows mới từ unembedded sang embedded; hai Gia Đình đã có trong registry nên không thêm lần nữa. Unembedded còn 1.706 dropped rows, remaining 7.434, excluded 183; bốn registry vẫn phân hoạch chính xác 1.220.598 ID–URL BTC. FAISS FlatIP, sparse CSR, chunk IDs và global metadata đã rebuild; index cũ cùng registry trước chuyển được giữ làm backup. [Manifest](../data/audits/recovered_index_merge_20261019/manifest.json). Không tái dùng cache retrieval/rerank/submission của index cũ nếu chưa kiểm tra fingerprint và candidate coverage. Coverage URL thô `99,2362%` không đồng nghĩa recall trên ground truth; theo thông báo BTC người dùng cung cấp, tài liệu không truy cập được/không còn nội dung không thuộc nhãn chấm, nên không lấy việc cứu đủ mọi URL làm gate tăng điểm.

**Snapshot lịch sử 19/10/2026 trước merge:** active index `1.205.935` docs / `1.707.237` chunks; embedded registry `1.205.937`, unembedded `7.044`, remaining `7.434`, excluded `183`. Hai bài Gia Đình Online (`103007`, `116642`) khi đó đã có vector nhưng chưa merge index. Chi tiết [recovery report](remaining_crawl_analysis.md) và [audit ZIP/registry](../data/audits/embedded_2k_zip_20261019_append/manifest.json).

**Snapshot lịch sử 16/10/2026 (giữ để truy vết):**

| Nhóm                         |      Tổng rows | Hợp lệ theo BTC | Trạng thái                       |
| ---------------------------- | -------------: | --------------: | -------------------------------- |
| Active index sau rebuild     | 1.115.733 docs |       1.115.733 | Đã index; không có ID lỗi        |
| Embedded artifact đã merge   |         99.448 |          99.448 | Đã nằm trong active index        |
| `unembedded_samples.parquet` |         91.908 |          91.908 | Có text, đang/chờ embed          |
| `remaining_urls.parquet`     |         12.774 |          12.774 | URLs còn lại sau crawl/reconcile |

`embedded_samples.parquet` cũng đã được lọc từ `1.156.349` xuống `1.115.733` rows để khớp chính xác active index. Backup có thể phục hồi nằm tại `data/embedded_samples.parquet.pre_clean_rebuild_20261016T155529.bak`.

`unembedded_samples.parquet` từng được lọc loại đúng `4.370` cặp `(id, url)` ngoài corpus, sau đó được bổ sung các URL crawl/recover thành công; trạng thái active mới nhất là `91.908` rows hợp lệ có text.

`remaining_urls.parquet` đã tiếp tục được giảm sau các đợt crawl/recover và loại URL 404 đã xác minh; trạng thái active mới nhất là `12.774` rows.

Nếu hoàn thành theo thứ tự:

1. Hoàn tất: clean rebuild và merge 99.448 docs, coverage `91,41%`.
2. Tiếp theo: embed `91.908` docs hợp lệ trong `unembedded_samples`; nếu toàn bộ được index, coverage đạt khoảng `98,94%`.
3. Sau đó: crawl và embed `12.774` URLs còn lại. Không khẳng định ba registry là phân hoạch tuyệt đối cho tới khi chạy lại audit sau embedding và đối chiếu các URL 404 đã loại.

Hai registry `embedded_samples.parquet` và `unembedded_samples.parquet` hiện không trùng ID/URL và mọi cặp `(id, url)` đều thuộc corpus chính thức.

## 5. Phân tích điểm hiện tại

**Cập nhật 19/10:** Exp74 có Docs F2 `0,3574`, Chunks F2 `0,2868`, Final `0,3221`; Docs P/R `0,1813/0,6086`, Chunks P/R `0,2401/0,3685`. So với Exp73, Docs F2 tăng `+0,0014` và Final `+0,0007`; chunks giữ nguyên đúng thiết kế. Gain chưa tách riêng batch 1k với các batch merge trước và pool refresh. Dòng leaderboard người dùng cung cấp cho `toptire`, submission `6084`, ngày 18/10 lúc 23:23: Final `0,4071`, Docs F2 `0,4073`, Chunks F2 `0,4068`, Docs P/R `0,2317/0,5706`, Chunks P/R `0,2286/0,5725`. Không xác minh thứ hạng trực tiếp và không suy diễn phương pháp của đội đó từ điểm tổng hợp.

Docs Recall của ta cao hơn (`0,6086`) nhưng Docs Precision thấp hơn (`0,1813`). Chunk Precision của ta cao hơn (`0,2401`) nhưng Chunk Recall thấp hơn nhiều (`0,3685`). Khoảng `71%` chênh lệch tổng hai F2 nằm ở chunk axis. Điều này định hướng ưu tiên evidence coverage; không chứng minh thiếu chunk là nguyên nhân duy nhất.

Các ngưỡng cần đạt theo công thức BTC:

- Giữ Docs F2 `0,3560`: cần Chunks F2 `0,4040` để Final đạt `0,3800`.
- Giữ Chunks F2 `0,2868`: cần Docs F2 `0,4732`.
- Một mục tiêu cân bằng: Docs F2 `0,4000` và Chunks F2 `0,3600`.
- Nếu đạt Chunk F2 của dòng tham chiếu `0,4068` với Docs hiện tại, Final sẽ là `0,3814`. Đây là phép tính điều kiện, không phải dự báo.

F2 là macro-average theo query; không tính F2 từ hai số macro Precision/Recall, không suy ra số ground-truth documents hoặc cấu hình đối thủ từ tỷ lệ hai số này.

**Phân tích lịch sử tại Exp50:**

| Cấu hình                 | Docs F2 | Chunks F2 |  Final |
| ------------------------ | ------: | --------: | -----: |
| Exp50 champion           |  0,3336 |    0,2851 | 0,3093 |
| BM25 baseline BTC        |  0,5587 |    0,1941 | 0,3764 |
| Mốc công khai tham chiếu |  0,4183 |    0,4246 | 0,4214 |

Docs và chunks được chấm độc lập. Nếu tái tạo được Docs F2 của baseline `0,5587` và giữ Chunks F2 Exp50 `0,2851`, điểm suy ra là:

`(0,5587 + 0,2851) / 2 = 0,4219`

Để đạt Final `0,60` trong điều kiện giữ Chunks F2 `0,2851`, Docs F2 phải đạt `0,9149`, gần như bất khả thi. Nếu chỉ giữ Docs F2 baseline `0,5587`, Chunks F2 phải đạt `0,6413`. Một cấu hình mục tiêu cân bằng hơn là Docs F2 `0,65` và Chunks F2 `0,55`.

Đây là phép suy luận định hướng thử nghiệm, không phải dự đoán chắc chắn và không nói lên thứ hạng thực tế.

## 6. ICD-10 routing và chiến lược hướng tới 0,60

### 6.1 Kết luận từ gợi ý của BTC

Nên làm theo hướng phân vùng tài liệu bằng ICD-10, nhưng triển khai dưới dạng **multi-label soft routing**:

- Query nhận top-3 chapter/block, confidence và cờ `UNKNOWN`.
- Global BM25/dense/sparse candidates luôn được giữ lại.
- ICD match chỉ là feature boost/rerank; không xóa candidate ngoài vùng ở thử nghiệm đầu tiên.
- High-confidence dùng top-1 boost mạnh hơn; medium-confidence dùng top-2/3 với boost nhỏ; low/`UNKNOWN` chỉ dùng global retrieval.
- Hard filter chỉ được cân nhắc nếu soft routing thắng ít nhất hai ablation và không làm Docs Recall giảm.

Lý do: query bệnh nhân thường chứa đồng thời bệnh, triệu chứng, xét nghiệm, thuốc, thai sản hoặc thủ thuật. ICD phù hợp cho bệnh/chẩn đoán nhưng không bao phủ tốt mọi intent; về dài hạn cần kết hợp LOINC cho xét nghiệm, ATC cho thuốc và anatomy/symptom lexicon cho query chưa có chẩn đoán.

### 6.2 Prototype offline đã triển khai

Artifact:

- Router: `src/retrieval/icd10_router.py`.
- Builder: `scripts/build_icd10_query_routes.py`.
- Snapshot: `data/reference/icd10/chapters.parquet` và `entries_en.parquet`.
- Routes: `data/reference/icd10/query_routes.parquet`.
- Summary: `data/reference/icd10/routing_summary.json`.

Nguồn là WHO ICD-10 2019 plain-text metadata và danh sách 22 chương tiếng Việt từ hệ thống mã hóa lâm sàng của Cục Quản lý Khám, chữa bệnh/Bộ Y tế. Prototype dùng `query` và `query_en` đã có sẵn, không gọi model/API đóng.

Kết quả trên 1.200 query và 12.217 mô tả ICD:

- High confidence: `416` (`34,7%`).
- Medium confidence: `420` (`35,0%`).
- Low/`UNKNOWN`: `364` (`30,3%`).
- Có 9 query không tạo được route hữu ích.
- Chương XVIII (triệu chứng/xét nghiệm chưa phân loại) có `188` query; chương XXI (tình trạng sức khỏe/tiếp cận dịch vụ) có `164` query. Tỷ trọng lớn của hai vùng này là tín hiệu rõ rằng hard filter theo bệnh/chương duy nhất sẽ dễ sai.

### 6.3 Kiến trúc retrieval đề xuất

1. Global candidate generation: BM25 document + dense VI/EN/ZH + BGE sparse.
2. Query routing: top-3 ICD chapter/block + confidence + `UNKNOWN`.
3. Document routing: batch-label title + lead + nội dung bằng BGE-M3 với chapter descriptions VI/EN sau khi embedding hoàn tất.
4. Candidate union: global pool luôn tồn tại; routed pool chỉ bổ sung ứng viên.
5. Reranker features: lexical score, dense score, language/domain, ICD chapter/block match và routing confidence.
6. Document-gated evidence extraction: tìm sentence windows trong top documents, sau đó merge evidence gần nhau theo prior đã thắng ở Exp47.

### 6.4 Submission ladder để kiểm chứng bằng scorer BTC

Đây là ladder đề xuất cũ; các số Exp51–55 bên dưới không phải lịch sử artifact thực tế. Xem nhật ký để biết cấu hình đã chạy và mục 13 cho số thí nghiệm mới, không tái sử dụng số experiment đã có.

Không có ground truth local nên mỗi kết luận điểm phải đến từ hệ thống BTC. Khi test document branch, giữ nguyên chunks Exp47/Exp50.

**Exp51 — BM25F document-level đúng corpus**

- Index sau embedding, chỉ official IDs.
- Title/lead/body là field riêng; analyzer VI/EN/ZH và một BGE-M3 wordpiece branch để đối chiếu gợi ý BTC.
- Query VI/EN/ZH retrieve độc lập, fusion theo rank.
- Go nếu Docs F2 tăng ít nhất `+0,03`; nếu không, audit tokenizer, normalization và document construction trước khi thêm model.

**Exp52 — Adaptive document count**

- So fixed `100/125/150` với policy theo score margin/percentile.
- Không sao chép raw threshold `0,73` sang score domain khác.
- Chọn theo Docs F2, không theo precision riêng lẻ.

**Exp53 — ICD soft boost**

- Chỉ áp dụng cho high-confidence query.
- Boost nhỏ cho top-1 và top-2/3 chapter match.
- Giới hạn churn không quá 10–15 documents/query so với document champion.
- Go nếu Docs F2 tăng ít nhất `+0,005` và recall không giảm; kill nếu Docs Recall giảm trên `0,005` hoặc Final giảm trên `0,003`.

**Exp54 — Routed candidate union**

- 80–100 global docs + 25–45 docs từ top-2 ICD regions.
- Medium-confidence dùng nhiều vùng; `UNKNOWN` dùng 100% global.
- Chỉ chạy nếu Exp53 thắng.

**Exp55 — Block-level routing có điều kiện**

- Chỉ dùng cho nhóm high-confidence mà chapter routing đã có lợi.
- Retrieve top ICD codes/blocks từ descriptions/synonyms rồi aggregate lên chapter.
- Hard negatives cho fine-tune phải lấy trong cùng chapter/block để học phân biệt bệnh gần nhau.

### 6.5 Nhánh bắt buộc để tiến từ 0,42 lên 0,60

ICD/BM25 chủ yếu cải thiện document axis. Để kéo Chunks F2 từ `0,2851` lên vùng `0,45–0,55+`:

1. Lấy top documents từ document branch tốt nhất.
2. Chia mỗi document thành sentence windows có overlap.
3. Rank windows bằng BM25/local dense/late interaction hoặc reranker open-weight hợp lệ.
4. Chọn nhiều evidence khi cách xa; merge khi gap nhỏ như Exp47.
5. Giữ mọi span nguyên văn và điều chỉnh số chunk theo confidence; không cắt tail cố định như Exp48.
6. Sau khi evaluator và candidate pool ổn định, fine-tune bằng weak positives từ Q&A pages và same-chapter hard negatives.

### 6.6 Chạy secondary embedding song song sau khi hoàn tất BGE-M3

**Gate cập nhật 20/10:** quyết định hoãn embedding model thứ hai tới sau baseline đã bị hủy. Trong lúc các ablation submission/reranker tiếp tục, chạy secondary embedding theo shard và checkpoint trên Kaggle. Công việc này không tiêu slot nộp, không chặn thử nghiệm nhanh trên BGE và không ghi đè active index.

Quyết định: giữ BGE-M3 làm index nền vì model này cung cấp đồng thời dense, sparse lexical và ColBERT. Qwen3 là dense branch độc lập để tạo candidates mới và fusion có đối chứng. Full corpus `Qwen3-Embedding-0.6B` được chạy trước để có index hoàn chỉnh sớm; `Qwen3-Embedding-4B` vẫn là model chất lượng chính nhưng chạy staged/resume vì 1.724.798 chunks ở max length 1.024 không thực tế để hoàn tất trong một phiên T4×2.

Shortlist:

1. `Qwen/Qwen3-Embedding-4B` ở output dimension `1024`: ứng viên chính để tạo bước nhảy chất lượng.
2. `Qwen/Qwen3-Embedding-0.6B` ở dimension `1024`: đối chứng rẻ, dùng để kiểm tra pipeline và có thể chạy local với batch nhỏ.
3. `ncbi/MedCPT-Query-Encoder` + article encoder: chỉ dùng cho nhánh 240k PubMed tiếng Anh, không embed toàn corpus đa ngữ.
4. Chưa ưu tiên `Qwen3-Embedding-8B`: chi phí inference/index gần gấp đôi 4B trong khi mức tăng benchmark công bố nhỏ hơn nhiều so với bước nhảy từ 0.6B lên 4B.

Qwen3-Embedding hỗ trợ hơn 100 ngôn ngữ, context 32K, instruction-aware và Matryoshka Representation Learning. Bản 4B có dimension gốc 2.560 nhưng phải benchmark ở 1.024 dimensions trước để giữ footprint tương đương BGE-M3 và tránh tăng chi phí FAISS không cần thiết.

#### Pha A — Candidate-pool ablation và full 0.6B chạy song song

1. Lấy top-500 candidates/query từ BGE-M3 champion trên index hoàn chỉnh.
2. Dedup thành tập candidate documents/chunks duy nhất rồi chỉ embed tập này bằng Qwen3-Embedding-0.6B và 4B.
3. Query dùng instruction tiếng Anh nhất quán:

```text
Instruct: Given a Vietnamese medical question, retrieve multilingual medical documents that directly answer the question.
Query: {query}
```

4. Giữ nguyên chunks Exp47/Exp50 để chỉ đo document axis.
5. So sánh ba policy:
   - Qwen ranking thuần trong BGE candidate pool.
   - RRF bảo thủ giữa BGE rank và Qwen rank.
   - Giữ BGE champion, chỉ cho Qwen thay tối đa 10–20 documents/query.
6. Chạy query VI trước; chỉ ablate EN/ZH riêng sau khi VI có tín hiệu dương, tránh lặp lại regression do fusion nhiều branch của Exp41.

#### Tiêu chí go/kill

- Go tới full-corpus Qwen3-4B nếu candidate rerank tăng Docs F2 ít nhất `+0,01`.
- Có thể go nếu candidate union chỉ tăng `+0,005` nhưng Docs Recall không giảm và kết quả ổn định ở hai ablation.
- Kill nếu Docs Recall giảm trên `0,005`, Final giảm trên `0,003`, hoặc phần lớn gain chỉ đến từ thay đổi output count.
- Qwen3-0.6B chỉ là model production candidate nếu điểm gần 4B trong biên `0,003–0,005`; nếu không, giữ nó làm pipeline smoke test.

#### Pha B — Full secondary index và staged 4B

- Embed toàn corpus bằng Qwen3-Embedding-0.6B ở 1.024 dimensions trước; sau đó chạy 4B theo shard/resume hoặc chỉ candidate pool nếu ETA full-corpus không khả thi. Không dùng dimension gốc 2.560 ở lần đầu.
- Giữ BGE-M3 và Qwen3 thành hai index độc lập để ablate và ensemble; không ghi đè artifact BGE hiện tại.
- Query encoder phải dùng đúng prompt/instruction đã khóa trong Pha A; document không thêm query instruction.
- Retrieval full-corpus Qwen có mục tiêu cứu relevant documents nằm ngoài BGE top-500, sau đó fuse bảo thủ với champion.
- Chỉ tăng lên 2.560 dimensions hoặc thử 8B nếu bản 1.024d full-corpus đã thắng rõ và storage/latency còn ngân sách.

#### Footprint và tài nguyên

Với `1.724.798` chunks hiện tại:

- BGE-M3 1.024d: FAISS hiện tại `7.064.772.653` bytes.
- Qwen3 1.024d: output transfer FP16 khoảng `3,29 GiB`; FAISS FlatIP FP32 khoảng `6,58 GiB`, tương đương BGE.
- Qwen3-4B 2.560d: ước tính khoảng `16,45 GiB` chỉ cho FAISS float32.
- Qwen3-8B 4.096d: ước tính khoảng `26,32 GiB`.

**Artifact triển khai 20/10:** `prepare_qwen3_embedding_kaggle.py` đã dựng đủ `1.724.798` chunks thành 18 Parquet shards, tổng `1.157.306.381` bytes. Audit xác nhận mọi `row_id` xuất hiện đúng một lần, `row_id == chunk_id`; 31 span chỉ chứa whitespace được giữ mapping nhưng notebook gán zero-vector thay vì tạo nội dung giả. Notebook `12_qwen3_embedding_full_kaggle.ipynb` pin revisions `Qwen3-Embedding-0.6B@97b0c614...` và `Qwen3-Embedding-4B@5cf2132a...`, max length 1.024, output 1.024d, document không có instruction, query VI/EN/ZH dùng cùng instruction. Có T4×2, checkpoint/resume theo shard và manifest chống trộn model/config.

RTX 3050 Ti 4GB không phù hợp để full-embed Qwen3-4B/8B ở BF16. Bản 0.6B có thể chạy local với batch nhỏ; benchmark/full embedding 4B nên chạy trên Kaggle/L4/T4 hoặc GPU có VRAM lớn hơn. Luôn ghi model revision, dimension, dtype, prompt và checksum vào manifest để tránh trộn vector khác không gian.

## 7. Root causes trong retrieval và evaluation

### Deferred — Local evaluator khác metric chính thức

`src/evaluation/scorer.py` đang dùng token-set overlap với ngưỡng `0,5`; metric chính thức dùng normalized ordered-token LCS với ngưỡng `0,4`.

Hệ quả: các kết luận về chunk window, reranker và output count chưa có tín hiệu local đáng tin. Tuy nhiên, đây không còn nằm trên critical path: các ablation sẽ được đo trực tiếp bằng hệ thống chấm của BTC. Chỉ sửa evaluator nếu cần tăng tốc vòng lặp sau này.

### P0 — Hybrid chưa tạo candidate độc lập

`src/retrieval/faiss_searcher.py` lấy dense top-400 trước rồi mới chấm sparse trên chính tập đó. Sparse/BM25 và query translation không thể cứu document nằm ngoài dense top-400.

Cần tạo candidate riêng từ:

- BM25 document retrieval.
- BGE-M3 sparse retrieval.
- Dense VI.
- Dense EN.
- Dense ZH.

Sau đó union và fuse bằng rank-based fusion hoặc score đã calibrate.

**Trạng thái 16/10/2026:** đã triển khai Exp41 với candidate độc lập toàn index cho BGE-M3 sparse và dense VI/EN/ZH, sau đó weighted RRF riêng ở cấp chunk và document. SQLite FTS5 cũ không được đưa vào submission chính vì dùng corpus stale 1.358.107 docs, analyzer `unicode61` và Exp20 chỉ đạt Docs F2 `0,0736`; nhánh BM25 đúng analyzer/corpus vẫn là một thử nghiệm riêng ở Gate 1.

**Kết quả Exp41:** Final `0,2523`, Docs F2 `0,2747`, Chunks F2 `0,2298`, thấp hơn Exp40 ở mọi chỉ số chính. True union không bị bác bỏ, nhưng cấu hình weighted RRF bốn nhánh đã thay ranking quá mạnh. Bước tiếp theo phải ablate từng branch, giữ nguyên chunks champion và chỉ cho phép thay khoảng 5–10 docs/query.

**Exp42 sẵn sàng nộp:** giữ nguyên toàn bộ chunks Exp40; chỉ thêm sparse VI độc lập với RRF weight `0,5`, làm thay trung bình 5,53 docs/query. Đây là phép thử docs-only đầu tiên đủ sạch để quyết định có giữ nhánh sparse độc lập hay không.

**Kết quả Exp42:** Final `0,2966`, Docs F2 `0,3173`, Chunks F2 giữ đúng `0,2759`. Sparse VI độc lập làm Docs F2 giảm `0,0050`, vì vậy branch này bị loại ở weight `0,5`. Protocol docs-only được xác nhận và sẽ dùng tiếp để thử từng branch dense ZH/EN riêng.

**Exp43 sẵn sàng nộp:** giữ nguyên chunks Exp40, chỉ inject dense ZH weight `0,45`; thay trung bình 5,64 docs/query, tối đa 10. Đây là phép thử ưu tiên trước dense EN vì query ZH từng cho tín hiệu tốt hơn trong Exp33.

**Kết quả Exp43:** Final `0,2958`, Docs F2 `0,3158`; dense ZH làm Docs F2 giảm `0,0065` trong khi chunks giữ nguyên. Dừng candidate injection (kể cả dense EN prior thấp hơn) và chuyển sang ablation `relevant_docs k=75` trên chính ranking Exp40.

**Kết quả Exp44:** Final `0,2868`, Docs F2 `0,2977`. Top-75 tăng precision nhưng làm recall giảm mạnh, xác nhận phải giữ top-100. Bước kế tiếp là rerun nguyên cấu hình Exp40 trên clean index 1.115.733 docs để đo riêng tác động của rebuild và 58.832 valid docs tăng thêm.

**Kết quả Exp45:** Final `0,3029`, Docs F2 `0,3266`, Chunks F2 `0,2792`. So với Exp40, cả 7 chỉ số đều tăng; clean rebuild và 99.448 valid docs mới là hướng đã được BTC xác nhận.

**Kết quả Exp46–50:** top-125 documents tăng Docs F2 lên `0,3336`; merge evidence gần nhau tăng Chunks F2 lên `0,2851`; kết hợp hai axis tạo Exp50 Final `0,3093`. Exp48 top-64 tăng chunk precision nhưng giảm recall mạnh, xác nhận không được cắt chunk tail quá sâu.

**Kết quả full corpus và BM25/ICD ngày 17/10:** Exp51 trên `1.205.935` documents là champion mới với Final `0,3098`, Docs F2 `0,3343` và Docs Recall `0,4710`. Exp55 BM25F + multilingual RRF + ICD soft boost, adaptive `5–12` docs/query, chỉ đạt Final `0,1558` và Docs F2 `0,0263` (P `0,1281`, R `0,0237`) trong khi Chunks F2 giữ nguyên `0,2853`. Kết luận: dừng pure-BM25 top nhỏ và không nộp các biến thể top-1/top-3; BM25 chỉ được giữ làm candidate generator sâu trước dense scoring/rerank. ICD phải được ablate độc lập trên cùng dense pool, không dùng để hard-filter hoặc thay ranking champion.

**Kết quả Exp56:** mở rộng cùng dense ranking từ 125 lên 150 documents/query tăng Docs Recall từ `0,4710` lên `0,5088`, Docs F2 từ `0,3343` lên `0,3408` và Final từ `0,3098` lên `0,3131`; chunk metrics giữ nguyên. Tiếp tục sweep top-175, sau đó chỉ thử top-200 nếu Docs F2 còn tăng.

**Kết quả Exp57:** top-175 tiếp tục tăng Docs Recall lên `0,5408`, Docs F2 lên `0,3448` và Final lên `0,3150`; precision giảm còn `0,1966`, nhưng F2 vẫn được lợi. Lợi ích biên Docs F2 là `+0,0040`, do đó thử top-200 như mốc kế tiếp và đánh giá bão hòa trước khi mở rộng thêm.

**Kết quả Exp58:** top-200 tăng Docs Recall lên `0,5690`, Docs F2 lên `0,3455` và Final lên `0,3154`; precision giảm còn `0,1834`. Docs F2 chỉ tăng thêm `+0,0007`, cho thấy gần bão hòa nhưng chưa đạt đỉnh. Tiếp tục sweep `+25` documents mỗi lần đến bước đầu tiên không tăng; khi thấy giảm, giữ champion trước đó và chỉ kiểm tra midpoint nếu chênh lệch đủ đáng kể.

**Kết quả Exp59 đã hiệu chỉnh:** submission top-225 đạt Final `0,3156`, Docs F2 `0,3459`, Docs Precision `0,1727` và Docs Recall `0,5965`. So với Exp58, Docs F2 tăng `+0,0004` và recall tăng `+0,0275`; scorer có xét tail sau rank 200. Kết quả giống Exp58 được báo trước đó là nhầm số liệu, vì vậy thu hồi kết luận cap 200. Tiếp tục sweep top-250 và dừng khi Docs F2 giảm thật sự.

**Kết quả Exp60:** top-250 đạt Final `0,3145`, Docs F2 `0,3437`, Docs Precision `0,1627` và Docs Recall `0,6178`. So với Exp59, recall tăng `+0,0213` nhưng precision giảm `-0,0100`, khiến Docs F2 giảm `-0,0022` và Final giảm `-0,0011`; chunk metrics bất biến. Đây là bước giảm đầu tiên, vì vậy dừng mở rộng top-k, giữ Exp59 top-225 làm champion. Ba mốc top-200/225/250 nội suy cực đại xấp xỉ 216 docs/query; dùng Exp61 top-216 để tinh chỉnh cutoff trong khoảng thắng thay vì thử top-275.

**Kết quả Exp61:** top-216 đạt Final `0,3157`, Docs F2 `0,3461`, Docs Precision `0,1765` và Docs Recall `0,5869`; chunk metrics tiếp tục bất biến. So với Exp59 top-225, precision tăng `+0,0038`, recall giảm `-0,0096`, nhưng Docs F2 vẫn tăng `+0,0002` và Final tăng `+0,0001`. Exp61 là champion mới và xác nhận cực đại nội suy gần đúng. Dừng sweep fixed-k ở đây: thử 215/217 chỉ có kỳ vọng dưới độ phân giải leaderboard; bước tiếp theo phải cải thiện thứ tự ranking hoặc dùng adaptive-k theo độ tin cậy từng query.

### P0 — Output cố định làm loãng precision

Sweep fixed-k đã hội tụ tại `216` docs/query (Exp61, Docs F2 `0,3461`), nhưng một cutoff chung vẫn không phản ánh độ khó khác nhau giữa các query. Không tiếp tục thử 215/217 vì lợi ích kỳ vọng dưới độ phân giải leaderboard. Bước kế tiếp là adaptive-k quanh vùng `175–250` theo score gap/confidence, với fallback `216`, tối ưu trực tiếp theo F2; chunks vẫn giữ nguyên để cô lập document axis.

**Exp62 adaptive-k đã tạo, chờ điểm BTC:** ngưỡng cosine tuyệt đối bị loại ngay trong phân tích offline vì tạo phân phối hai cực (`497/1.200` query xuống 175 và `608/1.200` query lên 250), cho thấy score offset giữa query/ngôn ngữ quá lớn. Rule chính thức chuẩn hóa riêng từng score curve theo hai anchor rank 175 và 250, rồi chọn cùng mức suy giảm chuẩn hóa `0,601853`; tham số này được hiệu chỉnh không nhãn để mean-k bằng `216`, không dùng ground truth hay phản hồi từng query. Kết quả artifact có k từ `193–250`, mean/median `216`, độ lệch chuẩn `4,707`, p05/p95 `209/224`; giữ nguyên thứ tự document và toàn bộ chunks của Exp61. Nếu Exp62 không thắng, quay lại fixed top-216 và chuyển nguồn lực sang rerank tail thay vì thử thêm công thức cutoff.

**Kết quả Exp62:** Final `0,3156`, Docs F2 `0,3458`, Docs Precision `0,1765`, Docs Recall `0,5862`; chunks bất biến. So với Exp61 fixed top-216, precision bằng nhau ở độ phân giải 4 chữ số nhưng recall giảm `-0,0007`, Docs F2 giảm `-0,0003` và Final giảm `-0,0001`. Adaptive-k theo score-curve shape không tạo tín hiệu query-level đủ chính xác, nên quay lại Exp61 làm champion và dừng cutoff tuning. Bước kế tiếp là thay đổi chất lượng/thứ tự candidates trong tail, không tiếp tục biến đổi số lượng trên cùng ranking.

**Exp63 cho slot cuối ngày, chờ điểm BTC:** chưa rerank như kế hoạch ngày mai; giữ nguyên fixed top-216 của Exp61 và thử độc lập chunk axis. Gap giữ `2.000`, max envelope span tăng `7.000→8.000`, làm số chunks giảm từ `106.182` xuống `105.864` (`-318`) trong khi tổng ký tự chỉ tăng `1.658`. Audit xác nhận từng chunk Exp61 đều nằm nguyên vẹn trong một envelope Exp63 cùng `doc_id`, nên theo LCS/|g| của BTC, mọi ground-truth hit cũ vẫn có một submitted chunk bao chứa evidence tương ứng. Mục tiêu là giảm mẫu số chunk precision mà không mất recall; nếu không thắng, quay lại chunks Exp61 và không tăng span thêm.

**Kết quả Exp63 và chốt ngày:** Final `0,3158`, Docs F2 `0,3461`, Chunk F2 `0,2855`, Docs P/R `0,1765/0,5869`, Chunks P/R `0,2419/0,3654`. Document metrics khớp Exp61 như thiết kế; riêng chunk axis tăng Precision `+0,0005`, Recall `+0,0001`, F2 `+0,0002`, kéo Final tăng `+0,0001`. Exp63 là champion mới. Đã hết slot ngày 17/10; không tạo thêm submission để nộp hôm nay. Ngày mai ưu tiên rerank hoặc thay candidates yếu trong document tail 150–250, sau đó kết hợp với chunk policy span 8.000 của Exp63.

**Exp64 ngày 18/10, chờ điểm BTC:** tái sử dụng tín hiệu BGE cross-encoder đã tính ở Exp38 thay vì chấm lại toàn bộ hàng trăm nghìn cặp trên GPU local. Exp38 từng tăng Docs F2 `+0,0064`, nhưng Final giảm vì output một chunk/document; Exp64 loại confound này bằng cách giữ chunks Exp63 value-by-value. Chính sách: khóa top-150 của Exp63, mở pool đến rank 300, ưu tiên các candidate thuộc top-100 cross-encoder Exp38 rồi xuất đúng 216 docs. Có `927/1.200` query thay đổi; số swaps min/mean/median/max là `0/3,399/3/21`, docs được đưa vào có original rank `217–300` (median `247`). Đây là rerank consensus bảo thủ trên document axis; nếu thắng sẽ chấm lại cross-encoder trực tiếp trên full-corpus pool hiện tại, nếu thua sẽ không mở rộng mức can thiệp của cached ranking.

**Kết quả Exp64:** Final `0,3166`, Docs F2 `0,3478`, Docs Precision `0,1772`, Docs Recall `0,5901`; Chunk F2/P/R giữ nguyên `0,2855/0,2419/0,3654`. So với Exp63, Docs Precision tăng `+0,0007`, Recall tăng `+0,0032`, Docs F2 tăng `+0,0017` và Final tăng `+0,0008`. Exp64 là champion mới. Kết quả xác nhận tín hiệu cross-encoder Exp38 còn giá trị trên full corpus và regression trước đây đến từ chunk output, không phải document reranking. Bước kế tiếp nên mở candidate pool cached-consensus một mức có kiểm soát (300→400) trước khi đầu tư inference mới toàn bộ; vẫn khóa top-150, xuất 216 docs và giữ chunks Exp63 để đo riêng membership gain.

**Exp65 đã tạo, chờ điểm BTC:** giữ frozen top-150, output 216 và chunks Exp63; chỉ mở cached CE candidate pool từ rank 300 lên 400. So với Exp63, `941/1.200` query thay đổi với mean/median/max swaps `4,838/4/39`. Quan trọng hơn, so trực tiếp với Exp64 chỉ có `583` query đổi, trung bình `1,439` swaps bổ sung/query, trung vị `0`, tối đa `18`; mọi doc mới đều thuộc top-100 cross-encoder Exp38 của đúng query. Nếu Exp65 tăng, tiếp tục pool-500 hoặc chuyển sang inference mới; nếu giảm, pool-300 của Exp64 là biên tối ưu cho cached signal.

**Kết quả Exp65:** Final `0,3172`, Docs F2 `0,3489`, Docs Precision `0,1777`, Docs Recall `0,5925`; Chunk F2/P/R giữ nguyên `0,2855/0,2419/0,3654`. So với Exp64 pool-300, Docs Precision tăng `+0,0005`, Recall tăng `+0,0024`, Docs F2 tăng `+0,0011` và Final tăng `+0,0006`. Exp65 là champion mới; cached cross-encoder signal chưa bão hòa ở pool-400. Bước kế tiếp là pool-500 với cùng top-150/output-216/chunks, sau đó dừng sweep ở bước giảm đầu tiên hoặc chuyển sang inference mới nếu phần consensus cũ đã gần cạn.

**Exp66 đã tạo, chờ điểm BTC:** giữ top-150, output 216 và chunks Exp63; chỉ mở cached CE pool từ 400 lên 500. So với Exp63, `941/1.200` query thay đổi với mean/median/max swaps `5,177/4/47`. So trực tiếp với Exp65, chỉ `185` query đổi, trung bình `0,338` swaps bổ sung/query, trung vị `0`, tối đa `13`; mọi doc mới vẫn thuộc top-100 cross-encoder Exp38. Lợi ích biên về membership đã giảm mạnh, nên Exp66 là phép đo bão hòa: nếu không tăng thì giữ pool-400; nếu tăng rất nhỏ cũng nên ưu tiên inference mới thay vì tiếp tục pool sâu hơn một cách mù quáng.

**Kết quả Exp66:** Final `0,3173`, Docs F2 `0,3490`, Docs Precision `0,1777`, Docs Recall `0,5927`; Chunk F2/P/R giữ nguyên `0,2855/0,2419/0,3654`. So với Exp65, Recall chỉ tăng `+0,0002`, Docs F2 và Final cùng tăng `+0,0001`, precision không đổi ở độ phân giải báo cáo. Exp66 là champion mới nhưng sweep cached CE pool đã gần bão hòa. Không tiếp tục pool-600 theo quán tính; bước tiếp theo là chấm cross-encoder mới trên candidates của full index, tập trung quanh biên top-216 và giữ chunks Exp63.

**Exp67 đã tạo, chờ điểm BTC:** chạy inference mới bằng `BAAI/bge-reranker-v2-m3` trên 96.000 pairs thuộc ranks 181–260 của full index; khóa top-180, blend `0,75` fresh CE với `0,25` stage-rank và xuất 216 docs/query. So với Exp66, `1.199/1.200` query thay đổi, tổng `15.644` swaps, mean/median/max `13,037/13/26`; churn trung bình chỉ `6,0%` tổng output vì top-180 giữ nguyên. Toàn bộ chunk giữ nguyên Exp66/Exp63 để đây là ablation docs-only. Audit đã qua official IDs, uniqueness, candidate membership, ZIP CRC/payload và `4/4` tests. Nếu Docs F2 tăng, bước kế tiếp nên thử multi-chunk evidence hoặc một biến thể blend bảo thủ hơn; nếu giảm, không mở pool mà giảm CE weight/churn dựa trên cùng score cache, không cần chạy inference lại.

**Kết quả Exp67:** Final `0,3193`, Docs F2 `0,3532`, Docs Precision `0,1796`, Docs Recall `0,6001`; Chunk F2/P/R giữ nguyên `0,2855/0,2419/0,3654`. So với Exp66, Final tăng `+0,0020`, Docs F2 `+0,0042`, precision `+0,0019` và recall `+0,0074`. Exp67 là champion mới và xác nhận fresh CE có tín hiệu mạnh hơn cached consensus. Sensitivity trên score cache: weight `0,85` chỉ thay thêm trung bình `2,95` docs/query so với Exp67, trong khi pure CE `1,0` thay `6,64`; ưu tiên Exp68 với CE/stage-rank `0,85/0,15`, giữ nguyên pool, top-180, output-216 và chunks để tiếp tục ablation một biến duy nhất.

**Exp68 đã tạo, chờ điểm BTC:** tái sử dụng score cache Exp67 và chỉ đổi CE/stage-rank weight từ `0,75/0,25` thành `0,85/0,15`. So với Exp67, `1.186/1.200` query thay đổi nhưng churn nhỏ: tổng `3.536` swaps, mean/median/max `2,947/3/8`. Top-180, candidate pool 181–260, output-216 và chunks giữ nguyên. Nếu Docs F2 tăng, thử weight `1,0` hoặc mở multi-chunk evidence; nếu giảm, `0,75` là biên tốt hơn và chuyển thẳng sang multi-chunk thay vì tiếp tục sweep weight.

**Kết quả Exp68:** Final `0,3193` và Docs F2 `0,3532` hòa Exp67 ở độ phân giải báo cáo, nhưng Docs Precision giảm `-0,0001` còn `0,1795` và Docs Recall giảm `-0,0004` còn `0,5997`; Chunk metrics giữ nguyên. Exp67 vẫn là champion và weight `0,75` là biên tốt hơn `0,85`. Dừng sweep CE weight, không thử pure CE `1,0`; bước tiếp theo là multi-chunk evidence trên cùng vùng rank 181–260, giữ blend `0,75/0,25` và các policy còn lại của Exp67.

**Exp69 đã tạo, chờ điểm BTC:** tái sử dụng 96.000 first-chunk scores của Exp67 và chấm thêm `26.277` diverse chunks cho `23.311` documents; aggregate bằng max score rồi giữ blend `0,75/0,25`, top-180, pool 181–260, output-216 và chunks Exp67. Extra evidence nâng CE score cho `8.647` documents. So với Exp67, `916/1.200` query thay đổi với tổng `2.051` swaps, mean/median/max `1,709/1/9`; `97,2%` insertions được extra chunk nâng score trực tiếp. Đây là multi-chunk ablation bảo thủ. Nếu Docs F2 tăng, mở rộng multi-chunk sang candidate pool sâu hơn hoặc áp dụng cùng evidence cho vùng ranks 151–180; nếu giảm, giữ single-chunk Exp67 và chuyển sang cải thiện chunk output thay vì tăng document churn.

**Kết quả Exp69:** Final `0,3197`, Docs F2 `0,3540`, Docs Precision `0,1799`, Docs Recall `0,6012`; Chunk F2/P/R giữ nguyên `0,2855/0,2419/0,3654`. So với Exp67, Final tăng `+0,0004`, Docs F2 `+0,0008`, precision `+0,0003` và recall `+0,0011`. Exp69 là champion mới và xác nhận max aggregation trên diverse chunks có ích, nhưng lợi ích biên nhỏ. Bước tiếp theo ưu tiên Exp70: khóa top-150, mở fresh multi-chunk CE trên ranks 151–260 và chọn 66 docs để output-216. Cấu hình này tái sử dụng toàn bộ scores ranks 181–260; chỉ cần chấm mới first/extra chunks cho ranks 151–180, đồng thời kiểm nghiệm vùng head-150 từng thắng ở Exp64–66.

**Exp70 đã tạo, chờ điểm BTC:** khóa top-150 Exp69, fresh multi-chunk rerank source ranks 151–260 rồi chọn 66 docs để output-216; chunks giữ nguyên. Tái sử dụng scores ranks 181–260 và chấm mới `47.551` pairs cho 36.000 documents ranks 151–180. So với Exp69, `1.179/1.200` query thay đổi với tổng `4.385` swaps, mean/median/max `3,654/4/12`; trung bình giữ `26,81/30` docs gốc ranks 151–180, churn chỉ `1,69%` toàn output. Nếu Docs F2 tăng, có thể thử hạ frozen head thêm một bước nhỏ hoặc mở candidate end; nếu giảm, top-180 của Exp69 là vùng bảo vệ đúng và quay sang tối ưu chunk branch.

**Kết quả Exp70:** Final `0,3199`, Docs F2 `0,3543`, Docs Precision `0,1801`, Docs Recall `0,6014`; Chunk F2/P/R giữ nguyên `0,2855/0,2419/0,3654`. So với Exp69, Final tăng `+0,0002`, Docs F2 `+0,0003`, precision và recall cùng tăng `+0,0002`. Exp70 là champion mới nhưng lợi ích biên đã nhỏ. Boundary diagnostic cho thấy `43,24%` insertions đến từ ranks 241–260 và `22,46%` đến từ 251–260, nên pool 260 vẫn bị truncate. Ưu tiên một Exp71 cuối cho document branch: giữ top-150, mở fresh multi-chunk pool 151–300, output-216 và chunks Exp70; sau đó dừng document sweep bất kể kết quả để chuyển sang chunk reranking/selection.

**Exp71 đã tạo, chờ điểm BTC:** khóa top-150 Exp70, mở multi-chunk pool từ 151–260 lên 151–300 và giữ output-216/chunks. Tái sử dụng scores 151–260, chấm mới `62.092` pairs cho 48.000 documents ranks 261–300. So với Exp70, `1.196/1.200` query thay đổi với tổng `7.732` swaps, mean/median/max `6,443/6/15`, tương đương churn `2,98%`; `96,1%` insertions đến trực tiếp từ pool mới. Top-260 được anchor vào cache lịch sử để tránh tie-order drift ở query 159. Exp71 là document experiment cuối; sau khi nhận điểm, giữ champion tốt hơn giữa Exp70/71 và chuyển sang chunk reranking/selection.

**Kết quả Exp71:** Final `0,3207`, Docs F2 `0,3560`, Docs Precision `0,1808`, Docs Recall `0,6059`; Chunk F2/P/R giữ nguyên `0,2855/0,2419/0,3654`. So với Exp70, Final tăng `+0,0008`, Docs F2 `+0,0017`, precision `+0,0007` và recall `+0,0045`. Exp71 là champion mới. Dừng document pool/head sweep theo kế hoạch và dùng hai slot cuối ngày cho chunk-only ablation.

**Kết quả Exp72:** Final `0,3212`, Docs F2/P/R giữ nguyên `0,3560/0,1808/0,6059`; Chunk F2 `0,2863`, Precision `0,2407`, Recall `0,3675`. So với Exp71, Final tăng `+0,0005`, Chunk F2 tăng `+0,0008`: precision giảm `-0,0012` nhưng recall tăng `+0,0021`, xác nhận addition strategy có lợi. Exp72 là champion mới.

**Cấu hình Exp73 đã nộp cho slot cuối ngày 18/10:** giữ nguyên toàn bộ Exp72 và thêm tối đa một evidence thứ hai khi CE score `>2,5`. Có `624/1.200` query được thêm đúng một chunk; score additions min/mean/median/max `2,502/3,981/3,769/8,375`. ZIP `99.553.194` bytes, chỉ còn `446.806` bytes dưới ngưỡng 100 MB. Audit xác nhận docs giống hệt Exp72, chunks cũ giữ nguyên thứ tự, chunks mới nguyên văn và thuộc official corpus; `4/4` tests pass.

**Kết quả Exp73 (nhận ngày 19/10):** Final `0,3214` (`+0,0002`), Docs F2/P/R giữ nguyên `0,3560/0,1808/0,6059`; Chunks F2 `0,2868` (`+0,0005`), Precision `0,2401` (`-0,0006`), Recall `0,3685` (`+0,0010`). Exp73 là champion nội bộ mới. Dừng chuỗi cộng một chunk/lần; chuyển sang kế hoạch mục 13.

### P1 — Reranker cũ bị confound

Exp38 chỉ giữ một chunk trên mỗi document và dùng context 512 tokens. Cần chạy lại sau khi:

- Giữ nhiều candidate chunks/document.
- Dedup theo `(doc_id, start, end)` thay vì text toàn cục.
- Dùng metadata ngôn ngữ thật.
- Tăng context phù hợp với chunk hiện hành.
- Dùng rank blending thay cho per-query min-max dễ bị outlier.

## 8. Roadmap thực thi

Roadmap tổng thể lưu từ giai đoạn trước. Thứ tự và gates thực thi ngày 19/10 lấy theo mục 13; các references Exp47/50 bên dưới là baseline lịch sử.

### Gate 0 — Đo đúng và làm sạch dữ liệu

- [ ] (Deferred) Sửa evaluator theo NFKC, HTML unescape, lowercase, whitespace normalization và token-LCS `0,4`.
- [ ] (Deferred) Viết unit tests đối chiếu đặc tả BTC.
- [x] Rebuild consolidated index sau khi lọc toàn bộ ID không hợp lệ.
- [x] Merge artifact 99.448 docs đã embed.
- [x] Kiểm tra invariant giữa vector rows, sparse rows, chunk IDs, FAISS, text và metadata.
- [ ] Gắn fingerprint mới vào query cache và config để tránh dùng cache cũ.

### Gate 1 — Tái tạo document baseline

1. Chạy BM25F ở cấp document theo đúng corpus, tokenizer/analyzer và score domain được mô tả trong tài liệu BTC.
2. Giữ nguyên chunks của Exp47/Exp50 để chỉ đo Docs F2.
3. Nếu Docs F2 không vượt `0,40`, dừng mở rộng model và đối chiếu tokenizer, normalization, threshold và output policy.

### Gate 2 — Candidate generation

1. [x] Candidate union độc lập giữa BGE sparse và dense; BM25 đúng analyzer còn tách riêng ở Gate 1.
2. [x] Dense retrieval riêng cho `q_vi`, `q_en`, `q_zh`.
3. So sánh RRF với calibrated linear fusion.
4. Tune document output count trên cùng ranking.
5. Sau khi BGE index hoàn chỉnh, re-embed top-500 candidate pool bằng Qwen3-Embedding-0.6B/4B ở 1.024d và chạy docs-only ablation.

### Gate 3 — ICD-10 soft routing

1. Batch-label document thành top-3 chapter/block sau khi embedding hoàn tất.
2. Chạy Exp53 soft boost trước, giữ global candidates và giới hạn churn.
3. Chỉ chạy Exp54 routed union nếu Exp53 tăng Docs F2 mà không giảm recall.
4. Không hard filter query low-confidence/`UNKNOWN`.

### Gate 4 — Chunk evidence

1. Chạy lại BGE reranker sau khi sửa multi-chunk/document.
2. Thử wide verbatim span quanh vùng tốt nhất.
3. Chỉ thêm span thứ hai khi evidence cách xa và confidence đủ cao.
4. Sau khi có baseline sạch, thử Qwen3-Reranker-0.6B rồi 4B.
5. Thử nhánh MedCPT riêng cho 240k PubMed sau bản dịch EN.

### Gate 5 — Supervised retrieval/reranking

1. Tạo weak positives từ Q&A pages thuộc official corpus.
2. Dùng same-chapter/same-language hard negatives thay vì negatives quá dễ ở chương khác.
3. Fine-tune dual encoder hoặc reranker open-weight dưới 15B; checkpoint mới phải private/local.
4. Chỉ build full secondary Qwen3-Embedding-4B index nếu candidate-pool ablation đạt gate ở mục 6.6.

## 9. Retest queue cho corpus hiện tại

| Thử nghiệm cũ                | Quyết định             | Cách chạy lại                                                                                                  |
| ---------------------------- | ---------------------- | -------------------------------------------------------------------------------------------------------------- |
| Exp03/04/20 — BM25/FTS       | P0 — chạy lại          | Corpus chính thức, analyzer tiếng Việt đúng; lần cũ bị nhiễu bởi corpus 4,4M, corpus thiếu hoặc FTS OR-unigram |
| Exp24/38 — reranker          | P0/P1 — chạy lại       | Sau khi sửa multi-chunk, context và candidate pool                                                             |
| Exp16–19 — RRF/fusion        | P1 — chạy lại          | Chỉ sau khi dense và sparse có candidate độc lập                                                               |
| Exp22/23 — top-k             | P1 — chạy lại          | So `50/75/100` và adaptive-k trên cùng ranking mới                                                             |
| Exp34 — threshold 0,70       | Diễn giải lại          | Không lặp dense threshold tuyệt đối; calibrate theo score domain hoặc percentile/margin                        |
| Exp06/11 — query translation | Chạy lại có điều kiện  | Bản dịch phải tham gia retrieval riêng rồi union                                                               |
| Exp07–10 — chunk/window      | P1 — chạy lại          | Chỉ sau khi evaluator LCS và document branch đã ổn định                                                        |
| Exp25–32 — tăng corpus       | Không lặp nguyên trạng | Thay bằng clean rebuild, exact ID coverage và delta-index có đối chứng                                         |

Mỗi submission chỉ thay một nhánh. Khi test document retrieval, giữ nguyên chunks của champion; khi test chunking/reranking, giữ nguyên docs. Đọc `DOCS_F2` và `CHUNKS_F2` riêng thay vì chỉ nhìn Final Score.

## 10. Ràng buộc cuộc thi

- Chỉ dùng model open-weight, mỗi model không quá 15B và phát hành trước 01/08/2026.
- Không dùng GPT, Gemini, Claude hoặc closed-source API trong hệ thống submission chính thức.
- External data phải có nguồn, giấy phép phù hợp và quy trình tái lập.
- `doc_id` phải thuộc danh sách BTC và là integer.
- `chunk_text` phải là substring nguyên văn của tài liệu nguồn; không dịch, viết lại hoặc sinh mới.
- Public tối đa 10 submissions/ngày; private tối đa 5 submissions tổng cộng.

## 11. Nguồn nghiên cứu kỹ thuật

- [ViBioMIR dataset card](https://huggingface.co/datasets/AIGuruTinix/ViBioMIR/blob/main/README.md)
- [BGE-M3 paper](https://arxiv.org/abs/2402.03216)
- [Qwen3-Embedding-0.6B model card](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B)
- [Qwen3-Embedding-4B model card](https://huggingface.co/Qwen/Qwen3-Embedding-4B)
- [Qwen3 Embedding technical report](https://arxiv.org/abs/2506.05176)
- [Qwen3-Reranker-4B model card](https://huggingface.co/Qwen/Qwen3-Reranker-4B)
- [MedCPT Query Encoder model card](https://huggingface.co/ncbi/MedCPT-Query-Encoder)
- [ColBERTv2 paper](https://arxiv.org/abs/2112.01488)
- [SPLADE v2 paper](https://arxiv.org/abs/2109.10086)
- [WHO ICD-10 browser](https://icd.who.int/browse10/2019/en?lang=en)
- [WHO ICD-10 downloads](https://icdcdn.who.int/icd10/index.html)
- [Cục Quản lý Khám, chữa bệnh — triển khai Thông tư 06/2026/TT-BYT](https://kcb.vn/tin-tuc/cong-van-so-4059-byt-bh-trien-khai-thong-tu-06-2026-tt-byt-quy-dinh-ma-hoa-benh-tat-theo-icd-10.html)
- [Multiple health terminologies for medical IR](https://pmc.ncbi.nlm.nih.gov/articles/PMC4341235/)
- [Semantic expansion evaluation](https://pubmed.ncbi.nlm.nih.gov/31837099/)
- [Hierarchical knowledge association — EMNLP 2021](https://aclanthology.org/2021.emnlp-main.285/)
- [Retrieve-and-rerank for ICD coding — NAACL 2024](https://aclanthology.org/2024.naacl-long.273/)
- [MedCodER — NAACL Industry 2025](https://aclanthology.org/2025.naacl-industry.37.pdf)

## 12. Definition of done cho index sạch

Trước khi tạo submission mới, index phải thỏa toàn bộ điều kiện:

- `set(index_doc_ids) ⊆ set(official_doc_ids)`.
- Số dense rows = số sparse rows = số chunk metadata rows = FAISS `ntotal`.
- `chunk_ids.npy` khớp theo thứ tự với FAISS và metadata.
- Mọi `(doc_id, start, end)` trích được đúng substring nguyên văn từ source text.
- Không có duplicate `chunk_id`.
- Có manifest ghi hash của official URL list, từng source artifact, model, tokenizer và config build.
- Query cache mang fingerprint của index và config; cache cũ không được tái sử dụng âm thầm.

## 13. Kế hoạch ngày 19/10/2026 — hướng tới Final ≥ 0,38

### 13.1 Mục tiêu và bằng chứng để chọn hướng

Mục tiêu vận hành là tạo bước thay đổi đủ lớn ở evidence coverage và document precision trong ngày. `0,38` là tiêu chí thành công, không phải điểm có thể bảo đảm trước khi BTC chấm. Không extrapolate mức tăng `0,0002` của Exp73 thành một chuỗi tăng chắc chắn.

Điều chỉnh theo xác nhận mới của người dùng: **không thử ZIP ≥100 MB, không có nhánh xin hỗ trợ upload qua email**. Mốc đầu tiên là BTC chấm Final >`0,3764`; sau đó mở pha model embedding thứ hai. Trước gate dùng BGE/index hiện có, ưu tiên ra submission sớm thay vì xây toàn bộ pool 777.600 pairs trước phép thử đầu.

Audit trực tiếp `submission_exp73_chunks_add_second_ce_gt2p5.json` trên 1.200 queries:

- Tổng 107.648 chunks; trung bình `89,707` chunks/query, min/max `67/100`.
- Tổng 106.546 cặp query/document có chunk; trung bình `88,788` documents/query, tương đương khoảng 41,1% số 216 docs xuất ra.
- Có 152.655 cặp query/selected-document chưa có chunk; trung bình `127,213`/query. Đây là candidates để tìm evidence, không phải 152.655 nhãn dương bị bỏ lỡ.
- Chỉ 1.102 chunks vượt quá một chunk/document; gộp trùng document đơn thuần không thể giải phóng phần lớn ngân sách.
- Tổng 263.007.029 ký tự chunk; mean/median `2.443/2.501`, max `7.999`. ZIP đã `99.553.194` bytes, chỉ còn `446.806` bytes dưới 100 MB.
- Có đúng một cặp query/chunk-document nằm ngoài `relevant_docs` của cùng query. Đặc tả chấm hai danh sách độc lập; không tự xóa evidence này chỉ để ép subset. Khi dựng nhánh mới, ghi rõ membership và giữ bản champion để đối chứng.

Từ source và manifest: Exp71 rerank ranks 151–300, giữ top-150, `max_length=384`; cache được Exp72/73 dùng chỉ cung cấp evidence trong các vùng đã chấm. Các cache này chưa đủ để chọn evidence tốt nhất trên toàn bộ 216 selected documents, đặc biệt ở head.

### 13.2 Đọc đúng metric và loại các giả định cũ

Nguồn quyết định là [đặc tả evaluation BTC](competition_information/2_evaluation.md), [submission](competition_information/3_submission_instructions.md), [rules](competition_information/5_policy_and_rules.md) và [ghi chép buổi họp](btc_meeting_insights_and_roadmap.md).

1. Overlap là `LCS_tokens(c,g)/len(g)`, threshold `0,4`; precision chia cho số chunks, không chia cho số tokens. Nếu thay từng chunk bằng một span chứa nguyên chunk cũ, cùng số chunks và doc IDs, và token sequence sau normalization vẫn chứa sequence cũ, overlap với mỗi nhãn không giảm. Theo công thức đã công bố, cả Chunk P/R/F2 không giảm trong điều kiện đó. Phải kiểm tra token boundaries, không suy rộng điều này sang thay chunk, gộp chunks hoặc giảm output count.
2. Exp48 thay cả độ dài lẫn top-count từ khoảng 98 xuống 64, nên regression không chứng minh mở rộng span có hại. Exp63 chủ yếu gộp các spans đã có, chưa phải phép thử mở rộng evidence ở mọi document.
3. Không nộp toàn bộ tài liệu tùy tiện. Chọn paragraph/section liên quan và trích một span liên tục từ source. Output không chèn context giả, dịch hoặc nối các đoạn rời thành một chunk.
4. Ghi chép buổi họp từng suy đoán mỗi query chỉ có 5–15 tài liệu đúng và threshold 0,73 không mất recall; đó không phải ground truth. Exp55 và sweep k đã bác bỏ việc dùng giả định này làm chính sách đầu ra chung.
5. Local scorer hiện sai metric; giữ trạng thái deferred theo quyết định trước của người dùng. Chỉ dùng kiểm tra schema/span/cache và dữ liệu tổng hợp để kiểm tra invariants; điểm chất lượng vẫn lấy từ BTC.

### 13.3 P0 — Chuẩn bị evidence trên toàn bộ selected documents

Làm tối thiểu đủ tạo candidate đầu; phần chấm rộng hơn chạy nối tiếp, không phụ thuộc embedding bổ sung:

1. Khóa Exp74 làm control, lưu hashes JSON/ZIP, query cache, source text và index; chunk axis vẫn là Exp73. Audit membership/evidence phải đối chiếu lại với Docs Exp74 vì tail đã đổi. Ghi nhận slot đã dùng thực tế trong ngày; không mặc định số slot còn lại chỉ từ việc đổi ngày.
2. Với mỗi trong 216 selected docs/query, tạo candidate spans từ toàn bộ source text: paragraph/sentence windows giữ offsets; chọn tối đa 3 vùng khác nhau bằng local lexical score, vector chunks đã có và lead fallback. Không chỉ lấy những chunk từng lọt dense top-k toàn corpus. Tách câu Trung theo dấu câu kể cả khi không có khoảng trắng.
3. Audit độ phủ của indexed spans trên full text, tỷ lệ text bị cắt, boilerplate và truncation theo VI/EN/ZH. Khả năng crawl/index bỏ nội dung chưa được chứng minh chỉ bằng số lượng docs.
4. Chấm evidence BGE trên cửa sổ vừa context; tránh để tokenizer chỉ đọc 384 tokens đầu một span dài rồi coi đó là score cho toàn span. Nếu tăng context lên 768/1.024, benchmark trước; ghi rõ query token budget và tỷ lệ passage bị truncate. Output có thể là paragraph/envelope rộng hơn cửa sổ chấm, nhưng vẫn có offsets nguồn.
5. Cache theo `(query_hash, doc_id, source_hash, start, end, model_revision, prompt_hash, max_length)`. Không dùng score cũ khi query/length/prompt thay đổi, không dùng raw score của hai cấu hình như cùng thang điểm.

Quy mô lý thuyết `1.200 × 216 × 3 = 777.600` pairs không phải đầu việc bắt buộc. Candidate đầu tái dùng cache hợp lệ và chấm một window cho docs thiếu evidence có document rank cao; giới hạn khoảng 60 docs mới/query ở vòng đầu (≤72.000 pairs mới). Chỉ mở rộng sau khi đo ETA và nhận tín hiệu BTC. Chạy pilot 2.000 pairs phân tầng ngôn ngữ/độ dài trước batch lớn. Không tái dùng score sai context chỉ để giảm thời gian.

Máy hiện tại có RTX 3050 Ti Laptop 4 GB. Trong 60 phút đầu sau khi triển khai phải có pilot và ETA. Nếu dự kiến một batch chiếm hơn 3 giờ, giảm số windows bằng preselection; giữ cache/resume và dành GPU cho một job tại một thời điểm. Đây là giới hạn vận hành đề xuất, không phải thời gian inference đã đo.

### 13.4 P1 — Thí nghiệm đầu tiên: evidence phủ nhiều documents hơn

**Kết quả Exp75: loại nhánh coverage 120/140/180.** Coverage 140 đạt Final `0,2585`; Docs F2/P/R giữ nguyên `0,3574/0,1813/0,6086`, nhưng Chunks F2/P/R rơi xuống `0,1596/0,1079/0,2293`. So với Exp74, Chunk F2 mất `0,1272`. Thí nghiệm đã thay/rút `70.369` spans cũ và thêm `60.758` spans mới nên không cô lập được hai nguyên nhân, nhưng regression đủ lớn để không dùng slot cho coverage 120 hoặc 180. Baseline tiếp tục là Exp74; mọi thử nghiệm sau phải giữ chunks Exp74 value-by-value khi tối ưu Docs.

**Triển khai Exp75 ngày 19/10:** script `scripts/generate_exp75_evidence_coverage.py`; pool 259.224 cặp từ 163.699 source docs, đã chấm đủ 72.000 windows (60 docs/query). Window output tối đa 1.500 ký tự; window chấm khoảng 500 ký tự quanh vùng lexical tốt và tuân thủ context 384 tokens thực tế. Pilot 2.000 pairs đạt 53,13 pairs/giây; phần còn lại mất 953,34 giây. CE cache mới có fingerprint query/source/span/model revision; không dùng lại raw scores của spans cũ. Loại khỏi selection 41 scoring passages whitespace-only. Xem [nhật ký Exp75](experiments_log/exp75_document_evidence_coverage.md).

**File nộp khuyến nghị:** `submission_exp75_coverage140.zip`, 85.320.918 bytes. Đạt 167.304 chunks / 139,42 chunk-documents/query, thêm 60.758 cặp evidence, giữ đủ 106.546 cặp query/document cũ nhưng thay/rút 70.369 spans. Validator độc lập pass trên toàn bộ chunks, Docs giữ nguyên Exp74, 33/33 tests pass. Coverage 120 là bản dự phòng (73.223.459 bytes); bản target 180 chỉ đạt 148,754 documents/query do cap candidates (91.304.847 bytes), không coi là đã thử đủ 180. Chờ điểm BTC của coverage 140 trước khi chọn nhánh tiếp theo; chưa cập nhật champion từ 0,3221.

- Chuẩn bị offline các mức 120/140/180 để đo kích thước và số docs thực sự thêm được; chọn 140 làm phép thử BTC đầu nếu vừa ngân sách.
- Output span khởi điểm khoảng 1.400–1.600 ký tự, theo ranh giới câu/đoạn và không cắt đôi evidence chính. Đây là thông số khởi điểm để đo byte-size, không phải độ dài đã tối ưu. Ký tự không tương đương tokens giữa VI/EN/ZH.
- Dành ngân sách cho nhiều document khác nhau; không lấy lại top-N chunk toàn cục khiến vài doc chiếm hết chỗ. Xếp hạng kết hợp document rank và evidence rank; cache model có thể tái sử dụng chỉ khi đúng fingerprint.
- Nhắm ZIP ≤95.000.000 bytes, kiểm tra kích thước nén thực tế. Giảm target trước khi cắt span đến mức mất câu trả lời; không suy dung lượng ZIP từ số ký tự bằng một hệ số cố định.
- Báo cáo intersection với chunk-documents Exp73, số documents thêm/mất và số spans được giữ/mở rộng/thay. Đây là thay đổi thiết kế đầu ra gồm coverage và độ dài, nên nếu thắng chỉ kết luận policy mới tốt hơn; không quy toàn bộ gain cho riêng top-k.

**Exp76: document head rerank, chunks rollback chính xác về Exp74.** Chấm tối đa ba lexical spans/document cho ranks 51–150 bằng cùng revision BGE; ghép scores rank 151–300 đã có, khóa top-50 Exp74, blend CE/stage rank `0,75/0,25`, xuất 216 docs và giới hạn tối đa 10/20/30 membership swaps/query. Tạo ba cap offline nhưng chỉ nộp một bản sau khi audit churn; đây là docs-only ablation. Không dùng coverage-120 làm Exp76 vì Exp75 giảm cả chunk precision lẫn recall với biên quá lớn.

**Triển khai Exp76:** đã chấm đủ `242.019` passages cho `120.000` head query/doc pairs; ghép `180.000` tail documents và build cap 10/20/30. Churn tự nhiên mean/median/max `11,64/11/33`; cap 30 chỉ bind 1 query, cap 20 bind 49, cap 10 bind 677. Nộp cap 30 trước: ZIP `99.551.214` bytes, chunks bằng Exp74, SHA-256 `b7dd4262cbbaaca0da6776134bf3d13eec8fa9b400b183ffb02188bbdaafee68`. Exp81 combo Docs cap-30 + chunks Exp78 đã chuẩn bị nhưng chỉ nộp nếu Exp76 tăng Docs F2; cutoff 175/200 cũng là conditional artifacts, không dùng slot trước kết quả.

**Kết quả Exp76 cap 30:** Final `0,3225`, Docs F2/P/R `0,3581/0,1816/0,6092`, tăng `+0,0007/+0,0003/+0,0006` so với Exp74; chunks control giữ nguyên. Nộp Exp81 kết hợp Docs Exp76 và chunks Exp78. Vì gain Docs chưa đạt gate `+0,005`, không tiêu slots cuối cho cutoff 175/200; dùng cap20/cap10 để đo mức churn rồi ghép chunk Exp78 với cap Docs tốt nhất.

**Kết quả Exp81/84/85/87:** Exp81 ghép Docs cap30 với chunks Exp78, tái hiện đúng Docs F2 `0,3581` và Chunks F2 `0,2870`, Final `0,3225`. Exp84 cap20 docs-only tăng Docs F2/P/R lên `0,3582/0,1817/0,6097`. Exp85 cap10 tiếp tục tăng rất nhẹ lên `0,3583/0,1818/0,6098`, Final `0,3226`. Exp87 ghép Docs Exp85 với chunks Exp78 và tái hiện chính xác hai axis: Docs F2 `0,3583`, Chunks F2 `0,2870`, Final `0,3226`; đây là champion tổng mới. Sweep cap 30 → 20 → 10 và ladder chunk CE đều đã bão hòa, nên không dùng thêm slot cho cap lân cận hoặc threshold nội suy. Chuyển sang candidate/signal mới: BM25 rescue có rerank, ICD soft có nhãn đáng tin, hoặc reranker/model thứ hai theo gate và audit bên dưới.

**Triển khai Exp88:** lấy 50 multilingual BM25 candidates/query nhưng loại chính xác dense pool rank 1–300, chấm 60.000 documents / 100.727 passages bằng cùng BGE revision, bảo vệ top-50 và giữ chunks Exp87 bất biến. Natural rerank đề xuất trung bình 21,59 lexical entrants/query, quá mạnh so với bằng chứng Exp55; bản nộp đầu tiên dùng cap3 với 3.592 replacements (`2,9933`/query). ZIP `99.629.531` bytes, SHA-256 `def521f683196240d22a87521141cc10c4ce2a9e9f1749b92c3d7b495f443a11`, đã pass CRC/schema/official-ID/top50/chunk invariants. Cap5 và cap10 chỉ dùng nếu cap3 tăng Docs F2; nếu cap3 hòa hoặc giảm, dừng ladder BM25 và không rebuild index lexical trước khi có signal mới.

**Kết quả Exp88:** Final `0,3221`; Docs F2/P/R `0,3572/0,1809/0,6095`; Chunks F2/P/R giữ đúng control `0,2870/0,2396/0,3688`. So với Exp87, Docs F2 giảm `0,0011` và Final giảm `0,0005`. Dừng cap5/cap10, không rebuild BM25 full cho cùng policy. Champion vẫn là Exp87 `0,3226`. Bước tiếp theo phải thay đổi scorer hoặc representation thay vì mở rộng thêm lexical-only candidates với BGE hiện tại.

**Triển khai Exp89:** đã tạo Kaggle input 300.000 rows cho dense ranks 51–300, đúng 250 docs/query, một BGE-preselected passage/document. Parquet `184.617.902` bytes, SHA-256 `4101aa0a741326240724793fdb95176ccdf3e7d94e9504e0514fee6194f47872`; 101 empty cached passages được fallback bằng lexical source span. Notebook `11_qwen3_reranker_exp89_kaggle.ipynb` pin Qwen3-Reranker-0.6B revision `e61197ed45024b0ed8a2d74b80b4d909f1255473`, chạy T4×2 có checkpoint/resume và chỉ xuất scores. Local builder giữ top-50/chunks Exp87 và tạo cap3/5/10 sau khi xác thực score manifest. Dataset Kaggle bắt buộc Private.

**Exp77–79:** giữ Exp74 và thêm tối đa một scoring passage/query từ selected doc chưa có evidence. Exp77 CE `>5,5`, 116 additions đạt Final `0,3221`, Chunks F2/P/R `0,2869/0,2399/0,3687`. Exp78 CE `>4,5`, 282 additions tăng lên Final `0,3222`, Chunks F2/P/R `0,2870/0,2396/0,3688`. Exp79 CE `>3,5`, 490 additions hòa Exp78 về Final/F2, recall lên `0,3690` nhưng precision xuống `0,2393`. Ladder đã bão hòa; không nộp Exp80 `>2,5`. Giữ Exp78 làm chunk variant ưu tiên và dành slots còn lại cho Exp76 document rerank.

Các ngưỡng `0,005` ở đây là quy tắc ưu tiên tài nguyên, không phải mức tăng được đảm bảo hoặc kiểm định ý nghĩa thống kê.

### 13.5 P2 — Span trong ngân sách ZIP cố định

**Ứng viên tùy chọn sau coverage:** giữ số chunks/doc IDs của chunk policy tốt nhất, mở một tập spans tới paragraph/section chứa evidence trong phần byte-budget còn trống; trần đề xuất 4.000 ký tự, chunk cũ dài hơn giữ nguyên. Không cắt top-count như Exp48. Kiểm tra span mới chứa span cũ, sau normalization vẫn giữ chuỗi tokens cũ và không tạo duplicates. Nếu budget không cho phép thay đổi có ý nghĩa thì bỏ qua, chuyển thẳng sang document rerank.

Nhánh này có thể tăng coverage trong cùng doc mà không tăng denominator. Chỉ nộp nếu thay đổi đủ rộng để có giá trị học hỏi, ví dụ ≥10% chunks được mở rộng ít nhất 20% độ dài; nếu không thì bỏ qua slot, không tiêu một submission chỉ vì thay vài KB.

Giới hạn cứng là ZIP `<100.000.000` bytes; builder nhắm `≤95.000.000` bytes và đo thực tế sau nén. Không chuẩn bị/nộp artifact lớn hơn giới hạn hoặc phụ thuộc BTC hỗ trợ. Ghi chép họp về email đã lỗi thời theo xác nhận người dùng; chỉ giữ làm lịch sử. Dùng ZIP Deflate tương thích portal. Không tăng độ dài đồng loạt rồi hy vọng nén đủ.

Không vì mở rộng span mà loại các chunks khác: làm vậy mất tính chất không giảm overlap ở mục 13.2 và trở thành một ablation khác.

### 13.6 P3 — Qwen reranker và secondary embedding chạy song song

Nguồn nghiên cứu kiểm tra ngày 19/10: [BGE reranker model card](https://huggingface.co/BAAI/bge-reranker-v2-m3), [Qwen3-Reranker-0.6B](https://huggingface.co/Qwen/Qwen3-Reranker-0.6B), [Qwen3-Reranker-4B](https://huggingface.co/Qwen/Qwen3-Reranker-4B), [Qwen công bố ngày 05/06/2025](https://qwenlm.github.io/blog/qwen3-embedding/). Qwen rerankers hỗ trợ đa ngữ/instruction, 0.6B và 4B đều dưới giới hạn 15B và thuộc dòng phát hành trước cutoff. Lưu revision checkpoint, license và nguồn trước khi chạy. Benchmark công bố trên pool Qwen không bảo đảm chuyển thành mức tăng R2AI.

**Quyết định cũ hoãn Qwen tới sau baseline đã được thay thế sau Exp88 và theo phê duyệt của người dùng ngày 20/10.** Exp89 dùng cùng dense candidate pool rank 51–300, passage/output count và chunks để đo riêng scorer `Qwen3-Reranker-0.6B`; chạy trên Kaggle T4×2 bằng prompt/scoring `yes/no` chính thức, không bê raw threshold BGE sang Qwen. Model pin revision, instruction, max length và input hash. Secondary embedding ở mục 6.6 chạy song song, độc lập với điểm Exp89; kết quả retrieval Qwen vẫn phải ablate thuần và fusion bảo thủ trước khi thay membership champion.

**Exp89 inference đã hoàn tất:** 300.000 scores hợp lệ. Qwen natural ranking muốn thay trung bình 45,41 documents/query nên phải giữ cap bảo thủ. Đã build cap3/cap5/cap10, tất cả giữ top-50 và chunks Exp87; cap3 thay đúng 3 docs/query và là submission ưu tiên. ZIP cap3 `99.628.991` bytes, dưới giới hạn decimal 100 MB nhưng sát trần; không thêm payload nào vào ZIP.

**Kết quả Exp89 cap3:** Final `0,3221`, Docs F2/P/R `0,3572/0,1813/0,6075`, Chunks F2 `0,2870`. So với Exp87, Final `-0,0005`, Docs F2 `-0,0011`, Docs Recall `-0,0023`; chunk axis giữ nguyên đúng thiết kế. Dừng cap5/cap10 và không chạy 4B trên cùng passage/membership policy. Không suy rằng Qwen embedding full-corpus sẽ thất bại: Exp89 chỉ kiểm tra reranking một passage do BGE preselect trong candidate pool cũ.

**Phép thử chính sau coverage: document rerank pool 1–300, top-216 bằng BGE hiện có.** Dùng scores P0 để mở vùng head từng bị khóa top-150; bảo vệ top-50, giới hạn tối đa 30 membership swaps/query so với Exp73; blend CE/stage rank 0,75/0,25 là điểm khởi đầu. Chấm bổ sung candidates thiếu evidence theo ETA; chunks giữ nguyên chunk champion. Nếu pool 300 quá chậm, pilot trên pool 216 trước và ghi rõ phạm vi; không giả lập scores. Đây là thay đổi ranking, không đổi model.

**Cutoff 175 có điều kiện trên ranking mới**, chỉ khi document rerank tăng Docs F2 ≥`0,005`. Cutoff 216 từng tối ưu cho ranking cũ, không nhất thiết tối ưu sau rerank. Giữ chunks/ranking, chỉ đổi count. Nếu Docs F2 giảm, quay về champion; không suy cutoff tối ưu từ macro P/R đối thủ.

### 13.7 P4 — BM25/ICD là nhánh bổ sung có đối chứng

**BM25 VI tạo candidates mới, rerank bằng cùng BGE scorer với dense candidates.** Lấy top-500 BM25, loại trùng official IDs, preselect/chấm tối đa 50 candidates mới/query; cho tối đa 20 replacements trong tail của document champion, giữ output count/chunks. Không fusion RRF trực tiếp nhiều language branches như Exp55. Chỉ chạy khi đủ throughput và candidate audit; nếu không có thay đổi đáng kể thì không tiêu slot.

**ICD soft routing là ứng viên cho một slot tùy chọn, không bắt buộc hôm nay.** Giữ candidate pool, scorer và count cố định; boost nhỏ trên high-confidence top-3 chapter/block, `UNKNOWN` không đổi. Giới hạn churn tối đa 10 docs/query, không hard filter. Cần có document labels đáng tin trên candidate pool; route query đơn thuần chưa đủ. Nếu thiếu labels hoặc không đo được tác động độc lập, ưu tiên slot cho nhánh evidence đã có tín hiệu.

### 13.8 Embedding bổ sung và phân bổ tối đa 10 slots

Exp87 là champion hiện tại `0,3226`, với Docs F2 `0,3583` và Chunks F2 `0,2870`. Exp75 coverage 140 đạt `0,2585` và bị loại; các sweep BGE cap10–30 và chunk CE-additions đã bão hòa. Thứ tự tiếp theo phải ưu tiên thay đổi candidate/signal đủ lớn để rút ngắn khoảng cách tới baseline, không tiếp tục nội suy các tham số quanh Exp87.

Phân bổ khi còn đủ 10 public slots ngày 19/10:

1. Evidence coverage 140 (Exp75): đã thất bại, dừng nhánh.
2. Document head rerank bằng BGE, giữ chunk champion (Exp76).
3. Chỉ sau kết quả Exp76 mới chọn BM25 candidate rescue hoặc reranker/model thứ hai.
4. Kết hợp hai axes tốt nhất ngay khi có kết quả để thử vượt baseline sớm, không đợi dùng hết ngày.
5. Cutoff trên ranking mới, chỉ nếu ranking thắng.
6. Span expansion chọn lọc trong ≤95 MB; bỏ qua nếu không có dung lượng.
7. BM25 candidate rescue, sau audit/pilot.
8. Follow-up nhánh thắng hoặc ICD đủ labels; khi đã vượt baseline có thể chuyển slot này sang candidate-pool model thứ hai sau pilot.
9. Dự phòng embedding merge: rerun nguyên winning policy trên index mới để đo riêng corpus delta.
10. Dự phòng kết hợp document champion và chunk champion thành final candidate.

Đây là ngân sách trần, không phải yêu cầu dùng hết. Slot có điều kiện không đạt gate được chuyển cho nhánh khả thi đã có tín hiệu, không chạy cho đủ số. Nếu ngày đã dùng slot thì giảm số thử nghiệm tùy chọn trước, ưu tiên giữ slot cho merge và final candidate. Vòng private vẫn chỉ 5 lần tổng cộng theo luật, không áp dụng kế hoạch 10 slots này cho private.

Artifact BGE bổ sung mới đến lúc nào thì kiểm tra/merge lúc đó ở bản staging: official IDs, ID–URL mapping, vector dimensions, sparse/dense/metadata alignment, overlap với active index và text hash. Qwen secondary index không đổi registry embedded/unembedded vì nó chỉ re-embed đúng 1.724.798 chunks đã có; builder phải giữ riêng model/revision/prompt/hash và dùng active `chunks_metadata/text`. Không trộn Qwen vectors vào FAISS BGE.

Sau merge, invalidation caches theo fingerprint index; rerun retrieval/rerank với cùng policy thắng. Chỉ tái dùng CE score khi query, text, span, model và prompt thực sự không đổi. Recovery ngày 19/10 từng nâng hàng đợi BGE lên 7.046 rows; hai ZIP đầu bổ sung 5.340 docs. Sau sửa filter notebook, `1k_urls.zip` bổ sung thêm 1.146 docs / 1.156 chunks; embedded/index cùng 1.212.421 docs, unembedded còn 560 rows (190 PubMed quá ngắn, 370 VOV challenge). Exp74 refresh tail trên index này và đạt Final 0,3221; chưa refresh head/chunks. Giá trị điểm phụ thuộc relevance, không dự báo gain từ số lượng. Dùng snapshot index mới để rerun candidate retrieval; không chỉ nối cache/chunk IDs cũ rồi giả định pool vẫn đầy đủ.

Kết hợp hai axis tốt nhất được phép theo hai danh sách chấm độc lập trong đặc tả; lưu provenance và audit trước nộp. Điểm suy từ hai F2 riêng chỉ là dự kiến cho cùng tập query/phiên bản scorer; kết quả chính thức vẫn phải được BTC chấm.

### 13.9 Trình tự triển khai, mốc dừng và bàn giao

- **0–1 giờ kể từ bắt đầu triển khai:** khóa champion, audit spans/text/token truncation; benchmark 2.000 pairs; dựng cache evidence và báo ETA, khả năng vừa ZIP. Ưu tiên BGE đã có local.
- **Pha đầu:** dừng Exp89 cap ladder; tiếp tục Qwen secondary embedding trên Kaggle và chuẩn bị ablation retrieval độc lập sau khi đủ shards. Embedding là background compute, không giữ slot BTC và không chặn nhánh submission hiện hành.
- **Giữa ngày:** dành tối đa ba phép thử đầu cho evidence. Nếu Chunk F2 chưa tăng ít nhất `0,01` sau ba policy khác biệt, dừng count/window sweep; chuyển sang lỗi extraction/truncation, model hoặc document head. Không coi mức `+0,0002` là bằng chứng đủ để tiếp tục cả ngày.
- **Pha sau:** kết hợp axes tốt nhất ngay khi có kết quả, ưu tiên vượt baseline; cutoff/BM25/ICD chỉ khi đủ gate. Nếu inference chậm, giữ checkpoint/cache. Khi Qwen 0.6B hoàn tất, đo Qwen-only retrieval rồi RRF/union bảo thủ với BGE; không thay champion trực tiếp. 4B tiếp tục staged hoặc candidate-only dựa trên ETA và delta 0.6B.
- **Cuối ngày:** nhận embedding nếu có, rerun winning policy, kết hợp axes tốt nhất. Ghi score thật, delta từng axis và cấu hình tiếp tục/loại; nếu chưa đạt 0,38 thì ghi rõ khoảng cách và nút thắt còn lại, không báo thành công bằng dự báo.

Deliverables khi triển khai: evidence pool có offsets/provenance; score cache có fingerprint/resume; builder coverage/span-budget; báo cáo audit theo ngôn ngữ; manifest và JSON/ZIP mỗi experiment; cập nhật nhật ký sau từng điểm BTC. Tái sử dụng loaders/scoring từ `generate_exp67_fresh_crossencoder.py`, `generate_exp71_multichunk_pool300.py` và source-span logic từ `generate_best_submission.py`; builder mới cần hỗ trợ toàn bộ selected docs, không chỉ cache tail của `generate_exp72_chunk_ce_additions.py`.

Mỗi artifact phải đủ 1.200 query IDs duy nhất, integer official doc IDs, spans nguyên văn, không duplicate `(doc_id, chunk_text)`, và ZIP chỉ một JSON ở root. Kiểm tra axis bất biến đúng theo thiết kế, byte size thực, CRC, payload và SHA-256. Các kiểm tra này không thay thế điểm BTC. Không dùng closed-source model để tạo query/evidence trong pipeline nộp; không truy cập hoặc suy đoán nhãn ẩn từ từng query qua leaderboard. Chỉ dùng kết quả tổng hợp để so sánh các policy đã xác định trước.

## 14. Long-envelope breakthrough sau Exp114

### 14.1 Bằng chứng và mục tiêu định lượng

Exp114 đạt Final `0,3229`, Docs F2/P/R `0,3586/0,1816/0,6114` và Chunks F2/P/R `0,2873/0,2389/0,3696`. Nếu Docs F2 giữ nguyên, cần Chunks F2 ít nhất `0,4014` để Final vượt `0,38`; add-one theo threshold không thể tạo mức tăng này.

Dòng tham chiếu `0,4071` có Docs P/R `0,2317/0,5706` và Chunks P/R `0,2286/0,5725`, gần như trùng nhau. Đây không chứng minh pipeline đối thủ, nhưng phù hợp mạnh với chính sách một passage rộng cho mỗi document đúng: passage bao phủ hầu hết reference chunks trong document nên chunk confusion gần document confusion.

Theo luật BTC, overlap là `LCS(c,g)/|g|`, không chia cho độ dài dự đoán `c`. Vì vậy, một parent envelope nguyên văn chứa chunk cũ không thể làm mất overlap của chunk đó; nếu nhiều chunks cùng document được gộp, denominator precision còn giảm. Exp47 đã xác nhận merge 7.000 ký tự tăng đồng thời precision và recall, nhưng pipeline hiện tại chỉ tạo envelope trung bình khoảng 2.484 ký tự và gần như không mở context.

### 14.2 Ladder đã triển khai

Ba artifact giữ nguyên documents Exp114 và tái phân bổ cùng ngân sách văn bản/ZIP:

1. **Exp115:** mở unique docs của 20 chunks đầu thành parent gần-full-source, giữ prefix 75; `74,44` chunks/query, ZIP `97.356.130` bytes. Đây là phép thử đầu tiên vì đủ cường độ để đo giả thuyết.
2. **Exp116:** head10 / keep83; `82,03` chunks/query, ZIP `98.116.251` bytes. Chỉ nộp nếu Exp115 cho tín hiệu context dương nhưng tail pruning quá mạnh.
3. **Exp117:** head5 / keep87; `85,38` chunks/query, ZIP `98.132.844` bytes. Dùng làm ablation bảo thủ nếu cần tách hai hiệu ứng.

Mỗi parent là substring nguyên văn, chứa tất cả chunks cũ của cùng query-document, tối đa mục tiêu 32.000 ký tự; nếu envelope chứa các anchors đã rộng hơn thì giữ đủ envelope. Không dùng passage sinh lại, không thay doc IDs và không vượt giới hạn portal.

### 14.3 Quy tắc quyết định

- Exp115 đã nộp: Final `0,3204`, Chunk F2/P/R `0,2822/0,2608/0,3492`. So với Exp114, precision tăng `0,0219` nhưng recall giảm `0,0204`; parent context có tín hiệu đúng, còn cắt tail là sai.
- Hủy Exp116/117: cả hai vẫn trộn parent expansion với giảm coverage nên không trả lời được câu hỏi mới và khó tạo bước nhảy.
- Không nộp Exp118–120 one-parent top40/45/50 dù đã build hợp lệ. Chúng lặp lại rủi ro Exp48/Exp75: giảm tập query-document evidence, trong khi hai thí nghiệm cũ đã cho thấy recall/F2 sụp mạnh.
- Không tuyên bố đạt `0,38` trước điểm BTC. Mỗi artifact đột phá vẫn phải qua điểm chính thức.

### 14.4 Exp121 — full-parent nhưng giữ nguyên evidence coverage

Follow-up chính dùng một parent nguyên văn cho **mọi** `(query, doc_id)` đã có evidence trong Exp114. Parent chứa toàn bộ chunks cũ của cặp đó; tập document output và tập chunk-document per query giữ nguyên tuyệt đối. Chỉ gộp trung bình khoảng một duplicate chunk/query, không bỏ tail document nào.

Theo metric công khai, policy này có tính đơn điệu đối với overlap của từng chunk cũ: nếu chunk cũ đạt LCS threshold với một reference chunk thì parent chứa chunk cũ cũng đạt; mọi reference đã tìm thấy vẫn được tìm thấy nếu các anchors đều được giữ. Parent gần-full-source có thể tìm thêm reference chunks ở vị trí chưa từng retrieve. Tuy nhiên, gộp nhiều predictions thay đổi cách đếm tử/mẫu số precision, nên không có bảo đảm tổng quát precision hoặc F2 sẽ tăng; phải kiểm tra bằng score BTC.

Payload tăng từ `263,68M` lên khoảng `451M` ký tự nên Deflate không vừa portal. Dùng ZIP method 14 (LZMA), vẫn là container ZIP chuẩn, một `submission.json` ở root và phải CRC-pass bằng Python `zipfile`. Tài liệu cuộc thi chỉ yêu cầu ZIP, không quy định method nén; tuy nhiên portal compatibility chưa được đảm bảo cho tới khi upload được chấp nhận. Nếu file ≥100.000.000 bytes thì không upload; cắt tối đa 32 ký tự context dư ở mỗi mép nhưng không được chạm anchor cũ.

Gate nộp: ZIP `<100.000.000`, 1.200 query IDs, docs giống Exp114, chunk-document sets giống Exp114, mọi parent là source substring và chứa tất cả old chunks cùng query-doc. Nếu portal từ chối compression method thì quay về Deflate và phân bổ parent theo benefit/byte; trạng thái có tiêu slot hay không theo portal. Nếu Chunk F2 không tăng, cần phân tích riêng precision/recall và audit normalization/anchors, không kết luận scorer sai chỉ từ F2. Chỉ gửi câu hỏi kỹ thuật BTC khi có trường hợp tái lập mâu thuẫn với đặc tả.

**Kết quả Exp121:** Final `0,3412`; Chunk F2/P/R `0,3238/0,2668/0,4174`, tăng lần lượt `+0,0365/+0,0279/+0,0478` so với Exp114; document axis giữ nguyên. Giả thuyết full-parent được xác nhận mạnh. Khoảng cách tới `0,38` còn `0,0388`; nếu Docs F2 giữ `0,3586`, Chunk F2 cần đạt ít nhất `0,4014`.

### 14.5 Exp122 — append full-parent cho missing selected docs

Giữ nguyên toàn bộ Exp121 rồi thêm một full-source parent cho selected documents đầu tiên theo document rank chưa có chunk evidence ở mỗi query. Bản add25 gồm 30.000 additions / 113,72M ký tự nhưng ZIP đạt `104.319.110` bytes nên bị loại và xóa. Mức hợp lệ lớn nhất là **add19**: 22.800 additions, 86,78M ký tự, ZIP `99.361.586` bytes. Đây là append-only nên mọi hit Exp121 được bảo toàn; additions nhắm trực tiếp khoảng trống giữa Docs Recall `0,6114` và Chunks Recall `0,4174`.

Nộp Exp122 add19. Nếu Chunk F2 tăng, dùng kết quả P/R để chọn follow-up: recall tăng đủ nhưng precision giảm thì giảm xuống add10–15; cả precision và recall cùng tăng thì giữ add19 và cải thiện cách chọn additions bằng CE/Qwen consensus trong cùng count. Nếu F2 giảm, giữ Exp121 và chuyển từ document-rank additions sang CE-gated additions; tuyệt đối không thay hoặc cắt các parent Exp121.

**Kết quả Exp122:** Final `0,3516`; Docs F2 giữ `0,3586`; Chunk F2/P/R đạt `0,3446/0,2512/0,4682`, lần lượt `+0,0208/-0,0156/+0,0508` so với Exp121. Đây là tín hiệu rõ rằng bổ sung full parents cho selected docs chưa có evidence hiệu quả, dù precision giảm nhẹ. Còn `0,0284` tới mốc Final `0,38`; với Docs F2 giữ nguyên, Chunk F2 cần vượt `0,4014` để Final vượt `0,38`.

### 14.6 Exp123–124 — xếp hạng CE và mở rộng có kiểm soát

Để tách chất lượng lựa chọn khỏi số lượng additions, Exp123 giữ đúng 19 additions/query như Exp122 nhưng chọn missing selected docs theo cached BGE cross-encoder (mean khoảng 50 candidates/query). Artifact đã tạo: `submission_exp123_exp121_add19_ce_ranked_parents.zip`, `98.423.366` bytes. Đây là phép so sánh ưu tiên tiếp theo với Exp122; nộp trước vì cùng count, nên score sẽ kiểm tra trực tiếp ranking policy.

Exp124 mở rộng cùng CE policy lên 21 additions/query. ZIP là `99.995.774` bytes, chỉ `4.226` bytes dưới decimal 100 MB; giữ làm phương án sau, không ưu tiên upload do biên an toàn quá nhỏ. Cả hai append đầy đủ lên Exp121, không thay parent cũ. Chỉ chọn Exp124 nếu portal xác nhận nhận file và còn slot sau khi đọc Exp123; nếu không, tạo mức add20 an toàn hơn từ cùng builder.

Quy tắc tiếp tục: nếu Exp123 cải thiện Chunk F2 so với Exp122, dùng CE ranking và điều chỉnh count theo đường cong precision/recall; nếu kém hơn, quay lại document-rank và thử CE–document-rank consensus. Mỗi vòng chỉ đổi một biến. Mục tiêu `0,38` chưa đạt cho tới khi BTC trả score chính thức; không suy ra score từ CE hoặc số additions.

## 15. Kiến trúc sau Exp125 — ưu tiên hiểu query, candidate recall và bằng chứng đầy đủ

**Cập nhật 21/10/2026. Mục này thay thế các next-step cũ tại 13 và 14.6.** Exp122 vẫn là champion: Final `0,3516`, Docs F2 `0,3586`, Chunks F2 `0,3446`. Exp123 đạt `0,3501/0,3586/0,3417`; Exp125 đạt `0,3513/0,3579/0,3446`. Exp125 giữ chunks bất biến nhưng giảm Docs Precision/Recall/F2 nhẹ, nên dừng policy query-view RRF cụ thể này. Pilot gồm 50 dòng đầu trong ZIP: 48 parsed views được dùng (30 `ok`, 18 `needs_review`), 2 lỗi parse fallback về control; chỉ 48/1.200 query thay đổi. Kết quả không cô lập chất lượng query rewriting khỏi chất lượng view và giới hạn pilot. Exp124 add21 tiếp tục tạm dừng. Chưa xác minh leaderboard hiện tại; thứ hạng do người dùng báo không thay đổi tiêu chí chọn thí nghiệm.

Mục tiêu là `Docs F2 + Chunks F2 > 0,7600`, không phải tiếp tục tăng count hoặc trọng số từng chút. Nếu docs giữ nguyên, chunks phải vượt `0,4014`; nếu chunks giữ nguyên, docs phải vượt `0,4154`. Một mốc thiết kế cân bằng như docs `0,385` và chunks `0,380` cho Final `0,3825`, **không phải dự báo gain**. Không tính F2 từ macro precision/recall: BTC tính F2 từng query rồi mới lấy trung bình.

### 15.1 Bằng chứng mới từ dữ liệu và mã nguồn

Audit tái lập bằng `python scripts/audit_query_architecture.py`, kết quả tại `data/audits/query_architecture_post_exp123.json`. Đây là thống kê đầu vào và candidate, không phải relevance labels.

1. **Query thực sự không đồng nhất.** 1.200 query duy nhất; độ dài theo đơn vị tách whitespace: min 5, median 18, P95 84, max 281. Có 129 câu ≤10, 666 câu 11–30, 336 câu 31–80 và 69 câu >80. Regex tìm thấy 522 câu có từ xưng hô/gia đình, 419 câu có dấu hiệu lời chào/lịch sự, 35 câu có “bầu”, 91 câu có từ liên quan thai kỳ, 521 câu có số. Các nhóm chồng lấn; regex chỉ là gợi ý phân tầng, không phải classifier đã kiểm chứng. Từ “không” trong câu hỏi không nhất thiết là phủ định lâm sàng.
2. **Bản dịch có lỗi làm đổi nghĩa hoặc mất câu hỏi.** ID 42: “vùng háng” thành `armpit` trong EN và `肩部` (vai) trong ZH. ID 71: đi vệ sinh trong ngữ cảnh đại tiện thành `frequent urination`, đồng thời thay đổi mốc thời gian. ID 219 EN dừng ở `making`, mất các ý phía sau; ID 271 EN dừng ở `sne`. File đủ 1.200 IDs, không rỗng và query gốc khớp hoàn toàn, nên chỉ kiểm tra ID/non-empty không phát hiện được lỗi. Script `translate_queries_en.py` có default `max_new_tokens=96`; đây là cơ chế đáng nghi, chưa có provenance để khẳng định mọi bản dịch hiện tại đều sinh bằng cấu hình đó.
3. **Reranker nhìn thiếu ngữ cảnh.** `generate_exp75_evidence_coverage.py::score_window` cắt query ở 128 tokens và chọn một cửa sổ lexical ≤500 ký tự, tổng pair ≤384 tokens. Audit tokenizer hiện tại cho 21 query VI và 9 query ZH vượt 128 tokens: đây là số có nguy cơ bị cắt ở nhánh tương ứng, chưa phải số lỗi relevance. 72.000 CE passages có median 455 ký tự và 41 passages chỉ whitespace. Audit xác nhận không có additions Exp123 nào được chọn từ 41 passages rỗng này, nên không quy regression Exp123 cho lỗi đó. Vẫn phải loại các scores rỗng trước khi tái dùng; kiểm tra fingerprint phải bao gồm nội dung, không chỉ số rows.
4. **Exp123 không phải phép thử CE thuần trên cùng pool.** Trung bình `4,4792/19` additions Exp122 nằm ngoài cache CE của Exp75; hai policy chỉ trùng `11,3342/19` additions. CE trên một passage nhỏ cũng không đo trực tiếp utility của full source. Không thể quy toàn bộ regression cho chất lượng BGE hoặc kết luận tăng model size sẽ sửa được.
5. **Qwen chưa được dùng để quyết định toàn bộ tập docs.** `generate_exp110_qwen_rrf_w035.py` đóng băng 150/216 docs; manifest cho thấy trung bình chỉ thay 7,82 docs/query so với Exp106. Trong cache retrieval, Qwen VI top216 có trung bình 119,79 docs ngoài Exp122; EN 172,00; ZH 180,84. Đây là diversity, không phải số docs đúng bị bỏ sót. Cần kiểm tra bằng candidate union và scorer thống nhất thay vì tiếp tục giữ cố định phần lớn output.
6. **Cache có thể che khuất thí nghiệm query.** Một số loader query hiện kiểm tra IDs/order mà không so query-text hash (ví dụ `generate_best_submission.py::load_dense_queries`). Rewriting vẫn giữ IDs; nếu tái dùng đường dẫn cache cũ thì có thể đang tìm kiếm bằng query cũ. Mỗi view mới phải tạo fingerprint riêng, gồm source query, transformed text, tokenizer/model revision, instruction và max length.

### 15.2 Kiến trúc đích và nguyên tắc thiết kế

Pipeline mới: **query gốc → biểu diễn có cấu trúc và các view có kiểm chứng → retrieval đa nhánh → union theo official doc_id → chọn nhiều passages/document → rerank chọn lọc → chọn docs và full parents theo budget ZIP**. Giữ hai BGE/Qwen indexes hiện có; query transformation chỉ cần encode lại queries. Chỉ xây index mới khi pilot chứng minh document representation đang thiếu, không mặc định re-embed toàn corpus lần nữa.

Lưu từng stage thành artifact tái lập: `query_views.parquet`, `candidate_pool.parquet`, `document_passages.parquet`, `rerank_scores.parquet`, `run_manifest.json`. Mỗi candidate lưu query/view/family/language, doc_id, raw score, rank, source span và text hash. Điểm các model không cùng thang đo; không cộng raw cosine/BM25/logit trực tiếp.

Điểm docs dựa trên **tập IDs**, không dựa thứ tự. Rerank chỉ hoán vị cùng 216 docs sẽ không làm Docs F2 thay đổi. Nhánh thử rerank phải có candidates ngoài tập cũ và thực sự thay đổi membership hoặc cardinality; báo số docs thay đổi trước khi tiêu slot. Thử count sau khi chất lượng ranking đã có tín hiệu, không tune count trên ranking đứng yên.

### 15.3 P0 — sửa biểu diễn query và dịch thuật trước

LLM tạo JSON có schema gồm `intent`, `patient_groups`, `symptoms`, `anatomy`, `conditions_explicit`, `medications`, `measurements`, `time_course`, `negated_findings`, `uncertainties`, `facets`, `canonical_vi`, `aliases`, `translation_en`, `translation_zh`. Entities nên có source offsets hoặc source quotes kiểm chứng được. Tách thông tin bệnh đã được nêu với điều người hỏi đang nghi ngờ; không suy thành chẩn đoán mới.

Các ràng buộc phải bảo toàn: ai là người bệnh, tuổi/giới nếu được nói rõ, thai kỳ/tuần thai, triệu chứng/vị trí, thuốc/liều, con số/đơn vị, thời gian, phủ định và loại câu hỏi. Ví dụ ID 219 có trẻ em, người hỏi và chồng: không gộp thành một bệnh nhân. Lỗi chính tả không chắc nghĩa phải giữ token gốc cùng giả thuyết, không sửa âm thầm. Kiểm tra số theo dạng chuẩn hóa, tránh báo lỗi chỉ vì dấu phẩy/thập phân hoặc dịch chữ số.

Không ghi đè `query_translated.parquet` hiện tại. Tạo version mới, lưu model revision, prompt hash, generation settings, input/output tokens, finish reason và validation flags. Output đạt token limit hoặc JSON chưa đóng phải retry với budget lớn hơn; sau tối đa hai lần lỗi thì fallback view gốc và ghi lỗi. Việc có dấu chấm cuối câu không chứng minh bản dịch đầy đủ. Dịch trực tiếp từ query gốc kết hợp schema đã xác thực; không chỉ dịch bản tóm tắt có thể đã mất ý.

**Thí nghiệm đại từ:** so raw, bỏ đúng lời chào/lịch sự, canonical giữ thông tin người bệnh. Không dùng stopword list xóa toàn bộ “em/cháu/con/mẹ”, vì “trẻ em”, “con em 2 tháng” và “mẹ đang cho con bú” mang thông tin. Đo `cos(q_raw,q_view)` riêng trong BGE và Qwen; trên cùng một tập docs đo `sim(q_view,d)-sim(q_raw,d)`, overlap@100/216, rank displacement và docs mới. Cosine giữa hai queries chỉ đo mức biến đổi biểu diễn; cosine cao/thấp không chứng minh retrieval tốt/xấu. Relevance cần đánh giá độc lập hoặc BTC.

**Thí nghiệm từ đời sống:** “bầu” giữ ở view gốc, thêm “mang thai/phụ nữ mang thai” có điều kiện ngữ cảnh; bảo toàn tuần thai. Không thay “ăn bầu” thành thai kỳ, không coi thuật ngữ gần nghĩa là tương đương tuyệt đối. Mỗi query tối đa 1 canonical view + 1 alias view ban đầu; câu đã ngắn và rõ chuyên môn có thể không cần rewrite. Các ví dụ trong tài liệu này chỉ để giải thích thiết kế; artifacts nộp phải do pipeline model hợp lệ sinh, không dùng trợ lý đóng để viết lại test queries rồi đưa vào inference.

**Gate chất lượng:** pilot 120 query chọn theo seed và phân tầng độ dài/lời đời sống/số/đa ý, có bộ ca lỗi 42/71/219/271 để regression-check. Những ca này không dùng làm nhãn relevance. Không chấp nhận rewrite còn lỗi entity/số/phủ định đã phát hiện; validator fail thì fallback thay vì cố dùng. Review ngữ nghĩa ít nhất 40 mẫu pilot; chưa có nhãn BTC thì không báo Recall@k thật từ mẫu này.

### 15.4 P1 — retrieval nhiều view, không để bản dịch hoặc view lặp lấn át

Cho query gốc và canonical đi qua BGE dense+sparse, Qwen dense, BM25 document. Bản dịch EN/ZH đã qua validation tạo nhánh riêng. Khởi đầu lấy top300 docs/nhánh, union giữ toàn bộ 216 docs champion và tối đa khoảng 1.200 docs/query sau dedup; đây là budget khởi tạo cần benchmark, không phải cutoff đã tối ưu. Đếm candidate mới theo view/ngôn ngữ/topic. Nếu query có nhiều facets, bảo lưu candidates cho từng facet trước khi pruner cắt chung.

Fusion hai tầng: hợp nhất raw/canonical/alias trong từng retrieval family, rồi mới hợp nhất BGE/Qwen/BM25. Chuẩn hóa tổng đóng góp của mỗi family để thêm ba paraphrases không tự động thành ba phiếu. Không bỏ mọi docs cũ trước khi pool/scorer mới được kiểm tra; nhưng thí nghiệm kiến trúc cho phép scorer thay cả head khi bằng chứng đủ, thay vì đóng băng 150 docs vĩnh viễn. Giữ raw branch làm fallback cho queries có view lỗi.

BM25 dùng title/lead/body và phân tích VI/EN/ZH; kiểm tra truncation body 16.000 ký tự trong builder hiện có và tokenization trước khi quy lỗi cho BM25. ICD dùng nhãn nhiều chủ đề/UNKNOWN như một feature mềm; không hard filter toàn corpus bằng một chapter. Thai kỳ + thuốc + nội tiết có thể cần nhiều chương. Không tái dùng ngưỡng `0,73` từ buổi họp cho model/score khác khi chưa biết cách BTC tạo điểm.

**Ablation chủ đạo:** cùng scorer, count và chunks Exp122, so candidate union từ queries cũ với union từ views mới. Sau đó mới đổi reranker. Không chỉ xuất docs đứng đầu raw cosine trong một language branch để kết luận model đó kém.

### 15.5 P2 — rerank ở cấp document với nhiều passages và compute có chọn lọc

Mỗi document có title/lead và tối đa 3 passages từ các vị trí khác nhau, chọn bằng lexical+dense/facet coverage, không chỉ đoạn đầu hoặc một cửa sổ 500 ký tự. Passages giữ offsets vào source. Context ngắn lấy đầy đủ; context dài chọn theo từng facet. Query long dùng canonical đã kiểm chứng cùng các ràng buộc, không cắt mù ở token 128.

Tầng rẻ: BGE CE chấm khoảng 300 docs/query × tối đa 3 passages = tối đa 1,08 triệu pairs. Cache theo query-text/source-span/model/prompt; title hoặc passage thay đổi thì score cũ vô hiệu. Aggregator khởi đầu dùng max passage score + tín hiệu coverage facets để tránh một đoạn tốt bị trung bình với đoạn không liên quan. So với top2 aggregation ở cùng pool; kiểm tra document dài có lợi thế chỉ vì nhiều cửa sổ. Không coi sigmoid logit là xác suất relevance đã được hiệu chuẩn.

Tầng đắt chỉ gọi cho trường hợp nhánh retrieval bất đồng, gần biên chọn/loại, query có nhiều bệnh nhân/facets hoặc coverage thiếu. Pilot cap 20% query × 30 docs × 2 passages = 14.400 pairs; không rerank toàn bộ triệu pairs bằng model 14B. Ưu tiên Qwen3-Reranker-4B chuyên dụng cho pair scoring; Qwen3-14B dùng query understanding hoặc adjudication các ca khó. Một generator 14B không tự động tốt hơn reranker 4B. Benchmark phiên bản nhỏ trên cùng inputs trước.

Nếu dùng LLM listwise, nhóm khoảng 8–12 docs với các passages đã chọn; đầu ra là candidate IDs và nhãn relevance có evidence refs, không tạo IDs mới. Kiểm tra độ nhạy thứ tự bằng một lần đảo nhóm trên pilot. Không trộn các score ordinal từ nhiều batch như xác suất chuẩn. Đối chiếu với CE cùng pool, giữ count 216 và chunk output cố định ở phép thử docs đầu tiên. Sau khi docs thắng mới kiểm tra lại count/adaptive-k.

### 15.6 P3 — HyDE/Query2doc, HyPE và multihop là ba hướng khác nhau

**HyDE:** sinh một hypothetical passage ngắn cho retrieval, encode nó và tìm tài liệu thật. **Query2doc:** dùng pseudo-document để mở rộng query, có thể dùng cả sparse và dense. Hai hướng có cơ sở nghiên cứu, nhưng có nguy cơ tự điền diagnosis/thuốc không có trong câu hỏi; thử dưới dạng nhánh bổ sung có trọng số giới hạn, luôn giữ raw branch. Nội dung giả định chỉ là khóa tìm kiếm, tuyệt đối không đưa vào `chunk_text`. Với Qwen, dùng preprocessing đúng model và version rõ cách encode text giả định; không giả định kết quả HyDE gốc trên Contriever sẽ chuyển nguyên sang Qwen. [HyDE](https://arxiv.org/abs/2212.10496), [Query2doc](https://arxiv.org/abs/2303.07678).

**HyPE/doc2query:** sinh câu hỏi mà document có thể trả lời ở giai đoạn indexing, tạo index phụ ánh xạ về doc_id/source span. Khác với rewrite query tại runtime. Chỉ pilot trên sample corpus có phân tầng (ví dụ 20.000 docs, tối đa hai câu hỏi/doc), đo chi phí và lỗi trước; không sinh cho toàn corpus ngay. Sinh câu hỏi từ nội dung nguồn, không lấy official test query làm nhãn huấn luyện; model sinh phải hợp lệ BTC. Index phụ không thay thế vectors hiện tại. [HyPE](https://arxiv.org/abs/2607.29402).

**Decomposition trước multihop:** câu có ba câu hỏi độc lập cần ba subqueries; chưa chắc cần suy luận nhiều bước. True multihop chỉ bật khi một facet còn thiếu sau hop1: lấy entity/quan hệ có trích dẫn trong tài liệu thật, tạo tối đa hai truy vấn tiếp và chạy thêm một hop. Recheck kết quả hop2 với intent/ràng buộc query gốc; dừng nếu không có evidence mới hoặc bắt đầu đổi chủ đề. Tránh biến triệu chứng thành diagnosis phỏng đoán rồi retrieval theo diagnosis đó. Lưu provenance `query → source doc/span → bridge entity → hop2 doc`; không cần lưu suy luận tự do dài. [IRCoT](https://arxiv.org/abs/2212.10509) là cơ sở phương pháp, không phải bằng chứng hiệu quả trên ViBioMIR.

### 15.7 P4 — document selection và full-parent coverage dưới 100 MB

Exp121/122 cho thấy output evidence là nút thắt riêng, không thể giải quyết chỉ bằng embedding. Hiện Exp121 còn trung bình 128,10 selected docs/query chưa có evidence. Một document đúng nhưng thiếu parent không giúp chunk recall; cải thiện docs phải được kiểm tra xem có chuyển thành evidence hay không. Docs recall và chunk recall có denominator khác nhau, không trừ hai macro recalls để đếm số evidence thiếu.

Bước rẻ đầu tiên: tối ưu **lossless serialization/compression** của champion. Có thể thử nhóm queries có nhiều docs chung và thứ tự chunks để tăng tái dùng LZMA dictionary, giữ chính xác mapping query → docs/chunk strings. Audit semantic hash theo ID và multisets, integer IDs, exact Unicode text; chỉ đổi bytes/container thì không cần slot BTC mới. Không dùng JSON references, schema lạ hoặc nội dung sinh thay source. Kích thước ZIP là thực đo, không suy từ tổng số ký tự.

Nếu có thêm budget, thử mở rộng full-parent theo document rank hiện thắng, giữ nguyên parents champion. Kiến trúc tiếp theo phân bổ budget theo predicted relevance, facet coverage, source length và marginal compressed bytes, với quota tối thiểu per query để câu ngắn không chiếm hết budget. Không ưu tiên doc ngắn chỉ vì rẻ. Fit surrogate bytes từ pilot rồi kiểm tra nén thật với cap nội bộ ≤99.000.000 bytes cho artifacts mới; Exp122 đã được BTC nhận vẫn giữ nguyên làm control. Không tăng full-parent count bằng cách cắt mất evidence cũ như Exp75.

LCS trong đặc tả chia cho độ dài reference, nên mở rộng một chunk chứa nguyên chunk cũ bảo toàn overlap của chunk đó. Điều này không đảm bảo toàn bộ precision/F2 luôn tăng khi thêm docs hoặc gộp nhiều predictions; phải dùng BTC xác nhận. Bộ đóng gói cần báo cả số source docs mới, số parents, độ dài, coverage anchors và bytes để phân biệt gain retrieval với gain context.

### 15.8 LLM Kaggle và API qua Cloudflare

**Model ưu tiên cho query transformation: `Qwen/Qwen3-14B`, tổng 14,8B**, không phải 13,2B non-embedding. Qwen công bố dòng này ngày 29/04/2025; phù hợp giới hạn ≤15B/model và cutoff trước 01/08/2026 trong luật lưu tại repo. Dùng official weights, pin commit revision trước khi chạy. `enable_thinking=False` cho tác vụ schema/translation; lưu sampling settings/seed và cache outputs để tái lập. So trên pilot với Qwen3-8B để biết 14B có đáng chi phí. [Model card](https://huggingface.co/Qwen/Qwen3-14B), [release](https://qwenlm.github.io/blog/qwen3/).

Trên T4 16 GB, khởi đầu Transformers + bitsandbytes NF4 4-bit, compute FP16, context 4.096 rồi kiểm tra 8.192 nếu đủ VRAM, batch 1–2. 14,8B × 4-bit là khoảng 7,4 GB **chỉ phần weight lý tưởng**; scales, non-quantized tensors, activations, KV cache và runtime làm thực tế cao hơn. Không hứa model/context sẽ vừa trước benchmark. Hai T4 không tự thành một GPU 32 GB: nếu một replica vừa GPU thì có thể dùng hai workers chia query IDs; nếu không thì model sharding và đo lại tốc độ. Không mặc định tensor-parallel hoặc FlashAttention chạy tốt trên mọi Kaggle GPU. [Quantization reference](https://huggingface.co/docs/transformers/quantization/bitsandbytes).

Notebook `notebooks/13_query_architecture_llm_kaggle.ipynb` đã được tạo: kiểm tra GPU/runtime; pinned dependencies/model; load NF4; pilot mặc định 120 query; checkpoint/resume; validator quote/schema; endpoint cá nhân; Cloudflare Tunnel; artifacts-only ZIP. Trước full run phải in input/output tokens/s, median/P95 latency, max VRAM, schema failure rate và ETA tính từ thực đo. Dùng tiến độ theo **rows đã lưu**, heartbeat từng worker, last-success/last-error; quá timeout thì trả lỗi có thể retry, không để `0/18 shards` im lặng hàng giờ. Không đưa model cache vào ZIP export.

Notebook hiện expose `/health`, `/v1/models`, `/v1/query-views`, `/v1/chat/completions`; hai route inference yêu cầu bearer `LLM_API_KEY`, giới hạn 12 request/phút, tuần tự hóa inference và tự dừng sau 2 giờ. Batch JSONL chạy cùng lúc trên một GPU nên cạnh tranh lock/inference với API; nên ưu tiên dùng endpoint sau khi pilot/batch đã xong. Public hostname không đồng nghĩa anonymous access. Không gửi toàn corpus qua API: query transformation chỉ gửi queries; selective rerank chỉ gửi passages cần chấm. Batch JSONL là đường dự phòng khi notebook/tunnel ngắt.

`CF_TOKEN` trong Kaggle Secrets phải chứa **Cloudflare Tunnel token** của named remotely-managed tunnel, không phải Cloudflare management API token. Notebook đọc bằng `UserSecretsClient().get_secret('CF_TOKEN')`, ghi tạm token vào file mode `0600` để chạy `cloudflared --token-file`, rồi xóa file khi tunnel dừng; token không được in hoặc đưa vào ZIP. Trước khi chạy, owner phải tạo tunnel/hostname route tới `http://localhost:8000`, đặt `CF_TOKEN` và một `LLM_API_KEY` ngẫu nhiên dài ít nhất 32 ký tự trong Kaggle Secrets, sửa `PUBLIC_API_BASE_URL`, và chỉ lưu API key tương ứng ở máy local. `CF_TOKEN` chỉ xác thực connector, không tự bảo vệ người gọi endpoint và không tự tạo hostname. [Cloudflare permissions](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/remote-tunnel-permissions/), [run parameters](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/run-parameters/), [Kaggle Secrets API](https://github.com/Kaggle/docker-python/blob/main/patches/kaggle_secrets.py).

Người dùng yêu cầu dùng endpoint dù hostname công khai, với phạm vi chỉ cá nhân sử dụng. Kaggle AUP nêu “server farming” là ví dụ lạm dụng tài nguyên; API tạm thời, xác thực, giới hạn request và tự tắt sau 2 giờ là biện pháp giảm phạm vi/rủi ro, **không đảm bảo** cách dùng này được Kaggle cho phép. Không chia sẻ URL/key, không chạy liên tục, dừng thủ công ngay khi xong; nếu Kaggle báo vi phạm/chặn endpoint thì chuyển sang batch. [Kaggle AUP](https://www.kaggle.com/aup). Về BTC, HTTP API tự host open-weight model không đồng nghĩa closed-source LLM API; tất cả weights, revision và generated artifacts phải truy vết được.

### 15.9 Thứ tự triển khai và thử nghiệm có khả năng phân biệt giả thuyết

Không build hàng loạt submissions chỉ khác cap. Các mã dưới đây là **nhánh kế hoạch**, chưa phải artifacts hay Exp IDs đã chạy:

1. **A — kiểm chứng dịch và rewrite:** dựng notebook/client/schema/cache; chạy pilot 120; đối chiếu 40 mẫu ngữ nghĩa; benchmark 14B so 8B và ước lượng full 1.200. Chạy similarity/rank diagnostics cho ba view raw/clean/canonical trên cùng index. Sửa cache invalidation và blank-passage validation trước khi reuse. Chưa dùng slot BTC cho bước này.
2. **B — repair translation only:** regenerate EN/ZH hợp lệ bằng open model; chạy cùng candidate recipe, scorer, output count và chunk axis Exp122, chỉ đổi bản dịch/query cache. Nộp một phép thử docs khi membership thực sự đổi; nếu không đổi, đo ở retrieval và bỏ slot no-op. Không dùng mã của bài cũ để ghi đè kết quả.
3. **C — canonical+alias retrieval:** từ control B đã khóa, bổ sung VI views và union theo family; reranker/count/evidence giữ cố định. Nếu B giảm điểm, control quay về Exp122 trước khi đánh giá C. Đây là phép thử cho ngôn ngữ đời sống và câu dài, không trộn HyDE cùng lúc.
4. **D — multi-passage document scorer:** cùng candidate pool của control C, thay single-window CE bằng multi-passage; count/chunks cố định. Đo cả selection churn và language/facet distribution. Nếu tốt mới cho tầng reranker đắt can thiệp các ca bất đồng.
5. **E — evidence trên docs/ranking đã thắng:** dùng full parents theo budget, preserve anchors và fingerprint source. Nộp riêng chunk axis để kiểm tra gain docs có chuyển thành chunk recall. Kết hợp axes thắng trong artifact đã validate.
6. **F — HyDE hoặc Query2doc:** chọn một nhánh, dùng gate query ambiguity/coverage và budget variants cố định; chạy cùng pipeline đã thắng. Không cộng hết transformations trong một submission vì sẽ không biết phần nào tạo gain/lỗi.
7. **G — selective multihop hoặc HyPE pilot:** ưu tiên multihop nếu diagnostics cho thấy nhiều facets thiếu evidence; ưu tiên HyPE nếu candidate recall bị khoảng cách query/document style và pilot corpus đủ cơ sở. Chưa re-embed corpus lớn hoặc fine-tune chỉ từ các điểm aggregate trên leaderboard.

Ưu tiên thực thi **A → B/C → D → E**; F/G là nhánh sau, không phải việc phải xong trước khi có submission mới. Thời gian phụ thuộc pilot: query transformation khoảng vài nghìn outputs; CE có thể đến 1,08M pairs nên phải benchmark 2.000 pairs trước. ETA = số tokens/pairs còn lại chia throughput thực đo, cộng tải model/retry/packaging; không hứa hoàn thành một giờ trước khi có số liệu.

**Tiêu chí tiến/thoái:** correctness gate (schema, preserving constraints, source provenance, cache hashes) phải qua; output thật sự khác control; chỉ BTC mới xác nhận gain chính thức. Một improvement ≥0,005 Final hoặc ≥0,01 ở axis mục tiêu là tín hiệu đáng ưu tiên compute tiếp, không phải ngưỡng significance thống kê. Gain nhỏ vẫn ghi nhận nếu thật nhưng không làm lý do sweep cả ngày. Hai thử nghiệm kiến trúc cùng nhánh không có tín hiệu thì quay lại diagnostics/candidate ceiling; không chạy thêm năm cap gần nhau. Không có per-query labels thì không thể tính significance hoặc official oracle recall; các proxy chỉ giúp loại lỗi rõ ràng.

Tối đa 10 public submissions/ngày và 5 tổng lượt private theo luật repo; số slot còn lại phải lấy từ tình trạng thực tế, không mặc định còn đủ. Mỗi submit giữ manifest control/treatment, axes bất biến, provenance models và diff counts. Không gửi bài tự động bằng browser; user tiếp tục nộp ZIP.

### 15.10 Các giới hạn tuân thủ và deliverables

Luật đã đọc: `competition_information/1_overview.md`, `2_evaluation.md`, `3_submission_instructions.md`, `4_data.md`, `5_policy_and_rules.md`. Mỗi model ≤15B **total**; base phát hành trước 01/08/2026; fine-tune sau cutoff giữ private/local. Không dùng closed-source API để sinh queries, synthetic training examples, judging scores hoặc evidence cho pipeline chính thức. Query expansion/hypothetical text chỉ phục vụ retrieval; evidence nộp phải trích nguyên văn corpus và giữ official doc_id. Nguồn dữ liệu ngoài phục vụ train/eval cần provenance/license; nhãn dương output vẫn chỉ thuộc official corpus. Không dùng leaderboard để dò nhãn từng query.

Đã hoàn tất: ghi kết quả Exp123, dừng đề xuất Exp124, audit query/candidate/cache và lưu JSON; tạo generator `scripts/create_query_architecture_kaggle_notebook.py` và notebook `notebooks/13_query_architecture_llm_kaggle.ipynb`. Notebook mặc định pilot 120; chưa chạy trên Kaggle GPU, chưa chạy LLM transformations, chưa đo cosine sau rewrite, chưa build hoặc nộp submission kiến trúc mới. Cần người dùng cấu hình Kaggle secrets/Cloudflare hostname trước khi chạy; có thể tắt tunnel bằng `ENABLE_CLOUDFLARE_TUNNEL = False` nếu chỉ muốn tạo artifacts batch. Các module tiếp theo: `src/query_processing/` (schema/validators/views), `src/llm/` (client/cache), candidate-union builder và multi-passage scorer dùng indexes hiện có. Bộ smoke/regression tests cần kiểm tra mất số/phủ định/patient group, stale cache, token-limit retry, invalid IDs/offsets và API resume; không kiểm thử bằng cách khẳng định relevance từ score của chính model.

Research nền bổ sung: [Query rewriting — EMNLP 2023](https://aclanthology.org/2023.emnlp-main.322/) hỗ trợ giả thuyết tối ưu cách diễn đạt; [AutoMIR](https://arxiv.org/abs/2410.20050) nghiên cứu HyDE cho medical retrieval; [RankZephyr](https://arxiv.org/abs/2312.02724) cho thấy open-model listwise reranking là một hướng khả thi; [Qwen3-Reranker-4B](https://huggingface.co/Qwen/Qwen3-Reranker-4B) cung cấp mô hình chuyên dụng để benchmark. Những nguồn này định hướng thiết kế, không chứng minh gain hoặc tính tương đương benchmark với cuộc thi.

### 15.11 Tín hiệu leaderboard cần theo dõi (22/10/2026)

Người dùng báo cáo leaderboard có một đội đang dẫn đầu với điểm ước lượng khoảng `0,76` (không nhớ chính xác do đội đã ẩn điểm). Theo trí nhớ của người dùng, Docs/Chunks Precision khoảng `0,99` và Docs/Chunks Recall khoảng `0,65`; đây là thông tin nghe/nhớ lại, **chưa xác minh độc lập**, không coi là kết quả chính thức hay target metric chính xác. Với công thức F2 trong thể lệ, P=`0,99`, R=`0,65` tương ứng F2 xấp xỉ `0,698`, nên các con số trên có thể bị nhớ thiếu/sai hoặc không cùng bộ chỉ số. Khi có screenshot hoặc số chính thức, cập nhật ở đây kèm ngày và phân biệt rõ precision/recall theo từng axis. Tín hiệu hiện tại gợi ý đáng kiểm tra chiến lược output chọn lọc, nhưng không đủ để suy ra cách làm của đối thủ; mọi candidate vẫn phải tối ưu và được chấm theo macro-F2 BTC.

### 15.12 Mentor Day 2: pipeline tham khảo từ BTC (22/10/2026)

Slide `docs/_AI_Guru__R2AI_Stage3_MentorDay_Oct_22th.pdf` mô tả một **pipeline ví dụ/khuyến nghị**, không xác nhận đây là cấu hình baseline hoặc hệ thống bí mật đang chấm:

- Query VI gốc + bản dịch sát nghĩa EN/ZH; giữ nguyên thuật ngữ và trạng thái bệnh, dùng câu gốc cho dense scoring/reranking.
- Stage document: BM25 lexical đa ngôn ngữ lấy khoảng 2.000 candidates → multilingual dense rerank trên shortlist còn khoảng 400; bắt đầu với title/headings/lead, encode theo phần với văn bản dài/đa chủ đề.
- Stage passage: khoảng 8 passages/doc cho 400 docs (xấp xỉ 3.200) → lexical/vector prescore → giữ/rerank khoảng 400 passage; dùng multilingual reranker và cập nhật document rank từ passage scores, trả passage nguyên văn với parent `doc_id`.
- Hướng nâng cao gồm glossary-augmented translation, retrieved bilingual examples, late chunking và late interaction; đây là đề xuất nghiên cứu, chưa phải kết quả được chứng minh trên điểm BTC.

Đối chiếu hiện trạng: Exp122 xuất 216 docs/query và trung bình khoảng 108 chunks/query (130.108 total), chủ yếu full-parent spans; Exp121 trước additions có 107.308 chunks tổng. Exp55 pure BM25/ICD thất bại nghiêm trọng; Exp88 BM25-only rescue làm giảm Docs F2 `0,0011`, nên không thay thế dense ranking bằng BM25 thuần. Tuy vậy, đây **không** phải phép thử mentor recipe: ta chưa dùng BM25 làm candidate generator rồi dense-rerank cùng một shortlist, cũng chưa làm passage selection/reranking 400 candidates/query. Exp125/126 chỉ đổi docs cho tối đa 48/30 queries, giữ nguyên chunks, nên không kiểm tra kiến trúc này.

Ưu tiên kế tiếp sau ladder chunk đang chờ điểm: (1) kiểm kê BM25 cache/version và dense rank/cache có thể tái sử dụng; (2) dựng offline candidate-recall/overlap proxy trên các giao điểm BM25, BGE-M3 và Qwen; (3) một ablation bounded: dịch VI→EN/ZH đã có + BM25 top-2k → dense rerank cùng shortlist → candidate docs, giữ rõ số docs đầu ra theo format BTC; (4) chỉ khi tín hiệu docs đủ tốt, thử chọn passage từ top docs bằng source-grounded passage scoring. Dùng cache BM25 hiện có (`data/indices/bm25_document/bm25_candidates.parquet`) và score/candidate cache đã audit; tránh rebuild toàn corpus nếu chưa chứng minh candidate coverage. Không suy ra rằng “400” là giới hạn đầu ra chính thức; slide đang nói số passage giữ lại trong pipeline ví dụ.

**Cập nhật ưu tiên tối nay:** bỏ qua thêm các sweep nhỏ 5/10/15 additions trong khi Kaggle Exp130 đang chạy; ba ZIP đó chỉ là fallback nếu notebook/input/runtime bị nghẽn hoặc còn slot sau khi có kết quả kiến trúc. Không tiêu submission slot trước khi có full 1.200-query artifact.

Rủi ro tuân thủ: slide nêu LLM reranker như một khả năng, nhưng luật competition hiện có cấm closed-source API trong pipeline nộp chính thức. Chỉ dùng model hợp lệ theo cutoff/size và dữ liệu/evidence nguyên văn từ corpus; không dùng slide để biện minh cho API bị cấm.

### 15.13 Kaggle deep-architecture run tối nay: Exp130

Đã chuyển từ plan sang bộ chạy Kaggle đầu tiên:

- Notebook: `notebooks/14_bm25_dense_passage_cascade_kaggle.ipynb`.
- Private input ZIP: `data/kaggle_inputs/exp130_bm25_dense_passage_input.zip` (21.292.058 bytes; CRC pass), chứa bản dịch query và 1.792.945 BM25 candidate rows; cần upload thành private Kaggle Dataset.
- Index active phải attach riêng và private: 23 dense shards, 1.724.798 chunk vectors FP16 (3,53 GB), cùng `chunks_metadata.parquet` và source text shards. Local audit đã xác nhận vector IDs liên tục và khớp đúng toàn bộ metadata rows.

**Thí nghiệm:** union/RRF các nhánh BM25 VI/EN/ZH top-500 (cache hiện tại giới hạn tối đa ~1.500 unique docs/query; không gọi đây là top-2.000) → exact BGE-M3 cosine trên chunk vectors để chấm candidate document bằng max chunk score → dense rerank top-400 → xuất top-216 docs để so sánh trực tiếp với output count lịch sử → rank chunk vectors trong các docs đó và xuất 96 exact source chunks/query. Tất cả 1.200 queries được xử lý đầy đủ trước khi tạo ZIP; `QUERY_LIMIT=120` chỉ dùng để benchmark tốc độ/throughput và không tạo submission một phần. Notebook ghi model revision đã resolve, input/index fingerprint, counts, ZIP hash và CRC.

Đây là ablation kiến trúc lớn: docs membership/ranking và passage selection cùng thay đổi, nên điểm BTC phải đọc riêng Docs F2 và Chunks F2; chưa thể quy gain cho riêng tầng nào. Nếu chạy xong, so với Exp122 và giữ artifacts/log. Bước sâu tiếp theo nếu Exp130 khả quan: giữ doc ranking thắng, mở rộng mỗi doc thành tối đa 8 passages, prescore bằng dense+lexical rồi dùng open Qwen3-Reranker trên top passage shortlist; pilot 20–40 query để đo throughput/VRAM trước khi chạy full. Không chạy 480.000 cặp rerank 4B tối nay nếu pilot chưa chứng minh ETA phù hợp.

Notebook và package đã tạo/kiểm tra schema Python, cấu trúc ZIP/CRC, candidate version và shard alignment ở local. Mình không điều khiển phiên Kaggle hoặc upload submission; cần người dùng gắn hai private datasets, bật GPU, chạy Kaggle và tự nộp ZIP trả về. Nếu pilot cho ETA vượt thời gian còn lại, dừng sau pilot, lưu progress/artifacts và hoàn tất full run ngày mai thay vì gửi partial output.

### 15.14 Sửa ưu tiên sau Exp129: local run và translation A/B (22/10/2026)

**Trạng thái:** kế hoạch NLLB ở mục này là lịch sử trước benchmark và đã được thay thế bởi quyết định tại mục 15.17. Không dùng NLLB làm translation production.

Exp129 đạt Final `0,3500`, Docs F2 `0,3586`, Chunks F2 `0,3414`, Docs P/R `0,1816/0,6114`, Chunks P/R `0,2547/0,4591`. So với Exp122, bớt 4 full parents/query làm chunk precision tăng `0,0035` nhưng recall giảm `0,0091`, khiến Chunks F2 giảm `0,0032`. Dừng Exp127/128: F2 hiện thiếu recall, không thiếu một sweep parent nhỏ hơn.

Exp130 không phụ thuộc Kaggle. Local RTX 3050 Ti 4 GB đủ encode 1.200 queries; dense corpus không nạp toàn bộ 3,53 GB vectors vào VRAM mà mmap theo shard và chỉ chuyển candidate rows của từng query lên GPU. Control và treatment phải dùng cùng VI dense scorer, candidate budget, output count và evidence policy.

Rà soát trực tiếp cho thấy `query_translated.parquet` hiện do Qwen2.5-1.5B tạo có lỗi thay đổi intent/thuật ngữ ngay trong mẫu đầu: `thuốc tăng cân` thành `weight-loss supplement`, `nhân tuyến giáp` thành `thyroid stalk`, `viêm dạ dày trợt xung huyết` thành `atrophic gastritis with persistent bleeding`, và query rốn trẻ sơ sinh bị bản EN lược gần hết. Vì vậy không kết luận kiến trúc BM25 đa ngôn ngữ từ candidate cache cũ.

Thực thi theo cặp kiểm soát:

1. **T0/control:** query VI gốc cho dense; BM25 VI/EN/ZH từ cache cũ; chạy local để đo runtime, membership và artifact shape. Không ưu tiên nộp nếu passage policy chưa giữ được recall của Exp122.
2. **T1/translation repair:** dịch trực tiếp query VI sang EN và Simplified Chinese bằng open `facebook/nllb-200-distilled-600M`, không rewrite/canonicalize; lưu file version mới và model revision, không ghi đè file BTC. Validator kiểm số/đơn vị, ASCII medical tokens, target script, độ dài bất thường, copy-source và câu rỗng. Fail thì không âm thầm dùng output đó.
3. Rebuild riêng cache BM25 T1; so overlap/churn của từng EN/ZH branch với cache cũ và VI control. Dense vẫn chỉ encode câu VI gốc, đúng gợi ý Mentor Day 2. Chỉ nộp treatment khi đủ 1.200 queries, artifact khác control và mọi source chunk/doc_id qua validation.
4. Nếu NLLB vẫn sai thuật ngữ y khoa, dùng agreement/gating giữa NLLB và translator lớn hợp lệ, cộng glossary bảo toàn tên thuốc, chỉ số, đơn vị và bệnh danh. Không cộng nhiều bản dịch thành nhiều phiếu RRF; hợp nhất trong language family để tránh query có nhiều views tự tăng trọng số.

Mục tiêu của vòng này là sửa candidate recall cho tài liệu EN/ZH. Query understanding/canonical VI, HyDE và reranker là ablation sau, không trộn vào T1 để kết quả leaderboard còn diễn giải được.

### 15.15 Benchmark dịch trên Kaggle theo gợi ý Mentor Day 2

Đã dừng pilot dịch local theo yêu cầu. Benchmark NLLB-600M local trên 12 query đầu cũng cho thấy lỗi y khoa/đời sống nghiêm trọng, nên output đó không được dùng cho retrieval hay submission. Các script local được giữ làm provenance nhưng không chạy tiếp.

Slide Mentor Day 2 không chỉ định một checkpoint dịch cụ thể. Slide 13–15 yêu cầu bản dịch EN/ZH sát nghĩa, giữ thuật ngữ/tình trạng bệnh, rà soát bằng mẫu song ngữ và nguồn chính thống, vẫn dùng query VI gốc cho dense/rerank; thứ tự hướng nghiên cứu là direct translation, glossary-augmented prompting, retrieved few-shot và domain-specific fine-tuning trên MedEV. MedEV chứa khoảng 360K cặp VI–EN. Paper gốc báo cáo trên test set Vi→En: `vinai-translate` base BLEU `33,44`, `envit5-translation` base `32,00`, NLLB/M2M-100 thấp hơn; sau fine-tune MedEV, `vinai-translate` đạt `42,38`, cao nhất nhóm open được thử. Checkpoint MedEV-finetuned chính thức không được paper phát hành, nên không được giả định rằng model base tương đương model thắng.

Notebook `notebooks/15_translation_model_benchmark_kaggle.ipynb` benchmark trên cùng 60 query phân tầng, bắt buộc gồm ID 1–12 và 42/71/219/271, cộng 128 câu MedEV test có reference cho chiều VI→EN:

- Profile `nmt`: VinAI Translate v2, EnViT5, NLLB-600M và MADLAD-400-3B-MT.
- Profile `llm`: Qwen3-4B/8B/14B-AWQ với prompt literal translation, thinking tắt; model lớn nhất 14,8B vẫn trong giới hạn ≤15B/model.
- Tài khoản Kaggle A chạy `nmt`, tài khoản B chạy `llm`; model cache được xóa sau từng model để tránh hết disk.
- EN có BLEU/chrF/TER trên MedEV. Query cuộc thi có validator số/đơn vị/abbreviation/script/độ dài, BGE-M3 source cosine và cross-model consensus, nhưng đây chỉ là diagnostic; notebook luôn xuất sheet review thủ công và không tự tuyên bố model thắng.
- ZH chưa có medical reference tương ứng trong MedEV; quyết định phải dựa vào review query thật, không chọn chỉ theo BGE cosine. NLLB được giữ làm baseline âm vì model card nói rõ đây là general-domain và không dành cho medical text; MADLAD và Qwen là treatment chính cho ZH.

Artifacts `translation_benchmark_nmt.zip` và `translation_benchmark_llm.zip` đã tải về, qua CRC và được phân tích tại `docs/translation_benchmark_analysis_20261023.md`. Quyết định production và execution gate nằm ở mục 15.17. Không ghi đè `data/raw/btc_provided/query_translated.parquet`.

Nguồn chính: [MedEV paper](https://aclanthology.org/2024.lrec-main.784/), [MedEV dataset](https://huggingface.co/datasets/nhuvo/MedEV), [VinAI Translate](https://github.com/VinAIResearch/VinAI_Translate), [EnViT5](https://huggingface.co/VietAI/envit5-translation), [MADLAD-400-3B-MT](https://huggingface.co/google/madlad400-3b-mt), [NLLB-600M](https://huggingface.co/facebook/nllb-200-distilled-600M), [Qwen3-14B-AWQ](https://huggingface.co/Qwen/Qwen3-14B-AWQ).

### 15.16 Kết quả Exp131–135 và quyết định dừng short-window breadth (23/10/2026)

BTC đã chấm toàn bộ ladder evidence mới:

| Exp | Policy | Final | Docs F2 | Chunks F2 | Chunks P | Chunks R |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 131a | mọi missing docs, width 512 | 0,3047 | 0,3586 | 0,2509 | 0,1213 | 0,4531 |
| 131b | mọi missing docs, width 384 | 0,3079 | 0,3586 | 0,2572 | 0,1249 | 0,4622 |
| 132 | anchored missing, width 512 | 0,3162 | 0,3586 | 0,2738 | 0,1499 | 0,4491 |
| 133 | top 75, width 640 | 0,3233 | 0,3586 | 0,2879 | 0,1628 | 0,4558 |
| 134 | top 60, width 768 | 0,3285 | 0,3586 | 0,2985 | 0,1784 | 0,4557 |
| 135 | top 50, width 896 | 0,3326 | 0,3586 | 0,3065 | 0,1908 | 0,4559 |
| 122 control | 19 ranked full parents | **0,3516** | **0,3586** | **0,3446** | **0,2512** | **0,4682** |

Tất cả treatment giữ Docs P/R `0,1816/0,6114`, nên regression nằm hoàn toàn ở chunk axis. Không treatment nào vượt Chunks Recall của Exp122 dù xuất nhiều windows hơn; precision giảm từ `0,2512` xuống `0,1213–0,1908`. Đường cong top75→top50 chỉ hội tụ dần về control khi bớt windows và tăng span, không chứng minh còn gain nếu tiếp tục top40/top30. Dừng Exp136–138 và không tiêu thêm slot vào width/cap gần kề.

Suy luận kỹ thuật: official chunk match cần đủ ngữ cảnh/overlap; nhiều snippets ngắn được neo bằng retrieval score không đồng nghĩa evidence đúng. Exp122 thành công nhờ một số ít full-parent documents có chất lượng, không phải coverage mọi selected document. Kiến trúc tiếp theo phải cải thiện selection/ranking trước, sau đó mới trả evidence dài/nguyên văn cho tập nhỏ docs thắng.

### 15.17 Kết quả benchmark dịch và execution gate (23/10/2026)

Hai artifact benchmark đã qua CRC, không có model failure; báo cáo chi tiết tại `docs/translation_benchmark_analysis_20261023.md`.

- **EN default: VinAI Translate v2.** Validator pass `0,85`, number recall `0,9265`, MedEV BLEU/chrF/TER `34,7383/62,0807/57,5993`, tốt nhất benchmark và nhanh hơn nhiều so với Qwen14.
- **ZH default có điều kiện: Qwen3-14B-AWQ.** Không có reference ZH nên quyết định dựa trên proxy cộng review thủ công. Qwen14 bảo toàn query dài/đa chủ thể và thuật ngữ tốt hơn NLLB/MADLAD/Qwen4 trong các ca rà soát.
- **Qwen14 EN rescue:** chỉ dùng khi VinAI fail validator hoặc query quá phức tạp; không để hai bản dịch cùng family bỏ hai phiếu độc lập.
- Qwen8 từng bị cắt JSON ở ID 219. Full run phải dùng token budget động, kiểm `finish_reason`/JSON closure và retry; fail cuối cùng thì bỏ language branch cho query đó và giữ VI raw.

Thứ tự chạy tiếp:

1. Sinh đủ EN 1.200 query bằng VinAI; sinh ZH 1.200 query bằng Qwen14, có checkpoint/resume và chia shard nếu cần.
2. Audit tự động số, đơn vị, tên thuốc/abbreviation, target script, empty/truncation; review tập ca lỗi 1–12, 42, 71, 219, 271 và mẫu dài/đa chủ thể.
3. Lưu file versioned + model revisions/prompt hash; không ghi đè query BTC hoặc cache cũ.
4. Rebuild BM25 EN/ZH riêng. Đo branch overlap, candidate churn và docs membership sau fusion so với Exp122 trước khi tạo submission.
5. Phép thử leaderboard đầu tiên chỉ thay translation/candidate input; giữ count/scorer/chunk policy Exp122. Nếu membership không đổi hoặc validator coverage kém thì không dùng slot.

Benchmark là evidence về chất lượng dịch, chưa phải evidence về relevance. Không ghép ngay canonical rewrite, HyDE, reranker và translation vào một artifact vì sẽ mất khả năng quy nguyên nhân.

### 15.18 Production translation 1.200 query trên Kaggle 2×T4

Đã tạo `notebooks/16_translation_production_2xt4_kaggle.ipynb` và generator tái lập `scripts/create_translation_production_kaggle_notebook.py`.

- EN chạy VinAI Translate v2 trên toàn bộ 1.200 query. Chỉ các query fail structural validator mới được đưa qua Qwen14 EN-rescue; VinAI vẫn là default vì thắng rõ MedEV.
- ZH chạy Qwen3-14B-AWQ. Hai subprocess giữ hai model replicas độc lập, mỗi replica trên một T4 và một shard cân bằng độ dài, thay vì chia layer một model khiến GPU hoạt động nối tiếp.
- Qwen sinh plain text từng ngôn ngữ, thinking tắt, dynamic token budget `192–1.024`, retry riêng tối đa `1.536` tokens khi thiếu số/rỗng/truncated. Không dùng JSON song ngữ đã gây rỗng ID 219 ở Qwen8 benchmark.
- Input bắt buộc đúng 1.200 IDs và SHA-256 `ce13508b893bbd6b9169679d540630bc37eb5950cad08b4d5e0e5d7063670c08`. Model revisions pin đúng benchmark; `HF_TOKEN` đọc từ Kaggle Secrets và không được ghi ra artifact.
- Notebook checkpoint mỗi 20 query/worker, kiểm source/ID/duplicate/CJK/token-limit, xuất production parquet + full audit + review CSV + manifest trong `translation_production_v1.zip`, rồi xóa model cache để không đóng gói weights Kaggle.

Sau khi tải artifact về, chưa thay file BTC ngay. Local phải audit các rows `needs_review`, rebuild cache BM25 EN/ZH version mới, đo candidate churn và docs membership so với Exp122. Submission đầu tiên giữ scorer/count/chunks Exp122 để cô lập tác động translation repair.
