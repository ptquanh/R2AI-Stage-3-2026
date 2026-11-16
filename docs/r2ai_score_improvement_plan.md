# R2AI Stage 3 — hồ sơ BTC, UI và chốt private

> **Kế hoạch hiện hành, 03/11/2026.** Hạn nộp private và bộ thuyết minh: **23:59 ngày 04/11/2026, giờ Việt Nam**. Người dùng xác nhận đã nộp **1/5 lượt**, private không công bố điểm trước khi kết thúc. Thông tin “trả điểm từng lượt” trong kế hoạch ngày 02/11 đã bị đính chính, không còn dùng để ra quyết định. Quy tắc lấy điểm cao nhất giữ theo xác nhận trước đó.
>
> **Thứ tự thực hiện:** hồ sơ theo 5 mục email + khả năng tái hiện → UI minh chứng + slide → thử nghiệm bổ sung nếu còn thời gian. Email không quy định riêng UI hay số slide; UI là yêu cầu bổ sung của người dùng, slide hỗ trợ thuyết minh và Demo Day. Không được dùng UI/slide thay cho data, checkpoint, source hoặc README.
>
> **Trạng thái 03/11:** Exp143 replay đã build/audit và người dùng xác nhận đã nộp; **chưa có điểm private**. Release CLI, UI review local, báo cáo kỹ thuật, slide PPTX/PDF, manifest, source ZIP và clean-room validation đã hoàn tất. Việc còn lại cần người dùng thực hiện là đóng gói/upload data-index, kiểm tra link bằng phiên ẩn danh, điền thông tin liên hệ, gửi email BTC và lưu bằng chứng gửi. Compute: local + Colab Pro hiện có, không mua thêm.

## A. Việc làm trước và tiêu chí hoàn thành

1. [x] Khóa release Exp143, truy ngược dữ liệu/model/code/cache thực sự tạo bài nộp; dùng chung `configs/release_exp143.json` cho CLI và UI.
2. [x] Viết đủ năm phần hồ sơ BTC; dựng model registry, artifact manifest, access checklist và email nháp.
3. [x] Dựng UI review chạy local, hiển thị query, document, chunk, URL và exact source provenance; UI công bố rõ đây là replay, không phải chẩn đoán hay fresh inference.
4. [x] Chụp UI thật; tạo slide pitching editable 15 trang và bản PDF; tạo báo cáo kỹ thuật Markdown/PDF 5 trang; rà toàn bộ trang về font, tràn lề và nội dung.
5. [x] Giải nén `source_release.zip` vào thư mục sạch: 8 test pass sau khi thêm graph UI; `verify` khớp 1.200 query, 183.703 docs, 127.271 chunks và bốn SHA256 đã khóa. Bằng chứng: `deliverables/stage3_20261104/clean_room_validation.md`.
6. [ ] **Người dùng:** đóng gói/upload data và active index theo manifest; điền Drive URL + thông tin liên hệ; kiểm tra link bằng phiên không đăng nhập; gửi email BTC và lưu timestamp.
7. Chỉ chạy các treatment private ở mục G khi không làm chậm bước 6. Nếu xung đột thời gian, dừng treatment, không giảm yêu cầu hồ sơ.

**Bộ nộp kỹ thuật đã tạo** tại `deliverables/stage3_20261104/`: `README.md`, `technical_report.md/pdf`, `presentation.pptx/pdf`, `source_release.zip`, `artifact_manifest.json`, `model_registry.json`, `access_checklist.md`, `email_draft.md`, `clean_room_validation.md`; kèm các gói data/index/cache riêng do người dùng upload lên Drive. `artifact_manifest.json` là nguồn chuẩn về bytes/SHA256; active index hiện vẫn là directory 15,681,022,446 bytes và cần đóng gói trước khi upload.

**Control:** Exp143, public evaluator mới Final **0.3190**; Docs F2/P/R **0.3731/0.2261/0.5631**; Chunks F2/P/R **0.2648/0.2047/0.3510**. File private đầu tiên `submission_private01_exp143_replay.zip`, 94.478.622 bytes, SHA256 `14687b27b12a98777daddc290e54e2c25d310743917511866a06cee51e7c4ac3`. Không dùng 0.3516 của Exp122 evaluator cũ làm best hiện tại. [Ledger Private01](experiments_log/private01_exp143_replay.md).

## B. Hồ sơ đáp ứng từng mục email BTC

### B1. Email 1.1 — Tổng quan hệ thống

**Đầu ra:** chương 1–3 báo cáo, sơ đồ editable, slides 2–3 và 6–9; README có phần kiến trúc.

- Mô tả đúng bài toán retrieval y khoa VI/EN/ZH: input query, output `relevant_docs` và `relevant_chunks`; không giới thiệu như một bác sĩ AI sinh chẩn đoán.
- Hai luồng kiến trúc: offline (corpus → làm sạch → chunk/offset → embedding/index) và online (query → retrieval/fusion → reranking → docs/chunks → validation → ZIP/UI).
- Với mỗi thành phần, ghi input/output, model hoặc thuật toán, cấu hình, cache và điều kiện fallback.
- Mô tả lineage champion: retrieval gốc và Qwen embedding bổ sung; P1 Qwen4B docs; owner protection; Qwen4B keep90 chunks; Exp142 missing-owner parents; Exp143 P2a source spans.
- Phân biệt BGE-M3 learned sparse với BM25. Không tự ghi “BM25/ICD production” chỉ vì repo có code thử nghiệm.
- Tách thành phần thực sự dùng trong champion, nhánh đã thử nhưng không giữ, và ý tưởng chưa triển khai. Sơ đồ phải khớp code/config release, không phải kiến trúc mong muốn.

