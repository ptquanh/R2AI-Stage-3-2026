# CHIẾN LƯỢC TỐI ƯU HÓA ĐIỂM SỐ & KẾ HOẠCH THỰC NGHIỆM EXP 29+

> **Dự án:** Medical Information Retrieval (R2AI Stage 3 2026)  
> **Tài liệu tham chiếu:** [`docs/experiments_log.md`](file:///d:/CODE%20PLAYGROUND/Projects/Competitions/R2AI-Stage-3-2026/docs/experiments_log.md)  
> **Thời gian cập nhật:** 12/10/2026  

---

## 1. TỔNG QUAN HIỆN TRẠNG & BÀI HỌC TỪ 28 THỰC NGHIỆM

### 1.1. Bản chất Hàm Mục tiêu $F_2$-Macro
Điểm số chính thức của cuộc thi được xác định bởi:
$$\text{FINAL\_SCORE} = \frac{1}{2}(\text{DOCS\_F2MACRO} + \text{CHUNKS\_F2MACRO})$$
Trong đó công thức $F_2$ cho cả Document và Chunk:
$$F_2 = \frac{5 \cdot P \cdot R}{4 \cdot P + R}$$
- Do hệ số $\beta = 2$, **Recall được ưu tiên gấp 2 lần Precision** trong mẫu số ($4P + R$).
- Tại điểm vận hành hiện tại ($R \approx 0.34, P \approx 0.21$):
  $$\frac{\partial F_2}{\partial R} \approx 1.38 \times \frac{\partial F_2}{\partial P}$$
- **Kết luận:** Recall là động lực tăng điểm lớn nhất. Tăng 1% Recall mang lại hiệu quả gấp ~1.4 lần so với tăng 1% Precision. Mọi chiến lược phải tập trung đưa đúng tài liệu Ground Truth vào Top 100.

### 1.2. Tổng kết các Cột mốc Đột phá (Exp 21 → Exp 28)
| Thử nghiệm | Mô tả Cấu hình | Final Score | Docs Recall | Docs Precision | Docs $F_2$ | Chunks Recall | Chunks $F_2$ |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Exp 21** | Linear Hybrid w=0.2 (11 Shards) | 0.2121 | 28.75% | 18.02% | 0.2233 | 25.36% | 0.2010 |
| **Exp 23** | Nới Top 200 Docs | 0.2110 | **35.47%** | 11.80% | 0.2195 | 25.36% | 0.2010 |
| **Exp 24** | Zero-shot Reranker (BGE-Reranker-v2-m3) | 0.1835 | 23.41% | 15.60% | 0.1880 | 21.05% | 0.1790 |
| **Exp 26** | Bổ sung Long Châu thô | 0.2146 | 29.04% | 18.15% | 0.2252 | 25.78% | 0.2041 |
| **Exp 27** | Bổ sung Tier 1 1300-1400k (19 Shards) | **0.2441** 🏆 | **33.95%** | **20.59%** | **0.2604** | **29.13%** | **0.2278** |
| **Exp 28** | Bổ sung Tier 1 1000-1100k: 120ask (20 Shards) | 0.2423 | 33.37% | **20.99%** 🥇 | 0.2582 | 28.88% | 0.2265 |

### 1.3. Rút ra 3 Bài học Cốt lõi
1. **Corpus Tier 1 Nội địa & Y tế Chuyên sâu là Đòn bẩy Số 1:** Exp 27 chứng minh khi nạp thêm 50k bài Long Châu, YouMed, Vinmec, ask.39, điểm số bứt phá **+13.7%** (từ 0.2146 lên 0.2441), cả Recall và Precision cùng tăng mạnh.
2. **Hiện tượng Cạnh tranh Slot Top 100 (Language / Shard Competition):** Khi kho dữ liệu đạt ngưỡng 2 triệu docs (Exp 28), tài liệu tiếng Trung từ `120ask` có điểm lexical/dense cao đã đẩy rớt một số tài liệu tiếng Việt Ground Truth ra khỏi vị trí Top 100, làm giảm Recall 0.58%.
3. **Bài học Xương máu về Reranking (Exp 24):** Tuyệt đối không dùng mô hình Cross-Encoder zero-shot để ghi đè 100% điểm Stage 1. Reranker phải kết hợp theo dạng **Score Interpolation (Nội suy điểm)** để bảo vệ exact-matches tiếng Việt.

---

## 2. PHÁT HIỆN 3 NÚT THẮT & LỖ HỔNG KỸ THUẬT

### 2.1. Lỗ hổng 1: Tồn tại 2 Khối Chỉ mục Bị Duplicate 100%
Quét chữ ký tài liệu trên toàn bộ 22 khối trong `data/indices` phát hiện:
- `data/indices/tier 1/100-200k/index` **trùng lặp 100%** với `data/indices/tier 1/0-100k/index` (cùng 100k chunks, cùng dải `doc_id` 584 → 334798).
- `data/indices/tier 1/1400-1500k/index` **trùng lặp 100%** với `data/indices/tier 1/1300-1400k/index` (cùng 166,093 chunks, cùng dải `doc_id` 681 → 4005839).

### 2.2. Lỗ hổng 2: Candidate Buffer Starvation (Bóp nghẹt Pool Ứng viên)
Trong [`scripts/run_submission.py`](file:///d:/CODE%20PLAYGROUND/Projects/Competitions/R2AI-Stage-3-2026/scripts/run_submission.py#L338-L344):
```python
cand_limit = max(args.top_docs, args.top_chunks) + 50  # = 150
if len(cfg["results"][q_idx]) > cand_limit:
    cfg["results"][q_idx] = sorted(cfg["results"][q_idx], key=lambda x: x[0], reverse=True)[:cand_limit]
```
- Khi quét qua shard trùng lặp, các tài liệu điểm cao bị nhân đôi với điểm số bằng nhau.
- Buffer chỉ cho phép giữ 150 phần tử $\to$ các tài liệu trùng chiếm 2 slot, đẩy văng các tài liệu hợp lệ từ shard khác.
- Hơn nữa, việc cắt tỉa theo số lượng *chunks* (chứ không phải *unique docs*) khiến 150 chunks chỉ tương ứng với khoảng 40–60 tài liệu duy nhất. Khi xuất `top_docs = 100`, hệ thống bị thiếu ứng viên tài liệu trầm trọng!

### 2.3. Lỗ hổng 3: Shard Mới `tier 2/600-700k` Đang Bị Bỏ Quên
- `data/indices/tier 2/600-700k/index` chứa 194,200 chunks (50,000 docs) đã được index hoàn chỉnh nhưng chưa từng được đưa vào đánh giá ở Exp 27.

---

## 3. LỘ TRÌNH 4 HƯỚNG THỬ NGHIỆM CHIẾN LƯỢC

### 📌 Hướng 1: Exp 29 - Khắc phục Shard Duplicate & Nâng cấp Candidate Buffer (Thực hiện ngay)
- **Mục tiêu:** Giải phóng dung lượng candidate pool, loại bỏ shard thừa, bổ sung shard `tier 2/600-700k`.
- **Cải tiến trong `run_submission.py`:**
  1. **Dynamic Shard Deduplication:** Tự động kiểm tra chữ ký part 0 của từng shard trước khi tìm kiếm. Nếu phát hiện shard trùng lặp thì log cảnh báo và tự động bỏ qua.
  2. **Candidate Buffer Expansion:** Nâng `cand_limit` từ 150 lên **400** (hoặc `--cand_buffer 400`).
  3. **Doc-Level Buffer Diversification:** Giới hạn tối đa 2 chunks cho mỗi `doc_id` trong buffer trung gian để đảm bảo 400 slot chứa ít nhất 200 unique docs.
- **Kỳ vọng:** Tăng Recall toàn diện, đưa Final Score bứt phá mốc **0.2480 – 0.2520**.

### 📌 Hướng 2: Exp 30 - Embedding 30.000 Tài liệu Vàng `tier_1_resume.parquet`
- **Mục tiêu:** Đưa **12.2k bài Long Châu** và các bài `ask.39.net` đã cào sạch vào index.
- **Quy trình:**
  1. Chạy semantic chunking + BGE-M3 (FP16) trên Kaggle GPU tạo khối `tier 1/1500-1600k`.
  2. Đưa vào `data/indices` và chạy pipeline tìm kiếm.
- **Kỳ vọng:** Đẩy Docs Recall lên mốc **36% – 38%**, Final Score chạm mốc **0.2650 – 0.2800+**.

### 📌 Hướng 3: Exp 31 - Cân bằng Trọng số Ngôn ngữ (`--zh_weight`)
- **Mục tiêu:** Khắc phục tình trạng tài liệu tiếng Trung lấn át tài liệu tiếng Việt ở ranh giới 80–100.
- **Phương pháp:** Grid search `--zh_weight` trong dải `[0.75, 0.80, 0.85, 0.90, 1.0]`.

### 📌 Hướng 4: Exp 32 - Đa dạng hóa Chunk Selection & Score Interpolation Reranking
- **Mục tiêu:** Thu hẹp chênh lệch giữa Chunks $F_2$ (0.2278) và Docs $F_2$ (0.2604).
- **Phương pháp:**
  1. Cho phép Top 10 documents có điểm số cao nhất được đóng góp tối đa **2 chunks** vào `relevant_chunks`.
  2. Reranking dạng nội suy: $\text{Score}_{\text{final}} = \text{Score}_{\text{Stage1}} + 0.2 \cdot \text{Score}_{\text{Reranker}}$ trên Top 120 ứng viên.

---

## 4. CHI TIẾT THỰC THI EXP 29

### 4.1. Thông số Cấu hình Exp 29
```powershell
python scripts/run_submission.py `
  --mode hybrid `
  --fusion linear `
  --dense_weight 1.0 `
  --sparse_weight 0.2 `
  --top_docs 100 `
  --top_chunks 98 `
  --cand_pool 200 `
  --cand_buffer 400 `
  --output submission_bgem3_hybrid_w02_exp29.json
```

### 4.2. Kiểm soát Ràng buộc Kỹ thuật
- **File Zip:** Tự động nén `ZIP_DEFLATED (compresslevel=9)`, cơ chế safe auto-trim đảm bảo `< 99.0 MB` (chuẩn BTC `< 100 MB`).
- **Bộ nhớ RAM:** Prune buffer 400 và `gc.collect()` sau mỗi shard, duy trì RAM ổn định `< 3.0 GB`.
- **Số Shards Thực tế:** 20 shards duy nhất (12 khối Tier 1 + 8 khối Tier 2).
