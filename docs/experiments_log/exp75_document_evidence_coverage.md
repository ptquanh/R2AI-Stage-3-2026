# Exp 75 — Evidence coverage trên Docs Exp74

## Giả thuyết và control

Exp74 đạt Final `0,3221`, Docs F2 `0,3574`, Chunks F2 `0,2868`. Giữ nguyên toàn bộ `relevant_docs` của Exp74 để đo thay đổi chunk axis. Trong Exp74 có 106.546 cặp query/chunk-document trên 1.200 queries (88,788/query), trong đó 24 cặp nằm ngoài selected Docs sau refresh tail. BTC chấm Docs và Chunks độc lập; các evidence có sẵn này được giữ trong candidate pool.

## Cấu hình triển khai

- Script: `scripts/generate_exp75_evidence_coverage.py` với các bước `prepare`, `score`, `build` có checkpoint.
- Source: text store active index 1.212.421 docs / 1.724.798 chunks, chỉ official IDs.
- Tạo windows liên tục theo câu/đoạn trên toàn bộ source, hỗ trợ dấu câu Trung không có khoảng trắng; lưu tối đa ba vùng lexical tốt với offsets gốc cho mỗi cặp query/document. Latin bỏ dấu chỉ dùng cho lexical ranking; source không bị sửa.
- Documents đã có evidence: chọn một window từ các chunks cũ, rộng tối đa 1.500 ký tự. Documents còn thiếu: preselect một window từ full source, chấm tối đa 60 docs/query theo document rank.
- Model: `BAAI/bge-reranker-v2-m3`, revision `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e`, FP16, context 384 tokens, batch 16.
- Chọn window chấm khoảng 500 ký tự quanh vùng lexical tốt trong output span, sau đó áp ngân sách tokenizer thực tế cho passage/query; inference tắt truncation và từ chối input vượt context. Output span có thể rộng hơn window chấm nhưng phải chứa nguyên window đó.
- Không tái sử dụng CE scores từ spans/context cũ. Cache mới gắn với query hash, doc ID, source hash, offsets, model revision, kiểu input pair và max length.
- Pilot 2.000 pairs phân tầng theo ngôn ngữ và độ dài, lưu throughput/ETA trước batch đầy đủ.
- Builder ưu tiên một evidence cho mỗi document đã được đại diện; thêm docs chưa có evidence bằng blend 0,75 CE normalized và 0,25 document rank. Documents và query IDs giữ nguyên Exp74.
- Đo offline các targets 120/140/180 trong cùng builder; ưu tiên 140 khi ZIP ≤95.000.000 bytes. Vòng đầu chỉ chấm tối đa 60 docs mới/query nên số đạt được có thể thấp hơn target 140/180; ghi rõ số thực tế.
- Đếm ZIP nén bằng stream trước khi ghi artifact. Chỉ xuất ZIP trong ngân sách target, không tạo ZIP ≥100 MB.

Thiết kế này thay đổi đồng thời số chunk-documents và độ dài/vị trí spans; kết quả tăng hoặc giảm không tách riêng được tác động của từng yếu tố. Báo cáo số docs thêm/mất, spans giữ nguyên/thay và độ phủ indexed offsets so với full source theo VI/EN/ZH.

## Trạng thái

Đã chuẩn bị 259.224 cặp query/document từ 163.699 source documents trong khoảng 920 giây: 106.546 cặp đã có evidence, 152.678 cặp thiếu evidence. Chấm mới đúng 72.000 cặp, 60 docs/query. Có 2.339 passages cần rút theo token budget trước inference.

Pilot 2.000 pairs: 37,64 giây, 53,13 pairs/giây, batch 16 trên RTX 3050 Ti Laptop 4 GB; mẫu gồm 796 ZH, 607 VI, 597 EN. ETA phần còn lại tại pilot: 1.317,5 giây (~22 phút). Lần khởi động pilot đầu thoát trước khi tạo score; chạy lại thành công và cache đầu vào không đổi. Đã chấm đủ 72.000 scores; phần còn lại sau pilot mất 953,34 giây, trung bình 73,43 pairs/giây.

Provenance/cache nằm tại `data/exp75_evidence/`: `prepare_manifest.json`, `pool.parquet`, `candidates.parquet`, `score_fingerprint.json`, `pilot.json`, `scores.npy`, `score_complete.json`, `build_manifest.json`.