**Nghiệm thu:** lần theo được một query từ input đến các doc_id/source spans trong output; tên component trên sơ đồ ánh xạ được sang entrypoint/config.

### B2. Email 1.2 — Dữ liệu và quyền truy cập

**Đầu ra:** chương dữ liệu, data README/manifest, gói Drive, slides 4–5 và phụ lục A3.

- Khóa SHA của corpus/query BTC; mô tả URL, doc_id/PMID, ngôn ngữ, crawl status, source text và schema chunk offsets.
- Tính lại số liệu từ snapshot release: URL hợp lệ, crawl thành công/thất bại, document có text, document indexed, chunks và phân bố ngôn ngữ. Không lấy số cũ 1 triệu/4,4 triệu hoặc coverage nhãn suy đoán.
- Manifest active hiện ghi 1.212.421 docs, 1.724.798 chunks; đây là số của index, **không chứng minh coverage đáp án**. Phải kiểm tra lại khi khóa release.
- Ghi cách xử lý redirect Pharmacity nhưng giữ doc_id gốc, duplicate URL, ngoài corpus, challenge/404, nội dung quá ngắn và sửa filter notebook. Không biến các trang lỗi thành văn bản giả.
- Bàn giao text snapshot dùng thực tế; crawl lại web hiện tại chỉ là hướng dẫn mở rộng, không phải điều kiện duy nhất để BTC tái hiện.
- Share tối thiểu corpus mapping, text sạch, chunk offsets, registry/manifests và cache cần thiết. Index cung cấp một representation chuẩn cùng lệnh rebuild, tránh đóng gói FAISS và vector gốc trùng nhau khi không cần.
- Data/model không nhét vào source ZIP. Không upload backup index, file tạm, optimizer, model download cache hoặc credentials.
- Gói chia theo chức năng; mỗi gói có size, SHA256, nơi giải nén, link Drive và dependency. Đo tổng size trước upload, chỉ bỏ dữ liệu dẫn xuất có thể rebuild, không bỏ nguồn cần nghiệm thu để vừa quota.
- Kiểm tra quyền tải bằng phiên không đăng nhập, tải thử file và đối chiếu checksum. Với nguồn hạn chế chia sẻ, xin quyền BTC phù hợp và ghi rõ, không mặc định public toàn bộ corpus.

**Nghiệm thu:** người ngoài đội tải được các file được chỉ dẫn và tìm đúng văn bản của doc_id bất kỳ trong bài nộp.

### B3. Email 1.3 — Mô hình/checkpoint/API

**Đầu ra:** model registry, chương mô hình, slides 10/A2.

- Truy vết đủ mọi model thực sự có ảnh hưởng đến release, kể cả embedding/query translation ở upstream, không chỉ các reranker cuối.
- Mỗi model ghi vai trò, ID, immutable revision nếu có chứng cứ, tổng tham số, ngày phát hành base, license/nguồn chính thức, tokenizer, precision/quantization, max length và cấu hình.
- Model dự kiến phải đối chiếu lineage: BGE-M3, Qwen3-Embedding-0.6B, Qwen3-Reranker-4B, BGE-reranker-v2-m3; bổ sung model khác nếu thực tế có dùng. Không áp một registry giả định thiếu upstream.
- Model public dùng link tải chính thức; nếu có adapter/checkpoint riêng thì chia sẻ riêng theo quy định BTC. Base <01/08/2026, từng model <=15B; checkpoint fine-tune sau mốc giữ private/local theo luật.
- Nếu release có gọi API: ghi exact model/provider, cấu hình, prompt/version/hash, retry/resume/cache và cách cấp key qua env. Không gửi key trong source, slide, notebook output hoặc HAR.
- Không thay tên “main” bằng một revision mới rồi nói đó là revision lịch sử. Mục chưa xác minh phải hiện rõ và giải quyết trước khi tuyên bố tái hiện hoàn toàn.
- Khai báo đúng vai trò nhãn ChatGPT/weak labels nếu có trong development; không gọi là gold BTC, không che giấu ảnh hưởng tới lựa chọn policy.

**Nghiệm thu:** tải đúng model theo hướng dẫn; model/tokenizer/index tương thích; checker từ chối mismatch và model chưa xác minh hợp lệ cho release mới.

### B4. Email 1.4 — Mã nguồn, cấu hình, dependencies

**Đầu ra:** source release, config cố định, dependency locks, source manifest, slides 14/A1.

