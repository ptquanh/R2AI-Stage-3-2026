[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 17: BGE-M3 Hybrid Retrieval (Dense 1.0 + Sparse 0.5, 700k docs)

- **Mục tiêu:** Thử nghiệm đẩy mạnh trọng số Sparse Lexical từ `0.3` lên `0.5` theo khuyến nghị của tác giả BGE-M3 nhằm tối ưu hơn nữa khả năng neo từ khóa y khoa.
- **Cấu hình & Tham số:**
  - `dense_weight = 1.0` | `sparse_weight = 0.5`
  - File nộp: `submission_bgem3_hybrid_w05.zip` (96.88 MB, 100 docs, 92 chunks)
- **Kết quả:**
  - `FINAL_SCORE: 0.1641` _(Giảm nhẹ -0.0043 so với Exp 16: 0.1684)_
  - `DOCS_F2MACRO: 0.1720` | `DOCS_PRECISION: 0.1397` | `DOCS_RECALL: 0.2181`
  - `CHUNKS_F2MACRO: 0.1562` | `CHUNKS_PRECISION: 0.1411` | `CHUNKS_RECALL: 0.1890`
- **Phân tích Đột phá (Root Cause Analysis - Hiện tượng Lệch pha Ngôn ngữ trong Sparse Retrieval):**
  - **Điểm tích cực:** `CHUNKS_PRECISION` tiếp tục tăng lên mức cao kỷ lục mới **`0.1411`** (tăng từ 0.1398). Điều này khẳng định tăng trọng số từ vựng giúp các đoạn văn được chọn lọc vô cùng chuẩn xác.
  - **Lý do Recall và Final Score sụt giảm:**
    1. **Bản chất Corpus đa ngôn ngữ:** Tập dữ liệu của BTC chứa một tỷ lệ rất lớn tài liệu tiếng Trung (các domain hàng đầu như `120ask.com`, `youlai.cn`, `cnkang.com`, `zhongyibaodian.net`...).
    2. **Sparse Lexical chỉ match đồng ngôn ngữ:** Truy vấn của bài thi là **Tiếng Việt**. Mô hình Dense Vector (1024d) của BGE-M3 là mô hình liên ngôn ngữ (Cross-lingual continuous space), nên query tiếng Việt vẫn tìm được tài liệu tiếng Trung rất tốt. Tuy nhiên, ma trận Sparse Lexical dựa trên token vocabulary rời rạc (XLM-RoBERTa vocab): từ tiếng Việt (`tiểu đường`) và từ tiếng Trung (`糖尿病`) có token ID hoàn toàn khác nhau, dẫn tới điểm Sparse giữa query tiếng Việt và tài liệu tiếng Trung luôn bằng **0.0**!
    3. **Hiệu ứng dìm tài liệu tiếng Trung:**
       - Tài liệu tiếng Việt nhận: $1.0 \times \text{Dense} + 0.5 \times \text{Sparse}$.
       - Tài liệu tiếng Trung chỉ nhận: $1.0 \times \text{Dense} + 0.0 \times \text{Sparse}$.
         👉 Khi $w_s$ tăng từ $0.3 \rightarrow 0.5$, khoảng cách điểm này càng bị kéo giãn, khiến các tài liệu tiếng Trung chuẩn xác bị tài liệu tiếng Việt "chen hàng" đẩy văng khỏi Top 100 docs và Top chunks. Kéo theo `DOCS_RECALL` rớt từ `22.28%` xuống `21.81%`.
- **Chiến lược & Hướng giải quyết mới (Multilingual Query Translation):**
  - Không cần nộp phương án B (`w_s = 0.7`) vì sẽ càng dìm tài liệu tiếng Trung mạnh hơn.
  - Nghiên cứu mô hình dịch thuật mở (Open-source $\le 15\text{B}$, phát hành trước 01/08/2026) để dịch query tiếng Việt $\rightarrow$ Tiếng Trung & Tiếng Anh. Khi đó:
    $$Q_{\text{sparse}} = \text{Merge}\big(\text{Sparse}(Q_{\text{vi}}), \text{Sparse}(Q_{\text{zh}})\big)$$
    Cả tài liệu tiếng Trung và tiếng Việt đều sẽ nhận được trọn vẹn điểm thưởng Lexical Matching, hứa hẹn tạo nên bước nhảy vọt Recall chưa từng có!

---

---
[← Exp 16](exp16_bge_m3_hybrid_700k.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 18 →](exp18_rrf_fusion.md)