## Artifact được khuyến nghị

- ZIP nộp: `submission_exp75_coverage140.zip`, 85.320.918 bytes (85,32 MB decimal), dưới target 95 MB và giới hạn 100 MB.
- JSON: `submission_exp75_coverage140.json`.
- Đủ 1.200 queries, mỗi query giữ nguyên 216 Docs Exp74.
- Tổng 167.304 chunks, mỗi chunk thuộc một document khác nhau trong query; trung bình 139,42 documents/query, min/max 123/140. Có 141 queries thấp hơn target do giới hạn số docs mới đã chấm; không bổ sung bằng passage rỗng.
- Giữ đủ 106.546 cặp query/document từng có evidence; thêm 60.758 cặp, không mất cặp cũ. Vẫn giữ 24 cặp chunk-documents ngoài selected Docs như control; hai trục được BTC chấm độc lập.
- 36.177 spans giữ nguyên, 70.369 spans được thay/rút trong source và 60.758 spans mới. Độ dài mean/median/max 1.213,20 / 1.388 / 1.500 ký tự. Việc giữ document có evidence không đồng nghĩa giữ nguyên nội dung span cũ.
- ZIP SHA-256: `6607d32e002ab83162a04dc49e18ac800bc1075dae5f007e262ee6f3af129c32`.
- JSON SHA-256: `ee74aa9fff21dae569fad21d70e41dd63d896f322644456d54e900bf54cb39fc`.

Đã đo hai bản offline cùng builder: coverage 120 đạt đúng 120 documents/query, ZIP 73.223.459 bytes; target 180 chỉ đạt trung bình 148,754 documents/query (min/max 123/160), ZIP 91.304.847 bytes. Cả ba dưới 95 MB; chỉ khuyến nghị nộp coverage 140 trước theo kế hoạch. Bản mang tên target 180 chưa phải ablation đạt đủ 180; muốn thử mức đó phải mở số candidates đã chấm.

## Audit cuối

- [Validator độc lập](../../data/exp75_evidence/independent_verification_140.json): pass trên toàn bộ 167.304 chunks từ 116.331 source documents, chỉ official IDs, đúng source substrings, schema/IDs/query coverage và document axis giữ nguyên Exp74. ZIP chỉ một `submission.json` tại root, CRC hợp lệ, payload khớp JSON ngoài ZIP.
- Phát hiện 41 scoring passages chỉ có whitespace trong cache đầu tiên; scores của chúng bị loại khỏi selection và ghi tại `quarantined_scoring_passages.parquet`. Bộ chọn window đã sửa để bỏ windows whitespace cho các lần prepare sau. Không cần sửa fallback output window nào trong lần build này (`window_repairs.json` là danh sách rỗng).
- [Audit indexed spans](../../data/exp75_evidence/indexed_span_coverage.json): trên 163.699 source docs, coverage ký tự trung bình VI 99,984%, EN 99,999%, ZH 100%; chỉ một EN doc dưới 90%. Chỉ đo phần text đã có trong text store, chưa chứng minh crawler lấy đủ nội dung website hoặc coverage nhãn.
- 33/33 tests cấp dự án pass. Bốn registry embedded/unembedded/remaining/excluded khớp SHA-256 sau merge 1k, không thay đổi dữ liệu embedding/index trong thí nghiệm này.

## Kết quả BTC — coverage 140

- Final Score: `0,2585` (`-0,0636` so với Exp74).
- Docs F2 / Precision / Recall: `0,3574 / 0,1813 / 0,6086`, giữ nguyên Exp74 đúng như control.
- Chunks F2: `0,1596` (`-0,1272`).
- Chunks Precision / Recall: `0,1079 / 0,2293`, cùng giảm mạnh từ `0,2401 / 0,3685`.

Exp75 thất bại rõ ràng trên chunk axis. Do thí nghiệm vừa thay/rút `70.369` spans cũ vừa thêm `60.758` spans mới, chưa thể quy toàn bộ regression cho riêng coverage; tuy nhiên mức giảm đủ lớn để loại target 180 và không tiêu slot cho target 120. Không dùng bất kỳ artifact Exp75 coverage nào làm baseline tiếp theo. Quay về toàn bộ chunks Exp74/Exp73 và chuyển sang Exp76 docs-only head rerank. Cache CE Exp75 chỉ là dữ liệu chẩn đoán/candidate, không phải chunk policy thắng.