- Đóng gói code preprocessing, chunk/index build, retrieval, reranking, selection, validation, notebook inference cần thiết và UI mới.
- Dùng một release config cho CLI/UI. Không tạo hai bộ top-k/model/prompt khác nhau.
- Không refactor/xóa toàn repo sát deadline. Tạo lớp điều phối và trích đúng phần cần tái sử dụng; giữ thí nghiệm trong archive để truy vết.
- Khôi phục policy add19 trực tiếp từ source, không phụ thuộc JSON add25 đã xóa. Sửa path/root của script archived khi đưa vào release.
- Sửa README hiện còn gọi `generate_best_submission.py` là control; defaults script đó thuộc Exp50.
- Source inventory phải gồm cả module cần thiết đang bị gitignore/untracked; không mặc định `git archive` đã chứa đủ. Manifest ghi commit và hash toàn bộ source thực bàn giao, không chỉ commit của worktree bẩn.
- Tách môi trường replay/core, inference GPU và UI; pin phiên bản từ môi trường thực đã chạy. Ghi Python, CUDA, PyTorch/Transformers/FAISS, thư viện embed và 7-Zip.
- Không copy source/UI/assets đội khác khi chưa rõ giấy phép. Học thiết kế, tự triển khai adapter và ghi attribution.

**Nghiệm thu:** cài từ source release trong thư mục sạch, import/CLI/test hoạt động mà không dựa vào file ngoài gói.

### B5. Email 1.5 — README và tái hiện từ đầu

**Đầu ra:** README + reproduction guide, log kiểm thử, slides 14/A1/A3.

- Liệt kê OS đã kiểm tra, Python/phần mềm, RAM/VRAM/disk, dung lượng tải; latency/ETA chỉ ghi theo đo thực tế.
- Các bước: tạo môi trường → tải và verify data/model → build/load index → encode/retrieve → rerank → select → validate/package → chạy UI.
- Ba chế độ riêng: **replay** từ cache đã khóa; **run** từ query/index với inference thực; **rebuild** từ text snapshot. Không dùng replay để tuyên bố đã fresh-run từ đầu.
- CLI đề xuất: `python -m src.release.cli replay|run|rebuild|verify --config ...`. Cho phép cấu hình data root/output root, query subset để smoke test, resume khóa fingerprint. Không đổi schema JSON nộp BTC.
- Replay phải pass toàn bộ 1.200 query, bằng prediction champion. Fresh smoke dùng 20 query cố định bao gồm VI dài/ngắn/nhiều ý và kết quả đa ngôn ngữ; ghi rõ chỉ mới kiểm tra subset nếu chưa chạy full.
- Có troubleshooting: thiếu artifact, sai model/index, OOM, Colab mất kết nối, checkpoint sai hash, ZIP vượt giới hạn, link Drive thiếu quyền.
- Trình bày lệnh kỳ vọng, output location và tiêu chí pass sau mỗi bước, không chỉ đưa danh sách notebook.

**Nghiệm thu:** người khác làm theo README tái hiện được bài nộp bằng replay và chạy được đường inference thực trên subset không cần kết quả prediction đã lưu sẵn.

## C. Tham khảo UI các đội và lựa chọn triển khai

Đã đọc README và các phần code UI liên quan:

- [ARCANE demo](../repos/r2ai-stage-2/arcane/src/demo/README.md), `static/index.html`, routing `app.py`: hai vùng kết quả/evidence, health, pipeline events, truy vết nguồn, nhãn fixture riêng. **Áp dụng:** evidence luôn dễ nhìn, thông báo mode trung thực và UI mỏng kết nối pipeline.
- [mscAI UI](../repos/r2ai-stage-1/mscai/src/ui/README.md), `app/page.tsx`, `lib/types.ts`: progress/state có kiểu và cùng nguồn config backend. **Áp dụng:** trạng thái từng bước và tránh cấu hình UI/CLI lệch nhau; không cần mang Next.js/PostgreSQL vào release này.
- [AISOLO UI](../repos/r2ai-stage-2/aisolo/src/r2ai-app/README.md): tách cảnh báo input/output, kiểm tra E2E theo trạng thái. **Áp dụng:** phân biệt integrity với relevance, test trạng thái hoàn thành/lỗi thật. Không mang luật kế toán sang y khoa.
- [LASTDANCE release](../repos/r2ai-stage-2/lastdance/src/submission_materials/README_NGHIEM_THU.md): tổ chức hồ sơ, release manifest và source provenance. **Áp dụng:** mọi màn hình/demo gắn đúng release.

**Stack chốt cho v1:** FastAPI phục vụ static HTML/CSS/JavaScript cùng origin, một process local tại `127.0.0.1:8000`. Tự viết UI, không tạo frontend build chain mới. Dependencies demo tách khỏi inference. Không tài khoản, database hội thoại, upload bệnh án, public tunnel hoặc deployment web trước hạn.

**Phong cách:** giao diện tra cứu kỹ thuật sạch, tiếng Việt, nền sáng, chữ dễ đọc, accent xanh; kết quả và nguồn cùng màn hình desktop. Không thêm câu trả lời sinh tự do hay hình bác sĩ tạo cảm giác tư vấn lâm sàng.

## D. UI v1 — chức năng, hợp đồng và nghiệm thu

### D1. Các màn hình

