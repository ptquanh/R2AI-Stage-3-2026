# R2AI Stage 3 — kế hoạch private test, đóng 04/11/2026

> **Ưu tiên hiện hành — 02/11/2026:** BTC xác nhận qua người dùng private dùng lại đúng 1.200 query hiện có; hạn cuối **23:59 ngày 04/11/2026 (UTC+7)**, tối đa **5 lượt cho toàn private**, không phải mỗi ngày. Lịch public bên dưới chỉ là lịch sử/backlog. Best public đã chấm theo evaluator mới là **Exp143 — 0.3190**, không phải Exp122 cũ 0.3516. Người dùng tự upload; tạo ZIP local không tiêu tốn lượt. Chưa có kết quả private.

> Người dùng xác nhận thêm: **portal trả điểm sau mỗi lượt và BTC lấy điểm cao nhất**. Vì vậy thử nghiệm sau không thay thế điểm tốt nhất đã đạt; vẫn cần quản lý đúng quota năm lượt.

## Private — hành động ngay và phân bổ 5 lượt

### Control cố định và lần chạy đầu

- Dùng nguyên policy Exp143: docs joint Qwen4B top130 + owner floor đã kiểm chứng; chunks keep90 và bảo toàn nhóm quá dài chưa được Qwen chấm; bổ sung tối đa 5 missing-owner evidence (Exp142), rồi tối đa 3 P2a spans/query từ nhóm chunk dài nhất (Exp143). Không dùng defaults Exp50 trong `generate_best_submission.py`, không chạy Exp144 cũ chưa sửa.
- Public reference: Final **0.3190**, Docs F2/P/R **0.3731 / 0.2261 / 0.5631**, Chunks F2/P/R **0.2648 / 0.2047 / 0.3510**. Đây **không phải dự đoán điểm private**; cùng query không bảo đảm cùng tập nhãn.
- `query.parquet` SHA256 `ce13508b893bbd6b9169679d540630bc37eb5950cad08b4d5e0e5d7063670c08`; đối chiếu đủ từng ID/text với input inference trước khi tái sử dụng cache. Vì inputs giống nhau, replay lựa chọn và đóng gói từ cache; không tốn GPU để chạy lại cùng model.
- Chạy `python -m scripts.prepare_private_champion`. **Đã build/audit PASS** `submission_private01_exp143_replay.zip` (94.478.622 bytes), audit và build manifest cùng prefix; sẵn sàng nộp lượt 1, chưa có điểm private. SHA256 `14687b27b12a98777daddc290e54e2c25d310743917511866a06cee51e7c4ac3`. Builder phải dừng nếu query/cache sai provenance, prediction lệch champion, ID ngoài corpus, trùng lặp, thiếu query hoặc ZIP >=100 MB.
- Audit yêu cầu đúng 1.200 query, 183.703 doc predictions và 127.271 chunks; toàn bộ dự đoán bằng champion. Source text kế thừa artifact đã audit, spans bổ sung kiểm tra hash/offset; không gọi đây là fresh full-corpus source scan.

### Phân bổ lượt — không tiêu hết vào sweep nhỏ

1. **Lượt 1, 02/11: control Exp143 replay.** Nộp ngay sau audit; lưu ID portal, hash ZIP, trạng thái và đủ bảy metrics nếu BTC trả điểm. Mục đích thiết lập control private, không suy diễn điểm cũ sang private.
2. **Lượt 2, mục tiêu 03/11: docs-only.** Ưu tiên A0 ở mục 0.3 sau khi sửa P0: full-query lexical + original-VI dense, union control, rank fusion dựa trên score/rank thật; giữ chunks lượt 1 exact. Phải có candidate provenance, query-tail không bị cắt, owner floor rõ ràng và ETA hoàn thành trước giờ freeze. Không gộp dịch/HyDE/ICD trong lượt này. Nếu nhánh chưa đạt các kiểm tra thì chưa nộp.
3. **Lượt 3, mục tiêu 03/11–04/11: chunks-only.** Ưu tiên R3/R4: contextual evidence ranking dùng title/heading có thật và chọn source-boundary spans trên pool hiện có; giữ docs lượt 1 exact. Kiểm tra nguồn/offset, không nộp prefix hoặc text sinh; không chỉ đổi width/top-k. Chạy pilot đo runtime trước; không khởi động job full mất 2 ngày.
4. **Lượt 4, 04/11: tổ hợp hai trục nếu có bằng chứng.** Khi BTC có điểm, ghép docs tốt nhất và chunks tốt nhất; audit lại toàn bộ. Nếu chỉ một nhánh thắng thì tổ hợp có thể trùng bài đã nộp: không lãng phí lượt để nộp duplicate. Khi đó dùng cho một treatment độc lập đã kiểm tra, hoặc giữ dự phòng.
5. **Lượt 5: dự phòng kỹ thuật/thử nghiệm cuối.** Dành cho sửa lỗi submission hoặc một candidate có cơ sở rõ ràng sau các lượt trước. BTC lấy điểm cao nhất (người dùng xác nhận), nên không cần nộp lại champion để “chốt cuối”; không lãng phí lượt vào file giống hệt.

