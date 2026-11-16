# R2AI Stage 3 — kế hoạch cải thiện điểm hiện hành

> Cập nhật 2026-10-27: **Exp139 keep90 vẫn là best với Final 0.3161**. Exp140 keep80 đạt `0.3154`, kém keep90 `0.0007`; cả hai giữ Docs F2 `0.3731`. Qwen cutoff sweep đã dừng: keep80 tăng precision nhưng làm recall/F2 chunk giảm.

### Best-axis recombination — đã promote

- Exact docs từ joint owner-release (BTC Docs F2 `0.3731`) + exact chunks từ top130/Exp122 (BTC Chunks F2 `0.2565`); không rerank/tune mới.
- `submission_best_axes_docs_joint_chunks_top130.zip`: 99.314.397 bytes, SHA-256 `b6bc6b304a8ccf5d55ebffdfd55e49633ab6822c1736556be65d8438a1e5215d`. Streaming equality/CRC pass; 1.200 query, 183.703 docs, 130.108 chunks.
- 8.311 chunk-owner query-docs ngoài `relevant_docs` là axis decoupling có chủ đích. Luật yêu cầu chunk đúng `doc_id` nguồn/nguyên văn nhưng không bắt buộc owner nằm trong `relevant_docs`; evaluator mô tả hai trục độc lập. [Chi tiết](experiments_log/best_axis_docs_joint_chunks_top130.md).
- BTC xác nhận đúng Final `0.3148`; promote làm control mới.

### Qwen4B original-chunk verification — full run hoàn tất, Exp139 đạt gain nhỏ

- Không thay segmentation và không localize paragraph. Chấm trực tiếp 130.108 chunk nguyên bản của control bằng Qwen3-Reranker-4B, cùng model/revision/template đã tạo gain ở docs axis.
- Mục tiêu là đo khả năng loại false-positive chunks tốt hơn BGE P2a; output treatment chỉ đổi chunk membership, còn best docs axis giữ nguyên.
- Chia query-disjoint trên Kaggle 2×T4, checkpoint/resume, không truncation ngầm. Candidate quá dài phải ghi `too_long` và fallback giữ nguyên; score cache khóa query/chunk hash/model revision/template.
- Trước full run: tạo exact-source pack và pilot 120 query để kiểm tra throughput/VRAM/overflow. Pilot không dùng làm local quality gate và không tạo submission.
- Đã tạo pilot pack 120 query / 12.880 chunks (`data/kaggle_inputs/qwen4b_chunks_pilot_v2`, 23.149.541-byte Parquet, SHA-256 `5697bdd7a1aae512b0c53d93fdb84994ee408448632b3e2df9aef77fde485240`). Passage chars median/p90/max `4.060/7.286/39.146`.
- Pilot Kaggle đã hoàn tất và tải về `data/kaggle_outputs/qwen4b_chunks_pilot/`. Coverage đúng 120 query / 12.880 chunks; `12.695 ok`, `185 too_long` (1,436%), không có inference error hay score không hữu hạn. Hai GPU đạt khoảng `0,615` và `0,607` pair/s; score chuẩn hóa có p10/median/p90 `0,0248/0,7879/0,9871`, đủ độ phân tách để tiếp tục full scoring nhưng chưa phải bằng chứng relevance.
- Full pack đã upload private thành `ptquanh/r2ai-qwen4b-original-chunks-full-v1`: 1.200 query / 130.108 chunks, Parquet 230.707.159 bytes, SHA-256 `7f3a746883c9fa52b2eeb06f46c962df940bede87dc9c82d689cd94a16ad6ba1`. Theo throughput pilot, cấu hình 2 part cần gần 15 giờ/part nên đã thay bằng bốn notebook query-disjoint, mỗi part 300 query / 32,4–32,6 nghìn chunk / ETA khoảng 7,4 giờ trên 2×T4. Không dùng hai notebook `part01of02`/`part02of02` cũ.
- Tài khoản `ptquanh` hết GPU quota nên full run chạy bằng `tramanhofficial`. Cả 4 part hoàn tất; từng part audit đủ 300 query, không có score lỗi và không lệch lineage/hash. Merge pass đủ 1.200 query / 130.108 chunks; `128.419 ok`, `1.689 too_long` (1,298%), revision đồng nhất và score hữu hạn. Audit/merge tại `data/audits/qwen4b_chunks_full_part01..04/` và `data/audits/qwen4b_chunks_full_merged/`.
- Worker full dùng `logits_to_keep=1` để chỉ chiếu token cuối ra vocabulary, thay vì tạo logits cho mọi token như pilot. Đây là tối ưu suy luận, không đổi prompt/input/score. Mỗi worker chạy self-check full-logits vs last-token logits trên một probe và dừng nếu sai khác > `1e-5`; không âm thầm tiếp tục. Không đổi treatment, không truncation và không giảm input để né quota.
- Đã tạo Exp139: giữ top 90% trong số chunk có score theo từng query, bảo toàn mọi chunk `too_long`, giữ nguyên docs và nguyên văn/thứ tự chunk. Candidate `submission_qwen4b_chunks_keep90_full.zip` có 117.835 chunks, bỏ 12.273 (9,43%), 88.723.672 bytes; độc lập audit pass và dưới hạn 100 MB. BTC đạt Final `0.3161`, Docs/Chunks F2 `0.3731/0.2591`: chunk precision tăng `0.0144`, recall giảm `0.0058`, Chunks F2 tăng `0.0026`; Final gain `+0.0013`. [Chi tiết Exp139](experiments_log/exp139_qwen4b_chunks_keep90.md).
- Quyết định: giữ Exp139 keep90 làm best BTC-confirmed `0.3161`; giữ ZIP best-axis 0.3148 làm reference reproducible. Exp140 keep80 từ cùng cache đạt `0.3154` (precision `0.2245`, recall `0.3259`, Chunks F2 `0.2578`) nên không promote. Hai cutoff xác nhận lọc mạnh hơn đổi precision lấy recall mà không cải thiện F2/Final. Dừng Qwen cutoff sweep và không chạy inference lại; hướng tiếp theo cần mở rộng/đa dạng hóa chunk candidates hoặc thiết kế passage theo evaluator matching, rồi đánh giá bằng một thử nghiệm độc lập.

### P1 Qwen4B top160 docs-only — đã promote

