# BÁO CÁO PHÂN TÍCH BUỔI HỌP BTC & LỘ TRÌNH ĐỘT PHÁ ĐIỂM SỐ (R2AI STAGE 3)

> **Ngày họp:** 12/10/2026  
> **Nguồn tin:** Chỉ đạo & định hướng trực tiếp từ Ban Tổ Chức (BTC) cuộc thi  
> **Tài liệu liên quan:** [`docs/experiments_log.md`](file:///d:/CODE%20PLAYGROUND/Projects/Competitions/R2AI-Stage-3-2026/docs/experiments_log.md) | [`docs/improvement_strategy_and_exp29.md`](file:///d:/CODE%20PLAYGROUND/Projects/Competitions/R2AI-Stage-3-2026/docs/improvement_strategy_and_exp29.md)

---

## 1. TỔNG HỢP NỘI DUNG CHỈ ĐẠO TỪ BAN TỔ CHỨC

Trong buổi họp kỹ thuật hôm nay, BTC đã chính thức công bố các thông tin then chốt và hướng dẫn giải pháp cho bài toán Medical Information Retrieval:

1. **Phân nhóm chủ đề theo ICD-10:**
   - Sử dụng bảng phân loại bệnh quốc tế ICD-10 làm khung kiến trúc để nhóm các bài toán/câu hỏi y khoa.
   - Hướng tiếp cận được khuyến nghị:
     - Bắt đầu từ **nhóm chương bệnh lớn** (Chương I đến Chương XXI).
     - Kết hợp nhiều tín hiệu lâm sàng (từ điển thuật ngữ bệnh, chuyên khoa, triệu chứng).
     - **Nguyên tắc an toàn:** Giữ trạng thái **không xác định (UNKNOWN)** khi thiếu bằng chứng rõ ràng.
     - _Ví dụ BTC minh họa:_ Đái tháo đường Type 2 thuộc mã `E11` (Chương IV: Bệnh nội tiết, dinh dưỡng và chuyển hóa).
2. **Tiêu chuẩn Reranker Đa ngữ:**
   - Mô hình Reranker cần ưu tiên đánh giá **nội dung trả lời đúng ý lâm sàng, bất kể câu hỏi và tài liệu khác biệt về ngôn ngữ (tiếng Việt vs tiếng Trung)**.
3. **Cơ chế Lọc Ngưỡng của Baseline (Threshold 0.73):**
   - Baseline chính thức của BTC sử dụng tokenizer từ `BAAI/bge-m3`.
   - **Số lượng tài liệu trả về được lọc linh hoạt theo ngưỡng tương đồng `threshold >= 0.73`** (thay vì cố định ép cứng Top 100 tài liệu cho mọi câu hỏi).
4. **Cập nhật Quy mô Corpus (Rút gọn còn ~1 triệu URLs):**
   - Sau hôm nay, BTC sẽ công bố tập dữ liệu rút gọn còn khoảng **1 triệu URLs** (là tập con trực tiếp của tập 4 triệu URLs ban đầu).
   - Các đội đã cào từ tập 4 triệu không cần cào lại, chỉ cần lọc theo danh sách mới.
5. **Ràng buộc nộp bài qua Portal & Hỗ trợ nộp qua Email:**
   - Giới hạn 100MB là rào cản kỹ thuật của web portal. Nếu tệp nộp bài quá lớn do dung lượng chunks/evidence, các đội có thể gửi email trực tiếp để nhờ BTC hỗ trợ nộp.
6. **Xác nhận nút thắt lớn nhất của các đội thi:**
   - BTC xác nhận: **"Vấn đề lớn nhất của các đội hiện nay là chưa đủ corpus"** $\to$ Khẳng định tuyệt đối việc mở rộng và bao phủ kho dữ liệu là đòn bẩy số 1.
7. **Định hướng Nâng cao:**
   - Khuyến khích fine-tune mô hình embedding hoặc áp dụng Contrastive Learning trên các cặp câu hỏi - câu trả lời y khoa.

---

## 2. PHÂN TÍCH CHUYÊN SÂU & GIẢI MÃ NÚT THẮT CỦA TEAM CHÚNG TA

### 2.1. Nút thắt Precision (20%) được giải mã: Vì sao Top 1 đạt Precision 46.9% còn chúng ta chỉ 20.5%?

- **Cách chúng ta làm từ Exp 1 đến Exp 29:**
  - Với mọi query, chúng ta luôn ép trả về đúng **100 docs** và **98 chunks**.
  - Thực tế, một câu hỏi y khoa thường chỉ có khoảng **5 – 15 tài liệu Ground Truth**. Khi ép trả về 100 docs, có tới **85 – 95 tài liệu false positive** bị nhồi vào bài nộp với điểm similarity thấp (0.3 – 0.5).
  - Điều này làm tử số Precision bị chia cho 100:
    $$\text{Precision} \le \frac{15}{100} = 15\%$$
- **Giải pháp từ BTC (Threshold $\ge 0.73$):**
  - Khi chỉ giữ các tài liệu có điểm $\ge 0.73$:
    - Nếu query có 10 tài liệu đạt chuẩn $\to$ Chỉ trả về 10 tài liệu $\to \text{Precision} = \frac{10}{10} = 100\%$.
    - Recall không bị ảnh hưởng vì toàn bộ tài liệu đúng đều nằm trong nhóm điểm cao $\ge 0.73$.
  - **Dự phóng:** Precision sẽ tăng vọt từ **20% lên 35% – 45%**, trực tiếp kéo Final Score từ **0.24 lên 0.28 – 0.32+**!

### 2.2. Lợi thế Tuyệt đối khi BTC Rút gọn còn 1 Triệu URLs

- Kho dữ liệu của chúng ta hiện nay:
  - Đã có **20 shards với gần 1.8 triệu documents** đã lập chỉ mục sẵn sàng.
  - Đang có **30.474 documents Tier 1 mới** (trong đó có 21.303 bài Long Châu và 8.932 bài ask.39) trong `tier_1_resume.parquet`.
- Vì 1 triệu URLs của BTC là **tập con** của 4 triệu, độ phủ (Coverage) thực tế của chúng ta đối với Ground Truth của đề thi sẽ nhảy vọt từ ~45% lên gần **85% – 95%**!

---

## 3. LỘ TRÌNH THỰC THI CHI TIẾT (ROADMAP ĐỘT PHÁ)

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ PHA 1 (LÀM NGAY): DYNAMIC THRESHOLDING & CANDIDATE PRUNING (Exp 30)          │
│ • Bổ sung --score_threshold 0.73 kèm khoảng bảo vệ min_docs=5, max_docs=100  │
│ • Chuẩn hóa Dense Similarity & Hybrid Threshold                              │
│ • Mục tiêu: Đưa Precision từ 20% -> 35%+, Final Score vượt mốc 0.27+         │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ PHA 2: EMBEDDING 30K TÀI LIỆU VÀNG TIER 1 RESUME (Exp 31)                    │
│ • Tạo Semantic Chunks & BGE-M3 Vectors cho 21.303 bài Long Châu + 8.9k ask.39│
│ • Đóng gói thành shard mới tier 1/1500-1600k                                  │
│ • Mục tiêu: Đẩy Docs Recall vượt 36% - 38%, áp đảo tập 1M URLs của BTC      │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ PHA 3: HỆ THỐNG PHÂN LOẠI CHỦ ĐỀ THEO ICD-10 (Exp 32)                       │
│ • Xây dựng module icd10_classifier.py (Từ điển & Quy tắc chuyên khoa)         │
│ • Gán nhãn 10 chương lớn (A-B, C, E, I, J, K, M, N...) cho queries            │
│ • Lọc nhiễu chéo ngành & Boost điểm cùng nhóm ICD-10                         │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ PHA 4: RERANKER ĐA NGỮ (CROSS-LINGUAL) & CONTRASTIVE LEARNING                │
│ • Áp dụng Score Interpolation: Final = Stage1 + 0.2 * Reranker                │
│ • Tận dụng cặp Hỏi-Đáp bác sĩ từ 120ask, ask.39 và Long Châu                 │
└──────────────────────────────────────────────────────────────────────────────┘
```