**Quy tắc quyết định bằng điểm private:** so lượt 2 và 3 với cùng lượt 1, kiểm tra trục được giữ nguyên có metrics bất biến trước khi quy kết gain. Khi cả hai trục cùng cải thiện, lượt 4 ghép winners và vẫn phải được BTC xác nhận; nếu không, dành lượt cho một giả thuyết độc lập đã kiểm tra. Không promote theo cảm giác/nhãn tự tạo; không dùng local scorer thay BTC hoặc khai thác đối chiếu đáp án/dữ liệu nhạy cảm. Nếu portal tạm lỗi không trả điểm, giữ control và không suy diễn. Không bắt buộc tiêu đủ năm lượt nếu chỉ còn các bản trùng/chưa kiểm tra.

**Mốc vận hành:** 02/11 gửi control; 03/11 ưu tiên hai thay đổi độc lập. Ngày 04/11 **18:00 dừng mở job nặng**, **20:00 chốt artifact/audit**, mục tiêu upload **trước 22:30**, còn đệm tới hạn 23:59. Model mới phải thỏa giới hạn/quy định BTC; không mua compute/API. Mỗi lần người dùng báo kết quả, cập nhật ledger và số lượt thực tế, không mặc định đã nộp khi chỉ build xong.

Ledger: [Private01 và kết quả private](experiments_log/private01_exp143_replay.md). Các mục 0–4 bên dưới là thiết kế tham khảo, không còn là yêu cầu chạy tất cả trong private.

---

> Cập nhật 29/10/2026: research AI Guru và kế hoạch Colab. Public đóng **23:59 ngày 31/10, giờ Việt Nam**, theo xác nhận người dùng. Exp143 Final **0.3190** vẫn là best đã chấm theo evaluator mới. Kaggle hết GPU; chuyển compute sang Colab Pro hiện có, không mua thêm. **Chưa khởi chạy Colab/chưa triển khai các nhánh mới.** Mục 0 và 4 là chỉ dẫn hiện hành; mô tả Exp141–144 giữ provenance lịch sử, không được chạy nguyên trạng Exp144 cũ. Người dùng tự nộp trên portal.

## 0. Làm gì tiếp — cập nhật từ AI Guru và rà soát 29/10

**Hướng chính:** sửa candidate/rank provenance → mở candidate bằng query đúng ngữ cảnh → selective rerank với evidence thân bài → chọn source spans. Không tiếp tục chạy nhiều ngày chỉ để rerank cùng pool cũ.

### 0.1. Chốt phạm vi conversational retrieval

- Query parquet chỉ có `id`, `query`, 1.200 rows; không có lịch sử hội thoại. Chỉ phân giải chủ thể/tham chiếu trong cùng query, **không nối các row thành conversation**.
- Ví dụ query 693: vợ dùng thuốc, chồng dị ứng bao cao su, có hai ý hỏi. Xóa mọi đại từ có thể làm mất chủ thể. Query 35: “kém ăn và gầy” không được rewrite thành chẩn đoán “suy dinh dưỡng”.
- Đã đọc AI Guru Advanced RAG01/02/05/06/10/11 và xác minh đúng [tài liệu24 — Conversational Retrieval](aiguru_24_conversational_retrieval.pdf), đối chiếu repo tác giả. Demo24 dùng TF-IDF char n-gram + rewrite bằng luật trên17 điều luật, không LLM; không là bằng chứng gain trên R2AI. Giữ câu độc lập, rewrite có căn cứ, log từng tầng; không copy history[-1], ngưỡng0.35 hoặc top1 output sang bài thi. Fanpage người dùng gửi bị hạn chế truy xuất, chưa audit toàn bộ tài liệu fanpage.
- [Research, nguồn trực tiếp và thiết kế R1–R5](aiguru_retrieval_research_20261029.md). Đây là kiến trúc thích nghi cho bài thi, không phải tái tạo baseline BTC hoặc lời hứa tăng điểm từ tutorial.

### 0.2. P0 — Sửa tiền đề trước mọi bài nộp mới