- Sau khi P1 top195 cho tín hiệu Docs F2 dương, triển khai một cardinality trial sâu hơn đã có trong policy curve trước đó; không thay đổi chunks và không dùng P2b.
- Top160 + owner protection loại 47.176/259.200 query-docs (18,20%), còn 212.024; giữ 20.024 owner docs ngoài cutoff. Tất cả 1.200 query thay đổi.
- `submission_p1_qwen4b_top160_full.zip`: 99.421.900 bytes, SHA-256 `a88feb29279cba04fb7c7caf6eed8499ac6e415678ef050cf3c82f6062b27f40`. Independent validator xác nhận chunks byte-identical và owner docs được giữ.
- BTC đạt Final 0.3138; Docs F2/P/R `0.3711/0.2085/0.5867`, chunk metrics giữ `0.2565/0.1957/0.3427`. [Chi tiết](experiments_log/p1_qwen4b_top160_full.md). Promote top160; không build top155/165/170/175 như một sweep lân cận.

### P1 Qwen4B top130 docs-only — đã promote

- Chọn một breakpoint sâu hơn sau tín hiệu BTC top195 → top160; top130 cách đủ xa và ít cực đoan hơn top120. Không dùng local labels để dự báo điểm.
- Owner-protected top130 loại 69.013/259.200 query-docs, còn 190.187; giữ 34.187 owner docs ngoài cutoff. Chunks byte-identical với control.
- `submission_p1_qwen4b_top130_full.zip`: 99.338.819 bytes, SHA-256 `ec32de34c32aca79b8a9986962291162cdc3042a267c2ef7fa26db369ebf6d27`; independent validation pass. [Chi tiết](experiments_log/p1_qwen4b_top130_full.md).
- BTC đạt Final 0.3143, Docs F2/P/R `0.3722/0.2215/0.5679`; promote top130 nhưng dừng fixed-cutoff ladder do gain chỉ +0.0005 Final. Không build top125/135. Builder đã được sửa hậu kiểm ZIP theo streaming để tránh `MemoryError`; policy/output không đổi bởi sửa lỗi này.

### Candidate đang chờ BTC: joint Qwen top130 + P2a keep90

- Không hạ cutoff tiếp. Dùng exact P2a chunk set để giải phóng owner protection cho docs không còn chunk evidence, trong khi Qwen top130 giữ head docs.
- Docs `259.200 → 183.703`; chunks `130.108 → 117.661`. Joint loại thêm 6.484 docs so với top130 docs-only. 946 external owners kế thừa từ Exp122/P2a không được tự ý thêm vào pool.
- `submission_joint_qwen_top130_p2a_keep90_v1.zip`: 88.961.424 bytes, SHA-256 `d1e618b33b4106ff832cabb2fd281a25b6abe44decead29199388c80294c7da0`; independent exact-policy validation pass. [Chi tiết](experiments_log/joint_qwen_top130_p2a_keep90.md).
- BTC: Final `0.3141`, Docs F2 `0.3731`, Chunks F2 `0.2551`. Docs axis thắng top130 nhưng chunk loss lớn hơn; không promote nguyên artifact. Giữ docs membership làm best-doc axis cho phép recombination đúng đặc tả.

### P2b paragraph localization — đã bác bỏ

- Đã ghi [kết quả P2a](experiments_log/p2a_bge_keep90_full.md): precision chunk tăng nhưng recall/F2 giảm. Không sweep keep85/80.
- `scripts/p2b_localization.py`: tạo paragraph groups nguyên văn trong từng chunk P1; giữ nguyên docs, chunk owner/order/count. Chỉ dùng paragraph có newline ở cả hai biên, bỏ biên parent có thể bị cắt cụt. Nguồn không có paragraph hợp lệ giữ nguyên parent; không tạo sentence splitter giả cho tiếng Trung.
- Dùng cửa sổ P2a mạnh nhất làm anchor để tạo tối đa 8 nhóm 1–3 paragraph liền nhau. Cửa sổ chỉ chọn vùng; không dùng window score đại diện cho đoạn output. Đây là localized search trong parent hiện có, chưa cứu evidence ngoài parent/doc hiện có.
- `scripts/p2b_score_worker.py`: BGE revision cố định, query gốc, 2 worker trên 2×T4. Chấm chính xác toàn bộ candidate có tổng query+passage ≤1024 model tokens; không truncation. Quá dài ghi `too_long`, không gán score; parent gốc luôn có sẵn để fallback. Checkpoint khóa hash input/model/code.
- Policy thử nghiệm khóa trước: candidate raw logit ≥1; nếu toàn bộ parent chấm được thì candidate phải cao hơn parent ≥0.5 logit; hòa điểm hoặc thiếu candidate hợp lệ fallback parent. Các ngưỡng là heuristic **chưa calibration**, không phải confidence đã kiểm chứng. Không đổi policy dựa trên local F2. Nếu lựa chọn tạo duplicate trong một doc thì rollback các slot của doc đó.
- Pilot 120 query đã chạy xong trên 2×T4. Independent audit pass: 105.206 pairs đúng nguồn; `paragraph_group:ok` 92.294, `paragraph_group:too_long` 32, `parent:ok` 5.576, `parent:too_long` 7.304. Đây là kiểm tra lineage/khả năng chấm, không phải đánh giá relevance.
- Audit chỉ xác minh nguồn/hash/count/provenance; không local scorer, không nhãn ChatGPT làm gold. Sau full audit mới build một BTC trial; ZIP-LZMA 64 MiB, <100 MB, người dùng tự nộp. Chất lượng chưa biết cho đến kết quả BTC.
- Trạng thái triển khai 2026-10-26: private pilot dataset và kernel đã hoàn tất. Score ZIP `data/kaggle_outputs/p2b_pilot/p2b_pilot_scores.zip`; audit báo 120 queries / 12.880 chunks / 105.206 pairs, exact-source pass; throughput quan sát khoảng 62–68 pairs/s/worker. Full pack `data/kaggle_inputs/p2b_full_v1` có 1.062.551 pairs / 130.108 chunks; mọi pilot pair khớp full theo IDs/query/hash/offset. Dataset full `ptquanh/r2ai-p2b-localization-full-v1` đã upload thành công (276 MB, private); kernel `ptquanh/r2ai-p2b-localization-full` version 1 đã push và báo `RUNNING`.
- Full run/audit/build đã hoàn tất; score ZIP `data/kaggle_outputs/p2b_full/p2b_full_scores.zip` audit exact-source pass. Candidate 40.429/130.108 chunks localized, docs và chunk counts/owners giữ nguyên, ZIP 68.434.748 bytes; xem [BTC result](experiments_log/p2b_bge_paragraph_localization.md). BTC Final 0.2641, Chunks F2 0.1632; **reject P2b, không sweep thresholds**. Control hiện hành là P1 top130. Metrics không chứng minh nguyên nhân đơn lẻ: candidate paragraph length, relevance score calibration và rule matching đều có thể góp phần; không dùng local score để chọn lại ngưỡng.

## 1. Chốt ưu tiên

