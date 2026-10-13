[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 26: BGE-M3 Linear Hybrid (Bổ sung nhathuoclongchau) 🚀🔥

- **Mục tiêu:** Kiểm chứng giả thuyết từ Exp 25 rằng
  hathuoclongchau là mảnh ghép Ground Truth quan trọng. Cào thêm dữ liệu từ domain khó này (vượt qua Cloudflare Anti-Bot), hợp nhất vào kho chỉ mục và chạy lại pipeline Hybrid.
- **Cấu hình Chi tiết:**
  - Vẫn giữ nguyên cấu hình Linear Hybrid (Dense 1.0 + Sparse 0.2).
  - Lấy top 100 Docs và top 98 Chunks (nhằm bảo đảm file ZIP nhỏ hơn 100MB).
  - Khối lượng dữ liệu: Đã cộng thêm các file dữ liệu tier 1 mới nhất (chứa kết quả cào
    hathuoclongchau.com.vn).
- **Kết quả:**
  - FINAL_SCORE: 0.2146 (Vượt mốc Kỷ lục cũ 0.2121 của Exp 21)
  - DOCS_F2MACRO: 0.2252 | DOCS_PRECISION: 0.1815 | DOCS_RECALL: 0.2904
  - CHUNKS_F2MACRO: 0.2041 | CHUNKS_PRECISION: 0.1714 | CHUNKS_RECALL: 0.2578
- **Phân tích kết quả:**
  - **Tăng trưởng toàn diện:** So với Exp 25, _mọi chỉ số_ từ Recall đến Precision của cả Document và Chunk đều tăng. Docs Recall bứt phá lên 29.04%, giúp tăng Precision và F2 tương ứng.
  - **Khẳng định tầm quan trọng của Tier 1 nội địa:** Như dự đoán,
    hathuoclongchau chứa đáp án chính xác (exact match) cho các câu hỏi bằng tiếng Việt, khiến các tài liệu này dễ dàng lọt vào top nhờ sự trợ giúp của Sparse Lexical Search.
  - **Chiến lược tiếp theo:** Tiếp tục huy động bot cào vét sạch lượng URL còn sót lại của các trang cực lớn như ask.39.net hoặc nới ranh giới cut-off (Top 100 lên Top 200) và dùng mô hình Reranker đã qua fine-tune thay vì zero-shot.

---

---
[← Exp 25](exp25_bge_m3_14shards.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 27 →](exp27_bge_m3_19shards.md)