- Khóa ZIP/hash Exp143, phiên bản evaluator và input manifests; giữ Exp142 fallback. Active index hiện hành là **BGE-M3**; Qwen là index thứ hai, phải dùng đúng encoder riêng.
- Dựng thứ hạng Qwen từ `qwen_score`; `stable_joint_docs` giữ thứ tự retrieval gốc sau lọc nên `relevant_docs` **không phải Qwen rank**. Sửa assumption trong `fuse_current_and_dense` trước dùng RRF.
- Bỏ cắt first-24 terms trong BM25 mới; rà soát tokenizer VI/EN/ZH và cache fingerprint. 419/1.200 query vượt 24 từ phân biệt theo kiểm tra lexical; đây là nguy cơ mất ý cuối, chưa là bằng chứng tăng F2 sau sửa.
- Join audit translation theo ID và xác minh query text/hash; không dùng 103 EN/485 ZH `needs_review` như view đã xác nhận. `status=ok` vẫn cần audit ngữ nghĩa, không phải gold.
- Chuẩn hóa tổng trọng số atom theo nhóm sau dedup: VI 0.75, EN 0.25, ZH 0.25, chia cho số view hợp lệ trong nhóm; không dùng `1/sqrt(n)` với lời khẳng định tổng weight cố định.
- Audit 60 query cố định, gồm ngắn/dài/nhiều ý/thuật ngữ/negation/tuổi-thai kỳ. Kiểm tra source đầu–giữa–cuối, doc_id/PMID, text truncation, boilerplate và cache query/model. Đây là diagnostic, không tạo scorer thay BTC.

### 0.3. Hàng đợi thử nghiệm hiện hành

Mã A/R/B/C là nhánh thiết kế; chỉ cấp số Exp khi build artifact. Mỗi nhánh mới giữ nguyên trục không thử; không gộp mọi thay đổi rồi quy kết gain cho rewrite.

1. **A0 — Original-VI retrieval sửa lỗi, docs-only.** BM25 đầy đủ query, union docs control, cap 2.000 new candidates/query, exact BGE-M3 top400; fusion với rank Qwen thật bằng RRF k=60, weights 1.0/1.25, top130 + chunk-owner floor. Giữ chunks Exp143 exact.
2. **A1/A2/A3 — EN-only, ZH-only, EN+ZH.** Mỗi bài so với cùng A0, chỉ thêm view dịch đã audit, tổng weight 0.35/ngôn ngữ; query gốc luôn giữ. Không đổi chunking hoặc rerank prompt. Đây là phép thử dịch sạch, không lặp confound Exp137.
3. **R1 — Gated grounded standalone rewrite.** Sau A0, chạy song song chuẩn bị với A1–A3; thêm tối đa một view VI giữ chủ thể/ý hỏi, weight0.5. Theo bài24: query đã rõ giữ nguyên; chỉ rewrite tham chiếu có antecedent trong cùng query, diễn đạt lặp hoặc biến thể từ vựng đã xác minh. Log lý do/source spans, không trigger chỉ bằng “vậy/còn”; fallback khi bất định. Dùng model hợp lệ trên Colab, không mua API. So với nhánh A tốt nhất, chunks bất biến; nhiều ý để R2 xử lý, không gộp vào R1.
4. **R2 — Facet-balanced retrieval.** Thay thế việc chạy A4/QuerySpec cũ không kiểm soát: tối đa ba ý hỏi có source spans, tổng weight 0.75; dành tối đa 50 candidate slots/facet trước cap2.000. Không ép mọi doc trả lời mọi ý. So với R1 trên cùng control; không thêm dịch mới trong lần này.
5. **A5/B1 — Ensemble Qwen index, rồi selective Qwen4B rerank.** Hai bài riêng: trước thêm nguồn Qwen đúng encoder; sau chỉ chấm tối đa 16 docs mới +16 docs ranh giới/query, tận dụng cache đúng fingerprint. Không rerank cả corpus/pool cũ. Giữ policy docs/chunks để đo tác động riêng.
6. **R3/B2 — Context-aware evidence reranking.** Nâng ưu tiên từ AI Guru: cùng pool và body spans, A/B chunk thô với title+heading nguồn (tổng tối đa64 tokens)+chunk; body budget giống nhau. Đây là bản nhẹ contextual retrieval, không re-embed corpus và không cần sinh prefix. Thử docs-only trước; namespace cache mới, chunks control không đổi.
7. **C1 rồi R4/C2 — Evidence coverage và source-boundary selection.** C1 thêm tối đa một evidence/doc từ năm docs mới chưa có chunk/query, giữ chunks cũ. R4 là bài riêng giữ docs và count, thay tối đa10 chunks/query theo bất đồng raw/context; section/paragraph cùng source, <=768 tokenizer tokens, cắt theo câu/offset. Không xuất prefix, summary hoặc ghép câu rời.
8. **D/R5 dự phòng:** BGE-M3 late interaction trên shortlist → một-hop rescue trong corpus cho facet thiếu support → HyDE giới hạn → ICD soft-routing nếu metadata đã audit. Chỉ chạy khi A–C đã có kết quả và budget phù hợp; không hard-filter ICD/global, không mở GraphRAG hay memory service mới.

