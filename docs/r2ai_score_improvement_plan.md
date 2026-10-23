# R2AI Stage 3 — kế hoạch cải thiện điểm hiện hành

> Cập nhật: 2026-10-23. Đây là tài liệu điều hành ngắn gọn. Lịch sử đầy đủ nằm tại [bản archive](archive/r2ai_score_improvement_plan_full_20261023.md); số liệu từng lần nộp nằm trong [experiments log](experiments_log.md).

## 1. Mục tiêu và trạng thái

- Mục tiêu gần nhất: vượt baseline BTC `0.3764`; ngưỡng làm việc là `FINAL_SCORE >= 0.38`.
- Best đã xác nhận: **Exp122 — 0.3516**.
- Khoảng cách tới 0.38: **0.0284**, quá lớn để tiếp tục kỳ vọng vào tune top-k/cap nhỏ.
- Nút thắt hiện tại là precision và candidate quality, không còn là coverage corpus.
- Full active index gần nhất: khoảng **1,212,421 documents / 1,724,798 chunks**; registry embedded đã được đối soát ở vòng full-corpus.

### Champion hiện tại

| Exp | Final | Docs F2 | Chunks F2 | Docs P/R | Chunks P/R |
|---|---:|---:|---:|---:|---:|
| 122 | **0.3516** | 0.3586 | **0.3446** | 0.1816 / 0.6114 | 0.2512 / 0.4682 |

Giữ Exp122 làm control bất biến. Mỗi treatment chỉ được thay một trục chính: query, document membership hoặc chunk selection.

## 2. Việc cần làm ngay

### P0 — Production multilingual query translation

Mục tiêu: sửa recall/precision đa ngôn ngữ trước khi thay retrieval architecture.

1. Chạy `notebooks/16_translation_production_2xt4_kaggle.ipynb` cho đủ 1,200 query trên 2×T4.
2. Dùng model đã chốt từ benchmark:
   - Anh: VinAI Translate làm nguồn chính;
   - Trung: Qwen 14B, đồng thời rescue các bản Anh thất bại/không tự nhiên;
   - luôn giữ nguyên query gốc làm một view riêng.
3. Tải `translation_production_v1.zip`; không tải model/cache.
4. Audit local trước khi retrieval:
   - đủ đúng 1,200 `query_id`, không trùng;
   - không có bản dịch rỗng, lỗi JSON hoặc bị cắt;
   - phát hiện copy nguyên văn sai ngôn ngữ và hallucination thuật ngữ y khoa;
   - lưu hash input, model, prompt và output.
5. Dùng `scripts/build_bm25_translation_treatment.py` để tạo candidate treatment.
6. Sinh submission A/B chỉ thay query views; giữ nguyên document/chunk policy của Exp122.

**Gate để nộp:** output treatment phải khác control, candidate membership phải có churn có ý nghĩa, ZIP dưới giới hạn 100 MB và validation pass.

### P1 — BM25 → dense passage cascade

Mục tiêu: thay candidate generation, không tiếp tục kéo dài envelope của cùng ranking.

1. Dùng query gốc + bản dịch đã audit để retrieve BM25 theo từng ngôn ngữ.
2. Union candidate ở document level với dense BGE-M3/Qwen index.
3. Dùng ICD-10 như soft routing/boost, tuyệt đối không hard-filter.
4. Rerank passage trong candidate pool bằng dense/cross-encoder.
5. Aggregate passage → document bằng max + top-n support; giới hạn duplicate passage cùng doc.
6. Chạy treatment qua `notebooks/14_bm25_dense_passage_cascade_kaggle.ipynb` hoặc pipeline local tương đương.

**Gate để nộp:** phải cải thiện proxy candidate recall hoặc thay document membership đủ lớn; nếu chỉ đổi thứ tự các doc cũ thì không tốn slot.

### P2 — Selective reranking và canonical query

Chỉ triển khai sau khi P0/P1 cho tín hiệu dương.

- Phân loại query theo độ dài, ngôn ngữ, độ mơ hồ và mật độ thuật ngữ.
- Canonicalize đại từ/cách nói đời thường nhưng giữ query gốc song song, ví dụ `bầu` ↔ `phụ nữ mang thai`.
- Chỉ dùng LLM rewrite/HyDE cho query mơ hồ hoặc candidate disagreement cao.
- Rerank sâu cho query khó; query dễ dùng lexical/dense consensus để tránh làm giảm precision.
- Multi-hop chỉ bật khi query thật sự chứa từ hai ràng buộc y khoa độc lập trở lên.

## 3. Thứ tự submission

