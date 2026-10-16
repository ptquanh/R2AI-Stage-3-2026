# R2AI Stage 3 — Kế hoạch cải thiện điểm

> Cập nhật: 16/10/2026. Clean rebuild đã hoàn tất. Số liệu được audit trực tiếp từ các file active trong workspace. Mốc `0.4214` chỉ là kết quả công khai dùng để tham chiếu, không phải khẳng định về thứ hạng hiện tại.

## 1. Kết luận điều hành

Điểm hiện tại `0.2991` không chỉ bị giới hạn bởi số lượng URL. Ba nút thắt lớn nhất là:

1. Index active đã được rebuild sạch: `1.115.733` documents, `1.590.459` chunks và `0` document ngoài danh sách BTC.
2. Artifact `99.448` document hợp lệ đã được merge; `40.616` document lỗi và `56.609` chunks tương ứng đã bị loại.
3. Nút thắt tiếp theo là document retrieval chưa tái tạo được BM25 baseline của BTC; hybrid hiện tại chưa phải candidate union độc lập.

Ưu tiên ngắn hạn là làm sạch và hoàn thiện index, sửa evaluator, tái tạo document baseline, sau đó mới tối ưu reranker và chunking.

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

| Thành phần | Kết quả đã xác minh |
|---|---:|
| Document hợp lệ trong active index | 1.115.733 |
| Document không thuộc danh sách BTC | 0 |
| Coverage corpus chính thức | 91,408719% |
| Chunks metadata | 1.590.459 |
| Dense vectors / FAISS `ntotal` | 1.590.459 |
| Sparse matrix | 1.590.459 × 250.005 |
| Text rows / unique document IDs | 1.115.733 / 1.115.733 |

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

## 4. Trạng thái corpus active mới nhất

| Nhóm                         |      Tổng rows | Hợp lệ theo BTC | Trạng thái                        |
| ---------------------------- | -------------: | --------------: | --------------------------------- |
| Active index sau rebuild     | 1.115.733 docs |       1.115.733 | Đã index; không có ID lỗi         |
| Embedded artifact đã merge   |         99.448 |          99.448 | Đã nằm trong active index         |
| `unembedded_samples.parquet` |         90.029 |          90.029 | Đã lọc sạch, có text, chưa embed  |
| `remaining_urls.parquet`     |         14.836 |          14.836 | Đã reconcile, sẵn sàng crawl      |

`embedded_samples.parquet` cũng đã được lọc từ `1.156.349` xuống `1.115.733` rows để khớp chính xác active index. Backup có thể phục hồi nằm tại `data/embedded_samples.parquet.pre_clean_rebuild_20261016T155529.bak`.

`unembedded_samples.parquet` đã được lọc từ `94.399` xuống `90.029` rows; loại đúng `4.370` cặp `(id, url)` ngoài corpus. Backup nằm tại `data/unembedded_samples.parquet.pre_official_filter_20261016.bak`.

`remaining_urls.parquet` đã được reconcile từ `14.652` lên `14.836` rows bằng cách bổ sung đúng `184` cặp `(id, url)` chính thức bị thiếu. Backup nằm tại `data/remaining_urls.parquet.pre_reconcile_20261016.bak`.

Nếu hoàn thành theo thứ tự:

1. Hoàn tất: clean rebuild và merge 99.448 docs, coverage `91,41%`.
2. Tiếp theo: embed 90.029 docs hợp lệ trong `unembedded_samples`, coverage tối đa `98,78%`.
3. Sau đó: crawl và embed `14.836` URLs còn lại. Ba registry hiện là một phân hoạch đầy đủ của toàn bộ `1.220.598` cặp `(id, url)` chính thức.

Hai registry `embedded_samples.parquet` và `unembedded_samples.parquet` hiện không trùng ID/URL và mọi cặp `(id, url)` đều thuộc corpus chính thức.

## 5. Phân tích điểm hiện tại

| Cấu hình                 | Docs F2 | Chunks F2 |  Final |
| ------------------------ | ------: | --------: | -----: |
| Exp40 hiện tại           |  0,3223 |    0,2759 | 0,2991 |
| BM25 baseline BTC        |  0,5587 |    0,1941 | 0,3764 |
| Mốc công khai tham chiếu |  0,4183 |    0,4246 | 0,4214 |

Docs và chunks được chấm độc lập. Nếu tái tạo được Docs F2 của baseline `0,5587` và giữ Chunks F2 hiện tại `0,2759`, điểm suy ra là:

`(0,5587 + 0,2759) / 2 = 0,4173`

Để vượt mốc công khai `0,4214` trong điều kiện giữ Docs F2 `0,5587`, Chunks F2 cần khoảng `0,2841`, chỉ cao hơn hiện tại `0,0082`.

Đây là phép suy luận định hướng thử nghiệm, không phải dự đoán chắc chắn và không nói lên thứ hạng thực tế.

## 6. Root causes trong retrieval và evaluation

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