1. **Tra cứu:** input câu hỏi độc lập, nút chạy/dừng; chọn một trong 1.200 query hoặc nhập câu mới. Có ví dụ ngắn/dài/nhiều ý, không quảng bá như ca đã biết gold. Không nối các query thành hội thoại.
2. **Kết quả:** tab Tài liệu/Đoạn trích, doc_id/PMID, URL gốc, ngôn ngữ nếu có metadata, số kết quả, phân trang 20 mục. Mặc định giữ thứ tự output; gọi là “vị trí xuất” khi không có chứng cứ đó là reranker rank.
3. **Nguồn:** click chunk mở văn bản snapshot ở panel cạnh, highlight đúng substring theo offset, hiện doc_id/source hash/offset. Nếu chưa có offset đã kiểm chứng thì hiện chunk exact và trạng thái chưa resolve, không highlight một đoạn gần giống.
4. **Truy vết:** mode, release/index/model fingerprint, số candidates ở các bước có log thật, cache hit, thời gian thực đo, warning và trạng thái worker. Dữ liệu không được lưu ở run cũ ghi “không có”, không dựng lại timeline giả.
5. **Thông tin hệ thống:** corpus/index counts từ manifest, model registry, health, link README/hồ sơ, public score có nhãn evaluator. Private hiển thị “chưa công bố”, không hiện 0 hoặc lấy điểm public thế vào.
6. **Export:** tải JSON kết quả query và provenance để kiểm tra; ghi rõ đây là export một câu, không phải submission đủ 1.200 query. Không có nút tự nộp BTC.

### D2. Hai mode và pipeline

- **Replay đã kiểm chứng:** mặc định để BTC xem ngay không GPU, đọc prediction/corpus snapshot đã khóa. Chọn ID hoặc text khớp exact query cache; luôn có banner “Kết quả cache của release, không chạy inference mới”.
- **Live retrieval:** gọi cùng service của CLI `run`, không implement thuật toán riêng trong web. Chỉ enable khi preflight xác nhận index/model và fresh smoke pass. Query mới không khớp cache không được trả nhầm prediction cũ.
- Nếu live chưa đủ điều kiện hoặc mất GPU, hiển thị unavailable/error và hướng dẫn; người dùng có thể **chủ động** chuyển replay. Không silent fallback rồi gọi là live, không dùng fixture giả làm kết quả thật.
- UI MVP trước hạn phải hoàn chỉnh replay/evidence/health; mục tiêu tích hợp live sau P0. Nếu live chưa pass ở mốc freeze thì khóa tính năng đó, báo giới hạn trong README/slide và ưu tiên gửi hồ sơ đúng hạn.
- Request đơn lẻ là một job; một worker inference để tránh tranh VRAM. Queue tối đa 4 job, job timeout mặc định 600s, báo rõ timeout thay vì chạy vô hạn. Cancel theo cờ giữa các stage, không kill process GPU dùng chung.
- Chỉ ghi latency inference khi thực sự đo inference; tốc độ replay không được báo là latency model.

### D3. API tối thiểu dự kiến

- `GET /api/health`: mode sẵn sàng, release ID, trạng thái corpus/index/model, counts. Không trả token hoặc đường dẫn nhạy cảm.
- `GET /api/queries?search=&offset=&limit=`: chọn query đã có; server cap limit=100.
- `POST /api/runs`: `{mode: replay|live, query_id?, query?}`; trả run_id. Replay yêu cầu ID/text nhất quán, live yêu cầu query không rỗng và tối đa 12.000 ký tự.
- `GET /api/runs/{id}`: queued/running/completed/failed/cancelled, stage, elapsed và warning; UI poll mỗi 1 giây khi job chưa terminal, dừng poll khi xong.
- `GET /api/runs/{id}/results?kind=docs|chunks&offset=&limit=`: kết quả + provenance, cùng schema lõi với CLI.
- `GET /api/runs/{id}/evidence/{chunk_ref}`: server resolve chunk_ref trong run sang doc_id/source offsets, context giới hạn 4.096 ký tự quanh highlight, không nhận filesystem path từ browser.
- `POST /api/runs/{id}/cancel` và `GET /api/runs/{id}/export`: hủy có kiểm soát và export một query.

Tất cả result dùng object có kiểu từ service; không chèn bản tóm tắt LLM giữa các stage. Docs/chunks membership của replay phải bằng artifact gốc, filter/ngôn ngữ trên UI chỉ là cách hiển thị, không mutate output.

### D4. Test UI và demo

- Mở trang → chọn query → chạy replay → thấy docs/chunks → click evidence → offset/hash đúng → export khớp; chạy ít nhất một query có text VI, EN, ZH để kiểm tra font/Unicode.
- Test câu mới/live khi worker sẵn sàng; test thiếu model, timeout, cancel, cache mismatch, query rỗng, không có kết quả và duplicate click.
- Render source text an toàn bằng text nodes, không đưa HTML crawl thẳng vào DOM; URL chỉ http/https. Chặn path traversal, không có API đọc file tùy ý.
- History chỉ trong memory phiên tab; không lưu nội dung người dùng/PHI vào browser storage hoặc remote analytics mặc định.
- E2E đợi trạng thái, không sleep cố định. Kiểm tra desktop 1440×900 và 1366×768, màn hình hẹp 390×844; bàn phím, focus, overflow và panel nguồn.
- Kịch bản demo 90–120 giây: chọn mode → tra cứu → mở 1–2 nguồn → xem provenance/export. Chuẩn bị ảnh chụp thật và video dự phòng từ UI đã chạy; không dùng mockup thay ảnh sản phẩm.
- Không hứa “relevance chính xác” từ việc source hash khớp. Integrity pass và relevance score là hai thông tin riêng.

## E. Slide — nội dung từng trang và cách thực hiện

### E1. Định dạng và nguồn sự thật