1. **Dừng Exp138 và sweep độ dài chunk theo ký tự.** Không sửa một tham số rồi nộp tiếp.
2. **Ưu tiên evidence-aware reranking và relevance filtering để tăng precision**, trước atomic retrieval hoặc embedding corpus bằng model mới. Bỏ điều kiện cũ “chờ atoms thành công mới triển khai verifier”.
3. **Thử docs precision trước, giữ nguyên evidence Exp122.** Bảo vệ tất cả chunk-owning docs; chỉ lọc docs còn lại bằng verifier đã kiểm định. Không ép mọi câu xuống một top-k nhỏ.
4. **Tận dụng bản dịch đã có bằng A/B đúng thiết kế.** Tách tác động query, candidate pool, ranking, chunk owners và segmentation; không đổi tất cả cùng lúc.
5. Pilot offline trước, chỉ build submission có giả thuyết phân biệt được nguyên nhân. Người dùng tự nộp; không tự chạy paid API hay dùng hết slot bằng sweep.

**Trạng thái P1 ngày 2026-10-24:** Pilot Kaggle hoàn tất và artifact `p1_reranker_pilot_outputs.zip` đã audit thành công. Đủ 40.454/40.454 pair scores cho mỗi model, 25.920 docs trên 120 query (đúng 216 docs/query), 0 non-finite scores; BGE/Qwen model ID, immutable revisions, hai GPU shards và score lineage đều hợp lệ. Model rank agreement trung bình 0,497; owner-proxy AUC xấp xỉ 0,659 cho cả hai chỉ mô tả độ trùng với Exp122 evidence owner, **không phải relevance/qrels và không dùng để chọn model**. Đã tạo blind review queue 818 doc-candidates, 818 unique annotation IDs: 80 query development và 40 query holdout, stratified theo rank hai reranker; split key khớp chính xác seed/calibration, rời nhau và phủ đủ 120 query. Reviewer không thấy score/rank/split/owner. Calibration CLI hỗ trợ human-only và model-generated labels tách biệt; các test P1 liên quan audit/calibration/builder đều pass. BTC không cung cấp qrels/dev labels; `data/dev_set/` tự tạo không đáng tin, tuyệt đối không dùng làm gold hoặc làm gate. ChatGPT Web đã điền file nhưng đây không phải human review; hiện chưa có human labels, chưa qua gate, chưa có submission P1. Điểm BTC vẫn là phép kiểm chứng cuối.

**P1 human-review gate (tạm không làm theo quyết định hiện tại):** phần trên là lịch sử của nhánh docs-only; không chặn P2a. Không sửa local scorer và không dùng ChatGPT-generated labels làm gold. Ưu tiên hiện tại là BTC-only validation của một candidate chunk-filtering, với docs và text chunks được khóa nguyên trạng.

**P2a hiện trạng (2026-10-26):** pilot và full BGE scoring hoàn tất; cả hai independent source/lineage audit đều pass. Nguồn là P1 top195 (BTC FINAL `0.3107`), không phải ZIP Exp122(2): full input 1.200 query, 130.108 chunks, 342.548 windows; model revision `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e`. Full audit `data/audits/p2a_chunk_full_audit.json`; candidate audit `data/audits/p2a_chunk_candidate_audit.json`. Đã tạo exploratory keep-top-90%-per-query artifact `submission_p2a_bge_keep90_full.zip` (89.169.813 bytes, hash `5c81bb37ed361d198f7f5fca7f72cb3bda7b42fbc1c788429605ab8caab4d673`): bỏ 12.447/130.108 chunks; 1.200 query và toàn bộ docs giữ nguyên; chunk text được giữ nguyên theo đúng thứ tự. BGE ranks là heuristic, không phải nhãn relevance; candidate chưa được chấm BTC, không có dự đoán điểm, và người dùng tự nộp.

Để giảm công rà soát, bộ lõi `data/audits/p1_reranker_pilot_audit/annotation_review/compact_human_review/p1_compact_human_review_240.csv` lấy hai tài liệu/query (Qwen rank 1 và 180) từ queue 818, giữ nguyên annotation IDs, không chứa score/rank/split/nhãn ChatGPT; manifest khóa hash và xác nhận 80/40 query split. Đây là mẫu có chủ đích để kiểm tra lỗi top-vs-cutoff, **không đại diện corpus** và không đủ tự chứng minh cải thiện; 818-row queue vẫn là nguồn đầy đủ. Người dùng có thể điền `label` khi thuận tiện, không cần chặn các bước scoring đang chạy.

**BGE full scoring hoàn tất và đã audit:** kernel `ptquanh/r2ai-p1-full-bge-reranker-2xt4` chấm 406.014 passage pairs trên 1.200 queries/259.200 query-docs (216 docs/query), từ private Kaggle dataset `ptquanh/r2ai-p1-reranker-full-v1`. ZIP gốc `data/audits/p1_full_bge_download/p1_full_bge_part01of01.zip` có SHA-256 `050884792243064da69df1007cc6f48855731436841f005311161094980388f8`; merged ZIP `data/audits/p1_full_bge_merged/p1_full_bge_merged.zip` có SHA-256 `d381da16934b9a0d0349a75c3745d5db5794218686cc8d4c681cee93568fb5f2`. Independent audit `data/audits/p1_full_bge_merged/part_audit.json` xác nhận exact pair/source lineage, exact passage→doc max, 0 nonfinite scores, input hash `732e313ece7c2f46f21ae543a2b831c044c9925726c6b9a111518352a02cea28`, model revision `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e`. Đây là score artifact, chưa phải submission hay bằng chứng BGE tốt hơn control.

**Pilot↔full consistency:** 40.454 pair IDs của 120 query pilot đều có trong full pack, query text giống hệt; 6 passage spans khác ở 5 query-docs do bước chọn top passages được tính lại khi tạo full pack (cùng source hash, nhưng dense ranking gần tie). Trên 40.448 passage không đổi, 15 raw BGE scores lệch >1e-5, lớn nhất 0,00879 logit (input token counts giống nhau); đây là sai khác số học inference nhỏ. 25.920 query-docs pilot đều có trong full; 13 doc scores lệch >1e-6, 3 lệch >0,001, lớn nhất 0,11426 tại một doc có passage thay đổi. 23 doc ranks lệch, không phải 23 docs mất khỏi pool. Như vậy full input không byte-identical với pilot; không trình bày pilot calibration là đo chính xác cùng passage trên mọi cặp. Khi audit Qwen full cũng cần đối chiếu tương tự.