**R6 — CPU dự phòng bổ sung từ bài24:** char n-gram TF-IDF trên fixed shortlist400 của nhánh thắng, không reindex corpus. Chỉ thêm lexical rank weight0.25 vào control rank1.0, RRF60, cùng top130+owner floor và chunks exact. Fit unique source representations, không fit query; giữ dấu, title+section nguồn, benchmark60 query với ETA<=1h. Kiểm tra tên thuốc gần giống/typo gây false positives; không áp cosine threshold hoặc coi char n-gram giải được đồng nghĩa. Đặt sau các bài A/R1–R3 có ưu tiên, có thể làm khi GPU bận. Chi tiết ở research; chưa triển khai/chưa có điểm.

R1 và R2 là hai ablation khác nhau: rewrite cùng ý vs tìm nhiều ý. Parent–child tách đơn vị tìm kiếm, đọc hiểu và output; không mặc định nộp parent dài hoặc child ngắn nhất. Chi tiết schema, fallback, caps và nguồn ở [research](aiguru_retrieval_research_20261029.md).

### 0.4. Tiêu chí giữ/loại và an toàn

- Chỉ promotion bằng bảy metrics BTC cùng evaluator. Hai bài có đối chứng không cải thiện cùng giả thuyết thì dừng; không dùng semantic plausibility, novelty hoặc cosine cao làm bằng chứng tăng F2.
- Docs-only phải giữ chunks exact; chunks-only phải giữ docs exact. Nếu trục bất biến đổi điểm, kiểm tra hash/file/evaluator trước diễn giải.
- Chỉ dùng corpus BTC và chunk nguyên văn; contextual prefix/HyDE/rewrite là input retrieval/scorer, không là evidence nộp. Không dùng web rescue ngoài corpus như tutorial CRAG.
- Mọi model riêng lẻ <=15B, base phát hành trước01/08/2026; không mặc định model API trong ví dụ AI Guru hợp lệ. Checkpoint hậu mốc private/local; không dùng leaked judge answers hay nhãn ChatGPT như gold.
- Model score không phải xác suất đã calibration; không áp ngưỡng 0.4/0.8 hoặc số relevant docs từ tutorial. Mốc top1 0.4235 do người dùng cung cấp là tham khảo, không bảo đảm cùng evaluator hay là best ẩn.

## 1. Control và quyết định hiện hành

- **Best theo evaluator mới: Exp143, Final 0.3190.** Docs F2/P/R: `0.3731 / 0.2261 / 0.5631`; Chunks F2/P/R: `0.2648 / 0.2047 / 0.3510`.
- Artifact: `submission_exp143_p2a_long_chunks_add3.zip`, 94.478.622 bytes; SHA-256 `039eb431209008b00eeb7b8df76b4d784c20a677c1b375444a167bf19f229649`.
- So với Exp142, Docs bất biến; chunk F2 `+0.0009`, precision `-0.0022`, recall `+0.0030`, Final `+0.0005`. Gain nhỏ, nhưng BTC đã xác nhận Exp143 là best. Giữ Exp142 làm fallback.
- Exp139 vẫn là fallback sạch nếu artifact Exp142 không khả dụng: Final 0.3161, hash `593a846ffdbe3e1fe2eaf4f8dd1f65c7e05728d6594a9926b229105531a92549`.
- Exp140 keep80 đạt `0.3154`: precision chunk cao hơn nhưng recall/F2 thấp hơn. **Dừng sweep keep fraction, top-k gần nhau và chạy lại Qwen toàn bộ.**
- Reference trước filtering: best-axis `0.3148`, hash `b6bc6b304a8ccf5d55ebffdfd55e49633ab6822c1736556be65d8438a1e5215d`. Giữ để tái lập. Không dùng mặc định cũ của `generate_best_submission.py` như thể đó là Exp139.
- Điểm BTC là tiêu chí chọn; không dùng synthetic dev set hoặc nhãn ChatGPT làm gold. Ghi đủ bảy metrics và hash từng artifact. [Kết quả Exp139–140](experiments_log/exp139_qwen4b_chunks_keep90.md).
- Nếu Docs F2 vẫn 0.3731 thì muốn Final 0.38 cần Chunks F2 ít nhất **0.3869**, tức tăng 0.1221 so với Exp143. Không có bằng chứng để hứa mức này từ thêm cutoff nhỏ.

## 2. Hai khoảng trống đã kiểm tra trên artifact

[Structural inventory](../data/audits/final_public_sprint_20261027/structural_inventory.json) xác minh hash JSON reference và dùng các score cache hiện có. Đây là thống kê cấu trúc, không phải relevance evaluation.

- Docs hiện tại: **183.703 query–doc pairs**. Top130 thuần theo cùng Qwen score có 156.000 pairs và là tập con của docs hiện tại. **27.703 pairs còn lại được giữ do owner protection** kế thừa từ P2a.
- Trong docs hiện tại có **61.906 pairs không có chunk ở tập 130.108 chunks ban đầu**; cả 1.200 queries đều có trường hợp này. Sau keep90, số pairs không có chunk là 70.631.
- Vì vậy có thể thử bổ sung tối đa 5 missing-owner docs/query, tức tối đa 6.000 additions, mà không khôi phục các chunk đã bị Qwen loại.
- Không được gọi các pairs này là false positives, gold docs hay evidence chắc chắn. Chỉ BTC mới cho biết treatment có tốt hơn.