- Giao **PPTX chỉnh sửa được + PDF**, tiếng Việt; **15 slide chính + 4 phụ lục**. Số trang là đề xuất của đội, không phải yêu cầu BTC. Draft trình bày khoảng 8–10 phút, điều chỉnh khi có thời lượng Demo Day chính thức.
- Report là tài liệu chi tiết; deck tóm tắt nhưng vẫn chỉ ra đủ 5 mục email và nơi tải minh chứng.
- Trước dựng deck, chọn template nếu công cụ khả dụng; nếu không có lựa chọn riêng, dùng bố cục 16:9 nền sáng, xanh navy/teal, font hỗ trợ tiếng Việt và CJK cho evidence.
- Mỗi slide có một ý chính, nguồn số liệu/claims trong notes, 60–100 từ speaker notes và câu chuyển sang trang sau. Các trường chưa xác minh phải xử lý hoặc nêu giới hạn, không để placeholder trong bản nộp.
- Dùng nguồn đã khóa: release manifest, model registry, data audit, experiment log cùng evaluator, source code và ảnh UI thật. Không lấy kết quả đội khác làm thành tích của đội mình.
- Sơ đồ pipeline, bảng model và biểu đồ metrics dùng đối tượng chỉnh sửa được. Không làm toàn bộ deck thành ảnh; không thêm tranh minh họa y khoa không cần thiết.

### E2. Storyboard chốt

1. **Tên hệ thống và phạm vi.** Tên đội/đại diện đã xác nhận, Stage 3, version/ngày release; một câu mô tả truy hồi y khoa đa ngôn ngữ. Hình: bìa đơn giản, không tuyên bố chẩn đoán hay điểm private.
2. **Bài toán và hồ sơ nghiệm thu.** Input/query và hai output docs/chunks; năm mục email cùng file minh chứng. Notes giải thích UI/slide là phần hỗ trợ, source/data/README mới cho phép kiểm chứng.
3. **Kiến trúc hệ thống.** Sơ đồ hai luồng offline/online, component thực tế, điểm cache và validation, UI là consumer của cùng service CLI. Evidence: release config và dependency graph.
4. **Corpus và nguồn dữ liệu.** Nguồn BTC, VI/EN/ZH, URL/PMID/doc_id, số liệu snapshot đã audit. Hình: phân bố ngôn ngữ/coverage crawl-index, không gọi là coverage gold.
5. **Thu thập và làm sạch.** Một ví dụ redirect giữ doc_id, các loại lỗi/filter, dedup và source snapshot. Hình: 4–5 bước preprocessing và một record minh họa lấy từ log thật.
6. **Chunking và xây index.** Source offsets, quan hệ doc/chunk/vector; BGE dense/sparse, Qwen index nếu có trong lineage; encoder/index mapping. Hình: sơ đồ một tài liệu–nhiều chunk, không bịa rule split mới.
7. **Query và truy hồi.** Query gốc, các view thực sự dùng, candidate generation/fusion; phân biệt BM25 và learned sparse. Hình: một query thật và luồng candidates; nghiên cứu chưa dùng chỉ ghi ở notes/phụ lục.
8. **Reranking và chọn documents.** Model P1, aggregation, score/rank thật, top130 và owner protection. Hình: trước/sau chọn membership trên ví dụ, không dùng score như xác suất đúng.
9. **Lựa chọn evidence.** Parent policy, keep90/overflow, Exp142 additions và Exp143 spans; LCS hai phía theo thông báo BTC. Hình: source text và offsets của chunk; không giả lập gold chunk để chứng minh hit.
10. **Mô hình và tuân thủ.** Registry có ID/revision/vai trò/size, ngày base và link tải; API prompt/config nếu thuộc release. Bảng tóm tắt editable, chi tiết xuống A2.
11. **Kết quả thực nghiệm.** Chỉ nhóm evaluator mới: Exp122(2) 0.3075, Exp139 0.3161, Exp142 0.3185, Exp143 0.3190; Docs/Chunks F2 theo log. Biểu đồ editable, label public; private “chưa công bố”. Không nối đường điểm cũ 0.3516 với điểm mới như cùng phép đo.
12. **UI và khả năng truy vết.** Ảnh UI thực ở màn query/kết quả/evidence; chú thích mode, doc_id, nguồn và nút export. Không chụp UI đội khác rồi giới thiệu là sản phẩm mình.
13. **Minh họa một lượt tra cứu.** Ba bước có ảnh thật: chọn query → xem docs/chunks → đối chiếu source. Ghi mode và thời gian đo. Notes chứa kịch bản demo/video fallback và cách báo lỗi khi live unavailable.
14. **Cài đặt và tái hiện.** Các đường replay/run/rebuild, yêu cầu môi trường, lệnh entrypoint và output; bảng đánh dấu đã kiểm thử full/subset. Không dùng audit replay để tuyên bố fresh full pass.
15. **Bàn giao và giới hạn.** Link index hồ sơ/Drive/source/model, version/hash tham chiếu, các giới hạn còn lại, kế hoạch Demo Day. Chỉ công bố link đã thử truy cập. Notes nhắc hạn email/portal và người liên hệ.
16. **A1 — Lệnh và dependencies.** Các lệnh cài, tải/verify, replay, run subset, rebuild, start UI; phiên bản runtime thật và troubleshooting ngắn.
17. **A2 — Checkpoint, prompt, cache.** Registry đầy đủ, precision/max length, prompt revision, fingerprint, cache policy, nguồn tải checkpoint. Không có secrets.
18. **A3 — Data/artifact contract.** Layout giải nén, schema query/doc/chunk, các gói chia sẻ/size/checksum, mapping source và manifest.
19. **A4 — Lỗi, giới hạn và nguồn tham khảo.** Ví dụ truy hồi chưa tốt, source integrity khác relevance, private chưa biết điểm; attribution các repo tham khảo, giới hạn evaluator/development labels và phạm vi chưa triển khai.