**Docs-only preflight trên BGE full scores:** `data/audits/p1_full_bge_merged/policy_impact.json` khóa hash control/scores và chỉ đo ảnh hưởng cấu trúc sau khi bảo vệ chunk owners. Top215 loại 941/259.200 query-docs (0,36%; 941/1.200 query thay đổi); top195 loại 18.774 (7,24%, median 16/query); top180 loại 31.722 (12,24%, median 27/query); top160 loại 48.202 (18,60%, median 40/query). Đây không phải dự báo điểm, vì chưa biết relevance của docs bị loại; đặc biệt BGE/top215 theo weak-label calibration gần như no-op nên không đáng tiêu slot BTC chỉ để xác nhận tác động rất nhỏ. Qwen/top195 phải audit tương tự khi đủ full scores; không suy ra Qwen có cùng phân bố loại docs.

**Weak-label cutoff diagnostic (chỉ giả thuyết):** trên 40-query holdout ChatGPT labels, Qwen/top160 giữ 88/90 `direct`, loại 17/68 `irrelevant` (pool precision 0,633; recall 0,978; F2 0,882); top180/top195 cùng giữ 90/90 direct nhưng chỉ loại 5/68 irrelevant. BGE/top160 trên cùng mẫu giữ 81/90 direct và loại 16/68 irrelevant. Mẫu bị lấy theo rank, chỉ 158 strict rows và nhãn đóng, nên các con số này không đại diện corpus/không được coi là kỳ vọng BTC. Khi Qwen full scores có, so sánh top160 với top180/top195 như **hai cutoff thăm dò**; chỉ nộp nếu cần thử, giữ chunks nguyên và gắn provenance weak-label.

**Candidate BTC thăm dò đã chuẩn bị, chưa nộp:** `submission_p1_bge_top180_exploratory_64m.zip` (99.477.217 bytes, SHA-256 `9a2dfe068f7581215aba54c661467ecb2553f327ee9f224803f7c08e99668a0b`). BGE/top180 là policy override được gắn nhãn **uncalibrated exploratory**, không qua human gate và không được quảng bá là đã cải thiện. Lý do thử: top215 do calibration trên mẫu nhãn yếu giàu positives chọn ra chỉ lọc 0,36% docs, trong khi top180 tạo can thiệp docs-only rõ hơn; tác động tới relevance/BTC score chưa biết. Validator độc lập `data/audits/p1_full_bge_merged/submission_p1_bge_top180_validation.json` xác nhận 1.200 queries, 31.722 query-docs bị loại, chunks giống hệt Exp122, chunk owners giữ nguyên, layout/CRC/hash/size hợp lệ. Control dùng ZIP/LZMA từ điển 64 MiB; builder đã sửa dùng 7-Zip cùng cấu hình vì Deflate tạo 199 MB và Python LZMA mặc định tạo 118 MB. Người dùng tự quyết định/nộp qua BTC; chưa có kết quả chấm. Các JSON/ZIP tạm vượt ngưỡng đã xóa sau khi kiểm chứng artifact cuối.

Qwen4B full-run notebooks cho bốn partition đã được generate. Partition 01 và 02 đã push lên các Kaggle kernels riêng `ptquanh/r2ai-p1-full-qwen4b-part-01-2xt4` và `ptquanh/r2ai-p1-full-qwen4b-part-02-2xt4`; status 2026-10-24 06:13 UTC cho thấy cả hai vẫn `RUNNING`, live logs có tiến triển (không treo). P01: GPU0 8.6k/51.3k at 1.58 pairs/s; GPU1 10.0k/51.2k at 1.85/s. P02: GPU0 9.0k/51.1k at 1.75 pairs/s; GPU1 8.4k/51.0k at 1.64/s. ETA thô theo GPU chậm nhất khoảng 7.2–7.6 giờ từ mốc log, dưới giới hạn 12h nhưng không bảo đảm. Thử push partition 03 bị Kaggle từ chối `Maximum batch GPU session count of 2 reached` (CLI trả exit code 0 dù thông báo lỗi); vì vậy 03/04 chưa chạy, phải đợi một slot GPU trống rồi push lại. Mỗi ZIP phải audit exact lineage riêng rồi mới merge đủ 1.200 query. Chưa có full Qwen scores hay submission.

**Tiến độ mới nhất (2026-10-25, UTC):** Qwen4B full-run đủ 4/4 shard, mỗi shard 300 queries; độc lập audit pass: đúng 64.800 query-doc/shard, tổng 406.014 passage pairs, lineage/aggregation chính xác, 0 non-finite scores, cùng model revision `22e683669bc0f0bd69640a1354a6d0aebcfeede5`, cùng full-input hash `732e313ece7c2f46f21ae543a2b831c044c9925726c6b9a111518352a02cea28`. Audits và ZIP nguồn nằm tại `data/audits/p1_full_qwen4b_part01..04/` và `data/audits/p1_full_qwen4b_part01..04_download/`. Đã merge thành `data/audits/p1_full_qwen4b_merged/p1_full_qwen4b_merged.parquet` + ZIP/manifest; coverage đúng 1.200 × 216 = 259.200 query-doc, rank 1..216 và scores hữu hạn. Structural impact report `data/audits/p1_full_qwen4b_merged/policy_impact.json`: top195 loại 18.822/259.200 docs (7,26%), thay đổi cả 1.200 query và giữ toàn bộ chunk-owner docs; đây chỉ là cấu trúc, không phải relevance/score evidence. Full-run schema dùng `qwen4b_score`, nên đã chuẩn hóa alias `qwen_score` trong builder; thêm test regression, P1 tests 50 passed, 47 deselected. Đã tạo docs-only candidate `submission_p1_qwen4b_top195_full.zip`, giữ chunks y nguyên Exp122: 1.200 queries, 240.378 docs còn lại, 18.822 bị lọc, 128.281 chunk-owner query-docs được bảo vệ. Independent validator pass; ZIP 99.525.760 bytes (<100 MB), SHA-256 `785637cb462f014f1bf35c1c994372a2561bac924ef416c0ccaea0a6b10b0c28`; validation `data/audits/p1_full_qwen4b_merged/submission_p1_qwen4b_top195_validation.json`, provenance manifest `submission_p1_qwen4b_top195_full_manifest.json`. Candidate gắn `uncalibrated_exploratory`/`exploratory_only_not_promoted`, do chọn cutoff dựa một phần trên model-generated labels và không có BTC qrels/human gate. Sẵn sàng để người dùng tự nộp làm một BTC-only trial; chưa có điểm BTC nên chưa thể kết luận cải thiện hoặc promote.

Weak-label hỗ trợ đã được đóng gói tại `notebooks/18_p1_weak_judge_14b_2xt4_kaggle.ipynb`: Qwen3-14B open-weight, 4-bit, hai worker query-disjoint, exact-evidence check và provenance. Chỉ chạy sau pilot; output phải qua review mù, không thay thế nhãn BTC.