**Kết quả Exp45 — new champion:** Final `0,3029`, Docs F2 `0,3266`, Chunks F2 `0,2792`. So với Exp40, cả 7 chỉ số đều tăng; clean rebuild và 99.448 valid docs mới là hướng đã được BTC xác nhận. Ưu tiên kế tiếp: hoàn tất coverage còn thiếu rồi rerun nguyên champion config, không thay fusion.

### P0 — Output cố định làm loãng precision

Pipeline đang trả cố định khoảng 100 docs và 98 chunks cho mọi query. Cần thử `k=50/75/100` và adaptive-k theo score gap/confidence, tối ưu trực tiếp theo F2.

### P1 — Reranker cũ bị confound

Exp38 chỉ giữ một chunk trên mỗi document và dùng context 512 tokens. Cần chạy lại sau khi:

- Giữ nhiều candidate chunks/document.
- Dedup theo `(doc_id, start, end)` thay vì text toàn cục.
- Dùng metadata ngôn ngữ thật.
- Tăng context phù hợp với chunk hiện hành.
- Dùng rank blending thay cho per-query min-max dễ bị outlier.

## 7. Roadmap thực thi

### Gate 0 — Đo đúng và làm sạch dữ liệu

- [ ] (Deferred) Sửa evaluator theo NFKC, HTML unescape, lowercase, whitespace normalization và token-LCS `0,4`.
- [ ] (Deferred) Viết unit tests đối chiếu đặc tả BTC.
- [x] Rebuild consolidated index sau khi lọc toàn bộ ID không hợp lệ.
- [x] Merge artifact 99.448 docs đã embed.
- [x] Kiểm tra invariant giữa vector rows, sparse rows, chunk IDs, FAISS, text và metadata.
- [ ] Gắn fingerprint mới vào query cache và config để tránh dùng cache cũ.

### Gate 1 — Tái tạo document baseline

1. Chạy BM25 ở cấp document theo đúng tokenizer/analyzer và score domain được mô tả trong tài liệu BTC.
2. Giữ nguyên chunks của Exp40 để chỉ đo Docs F2.
3. Nếu Docs F2 không vượt `0,40`, dừng mở rộng model và đối chiếu tokenizer, normalization, threshold và output policy.

### Gate 2 — Candidate generation

1. [x] Candidate union độc lập giữa BGE sparse và dense; BM25 đúng analyzer còn tách riêng ở Gate 1.
2. [x] Dense retrieval riêng cho `q_vi`, `q_en`, `q_zh`.
3. So sánh RRF với calibrated linear fusion.
4. Tune document output count trên cùng ranking.

### Gate 3 — Chunk evidence

1. Chạy lại BGE reranker sau khi sửa multi-chunk/document.
2. Thử wide verbatim span quanh vùng tốt nhất.
3. Chỉ thêm span thứ hai khi evidence cách xa và confidence đủ cao.
4. Sau khi có baseline sạch, thử Qwen3-Reranker-0.6B rồi 4B.
5. Thử nhánh MedCPT riêng cho 240k PubMed sau bản dịch EN.

## 8. Retest queue cho corpus hiện tại

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

## 9. Ràng buộc cuộc thi

- Chỉ dùng model open-weight, mỗi model không quá 15B và phát hành trước 01/08/2026.
- Không dùng GPT, Gemini, Claude hoặc closed-source API trong hệ thống submission chính thức.
- External data phải có nguồn, giấy phép phù hợp và quy trình tái lập.
- `doc_id` phải thuộc danh sách BTC và là integer.
- `chunk_text` phải là substring nguyên văn của tài liệu nguồn; không dịch, viết lại hoặc sinh mới.
- Public tối đa 10 submissions/ngày; private tối đa 5 submissions tổng cộng.

## 10. Nguồn nghiên cứu kỹ thuật

- [ViBioMIR dataset card](https://huggingface.co/datasets/AIGuruTinix/ViBioMIR/blob/main/README.md)
- [BGE-M3 paper](https://arxiv.org/abs/2402.03216)
- [Qwen3-Reranker-4B model card](https://huggingface.co/Qwen/Qwen3-Reranker-4B)
- [MedCPT Query Encoder model card](https://huggingface.co/ncbi/MedCPT-Query-Encoder)
- [ColBERTv2 paper](https://arxiv.org/abs/2112.01488)
- [SPLADE v2 paper](https://arxiv.org/abs/2109.10086)

## 11. Definition of done cho index sạch

Trước khi tạo submission mới, index phải thỏa toàn bộ điều kiện:

- `set(index_doc_ids) ⊆ set(official_doc_ids)`.
- Số dense rows = số sparse rows = số chunk metadata rows = FAISS `ntotal`.
- `chunk_ids.npy` khớp theo thứ tự với FAISS và metadata.
- Mọi `(doc_id, start, end)` trích được đúng substring nguyên văn từ source text.
- Không có duplicate `chunk_id`.
- Có manifest ghi hash của official URL list, từng source artifact, model, tokenizer và config build.
- Query cache mang fingerprint của index và config; cache cũ không được tái sử dụng âm thầm.
