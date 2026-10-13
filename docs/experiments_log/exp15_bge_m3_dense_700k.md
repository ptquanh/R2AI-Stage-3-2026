[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 15: BGE-M3 Dense Search (700k docs, top 100 chunks)

- **Mục tiêu:** Cập nhật kết quả truy xuất Dense Retrieval sau khi có thêm 300k tài liệu mới (400-700k) được lập chỉ mục.
- **Phương pháp:**
  - Kho dữ liệu: 700,000 tài liệu.
  - Vẫn sử dụng `run_local_submission.py` để rút top 100 docs, top 100 chunks.
- **Kết quả:**
  - `FINAL_SCORE: 0.1570` (Kỷ lục mới!)
  - `DOCS_F2MACRO: 0.1646` | `DOCS_PRECISION: 0.1348` | `DOCS_RECALL: 0.2093`
  - `CHUNKS_F2MACRO: 0.1494` | `CHUNKS_PRECISION: 0.1287` | `CHUNKS_RECALL: 0.1855`
- **Phân tích kết quả:**
  - Điểm `FINAL_SCORE` tiếp tục nhích lên (0.1557 -> 0.1570).
  - Độ bao phủ (Recall) của Document và Chunk đều tăng nhẹ khi có thêm dữ liệu (DOCS_RECALL từ 0.2079 lên 0.2093, CHUNKS_RECALL từ 0.1854 lên 0.1855).
  - Điểm F2MACRO của Docs tăng từ 0.1626 lên 0.1646, cho thấy độ chính xác và tính đầy đủ của các tài liệu tìm được đang đi đúng hướng.
  - Việc `tier_1.parquet` vừa được tổng hợp đầy đủ lên mức ~1.19 triệu bài hứa hẹn khi cắm vào chạy nối tiếp (resume) sẽ bứt phá mạnh hơn nữa.

---

---
[← Exp 14](exp14_bge_m3_dense_400k_chunks100.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 16 →](exp16_bge_m3_hybrid_700k.md)