## 2. Control, mục tiêu và kết luận đã sửa

### Điểm đã xác nhận dưới evaluator mới

- **Exp122 (2):** Final `0.3075`; Docs F2/P/R `0.3586 / 0.1816 / 0.6114`; Chunks F2/P/R `0.2565 / 0.1957 / 0.3427`.
- **Exp134 chấm lại:** Final `0.2913`; Chunks F2/P/R `0.2241 / 0.1393 / 0.3352`. Docs giống control.
- **Exp135 chấm lại:** Final `0.2944`; Chunks F2/P/R `0.2303 / 0.1493 / 0.3358`. Docs giống control.
- **Exp138:** Final `0.2031`; Chunks F2/P/R `0.0477 / 0.0365 / 0.0644`. Docs giống control. Final giảm `0.1044`, Chunks F2 giảm `0.2088`: loại treatment.
- Exp122 legacy `0.3516` không còn là control cho chunk/Final. Baseline BTC legacy `0.3764` chưa được xác nhận dưới evaluator mới.

Giữ bất biến `submission_exp122_exp121_add19_miss.zip`, SHA-256 `8c7f221cfafa401dfb5435df7da06464999c4b60594e69bc7726bb4ffb379886`.

Mục tiêu `Final >= 0.38` vẫn có ý nghĩa nội bộ, không đồng nghĩa đã vượt baseline mới/top 1. Nếu Docs F2 giữ `0.3586`, cần Chunks F2 khoảng `0.4014`; nếu chunks giữ `0.2565`, cần Docs F2 khoảng `0.5035`. Đây là phép tính từ trung bình hai F2, không phải dự báo. Nâng cả hai trục hợp lý hơn chỉ ép một trục.

**Thông tin top 1 cần lưu:** người dùng nhớ khoảng `0.76`, Docs/Chunks precision khoảng `0.99`, recall khoảng `0.65`, sau đó ẩn điểm. Chưa kiểm chứng số chính xác, phiên bản evaluator hoặc kiến trúc; không dùng làm nhãn kỹ thuật hay hứa sẽ vượt. Chưa xác nhận vilamiu Stage 2 là ongthomiu Stage 3.

### Translation chưa được thử một cách đủ cô lập

- **Exp136:** thay 66/216 docs mọi query, khóa head150; Docs F2 giảm `0.3586 → 0.3061`. Policy thay tail gây hại, không chứng minh mọi bản dịch đều sai. Chunks copy nguyên trạng và **cả ba chunk metrics trùng Exp122 (2)**: `0.2565 / 0.1957 / 0.3427`. Điều này rất phù hợp với việc đã dùng evaluator mới. Rút lại nhận định cũ rằng mismatch docs/chunks là nguyên nhân mạnh của chunk regression so legacy. Mismatch vẫn là lỗi nhất quán cần tránh.
- **Exp137:** Final `0.2940`, Chunks F2 `0.2295`; thay query fusion, passage selection, chunk owners và segmentation. Median chunk `3.934 → 1.867` ký tự, exact overlap chỉ `29.1%`. Không phải A/B thuần translation. Nếu cùng evaluator mới, delta Final là `-0.0135`, không phải `-0.0576` so legacy.
- Chưa có execution metadata xác nhận evaluator của Exp136/137; lưu bất định, kiểm tra timestamp nếu có. **Không ưu tiên nộp lại** hai treatment nhiều biến này chỉ vì chúng được báo trước lần re-eval Exp122.
- Production translations: 1.200 query, views audit `ok` gồm 1.097 EN / 715 ZH. Status/schema hợp lệ không tự chứng minh đúng thuật ngữ, phủ định, dân số hoặc ý hỏi.

## 3. Hậu kiểm Exp138 — có lỗi thực thi và sai thiết kế thí nghiệm

Đối chiếu trực tiếp payload Exp122 và Exp138 ngày 23/10:

- Docs không đổi ở cả 1.200 queries; tổng chunks đều 130.108.
- **Chunk-owner sets đổi ở cả 1.200 queries**; bỏ 28.998 cặp query–doc evidence và thêm 28.998 cặp khác. Mean retention của owner set control chỉ `77.776%`.
- Median độ dài `3.933,5 → 554` ký tự. Chunks có >20% ký tự CJK trong vùng U+4E00–U+9FFF giảm `25.256 → 15.411`. Đây là heuristic phân bố chữ, không phải bộ nhận diện ngôn ngữ hay bằng chứng relevance.
- Code bỏ hẳn câu đơn >1.500 ký tự. Regex tách sau dấu câu chỉ khi có khoảng trắng; test synthetic Trung 2.000 ký tự có dấu câu nhưng không khoảng trắng cho **1 sentence span, 0 passages**.
- Dense rank của passage được kế thừa từ indexed chunk, không chấm trực tiếp nội dung passage bằng cross-encoder. Lexical dùng query VI cho source đa ngữ; các score bằng 0 vẫn bị gán thứ hạng khác nhau theo input order.
- Mapping passage→chunk dùng `searchsorted` trên starts/ends: cần xác nhận ends đơn điệu; nhánh overlap không dùng đúng điều kiện `chunk_end > passage_start AND chunk_start < passage_end`, còn fallback có thể lấy chunk gần nhất không giao.
- Validator kiểm tra format/count/ownership, không chứng minh relevance hay match gold. **Pass validator không đủ làm gate chất lượng.**

Không thể phân bổ chính xác mức giảm điểm cho từng nguyên nhân khi chưa có nhãn hợp lệ. Không kết luận sửa splitter là phục hồi được điểm; trước khi tái sử dụng builder phải sửa và test các vấn đề này. Chi tiết: [Exp138](experiments_log/exp138_sentence_passages_fixed_docs.md).

## 4. Nguyên tắc metric và tuân thủ

