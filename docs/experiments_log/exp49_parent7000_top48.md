[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 49: Top-48 parent windows, tối đa 7.000 ký tự

## Mục tiêu

Thử nghiệm đột phá có mức can thiệp mạnh nhất: tập trung ngân sách vào các evidence rank cao và dùng parent windows dài để một dự đoán có thể bao phủ nhiều ground-truth chunks cùng document.

## Cấu hình

- Document lists giữ nguyên Exp45.
- Lấy top-48 chunks Exp45, mở rộng nguyên văn tới tối đa 7.000 ký tự.
- Số chunk/query thực tế: trung bình `44,33`, min `33`, max `48`; cửa sổ trùng được deduplicate.
- Độ dài trung bình `4.101,4` ký tự; tối đa `7.000`.

## Cách đọc kết quả

- Docs F2 phải giữ đúng `0,3266`.
- Đây là phép thử precision/coverage mạnh: cần parent windows bù được recall mất do bỏ rank 49–98.
- Nếu thắng, tiếp tục tối ưu theo tổng ngân sách ký tự thay vì số chunk cố định. Nếu thua nhưng Exp48 thắng, vùng tối ưu nằm giữa 48 và 64 chunks.

## Validation

- 1.200 query; document lists giống Exp45 cho cả 1.200 query.
- Mọi chunk là substring nguyên văn của đúng document.
- ZIP: `78.134.273` bytes, chỉ chứa `submission.json` ở root.
- SHA-256: `67f8327c2bd890fe055364b4cddab6cb9cea037b0f4b6689d8adaff97c487e65`.

## Artifact

- `submission_exp49_parent7000_top48.zip`
- Generator: `scripts/generate_breakthrough_submissions.py`

## Kết quả BTC

**Hủy nộp sau kết quả Exp48.** Exp48 top-64 đã làm Chunks Recall giảm `0,0586` và Final giảm `0,0102` so với Exp47. Exp49 còn cắt sâu hơn xuống top-48 nên không còn đủ prior để sử dụng một slot nộp chính thức.