## 3. Bốn thử nghiệm chính

Mỗi thử nghiệm có một giả thuyết và đối chứng cụ thể. Exp141 đã bị loại. Exp143 là control hiện hành. Exp144 là kiến trúc retrieval riêng nhưng chỉ thay docs; toàn bộ chunks Exp143 được giữ nguyên để tách hiệu ứng retrieval khỏi chunking.

### Exp141 — Bỏ owner floor ở docs (đã chấm; không promote)

**Câu hỏi:** các docs được giữ chỉ vì chúng có chunk có đang làm giảm Docs F2?

- Giữ chính xác top130 theo Qwen4B đã có; bỏ điều kiện union thêm chunk owners. Không thay k, scorer, candidate pool hay chunks Exp139.
- Docs giảm từ 183.703 xuống 156.000 pairs; loại đúng 27.703 pairs ngoài top130. Đây là ablation của điều kiện giữ docs, không phải một bước top-k ladder mới.
- Dùng `data/audits/p1_full_qwen4b_merged/p1_full_qwen4b_merged.parquet`. Không GPU; dự trù **1–2 giờ** cho builder, audit, đóng gói.
- Chunks metrics phải giữ nguyên. Nếu Docs F2 tăng, lấy docs này làm lựa chọn mới; nếu giảm thì giữ docs Exp139 và dừng nhánh owner-release. Không thử 125/135 để cứu giả thuyết.
- Candidate đã được tạo tại `submission_exp141_qwen_top130_keep90.zip`, 88.621.741 bytes, SHA-256 `8a65382eb9497c2f43084ce405dbd56aaaa17a7e15e9fcd9df14d18586f571d2`. Audit độc lập pass: 1.200 queries, 156.000 docs khớp Qwen top130, mọi ID thuộc corpus, chunks khớp exact Exp139 (117.835). Chi tiết `data/audits/final_public_sprint_20261027/exp141_audit.json`.
- BTC: Final **0.3094**, Docs F2/P/R `0.3596 / 0.2356 / 0.5226`; Chunks F2/P/R `0.2591 / 0.2101 / 0.3369`. So với Exp139, Docs F2 `-0.0135`, precision `+0.0095`, recall `-0.0405`; Chunks giữ nguyên; Final `-0.0067`. Kết luận: owner floor đang giúp recall/F2; đóng nhánh bỏ owner floor, không thử thêm top-k khác.
- Risk: các owner docs có thể thật sự liên quan; precision tăng một mình không đủ để promote.
- Điều kiện kỹ thuật: chứng minh chunks exact, docs đúng subset/corpus IDs; chunk owner vẫn đúng tài liệu nguồn dù không xuất hiện trong `relevant_docs`, theo đặc tả và các lần chấm hai trục độc lập hiện có.

### Exp142 — Thêm evidence cho docs đã tìm thấy nhưng chưa có chunk

**Câu hỏi:** một phần chunk recall đang mất vì pipeline không xuất evidence cho docs đã trả về?

- Giữ docs và toàn bộ chunks Exp139. Chỉ xét docs thuộc danh sách trả về nhưng **chưa có bất kỳ chunk nào trong tập gốc 130.108 chunks**; không dùng các docs chỉ vừa mất chunk vì keep90.
- Xếp các docs còn thiếu bằng rank fusion đồng trọng số Qwen4B/BGE P1, RRF k=60, trên cùng pool 216 docs/query. Chọn tối đa **5 docs/query**, không ép đủ khi thiếu nguồn hợp lệ.
- Xuất một parent nguyên văn/doc theo cách lấy source parent của Exp122, khóa doc_id/source hash/offset. Đây là thử nghiệm coverage; không gán reranker passage score thành xác suất đúng của toàn parent.
- Tối đa 6.000 additions. Kiểm tra toàn bộ chunks Exp139 vẫn còn, không duplicate. Mục tiêu ZIP ≤95 MB, bắt buộc <100 MB. Nếu quá dung lượng, giảm quota đồng loạt trước lần nộp đầu và ghi policy thực tế; không cắt text tùy tiện.
- Dùng score cache và text corpus hiện tại. Không GPU; dự trù **2–4 giờ**, phụ thuộc source lookup.
- Dưới quy tắc matching đã mô tả, thêm chunk và giữ toàn bộ chunk cũ không được làm recall giảm. Nếu BTC trả recall thấp hơn, kiểm tra artifact/evaluator trước diễn giải về retrieval.
- Chọn theo Chunks F2/Final; additions làm precision giảm vẫn có thể hữu ích nếu recall bù được. Nếu F2 giảm, bỏ treatment; không sweep add3/add7 theo public score.
- Builder `scripts/build_final_sprint_exp142_missing_parents.py` đã tạo `submission_exp142_missing_owners_add5.zip`. Manifest: 94.214.806 bytes, 5.708 unique parents được dùng để tạo 6.000 chunk additions (5/query), 117.835 chunks Exp139 được giữ nguyên, 123.835 tổng chunks. SHA-256 `7b545b65765c528e1abb708a89bd65be1ef57f507f04c101fc722bc094627a82`. Audit độc lập pass: CRC, corpus IDs, missing-owner eligibility, nguyên văn so với active index, docs không đổi và chunks control là prefix nguyên vẹn. Báo cáo: `data/audits/final_public_sprint_20261027/exp142_audit.json`. Risk: missing-owner docs chưa chắc relevant; full parent có thể dài đối với matching.