### E3. Quy trình sản xuất slide

1. **Evidence pack:** chốt release/model/data/metric JSON và 3–4 query minh họa đã rà soát nguồn; mỗi claim/figure có file/hash/section tham chiếu.
2. **Storyboard/copy:** viết tiêu đề, nội dung, speaker notes và nguồn cho đủ 15 trang trước khi trang trí. Kiểm coverage B1–B5.
3. **Visuals:** dựng diagram editable; xuất chart từ số BTC cùng evaluator; chụp UI sau khi chạy test; giữ caption chế độ thật.
4. **Author:** dùng quy trình local PPTX của Presentations và Artifact Tool JavaScript; không hand-edit XML hoặc dùng template asset chưa rõ license.
5. **Render/QA:** render toàn bộ slide, soi từng trang ở full size và contact sheet; sửa lỗi overflow, font VI/CJK, connector, tỷ lệ ảnh, rounding/chart data, hyperlink, notes và placeholder.
6. **Export:** xuất PPTX final và PDF từ cùng bản final; mở lại kiểm tra đủ trang, đúng thứ tự/Unicode/link. Chỉ nói “đã kiểm tra trong PowerPoint” nếu thực sự mở PowerPoint. Lưu hash final và validation report.
7. **Rehearsal:** chạy demo script 90–120s, đọc notes để đo tổng thời lượng; slide giới hạn/không có điểm private không được bỏ để làm kết quả đẹp hơn.

**Nghiệm thu:** đủ 5 mục email, 15 trang đúng storyboard pitching, PPTX editable, PDF khớp, citations/notes đầy đủ, không điểm/model/claim/link bịa và không lộ secrets.

## F. Đóng gói, thứ tự công việc và giờ chốt

### F1. Work packages và phụ thuộc

- **WP1 — Release/audit/manifest:** khóa champion và trace lineage, bổ sung source/entrypoints. Ưu tiên đầu tiên; không đợi UI mới làm tài liệu.
- **WP2 — Báo cáo + data/model/README:** viết từ WP1, đo size và đóng gói/upload data ngay khi từng gói ổn định. Người dùng upload Drive, cung cấp link/thông tin đội; chưa tự gửi email.
- **WP3 — UI:** xây vỏ + replay/evidence/health song song WP2, nối live sau fresh adapter pass. Capture ảnh sau test, không dựng ảnh giả trước.
- **WP4 — Slide:** storyboard/copy lấy từ WP1–2, slides 12–13 đợi ảnh WP3; render/QA sau content freeze.
- **WP5 — Nghiệm thu ngoài workspace:** giải nén source và data paths mới, test replay/fresh subset/UI; kiểm Drive và so báo cáo/slide/manifest; chuẩn bị email.
- **WP6 — Thử nghiệm điểm:** chỉ dùng phần thời gian/compute còn lại; không được làm WP1–5 trễ.

Nếu thiếu giờ, thứ tự cắt là thử nghiệm mới → UI live nâng cao → animation/video trang trí. **Không cắt corpus/source/model/README bắt buộc, UI replay/evidence MVP hoặc kiểm tra link.**

### F2. Timeline 03–04/11 (UTC+7)

- **03/11:** WP1, dàn ý đầy đủ B1–B5; gói data đầu tiên và UI replay skeleton; storyboard slide.
- **04/11 10:00:** bản hồ sơ nháp đủ năm mục, UI replay/evidence chạy được, upload đang tiến hành. Nếu chưa đạt, dừng mọi job thử nghiệm mới.
- **12:00:** không khởi động job GPU/treatment mới; quyết định bật/tắt UI live dựa trên smoke test, công khai giới hạn.
- **14:00:** freeze code/config/data và candidate có thể bàn giao; chụp UI và khóa nội dung slide. Job chưa có artifact/audit đầy đủ không được đưa vào bài nộp.
- **16:00:** xong PPTX/PDF/báo cáo/README; render và clean-room kiểm thử; hoàn tất các gói Drive.
- **18:00:** test download/quyền truy cập, verify manifests và đối chiếu các link; chuẩn bị email/portal checklist.
- **20:00:** gửi người dùng toàn bộ file và email nháp để nộp, ghi các hạn chế còn lại.
- **Trước 22:30:** người dùng gửi email tới **hr@aiguru.com.vn** và nộp candidate đã audit; lưu email sent/portal receipt. **23:59 04/11 là hạn cứng**.
- **09/11:** BTC công bố top10. **14/11:** Demo Day/Pitching. Sau deadline có thể nâng UX/live/demo nhưng không sửa âm thầm release đã bàn giao.

