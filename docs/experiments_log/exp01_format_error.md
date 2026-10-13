[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 01: Lỗi định dạng ID kiểu String (String ID Format Error)

- **Mục tiêu:** Thử nghiệm submission đầu tiên lên hệ thống.
- **Phương pháp:** Pipeline sinh file submission nhưng `doc_id` trong danh sách `relevant_docs` bị ép kiểu hoặc xuất ra dưới dạng chuỗi (`string`) thay vì số nguyên (`integer`).
- **Kết quả:**
  - `FINAL_SCORE: 0.0` (Tất cả các metric đều bằng 0.0).
- **Nguyên nhân & Bài học:**
  - Server chấm thi của BTC yêu cầu trường `doc_id` bắt buộc phải là kiểu **Integer (int)**.
  - Khi `doc_id` là kiểu String, hệ thống đối soát không match được với Ground Truth (hoặc parser trên server BTC reject).
  - 👉 **Quy tắc bất di bất dịch:** Toàn bộ pipeline xuất submission luôn phải ép kiểu `int(doc_id)` trước khi xuất file.

---

---
[← Exp 00](exp00_bm25_baseline.md) | [Bảng Xếp hạng Nội bộ](../experiments_log.md) | [Exp 02 →](exp02_bm25s_top5.md)