### Exp143 — Thêm P2a short spans cho chunk dài (đã chấm; best hiện tại)

**Câu hỏi:** có evidence đúng trong parent dài nhưng không khớp vì tỷ lệ token chung phía prediction quá thấp?

- Giữ nguyên toàn bộ docs/chunks Exp142. Chỉ append tối đa **3 cửa sổ/query**, không thay thế hoặc sửa chunks đang có.
- Nguồn là P2a windows đã được BGE chấm trên các chunks thuộc đúng control P1 cũ. Chỉ dùng window khi `chunk_sha256` khớp chính xác chunk hiện tại; audit xác nhận P2a offset cắt đúng source text.
- Chọn 10% chunks dài nhất trong exact-hash matches (cutoff 7.152 chars), lấy window điểm P2a cao nhất mỗi chunk, rồi tối đa 3/query theo normalized score. Điểm này là ranking proxy, không phải xác suất relevance.
- Candidate `submission_exp143_p2a_long_chunks_add3.zip`: 1.200 queries; 183.703 docs; giữ 123.835 chunks Exp142 và append 3.436 spans; 127.271 chunks tổng; ZIP 94.478.622 bytes; SHA-256 `039eb431209008b00eeb7b8df76b4d784c20a677c1b375444a167bf19f229649`.
- Audit pass: docs bất biến, toàn bộ chunks Exp142 là prefix nguyên vẹn, không trùng chunk trong query, ZIP CRC hợp lệ. Builder cũng xác minh mỗi span đúng source slice bằng offset/hash. Báo cáo `data/audits/final_public_sprint_20261027/exp143_audit.json`.
- BTC: Final **0.3190**, Docs F2/P/R `0.3731 / 0.2261 / 0.5631`; Chunks F2/P/R `0.2648 / 0.2047 / 0.3510`. So với Exp142, Final `+0.0005`, chunk F2 `+0.0009`, recall `+0.0030`, precision `-0.0022`. Keep Exp143; dừng thêm sweep P2a window/cap.
- Nếu recall không tăng hoặc F2 giảm, dừng nhánh bổ sung độ dài. Không thử tiếp hàng loạt width 384/512/768.
- Risk: tăng số predictions làm precision giảm; chưa có gold spans nên đây vẫn là giả thuyết về matching.

### Exp144 — QuerySpec candidate expansion → exact BGE-M3 docs rerank

> **Trạng thái lịch sử 27/10, bị chặn bởi P0 ngày29/10:** pool/input đã tạo nhưng chưa có điểm BTC. Các mô tả weights/rank bên dưới ghi lại implementation cũ, không là cấu hình được duyệt để chạy tiếp. Rebuild candidate/cache sau sửa P0; tiếp tục bằng các ablation mục0.3 trên Colab.

**Câu hỏi:** reranker hiện tại có bị khóa trong candidate pool cũ, khiến mọi lần sau chỉ tối ưu precision/recall trong cùng một tập docs thiếu coverage?

