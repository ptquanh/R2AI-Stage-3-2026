# AI Guru retrieval research — 29/10/2026

## Kết luận dùng cho sprint

Đề xuất: **query giữ đúng chủ thể/ý hỏi → retrieval theo nhiều ý → rerank có ngữ cảnh tài liệu → xuất evidence nguyên văn**. Đây là giả thuyết kỹ thuật cần BTC kiểm chứng, không phải cam kết tăng điểm. Không xây chatbot nhiều lượt hay reindex toàn corpus trong sprint.

Đã đọc các bài Advanced RAG 01, 02, 05, 06, 10, 11 trên kho công khai AI Guru; đối chiếu thêm tài liệu LangChain và nghiên cứu gốc Contextual Retrieval. Nội dung được lấy từ các Markdown public dưới `/content/` vì trang giao diện render bằng JavaScript. Ngày truy cập: 29/10/2026.

**Đã xác minh tài liệu 24 từ link người dùng:** [Google Drive](https://drive.google.com/file/d/1BKbT3NV33tGKdEnLCU0Jd0P_jkGCyPaO/view), bản lưu [PDF 23 trang](aiguru_24_conversational_retrieval.pdf), SHA-256 `71875af3253e1cf0a93400642a81f9d851296c64b75f7d1cbd28ab8f97630f5f`. Tác giả ghi trên trang1: Trần Thị Quỳnh Tiên, AI Guru x TiniX. Đây là tài liệu riêng, không phải bài24 coreference trong danh mục NLP. Đã đọc phần phương pháp/giới hạn, kiểm tra hình bảng đánh giá trang20 và đối chiếu code công khai. Trang [Facebook AI Guru](https://www.facebook.com/aiguru.vn/) bị hạn chế truy xuất trong phiên này; không khẳng định đã rà soát toàn bộ bài đăng/tài liệu trên fanpage.

### Bổ sung từ đúng tài liệu 24

- Trang1,9–11: demo dùng TF-IDF `char_wb`, n-gram2–4 và rewrite rule-based, không dùng LLM, trên17 điều luật. Không có benchmark độc lập đủ để suy ra gain trên corpus y khoa hơn một triệu docs.
- Trang11: không có history hoặc câu đã độc lập thì giữ nguyên. Điều này củng cố **gating**, không phải lý do rewrite toàn bộ1.200 câu. Với ta, chỉ dùng ngữ cảnh đã hiện diện trong cùng query; tuyệt đối không dùng row trước làm history.
- Trang18–20: ngưỡng0.35 chỉ kiểm tra trên3 câu in-scope và3 out-of-scope; có lỗi retrieval dù rewrite được xem là đúng. Không mang ngưỡng này sang BGE/Qwen, không bỏ docs/chunks vì cosine thấp khi chưa có nhãn calibration.
- Trang8–10: giữ ranh giới điều luật và title metadata. Bản thích nghi y khoa là section/heading có nguồn, không chia theo số ký tự rồi mặc định mọi đoạn đều độc lập về nghĩa.
- Trang12,14: log riêng original/rewrite/retrieved/output. Ta bổ sung `rewrite_applied`, `rewrite_reason`, `context_source_spans`, candidate rank/source và output offsets để truy vết đúng tầng lỗi.
- **Khác biệt tài liệu/code cần lưu ý:** trang16 mô tả các lượt rewrite ghép nối giúp nhìn xa hơn một lượt; nhưng [rewriter.py](https://github.com/Cmint22/conversational-retrieval-luat-dat-dai/blob/main/code/rewriter.py) chỉ đọc `history[-1]["user"]`, còn [pipeline.py](https://github.com/Cmint22/conversational-retrieval-luat-dat-dai/blob/main/code/pipeline.py) lưu `user_question` gốc. Vì vậy code đã đọc không chứng minh tích lũy rewritten context qua nhiều lượt. `extract_key_phrase` cũng trả lại câu hỏi trước gần như nguyên vẹn, không phải bộ trích noun phrase thật. Không sao chép các claim này thành năng lực hệ thống ta.

### Điều chỉnh thử nghiệm sau khi đọc bài24

**R1-gated ưu tiên hơn rewrite đại trà.** Query đã rõ nghĩa được giữ nguyên. Chỉ tạo view bổ sung nếu có tham chiếu với antecedent ngay trong query, diễn đạt lặp cần rút gọn, hoặc biến thể từ vựng đã xác minh; facet nhiều ý để R2 xử lý riêng. Record phải nêu lý do và spans làm căn cứ. Không trigger chỉ vì có chữ “vậy/còn”, không xóa chủ thể hay tự chẩn đoán. A/B so với cùng control, luôn giữ original branch. So sánh gated với all-rewrite chỉ là ablation sau đó nếu có budget; không coi gated chắc chắn thắng.

**R6 lexical robustness — CPU dự phòng, không thay index chính.** Trên fixed shortlist top400/query của nhánh thắng, thử TF-IDF character n-gram2–4 (`char_wb`, L2 normalization) cho title+source section, fit trên tập document representations unique của toàn shortlist, không fit chung query. Không lowercase/normalize source output; xử lý chỉ trên retrieval representation. Bản đầu giữ dấu tiếng Việt; dấu không được char n-gram tự khôi phục. RRF k=60, rank control weight1.0, lexical weight0.25; cùng top130 + owner floor, chunks exact. Đây chỉ là reranking độ bền lexical, **không tăng candidate coverage ngoài shortlist**, không semantic synonym engine. Benchmark60 query trên CPU; hoãn nếu projected full job >1h hoặc memory vượt budget. Không dựng ma trận char n-gram toàn corpus và không nộp thêm sweep n-gram/threshold; normalized không dấu chỉ là diagnostic về sau, không đồng thời trộn vào bài đầu.

R6 đặt sau A0/translation ablations/R1–R3 và trước các hướng đắt chưa có bằng chứng. Gain chỉ được chấp nhận qua BTC; lỗi chính tả/thuật ngữ gần giống có thể hưởng lợi nhưng cũng có thể gây false positives, nhất là tên thuốc gần nhau.

## 1. Conversational retrieval: học cách giữ ngữ cảnh, không dựng lịch sử giả

`data/raw/btc_provided/query.parquet` có 1.200 rows và hai cột `id`, `query`; không có conversation_id, turn_id hoặc history. Chưa có bằng chứng các row liên tiếp thuộc cùng hội thoại. Không nối query với row trước, không tạo memory liên-query.

[LangChain history-aware retriever](https://reference.langchain.com/python/langchain-classic/chains/history_aware_retriever/create_history_aware_retriever) dùng lịch sử thật để reformulate; không có history thì input đi thẳng tới retriever. Vì vậy phần áp dụng được ở đây là làm rõ tham chiếu **nằm trong chính một query**, không phải mang cả conversational chain vào hệ thống.

Ví dụ kiểm tra trực tiếp từ dữ liệu, dùng làm regression tests chứ không hardcode theo ID:

- Query 35: người bệnh là con gái 5 tuổi; người hỏi là phụ huynh. Giữ “kém ăn và gầy”, không tự kết luận “suy dinh dưỡng”. Rewrite cũ đã mắc lỗi thêm chẩn đoán.
- Query 693: người vợ dùng Drosperin ba năm, người chồng dị ứng bao cao su. Hai ý là ảnh hưởng sinh sản về sau và phương án tránh thai khác. Không chuyển dị ứng sang người vợ; không tự đoán chất gây dị ứng hoặc hoạt chất thuốc khi chưa xác minh.
- Query 594: kể lại nhiều lần cùng một vấn đề hiếm muộn. Có thể loại diễn đạt lặp nhưng không tự gán nguyên nhân hoặc mã ICD cụ thể.
- Query 22: hỏi “khi nào”, không đổi thành “điều kiện gì”; giữ phạm vi miễn phí/có phí và đối tượng được nêu.

**Suy luận áp dụng:** sửa lỗi quy chiếu/chủ thể có khả năng hữu ích hơn xóa tất cả đại từ. Đại từ xã giao và đại từ mang thông tin quan hệ phải được phân biệt. Khi không xác định được antecedent, giữ nguyên và đánh dấu unresolved; không đoán từ tài liệu truy hồi.

## 2. Nguồn AI Guru và phần áp dụng

### Multi-query và decomposition là hai phép thử khác nhau

[Bài 01 — Multi-Query & Query Expansion](https://knowledge.aiguru.com.vn/content/knowledgebase/21-advanced-rag-techniques/01-multi-query-expansion/01-multi-query-expansion.vi.md) mô tả mở các cách diễn đạt và fusion thứ hạng. [Bài 02 — Query Rewrite & Sub-Query Decomposition](https://knowledge.aiguru.com.vn/content/knowledgebase/21-advanced-rag-techniques/02-query-rewrite-decomposition/02-query-rewrite-decomposition.vi.md) tách nhu cầu thông tin thành các truy vấn con.

**Thiết kế của ta:** rewrite và facets phải được A/B riêng. Mỗi facet kế thừa đúng facts liên quan; không biến một câu điều trị thành danh sách bệnh có thể mắc. Giữ original branch, provenance theo view/facet và ngân sách trọng số cố định. Tài liệu đáp ứng một ý hữu ích vẫn là candidate; không hard-filter vì nó không trả lời mọi ý cùng lúc. Chưa có nhãn BTC nên độ trôi chảy của rewrite và số docs mới không phải tiêu chí thắng.

### Parent–child: tách đơn vị tìm kiếm, đọc hiểu và nộp bài

[Bài 05 — Hierarchical Parent–Child](https://knowledge.aiguru.com.vn/content/knowledgebase/21-advanced-rag-techniques/05-hierarchical-parent-child/05-hierarchical-parent-child.vi.md) tìm trên child rồi lấy parent để cung cấp ngữ cảnh. Điều đó phù hợp chatbot nhưng không có nghĩa toàn bộ parent là chunk tối ưu để nộp BTC.

**Thiết kế của ta:** child dùng tìm evidence; section/parent dùng chấm mức liên quan và giải quyết tham chiếu; output vẫn là đoạn liên tục từ nguồn. Giữ ba trường riêng: `retrieval_text`, `scoring_context`, `output_source_span`. Không mặc định append cả parent dài, cũng không mặc định child ngắn nhất tốt nhất. P2b đã cho thấy localization bằng BGE có thể thất bại.

### Contextual retrieval: thêm ngữ cảnh vào scoring, không sửa evidence

[Bài 06 — Contextual Retrieval](https://knowledge.aiguru.com.vn/content/knowledgebase/21-advanced-rag-techniques/06-contextual-retrieval/06-contextual-retrieval.vi.md) giải thích mất ngữ cảnh khi một chunk tách khỏi tài liệu. [Nghiên cứu gốc của Anthropic](https://www.anthropic.com/research/contextual-retrieval) thêm ngữ cảnh riêng cho chunk trước embedding/BM25; đây khác với chỉ thêm tóm tắt chung của cả tài liệu.

**Bản nhẹ của ta:** dùng title và heading có thật của source để rerank trên shortlist, chưa gọi LLM tạo contextual prefix toàn corpus. Đây là approximation cần thử, không gọi là đã tái tạo phương pháp Anthropic. Không có title/heading thì bỏ phần thiếu, không bịa. Prefix chỉ nằm trong đầu vào scorer; `chunk_text` xuất ra phải lấy từ source offsets, không cắt prefix bằng heuristic.

### Late interaction và corrective retrieval

[Bài 10 — Multi-Vector & ColBERT](https://knowledge.aiguru.com.vn/content/knowledgebase/21-advanced-rag-techniques/10-multi-vector-colbert/10-multi-vector-colbert.vi.md) mô tả so khớp token-level. Áp dụng dự phòng bằng BGE-M3 multi-vector trên shortlist, không xây index ColBERT mới cho hơn một triệu docs. Benchmark chi phí trước khi tăng quy mô.

[Bài 11 — Corrective RAG](https://knowledge.aiguru.com.vn/content/knowledgebase/21-advanced-rag-techniques/11-corrective-rag/11-corrective-rag.vi.md) đặt bước grading và truy hồi bổ sung khi evidence không đủ. **Biến thể hợp lệ của ta:** một vòng truy hồi bổ sung trong corpus BTC cho ý hỏi còn thiếu, không đưa kết quả web ngoài corpus vào submission. Không dùng các ngưỡng minh họa 0.4/0.8 như xác suất đã calibration; tài liệu liên quan không được coi là sai chỉ vì thiếu metadata tuổi/thời gian.

## 3. Thứ tự thử và hợp đồng đầu ra

Các tên R1–R5 là nhánh thiết kế, chưa là Exp đã chạy. Cấp số Exp mới lúc tạo artifact; không ghi đè Exp144 hoặc cache cũ.

1. **R1 — Gated grounded standalone rewrite, docs-only.** Tối đa một rewrite tiếng Việt/query theo gating bài24 đã mô tả ở trên; original weight1, rewrite0.5, RRF k=60. Chỉ thêm view qua semantic audit; câu rõ nghĩa/fail validation giữ nguyên. Giữ candidate cap, selection và chunks của control. Dùng model <=15B, revision hợp lệ đã audit trên Colab; không gọi API tính phí mặc định.
2. **R2 — Facet retrieval, docs-only.** So với cùng control R1; chỉ bật khi có >=2 ý hỏi thực sự. Tối đa ba facets, tổng weight 0.75 chia đều. Candidate union dành tối đa 50 vị trí/facet trước global cap 2.000, dedup trước khi đếm; pool đầy thì lấy phần còn lại theo fused rank. Đây là bảo vệ cơ hội được rerank, không phải ép xuất docs kém. Query một ý giữ nguyên. Query gốc vẫn quyết định relevance cuối.
3. **R3 — Context-aware reranking, cùng pool.** Trên cùng cặp query/chunk, so sánh scorer đọc chunk thô với title + heading + chunk. Giữ nguyên body token budget giữa hai nhánh; title/heading tổng tối đa 64 tokenizer tokens. Chấm theo budget selective reranking đã định, không toàn corpus. Thử docs-only trước, cùng policy top130 + owner floor; đầu vào đổi phải có cache namespace mới.
4. **R4 — Source-span selection, chunks-only.** Dùng ranking R3; giữ docs và số chunks. Chỉ thay tối đa mười chunks/query theo mức bất đồng raw/context cao nhất; candidate là paragraph/section liên tục chứa evidence trong cùng source. Section >768 tokenizer tokens chia tại ranh giới câu; câu quá dài dùng tokenizer offsets. Không thay bằng đoạn ngắn chỉ vì ngắn. Fail source/offset thì giữ chunk cũ.
5. **R5 — One-hop corpus-only rescue, dự phòng.** Chỉ tối đa 300 query có Jaccard top50 BM25/dense thấp nhất (tie theo query_id), và có >=2 facets hợp lệ. Tối đa một facet chưa được grader tìm thấy support span; tối đa một lượt search bổ sung, 100 candidates/query. Không tìm thấy support không chứng minh thiếu gold evidence. Rerank bằng query gốc; giữ control nếu không có candidate hợp lệ. Hoãn nếu R1–R4 chưa có kết quả hoặc ETA >2 giờ.

Schema view tối thiểu: `query_id`, `query_sha256`, `view_type`, `view_text`, `facet_id`, `source_spans`, `preserved_facts`, `unresolved_references`, `validation_errors`, `model_revision`, `prompt_hash`. Source spans là character offsets trên query gốc; không phải gold evidence. Tiêu chí semantic không thể chứng minh chỉ bằng JSON schema hoặc regex: audit 60 query cố định, rà soát mọi case bị flag và giữ fallback bảo thủ. LLM judge chỉ là diagnostic, không là gold.

Mỗi score record có query/view hash, doc_id, source hash, span offsets, representation version, model revision/prompt hash. Giữ provenance cả khi cùng doc được nhiều view tìm thấy. Không nhân trọng số chỉ vì một query có nhiều facets hay nhiều paraphrases trùng nhau.

## 4. Các điều không sao chép từ tutorial

- Không đưa chat history giả hoặc câu hỏi của người khác vào input.
- Không sao chép model Gemini/Claude/OpenAI trong ví dụ khi chưa chứng minh tổng tham số và release date đúng luật; API provider không miễn trừ giới hạn 15B.
- Không dùng generation, tóm tắt hoặc contextual prefix làm `chunk_text`.
- Không dùng Web Search rescue làm nguồn docs mới ngoài corpus.
- Không xây memory service, GraphRAG, agent framework mới chỉ để giống kiến trúc tutorial.
- Không xem các mức gain, latency hay tỷ lệ lỗi minh họa trong tutorial là bằng chứng trên R2AI. Metric của bài nghiên cứu ngoài không tương đương macro-F2 BTC.
- Không coi BM25/Qwen score là xác suất hoặc “số docs relevant thật”; không hard-threshold theo ví dụ.

## 5. Nghiệm thu và quyết định

Unit/regression: giữ đúng chủ thể và negation, không thêm chẩn đoán; facets không mất ràng buộc; query đơn không bị split; không history liên-query; source span exact; prefix không lọt output; stale cache bị từ chối; resume không lặp pairs; chunks/docs bất biến đúng trục thí nghiệm.

BTC quyết định promotion bằng đủ bảy metrics dưới evaluator mới. Nếu nhánh không đổi cũng đổi điểm, kiểm tra artifact/hash/evaluator trước kết luận. Không gán giảm điểm Exp137 chỉ cho translation; không gán tăng cosine cho tăng F2. Ngừng một hướng sau hai phép thử có đối chứng không cải thiện; ưu tiên khai thác cache đã có, không kéo dài một job GPU sang hai ngày.
