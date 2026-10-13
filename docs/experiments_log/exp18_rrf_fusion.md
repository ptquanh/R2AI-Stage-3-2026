[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 18: Reciprocal Rank Fusion (RRF) (Dense 1.0 + Sparse 0.8, k=60)

- **Mục tiêu:** Thử nghiệm thuật toán Reciprocal Rank Fusion (RRF) nhằm giải quyết sự khác biệt về biên độ phân phối điểm (score scale) giữa Dense Cosine Similarity và Sparse Lexical Dot-Product.
- **Cấu hình & Tham số:**
  - `fusion = rrf` | `dense_weight = 1.0` | `sparse_weight = 0.8` | `rrf_k = 60` | `cand_pool = 150`
  - File nộp: `submission_bgem3_rrf_w08.zip`
- **Kết quả:**
  - `FINAL_SCORE: 0.1483` _(Sụt giảm -0.0201 so với Exp 16: 0.1684)_
  - `DOCS_F2MACRO: 0.1559` | `DOCS_PRECISION: 0.1252` | `DOCS_RECALL: 0.1996`
  - `CHUNKS_F2MACRO: 0.1408` | `CHUNKS_PRECISION: 0.1229` | `CHUNKS_RECALL: 0.1730`
- **Phân tích nguyên nhân (Why RRF Underperformed):**
  1. **Triệt tiêu cường độ tín hiệu Cosine (Loss of Continuous Distance Confidence):** Dense Cosine Similarity phản ánh độ tin cậy liên tục rất nhạy (ví dụ cosine `0.88` so với `0.70` là một khoảng cách ngữ nghĩa cực kỳ lớn). Tuy nhiên công thức RRF $\frac{1}{60 + \text{rank}}$ chỉ quan tâm đến thứ hạng cục bộ, biến rank 1 thành $\approx 0.01639$ và rank 2 thành $\approx 0.01613$, triệt tiêu hoàn toàn ưu thế của những tài liệu có độ tin cậy ngữ nghĩa vượt trội.
  2. **Hiệu ứng phân mảnh đa phân mảnh (Multi-shard Partitioning Artifact):** Vì dữ liệu được chia theo từng shard (100k docs/shard) và chỉ giữ lại `cand_pool = 150` ứng viên mỗi shard trước khi RRF toàn cục, các tài liệu có điểm Dense rất cao ở một shard đơn lẻ dễ bị bất lợi so với các tài liệu xuất hiện rank trung bình ở nhiều phân mảnh.
  3. **Kết luận:** Linear Score Fusion vượt trội hơn hẳn RRF trong bài toán này nhờ giữ nguyên được độ tự tin khoảng cách (distance metric confidence).

---

---
[← Exp 17](exp17_bge_m3_hybrid_sparse05.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 19 →](exp19_bge_m3_linear_hybrid.md)