- Rule mới: `LCS(c,g)/|g| >= 0.4` **và** `LCS(c,g)/|c| >= 0.4`, cùng query/doc_id. Điều kiện cần: `0.4 <= |c|/|g| <= 2.5` theo **token sau chuẩn hóa**; không đủ bảo đảm match. Không biết gold lengths thì không suy ra một width tối ưu.
- Kiểm tra normalization/tokenizer/revision theo BTC. [Evaluation](competition_information/2_evaluation.md) còn mô tả rule một phía; kế hoạch áp dụng thông báo mới người dùng cung cấp, không sửa nguyên bản luật như thể BTC đã xuất bản lại.
- **Không lấy macro R/P suy số gold/prediction; không tính macro F2 từ macro P/R.** Rút lại kết luận cũ “dư docs 3,37 lần, dư chunks 1,86 lần”. Precision thấp cho thấy false positives nhiều trung bình, không xác định k tối ưu.
- Không dùng đáp án rò rỉ, file đối chiếu bị BTC thu hồi hoặc probing suy ngược gold. Chỉ dùng qrels BTC cho phép, dữ liệu công khai có provenance, hoặc đánh giá relevance độc lập từ corpus.
- Từng model ≤15B; foundation công bố trước 01/08/2026; fine-tune sau mốc phải private/local. Không dùng model đóng trong hệ thống thi; distillation không phải cách lách quy định teacher/model.
- OpenRouter host open-weight: cần làm rõ với BTC nếu điều kiện sử dụng còn mơ hồ, giữ self-host/Kaggle để tái lập. Pin model/provider/revision; không auto-route ngoài whitelist.
- Giữ doc_id corpus, evidence nguyên văn source, không sinh câu trả lời làm chunk. ZIP <100 MB theo yêu cầu người dùng.

## 5. P0 — Kiểm toán và tập đo relevance hợp lệ

**Không gọi lại QuerySpec hay dịch lại toàn bộ.** Dùng 120 query/34 strata pilot hiện có; gắn hash query, translation, index, source và control. Candidate cache cần `query_id, doc_id, language, branch, rank, score, source_hash, start, end, text_hash`; score cache thêm model/prompt/tokenizer/precision.

Kiểm tra mapping doc_id↔vector row↔source span; query instruction/normalization đúng encoder; translation đúng query ID và thực sự tham gia nhánh mong muốn. Thêm regression tests câu Trung không khoảng trắng, câu dài, nested/overlapping spans, lexical ties, negation/population. Không rebuild index khi chưa có bằng chứng lỗi.

### Tập kiểm định

1. BTC xác nhận qua người dùng là **không cấp qrels/dev labels**. Không dùng `data/dev_set/` làm gate: đây là synthetic set tự tạo từ pipeline cũ, câu hỏi sinh bởi `gpt-oss-120b` và ground truth giả định tài liệu/chunk đầu là gold; cả độ tin cậy lẫn giới hạn model đều không phù hợp P1. Dùng pooled relevance audit trên official queries + corpus; hard negatives cùng bệnh nhưng sai tuổi/thuốc/phủ định/ý hỏi.
2. Chia theo **query** trước tune: đề xuất 80 development / 40 holdout, giữ strata. Bộ nhỏ chỉ cho tín hiệu sơ bộ, không tune lặp trên holdout.
3. Nhãn: trả lời trực tiếp / chỉ cùng chủ đề / không liên quan. Người rà soát không thấy branch/rank. LLM open-weight ≤15B tự host có thể hỗ trợ weak labels; review các bất đồng, không coi LLM tự chấm là ground truth BTC. Không dùng synthetic qrels do model >15B hoặc provenance yếu để chọn scorer/ngưỡng.
4. Đo judged precision, pairwise ranking accuracy, retention của known positives và lỗi theo ngôn ngữ/query type. Pool chưa đầy đủ thì chỉ gọi **relative recall trên judged pool**, không phải recall thật.
5. Có span labels hợp lệ mới tính chunk F2 theo rule hai phía; weak relevance không đủ xác nhận chunk matching. Dùng paired uncertainty theo query, không promote từ vài mẫu thuận lợi.

Calibration implementation tách `exploratory` (weak/mixed labels, chỉ để định hướng) khỏi quyết định dựa trên nhãn human-only. Human annotation CSV nối bằng `query_id`+`doc_id`; nhãn weak-review nối bằng `judgment_id`, tránh nhầm ID giữa hai queue. Vì BTC không cấp qrels/dev labels và `data/dev_set/` không đáng tin, tuyệt đối không dùng synthetic dev set làm gold. Human review là một **pool ứng viên được lấy mẫu**, không phải qrels đầy đủ: các precision/recall trong đó chỉ mô tả pool đã rà soát; đặc biệt không suy ra corpus-wide recall hay đảm bảo điểm BTC. Holdout theo query giúp hạn chế tune trực tiếp trên cùng query, nhưng không biến mẫu nhỏ thành benchmark đại diện. Gate trong code chỉ là điều kiện vận hành trước một thử nghiệm thận trọng, không được gọi là “đã xác minh cải thiện” theo BTC. Không để weak labels tham gia human-only metrics; báo cáo phải ghi rõ phạm vi và provenance.

**Gate:** novelty/JSON hợp lệ/cosine cao không chứng minh relevance. Khi thiếu nhãn đầy đủ, submission là thăm dò có kiểm soát, không tự nhận đã chứng minh cải thiện offline.

## 6. P1 — Evidence-aware reranking và docs precision (ưu tiên cao nhất)

### Scoring pipeline

- Candidate union từ control + BM25 + BGE-M3 + Qwen embeddings đã có, quota rõ và dedupe. Khóa pool khi so scorer. **Không khóa head150 trong scoring**, không chỉ thay 1–3 docs/query.
- Mỗi doc chọn 2–3 passages theo query/cấu trúc bài, giữ title/heading/offsets; không chỉ 500 ký tự đầu. Chấm trực tiếp query–passage, để tài liệu dài có cơ hội cung cấp evidence ngoài phần đầu.
- Pilot **BGE reranker v2 m3 vs Qwen3-Reranker-4B trên cùng pairs**. Không mặc định model lớn hơn tốt hơn. Qwen dùng template/instruction/yes-no scoring đúng model card, không sinh bài giải dài.
- Aggregate passage→doc bằng best support và constraint/atom coverage, kiểm soát thiên lệch doc dài có nhiều cơ hội lấy max. Lưu raw scores; sigmoid score chưa phải xác suất relevance đã calibration.
- Calibrate cutoff trên development labels, đánh giá holdout/theo ngôn ngữ. Không copy threshold BTC `0.73` sang logits/RRF/cosine thang khác; không dùng số docs LLM đoán làm gold count.
- Selective LLM verification ≤15B chỉ cho cases bất đồng/không chắc: yêu cầu evidence nguyên văn **trả lời đúng ý hỏi**, không chỉ entities. Citation tồn tại vẫn cần relevance check.