Nếu bắt đầu một work package sau mốc của nó, áp dụng ngay thứ tự cắt ở F1, không dời hạn email. Bộ slide Demo Day có thể được tinh chỉnh riêng sau 04/11, giữ nguyên snapshot hồ sơ nghiệm thu.

### F3. Checklist gửi email

- [ ] Người dùng xác nhận tên đội/đại diện, tài khoản portal, thông tin liên hệ và receipt lượt private đã nộp.
- [ ] Báo cáo và slide khớp release; đủ từng mục email 1.1–1.5, không placeholder.
- [ ] README có lệnh cài/chạy/UI và trạng thái đã test full/subset rõ ràng.
- [ ] Source/config/dependencies đầy đủ; các artifact ignored nhưng cần chạy đã được đưa vào gói.
- [ ] Data/model links truy cập được; SHA256/size/extraction paths đúng; credentials đã loại.
- [ ] UI đúng mode, evidence truy nguồn được, có ảnh/video fallback thật nếu live không sẵn sàng.
- [ ] Private ghi “chưa công bố”, không dùng số public thay; source/model có khai báo trung thực.
- [ ] Email draft liệt kê link index hồ sơ, link data/source/model, file/hash bài nộp và hướng dẫn BTC bắt đầu từ README.
- [ ] Người dùng gửi email/portal trước hạn; lưu bằng chứng đã gửi. Chuẩn bị file không đồng nghĩa đã nộp.

## G. Bốn slot còn lại: chỉ sau khi hồ sơ không bị đe dọa

Không có private feedback nên không có “promote nhánh thắng” trước 04/11. Giữ nguyên slot1 đã nộp; không nộp duplicate.

**Cập nhật 08:10 ngày 04/11:** [Bốn ZIP private02–05 và audit](experiments_log/private02_05_final_sprint.md) đã tạo. Private02 docs BM25 đồng thuận +666; Private03 chunks P2A +2.053; Private04 kết hợp hai trục; Private05 docs BM25 rộng +1.997 là **dự phòng**. Tất cả <100 MB, audit cấu trúc PASS, chưa có điểm private. Người dùng có thể nộp 02/03/04 trước; giữ slot5 cho Exp144 nếu hoàn tất và audit trước freeze, nếu không thì dùng 05 đã chuẩn bị. Đây là các treatment triển khai thực tế, thay cho mô tả thiết kế slot2–5 bên dưới; không giả định chúng sẽ cải thiện điểm.

- **Slot2, docs-only:** original query BM25 đầy đủ (bỏ first-24 truncation), cap2.000 union control, BGE đúng encoder max chunk score/top400; fusion rank Qwen thật, RRF60 weights Qwen/BGE1.0/1.25, top130 + đúng protected set lịch sử. Chunks Exp143 exact.
- **Slot3, chunks-only:** từ ranking slot2 chọn tối đa2 docs/query chưa có evidence control; tối đa8 source paragraph candidates/doc, <=768 tokenizer tokens, BGE reranker chọn1 body nguyên văn/doc. Giữ docs và chunks cũ Exp143; chỉ append, thiếu source/score thì không thêm. Không thay hàng loạt parent theo width.
- **Slot4:** tổ hợp docs slot2/chunks slot3 nếu cả hai có artifact, manifest, test và hồ sơ mô tả; gọi là treatment phối hợp, không gọi winners.
- **Slot5:** dự phòng sửa lỗi có căn cứ. Không bắt buộc dùng hết quota.
- Pilot60 query cố định, full ETA<=6h và kết thúc trước freeze14:00 ngày04/11. ZIP mục tiêu<98MB, bắt buộc<100MB; nếu additions vượt budget giảm quota2 xuống1 đồng loạt và ghi manifest, không cắt text tùy ý.
- Không mở thêm embedding model, fine-tuning, HyDE toàn bộ, ICD hard-filter hoặc LLM lớn hơn luật. Tất cả private candidates phải có source/config/manifest tương ứng trong hồ sơ.
- Structural/source/semantic audit không thay thế relevance evaluation. Không hứa tăng điểm hoặc top1 khi chưa có kết quả private.

### G1. BGE-M3 multi-vector/ColBERT — full xong, **không promote vào private**