1. **Translation-only:** Exp122 + query views production.
2. **Cascade-only:** Exp122 + BM25/dense candidate membership, query control.
3. **Translation + cascade:** chỉ khi cả hai treatment riêng đều dương.
4. **Selective rerank:** chỉ trên winner ở bước 1–3.

Không gộp nhiều thay đổi chưa được đo trong một slot; nếu điểm đổi sẽ không xác định được nguyên nhân.

## 4. Tiêu chí quyết định

- Tiếp tục một nhánh khi tăng `FINAL_SCORE >= 0.005`, hoặc tăng `>= 0.01` trên đúng axis mục tiêu mà không phá axis còn lại.
- Dừng sau hai treatment kiến trúc độc lập cùng âm/không đổi.
- Không nộp nếu file output giống control, candidate set gần như không đổi, validation fail hoặc provenance thiếu.
- Với score hidden, ưu tiên thay đổi có giả thuyết và measurable intermediate signal thay vì sweep mù.

## 5. Những hướng đã bão hòa hoặc bị loại

- Không tiếp tục sweep nhỏ top-k, cap, width, span hoặc threshold quanh cấu hình hiện tại.
- Không hard-filter bằng ICD-10: thử nghiệm cũ làm Docs recall sụp mạnh.
- Không dùng Qwen3-0.6B như direct membership reranker: thay đổi rất nhỏ và không tạo bước nhảy.
- Không mở rộng envelope/chunk window mù: Exp131–135 đều thấp hơn champion.
- Không embed thêm model mới trước khi P0/P1 chứng minh dense representation là bottleneck.
- Không dùng closed API hoặc dữ liệu vi phạm luật cuộc thi.

## 6. Kết quả gần đây cần nhớ

| Exp | Thay đổi | Final | Kết luận |
|---|---|---:|---|
| 121 | full parents | 0.3412 | Bước nhảy chunk recall tốt |
| 122 | thêm 19 missing doc parents | **0.3516** | Champion |
| 123 | CE-ranked parents | 0.3501 | Thấp hơn champion |
| 125 | pilot query understanding 50 câu | 0.3513 | Prompt/model cũ chưa tạo lợi ích |
| 129 | add 15 ranked parents | 0.3500 | Không vượt champion |
| 131 | width 512 | 0.3047 | Loại |
| 131b | width 384 | 0.3079 | Loại |
| 132 | anchored missing | 0.3162 | Loại |
| 133 | top75 / width640 | 0.3233 | Loại |
| 134 | top60 / width768 | 0.3285 | Loại |
| 135 | top50 / width896 | 0.3326 | Loại |

Tham chiếu cạnh tranh: public top từng thấy `0.4071`; một kết quả khoảng `0.76` đã bị ẩn và chỉ được ghi nhận như thông tin chưa kiểm chứng, không dùng làm ground truth kỹ thuật.

## 7. Artifact và entrypoint đang dùng

- Query/corpus BTC: `data/raw/btc_provided/`
- Active indices: `data/indices/new_dataset/`
- Production translation notebook: `notebooks/16_translation_production_2xt4_kaggle.ipynb`
- Cascade notebook: `notebooks/14_bm25_dense_passage_cascade_kaggle.ipynb`
- Translation builder: `scripts/build_bm25_translation_treatment.py`
- BM25 index builder: `scripts/build_bm25_document_index.py`
- Submission control: `scripts/generate_best_submission.py`
- Validators: `scripts/validate_submission.py`, `scripts/validate_evidence_submission.py`
- Script map: `scripts/README.md`

## 8. Checklist bắt buộc trước khi nộp

- [ ] Đúng toàn bộ query ID và schema BTC.
- [ ] Không URL/doc ngoài corpus; giữ nguyên `doc_id` BTC kể cả khi crawl từ URL thay thế.
- [ ] Không duplicate doc/chunk ngoài chủ ý.
- [ ] Docs và chunks đều lấy từ artifacts hợp lệ.
- [ ] So sánh hash/diff với control để tránh no-op.
- [ ] Ghi config, source artifact, hash và giả thuyết vào `docs/experiments_log/`.
- [ ] Không vượt giới hạn dung lượng upload.
- [ ] Tuân thủ toàn bộ `docs/competition_information/`.

## 9. Tài liệu tham chiếu

- [Thông tin và luật cuộc thi](competition_information/)
- [Mentor Day 2](./_AI_Guru__R2AI_Stage3_MentorDay_Oct_22th.pdf)
- [Phân tích benchmark dịch](translation_benchmark_analysis_20261023.md)
- [Meeting insights](btc_meeting_insights_and_roadmap.md)
- [Lịch sử kế hoạch đầy đủ](archive/r2ai_score_improvement_plan_full_20261023.md)
- [Experiment log tổng](experiments_log.md)