Nguồn chính thức: [Qwen3-Reranker-4B](https://huggingface.co/Qwen/Qwen3-Reranker-4B) (4B, đa ngữ, instruction-aware); [BGE reranker v2 m3](https://huggingface.co/BAAI/bge-reranker-v2-m3) (cross-encoder đa ngữ). Lưu bằng chứng release/revision/license trước run.

### Submission đầu: lọc docs, không phá chunks

Đặt `C = doc_ids của chunks Exp122` theo query. Chấm toàn bộ 216 docs nhưng **bắt buộc giữ C**; chỉ bỏ docs ngoài C có bằng chứng không trả lời ý hỏi. Không thêm candidate mới/translation trong submission đầu. Chunks text/order/count phải giống control.

Known positives ngoài C cũng cần recall guard; confidence thấp fallback nguyên control. Ràng buộc C đặt sàn cardinality và giới hạn upside. Sau khi có tín hiệu tốt mới lọc docs/evidence đồng bộ; gọi rõ **joint treatment**, không coi là docs-only. Không ép 30–100 docs mọi query; chỉ đổi thứ tự IDs mà membership không đổi thì không đáng dùng slot.

### Kaggle và gate

Benchmark vài trăm pairs với độ dài thật trước full run. Nếu vừa VRAM, một worker/GPU và chia query disjoint trên 2×T4; không mặc định `device_map=auto` nhanh gấp đôi. Chọn batch/precision từ đo thực tế, kiểm tra quantization có đảo ranking. Log pairs/s, latency, GPU và completed queries mỗi batch; checkpoint/resume theo query/hash.

Budget pilot ví dụ `120 × 300 docs × 2 passages = 72.000 pairs`; ETA từ throughput đo, không hứa một giờ. Output ZIP chỉ scores/source references/audit/manifest, không weights/HF cache.

Pilot đã hoàn tất: output ZIP chứa đúng 7 artifact dự kiến, CRC pass, input/control/pairs hashes khớp; mỗi reranker chấm đủ 40.454 pair trên cả hai shard. Output score lineage và document aggregation đã qua validator. Blinded review pack (CSV/Parquet, key tách riêng, instructions, manifest) nằm ở `data/audits/p1_reranker_pilot_audit/annotation_review/`. Full BGE đã chấm/audit và Qwen đang chấm song song như cache điểm; việc chạy trước human review không được hiểu là đã chọn model hay được phép tối ưu theo synthetic dev/owner proxy. Sau calibration trên development labels, khóa quyết định trên query holdout, rồi mới cân nhắc một trial docs-only giữ nguyên chunks và đánh giá bằng BTC.

File `p1_annotation_labeled.csv` do ChatGPT Web tạo được đối chiếu khớp đủ 818 annotation IDs/nội dung; 814 nhãn có giá trị (295 direct, 320 related, 199 irrelevant), 4 trống. Đã chạy riêng ở chế độ `model_weak`, tuyệt đối không nhập vào human metrics/gate. Exploratory-only chọn Qwen4B/top195; holdout AUC strict 0.954 và AP 0.956 chỉ đo mức khớp với chính nhãn do model tạo, không chứng minh relevance thật. Cutoff top195 cũng chỉ loại tối đa 21/216 docs trước khi bảo vệ chunk owners nên upside kỳ vọng hạn chế. Vì vậy chưa build/submit full candidate từ kết quả này. ChatGPT Web là mô hình đóng: nhãn này chỉ để chẩn đoán nội bộ, **không đưa vào hệ thống nộp bài chính thức và không dùng làm gate chọn policy**; nếu muốn dùng nhãn model cho training/calibration cần thay bằng model open-weight hợp lệ và giữ provenance. Nếu sau này build exploratory artifact, manifest phải mang schema `p1_model_label_exploratory_docs_trial_v1`, hash nhãn model và trạng thái `exploratory_only_not_promoted`.

Với full pack 406.014 pairs, BGE dự kiến khoảng 2,6 giờ trên 2×T4 và có thể chạy một partition. Qwen4B dự kiến hơn 30 giờ nếu chạy một phiên, nên generator buộc chia tối thiểu bốn partition query-disjoint (khoảng 8–9 giờ/partition); merge chỉ pass khi đủ 1.200 query × 216 docs, cùng input hash và model revision. Không giảm passage/candidate chỉ để ép Qwen vào một phiên vì sẽ đổi treatment.

**Gate:** scorer phân biệt relevant với hard negatives tốt hơn control trên holdout, không làm mất positives vì ngôn ngữ/độ dài. Nếu không, sửa data/objective hoặc fine-tune trước tăng model size.

## 7. P2 — Chunk precision và localization: hai phép thử riêng

### P2a — Lọc evidence hiện có

Giữ nguyên docs và chunk text của candidate P1 top195 (`submission_p1_qwen4b_top195_full.zip`, BTC FINAL `0.3107`) làm control cho P2a; đây là nguồn thực tế của các score artifacts. **Không có qrels/dev labels đáng tin cậy; local scorer không dùng làm quality gate.** BGE chỉ chấm query–chunk trên các cửa sổ nguyên văn, giữ provenance/hash/offset; điểm reranker là tín hiệu heuristic, không phải nhãn relevance. Candidate P2a chỉ đổi chunk membership, giữ docs và nội dung từng chunk được giữ nguyên. Người dùng tự nộp BTC; **điểm hệ thống BTC là tiêu chí đánh giá**, không dự đoán điểm từ local scorer. Exp122(2) `0.3075` vẫn là control lịch sử khi đối chiếu evaluator, không phải payload dùng để tạo treatment P2a này.

Không sweep cutoff theo synthetic labels hay local score. Nếu policy cần ngưỡng, khóa trước một thử nghiệm phân biệt được tác động (ví dụ conservative per-query keep fraction cùng fallback), và chỉ so kết quả BTC với control theo cùng evaluator version. Docs metrics phải bất biến; precision tăng nhưng Final/F2 giảm thì không promote. P2b localization vẫn tạm hoãn vì đòi hỏi bằng chứng span/gold chunk đáng tin.

### P2b — Localize evidence có ngữ cảnh

Chỉ làm sau khi scorer tìm đúng evidence trên audit. **Khóa chunk-owning docs và số chunks từng doc**, không lặp Exp138. Tìm phần trả lời rồi mở theo paragraph/section, dựa cấu trúc nguồn và token budget thay vì width ký tự chung.

Source-offset slicing nguyên văn; câu dài có fallback giữ coverage, không bị xóa. Lưu coverage map, token histogram VI/EN/ZH, owner retention và text overlap. Dùng mẫu chunk BTC cho phép để đánh giá granularity nếu có; nếu không, thừa nhận chưa biết gold length, synthetic tests chỉ kiểm tra code. Query chưa xác định được span đủ tin cậy giữ nguyên chunks control.

## 8. P3 — Translation và atomic retrieval có verifier

Chạy offline song song P1, không chặn P1.

1. **Scoring-view A/B:** cùng candidate passages/segmentation/count/reranker, chỉ đổi query gốc → gốc+EN → gốc+ZH. So cross-lingual original với matching-language view; không mặc định bản dịch tốt hơn.
2. **Retrieval-view A/B:** giữ scorer/output policy, giữ candidates control và thêm quota riêng từng language×retriever. Đo view mang về known positives mới, không chỉ novel IDs; không thay bắt buộc 66 docs/query.
3. Review dịch theo phủ định, thuật ngữ, số/đơn vị, population, intent. View sai thì bỏ view, giữ query gốc. “Bầu ↔ phụ nữ mang thai” là alias; đại từ chỉ bỏ nếu không mang thông tin chủ thể/quan hệ.
4. Câu nhiều ý: retrieve từng atom rồi **rerank lại với toàn câu gốc**. Không yêu cầu mỗi doc phải trả lời hết mọi atom nếu nó là evidence đúng cho một phần câu hỏi.
5. ICD-10 là soft routing/feature có UNKNOWN và nhánh global. Exp55 small-k kém không đủ bác bỏ mọi BM25/ICD architecture; không hard-filter corpus.
6. Multi-hop chỉ bật khi thật sự thiếu một bước evidence; expansion có căn cứ source, không suy đoán thêm bệnh/thuốc. So với atomic one-hop cùng budget.

Exp89 (cap3), Exp110 (head150 locked), Exp123 (khác pool, CE thấy 500 chars nhưng output full parent) chưa kiểm tra đầy đủ pipeline mới này; chúng vẫn cảnh báo không promote reranker chỉ từ score nội bộ.

## 9. Thứ tự slot và tiêu chí dừng

Thứ tự candidate hiện hành:

1. **A — Docs-only Qwen4B:** top130 là control; dừng fixed-cutoff ladder.
2. **B — Joint Qwen top130 + P2a keep90:** đã build; đo owner-release architecture, không tune cutoff mới.
3. **C — Best-axis recombination:** đã thắng, trở thành control 0.3148.
4. **D — Qwen4B original-chunk verification:** chạy pilot/full; không đổi chunk text/segmentation.
5. **E — Translation candidate rescue:** chỉ khi P3 có known positives mới, giữ segmentation/output policy.
6. **F — Localized evidence (P2b):** đã thất bại; không quay lại threshold sweep.

A và B cùng tốt mới gộp joint pipeline, bảo đảm docs/chunks nhất quán. A thất bại: phân biệt scorer kém và floor owner docs quá cao. B thất bại: phân biệt false-negative verifier và granularity mismatch. Không tăng/giảm threshold liên tiếp chỉ theo điểm BTC.

Promote theo Final cùng evaluator, không chỉ precision. Tăng `>=0.005 Final` hoặc `>=0.01 F2 trục mục tiêu` là tín hiệu ưu tiên nguồn lực, không phải statistical significance từ aggregate scores. Giữ cải thiện nhỏ đã xác nhận nhưng không dành hàng chục slot tune quanh chúng.

## 10. P4 — Fine-tune có dữ liệu lỗi; embedding mới có điều kiện

Nếu verifier zero-shot chưa hiểu clinical relevance, tạo positive/hard-negative pairs có provenance từ corpus/nhãn hợp lệ: cùng chủ đề nhưng khác intent/population/negation. Teacher ≤15B hợp lệ, review mẫu; split query/topic/document tránh leakage. Fine-tune reranker private trước đầu tư re-embed cả corpus.

Chỉ thử encoder mới khi **known-positive candidate recall** của pooled BM25+BGE+Qwen bị giới hạn rõ, trong khi reranker trên pool bổ sung positives hoạt động tốt. Novelty hoặc benchmark model chung chưa đủ bằng chứng.

Kiến trúc đích học từ BTC/vilamiu: retrieval có quota → chấm evidence trực tiếp → tổng hợp doc → calibration membership/cardinality → source spans có ngữ cảnh. LLM xử lý nghĩa; code quản IDs/quota/offsets/cache/provenance/fallback.

## 11. Đã có, không làm lại

- Active index gần nhất khoảng 1.212.421 docs / 1.724.798 chunks. Coverage không phải ưu tiên mặc định; vẫn kiểm toán mapping/source quality.
- QuerySpec v6: 120 queries, 117 usable, 213 atoms; fallback IDs `71,270,336`; cache/resume đã chạy. Artifacts `data/audits/queryspec_pilot_v6_final/`; cache `data/cache/openrouter_queryspec_v1.sqlite`.
- P0.2 cũ **hoàn tất novelty, chưa pass relevance**: BM25 k500, novel docs/query khoảng 293.87 original, 307.14 normalized, 316.25 canonical+atoms, 328.24 atoms. Artifacts `data/audits/queryspec_bm25_pilot_v1/`. Không promote từ novelty.
- Translation production `data/query_translations/translation_production_v1.zip`; notebook `notebooks/16_translation_production_2xt4_kaggle.ipynb`.
- OpenRouter infra đã có: `src/llm/openrouter_client.py`, `src/llm/query_spec.py`, `configs/query_spec_v1.yaml`. Resume/cache/retry/provenance nằm trong code; chưa tự động có quyền dùng hosted inference cho mọi trường hợp.
- Exp138 builder/validator chỉ giữ để tái lập thất bại, không làm mặc định. [Script map](../scripts/README.md); notebook cascade 14 là nhánh retrieval sẵn có, không mặc nhiên đã có verifier P1.

## 12. Checklist trước submission

- [ ] 1.200 IDs/schema đúng; corpus doc_id hợp lệ; chunks thuộc docs output; duplicate được kiểm tra.
- [ ] Source/offset/hash đúng, không generated evidence; kiểm tra đa ngữ, token lengths, long-sentence fallback.
- [ ] Diff control: docs membership, chunk owners, count/query/doc, exact text overlap đúng biến tuyên bố khóa.
- [ ] Scorer thấy đúng input/template; cache không stale; model/tokenizer/revision/precision có provenance.
- [ ] Giả thuyết/pilot/tiêu chí bác bỏ rõ; weak labels không gọi là BTC ground truth.
- [ ] ZIP <100 MB, CRC/schema pass; không nộp no-op.
- [ ] Log đủ 7 metrics, artifact hash, thời điểm chấm, evaluator `two_sided_lcs_0.4` hoặc `unknown`; không so cross-version.
- [ ] Model/data/API đúng luật, không dữ liệu rò rỉ; người dùng tự nộp.

Tham chiếu: [luật](competition_information/), [BTC meeting insights](btc_meeting_insights_and_roadmap.md), [Mentor Day 2](./_AI_Guru__R2AI_Stage3_MentorDay_Oct_22th.pdf), [benchmark dịch](translation_benchmark_analysis_20261023.md), [vilamiu](../repos/r2ai-stage-2/vilamiu/). Các phỏng đoán cũ về số gold docs/threshold không thay thế kiểm định ở kế hoạch này.