- QuerySpec production đã chạy qua OpenRouter nhưng dừng do HTTP 402. Finalizer chỉ nhận record hợp lệ, ưu tiên production rồi pilot đã audit, và fallback query gốc cho phần còn lại: **401/1.200 QuerySpec usable**, 15 fallback Exp122, 784 fallback original; không dùng output lỗi/402. Audit pass với usable rate 33,42%, 660 evidence atoms và đủ 1.200 query IDs.
- Implementation cũ: original VI weight1.0; production EN/ZH0.35; canonical VI0.70, QuerySpec EN/ZH0.35; mỗi atom VI `0.75/sqrt(n)`, EN/ZH `0.25/sqrt(n)`. **Đính chính29/10:** tổng weight tăng theo sqrt(n), không bị chặn cố định; production translation chưa join status audit. P0 sửa hai vấn đề trước rebuild.
- Reuse exact original-VI BM25 cache; chỉ search các view mới. Pool đã hoàn tất: 1.472.936 pairs, trung bình 1.227 docs/query, min/median/max `548/900/2.000`; đủ 1.200 query, rank liên tục, không duplicate và không có doc ngoài corpus. Novelty chỉ chứng minh pool thay đổi, không phải relevance.
- Notebook `notebooks/23_exp144_queryspec_dense_2xt4_kaggle.ipynb` encode **query gốc tiếng Việt** bằng `BAAI/bge-m3`, union candidate mới với docs Exp143, rồi exact max-chunk dense-score trên vector index hiện hành. Query expansion chỉ mở recall; nó không trực tiếp quyết định thứ tự cuối.
- Notebook chia vector shards trên 1–2 T4, checkpoint atomic mỗi 25 query với fingerprint input/index/model/query IDs, và chỉ xuất top400 docs/query cùng diagnostics. Không tạo passages/chunks mới.
- Kaggle input đã đóng gói tại `data/kaggle_inputs/exp144_queryspec_dense_input.zip`: 10.915.573 bytes, SHA-256 `1b8036dba9b2e8cd4c9afba61a6e2a35e2044d5644b4e60793cb1b860640d7fd`. Exp143 control được chuyển thành rank-preserving docs Parquet (183.703 pairs) để không nhúng ZIP 94 MB; audit xác nhận danh sách docs giống hệt control.
- Builder cũ giữ **127.271 chunks Exp143**, gating401 query usable và799 fallback. Nó fuse thứ tự docs Exp143 với dense mới (weights1.0/1.25, RRF k=60), top130 rồi union chunk owners. **Đính chính29/10:** thứ tự docs Exp143 không phải Qwen rank; phải lấy rank từ score cache. `status=ok` không chứng minh rewrite đúng ngữ nghĩa. Chưa duyệt chạy `fused130_owner_gated` nguyên trạng.
- Các policy `add5`, `dense90`, `dense130`, `dense130_owner`, `dynamic4` chỉ là ablation/safety; `dynamic4` dựa trên `expected_max_docs` do LLM ước lượng nên **không phải lựa chọn nộp đầu tiên** khi chưa calibration.
- Trình tự nộp cũ đã được thay bằng P0 → A0 → A1–A3/R1–R2 ở mục0. Không nộp mọi policy như sweep mù; ranking có bất thường kỹ thuật phải sửa, không chỉ đổi policy để bỏ qua lỗi.
- Risk: chỉ 33,42% query có QuerySpec; translation/atoms có thể thêm nhiễu. Giảm risk bằng original-query dense rerank và giữ chunks control. Chỉ BTC xác nhận Docs F2/Final; không hứa tăng điểm trước khi chấm.
- Exp130 cũ (`notebooks/14_bm25_dense_passage_cascade_kaggle.ipynb`) được giữ làm archive/ablation nhưng không còn là next action vì nó đồng thời đổi docs và chunks, khó quy nguyên nhân.

## 4. Thứ tự làm và ngân sách submission