- Mục đích: kiểm tra *late interaction* trên shortlist P2A, không đào tạo model mới, không dùng private labels và **không tự nộp BTC**. Model `BAAI/bge-m3` được khóa revision `5617a9f61b028005a4858fdac845db406aefb181`. Input chỉ gồm query BTC và cửa sổ văn bản corpus có provenance; output là điểm rerank, không phải chunk mới để nộp.
- Pilot 60 query, 3.000 query-doc, 5.446 passage đã chạy xong: đủ 5.446 điểm, ID và SHA256 khớp, không NaN/duplicate; khoảng 11,29 passage/giây. [Notebook pilot](../notebooks/24_bgem3_colbert_pilot_kaggle.ipynb), [Kaggle pilot](https://www.kaggle.com/code/ptquanh/r2ai-bge-m3-colbert-pilot-20261103). Phân bố điểm chỉ chứng minh tính toán ổn, **không chứng minh tăng F2**.
- Full 1.200 query, 60.000 query-doc, 107.686 passage đã chạy xong tại [Kaggle full](https://www.kaggle.com/code/ptquanh/r2ai-bge-m3-colbert-full-20261103). [Notebook full](../notebooks/25_bgem3_colbert_full_kaggle.ipynb). Audit độc lập: đủ 107.686 pair/1.200 query, hash input/output và ZIP CRC khớp, score hữu hạn, không ID thiếu/trùng; tốc độ 11,36 passage/giây. Lệnh tái kiểm tra: `python -m scripts.audit_colbert_kaggle --input data/kaggle_inputs/colbert_full_20261103/colbert_full_pairs.parquet --output data/kaggle_outputs/colbert_full_20261104/colbert_full_outputs.zip`.
- So với docs của chính ZIP private Exp143, trong 50 doc shortlist/query ColBERT chỉ thấy trung bình 1,579 doc mới/query; **29/1.200 query** có doc mới trong top5, **88/1.200** trong top10; chỉ **2/1.200** có doc mới vượt score của mọi doc đã có. Đọc hai trường hợp đầu: query 855 về chấn thương cột sống D12 và mang thai nhưng doc mới nói về mang thai sau phá thai; query 98 về Biolac/tiêu chảy nhưng doc mới về đau dạ dày do diclofenac. Điểm cao không bảo đảm đúng clinical intent.
- **Quyết định:** Không dùng ColBERT-only như private treatment. Rerank cùng tập doc không thay Docs F2; thêm vài doc mới chất lượng kém có nguy cơ giảm precision. Full output vẫn giữ làm tài liệu nghiên cứu/đối chiếu, không lấy top passage làm chunk và không tuyên bố cải thiện F2. Chỉ xem lại nếu có shortlist mới chứa nhiều nguồn chưa được Exp143 thu hồi, kèm audit lâm sàng/query intent và manifest hợp lệ trước freeze 14:00 04/11. Bốn slot còn lại vẫn ưu tiên các treatment ở G, không tự động nộp.

## H. Hồ sơ lịch sử và việc chưa thực hiện

### Knowledge graph — nhánh thực nghiệm, chưa thuộc champion

- Đã xây `src/retrieval/concept_graph.py`, từ điển `configs/medical_concepts_v1.json` (25 khái niệm, alias VI/EN/ZH), lệnh build và audit. Cạnh chỉ có `alias → concept`, `concept → tài liệu có nhắc đến` với vị trí trong văn bản chuẩn hóa; ICD chapter là metadata. **Không có cạnh suy diễn bệnh–triệu chứng/điều trị** và không dùng làm hard filter.
- Pilot 20.000 văn bản: 12.258 tài liệu có mention, 23.634 cạnh. Ví dụ đồng xuất hiện “mang thai” và “tăng huyết áp” trong một bài có thể chỉ là hai đoạn xa nhau; đã thêm ngưỡng proximity 800 ký tự chuẩn hóa khi xếp ứng viên đa khái niệm. Đây vẫn chưa phải đánh giá relevance.
- Full build đã xong: quét 1.212.421 văn bản, 427.625 doc có mention, 754.262 cạnh, 0 ID ngoài corpus; SQLite ~113 MB. `python scripts/audit_concept_graph.py` cho 176/1.200 query có ứng viên, 8.800 candidate top50, 459 trùng docs Exp143 và 8.341 mới. **Novel không đồng nghĩa relevant**: kiểm tra mẫu thấy câu nhiều bệnh có thể bị kéo vào bài nhắc thoáng qua, ví dụ query 85 nhận bài về sữa đậu nành dù hỏi nhóm ưu tiên vắc-xin.
- Graph đã được thêm vào UI như một mục **Experimental**: query có curated concept → khái niệm → tài liệu corpus; query khác hoặc thiếu SQLite → thuật ngữ khớp trong chunk replay → tài liệu, cuối cùng là cạnh retrieval đã cache khi không có lexical overlap. Mỗi cạnh có `edge_basis`; không gán nhãn clinical KG cho tầng replay. Sweep API trên toàn bộ 1.200 query: 176 dùng corpus concepts, 1.024 dùng replay evidence, **0 lỗi/graph rỗng**. Đây là kiểm tra hoạt động UI, không phải phép đo chất lượng relevance. **Chưa dùng trong private submission**, chưa có căn cứ tiêu một trong bốn slot còn lại. Nếu tiếp tục, cần mở rộng từ điển có kiểm chứng, lấy query intent chính thay vì mọi term, chấm độ gần trong cùng đoạn thật và audit từng loại lỗi trước khi tạo treatment docs-only giữ chunks Exp143. Không thay private slot1 hoặc tự tuyên bố tăng điểm.

- [Plan trước khi đổi ưu tiên hồ sơ/UI, lưu nguyên văn](archive/r2ai_score_improvement_plan_before_dossier_ui_20261103.md): chỉ dùng provenance/backlog, các câu về trả điểm private từng lượt và chưa nộp slot1 đã lỗi thời.
- [Research AI Guru](aiguru_retrieval_research_20261029.md): ý tưởng tham khảo sau khi hoàn tất release, không phải danh sách việc bắt buộc trước deadline.
- [Nhật ký thực nghiệm](experiments_log.md): chỉ số public và treatment, tách evaluator; private ghi riêng tại ledger.
- Chưa có UI, slide hoặc source release mới chỉ vì kế hoạch này được viết. Mỗi WP cần cập nhật artifact thực, hash, test evidence và trạng thái trước khi đánh dấu hoàn thành.