**Chuẩn bị:** người dùng đăng nhập [Colab Pro](https://colab.research.google.com/), tự thực hiện OAuth/Drive consent. Kiểm tra GPU/CU thực tế; không mặc định2xT4, không mua thêm, không public tunnel. Local xử lý BM25/cache/ZIP và ưu tiên exact dot-product mmap; Colab chỉ encode/rerank/generation cần GPU. Upload input tối thiểu, không model cache hay toàn index mặc định. Loader hỗ trợ cả ZIP lẫn thư mục đã extract; checkpoint atomic theo manifest/hash, retry hữu hạn, resume không lặp pairs.

**29/10 — còn10 slots lúc lập plan:** P0 → A0 → ba translation ablations → R1 → R2 → A5 → B1 → R3 → recombination nếu kịp. Đây là hàng đợi có điều kiện, không hứa hoàn tất cả10 trong ngày. Chuẩn bị các nhánh CPU song song, nộp ngay khi artifact audit pass; không chờ cả batch, không nộp file trùng để lấp slot. R1–R3 đưa kiến trúc mới vào sớm hơn sweep tham số.

**30/10:** hoàn tất selective rerank/evidence; C1/R4; late interaction và R5 chỉ khi còn budget. Ablation bỏ thành phần trên nhánh thắng để giải thích gain; giữ hai slot cuối cho recombine/khắc phục bất thường. Hai trục thắng riêng vẫn cần nộp xác nhận bản ghép.

**31/10:** chỉ artifact có cache và audit trong khoảng một giờ; không mở job GPU mới sau18:00; chốt cấu hình20:00, mục tiêu nộp cuối trước22:30, deadline23:59 giờ Việt Nam. Dành hai slot dự phòng giai đoạn chốt. Không full embedding/fine-tune/rebuild model mới.

**Compute gate:** benchmark512 pairs trước Qwen4B. ETA >4h thì giảm caps đều16+16 →8+8 →4+4 docs/query; vẫn quá thì hoãn, không silently đổi model/prompt hay rerank kéo dài hai ngày. R5 budget<=2h. Chạy một GPU cũng được; batch theo VRAM, không CPU offload âm thầm. Mỗi job xuất scores+manifest+diagnostics, không tải weights về local.

**Sau mỗi artifact:** gửi người dùng link ZIP, bytes/hash, control, hypothesis, audit pass và nhắc nộp; nhận đủ bảy metrics → cập nhật experiment log → giữ/loại/chọn nhánh kế. Không tự submit. Chấp nhận gain nhỏ có bằng chứng nhưng ưu tiên compute lớn cho mở coverage/khôi phục ngữ cảnh, không tiny-k ladder.

## 5. Tài nguyên, điều kiện nộp và phần hoãn

Artifacts dùng lại:

- Docs scores: `data/audits/p1_full_qwen4b_merged/p1_full_qwen4b_merged.parquet` và `data/audits/p1_full_bge_merged/p1_full_bge_merged.parquet`, mỗi file 259.200 query-docs.
- Chunk scores: `data/audits/qwen4b_chunks_full_merged/qwen4b_chunk_scores_full.parquet`, 130.108 pairs; P2a windows/score ở `data/kaggle_outputs/p2a_chunk_full/p2a_chunk_full/`.
- Translations: `data/query_translations/translation_production_v1.zip`. Chỉ dùng rows/status/source query hash hợp lệ.
- Active index: `data/indices/new_dataset/index/`; không re-embed/rebuild mặc định. [Script map](../scripts/README.md).

Mỗi artifact phải đủ 1.200 query IDs, đúng corpus doc_id, không duplicate và nguồn chunk nguyên văn. So sánh docs/chunks/count/owners với đúng control; hash/cache khóa theo input, model, revision và prompt. ZIP <100 MB, CRC/schema/source checks pass. Local checks chỉ kiểm tra code/data; điểm BTC quyết định chất lượng.

Luật áp dụng: model riêng lẻ ≤15B, base model phát hành trước 01/08/2026, checkpoint fine-tune sau mốc phải private/local; không dùng dữ liệu đáp án bị lộ. Bản `competition_information/2_evaluation.md` còn mô tả LCS một phía; thông báo BTC do người dùng cung cấp và re-eval Exp122 xác nhận hiện yêu cầu ≥40% **cả hai phía**. Không so kết quả legacy với evaluator mới. Người dùng tự nộp qua tài khoản đội đã được BTC duyệt.

Model Qwen4B hiện có hỗ trợ reranking đa ngữ và instruction; trong sprint giữ nguyên template/revision đã audit. [Model card chính thức](https://huggingface.co/Qwen/Qwen3-Reranker-4B). Không dùng normalized score như xác suất relevance đã calibration.

Hoãn sau public: re-embed toàn corpus, fine-tune không có dữ liệu đáng tin, full multihop/GraphRAG/memory service mới, đổi sang model lớn để chạy lại130k chunks, sweep threshold/width. Cho phép R5 một-hop corpus-only theo caps ở research, không agent loop không giới hạn. Không mua thêm API generation; query transformation mới dùng Colab quota hiện có và model hợp luật. Hạng/điểm top1 người dùng cung cấp chưa được xác minh độc lập; không dùng suy đáp án hoặc hứa điểm đích.

## 6. Lịch sử và căn cứ

- [Plan chi tiết trước sprint cuối](archive/r2ai_score_improvement_plan_pre_final_sprint_20261027.md): giữ lịch sử P0/P1/P2/P3 và toàn bộ audit cũ; các ưu tiên/trạng thái chờ trong bản lưu không còn điều khiển sprint này.
- [Experiment log](experiments_log.md), [Exp139–140](experiments_log/exp139_qwen4b_chunks_keep90.md), [Exp122 re-eval](experiments_log/exp122_exp121_add19_missing_doc_parents.md), [P2b thất bại](experiments_log/p2b_bge_paragraph_localization.md), [Exp137 và confound dịch/chunking](experiments_log/exp137_translation_chunks_fixed_docs.md).
- [Luật BTC](competition_information/5_policy_and_rules.md), [định dạng submission](competition_information/3_submission_instructions.md), [Mentor Day 2](./_AI_Guru__R2AI_Stage3_MentorDay_Oct_22th.pdf).
- [AI Guru research29/10: nguồn, ví dụ query, R1–R5 và kiểm tra luật](aiguru_retrieval_research_20261029.md). Research bổ sung không đồng nghĩa đã triển khai hoặc đã có gain BTC.

Exp141/142/143 ZIP và audit pass; Exp141 bị loại; Exp143 là best đã chấm Final0.3190. Exp144 có code/notebook/input lịch sử nhưng cần P0/rebuild provenance trước chạy tiếp trên Colab. R1–R5 hiện là kế hoạch, chưa chạy/chưa có điểm. Lượt research này chỉ cập nhật tài liệu, không khởi chạy compute hoặc thay submission.
