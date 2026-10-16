[← Quay lại Bảng Xếp hạng](../experiments_log.md)

# Exp 48: Top-64 parent windows, tối đa 4.500 ký tự

## Mục tiêu

Đổi ngân sách từ nhiều chunk ngắn sang ít parent windows giàu ngữ cảnh hơn. Vì overlap của BTC dùng `LCS(c, g) / |g|`, phần context thêm không làm tăng mẫu số overlap; cửa sổ dài có cơ hội chứa trọn ground-truth span tốt hơn.

## Cấu hình

- Document lists giữ nguyên Exp45.
- Lấy top-64 chunks Exp45 rồi mở rộng cân đối trái/phải trong source document.
- Số chunk/query thực tế: trung bình `62,82`, min `53`, max `64`; một số cửa sổ trùng được deduplicate.
- Độ dài trung bình `3.387,2` ký tự; tối đa `4.500`.

## Cách đọc kết quả

- Docs F2 phải giữ đúng `0,3266`.
- Thắng Exp45 nếu parent context giữ đủ recall trong top-64 và precision tăng nhờ giảm 35 chunk/query.
- Nếu Exp47 thắng nhưng Exp48 thua, tín hiệu cho thấy chỉ nên merge overlap, không nên cắt đuôi rank 65–98.

## Validation

- 1.200 query; document lists giống Exp45 cho cả 1.200 query.
- Mọi chunk là substring nguyên văn của đúng document.
- ZIP: `92.001.593` bytes, chỉ chứa `submission.json` ở root.
- SHA-256: `c8f0d0ce7eef012feac09e8c3389351bf95e977b560563a8de7ac472f281b58c`.

## Artifact

- `submission_exp48_parent4500_top64.zip`
- Generator: `scripts/generate_breakthrough_submissions.py`

## Kết quả BTC

- Final Score: `0,2957`.
- Docs F2: `0,3266`; Precision `0,2553`; Recall `0,4337`.
- Chunks F2: `0,2647`; Precision `0,2952`; Recall `0,3067`.

So với Exp47 champion:

- Final `-0,0102`.
- Docs metrics giữ nguyên tuyệt đối, đúng thiết kế ablation.
- Chunks Precision `+0,0539`, nhưng Chunks Recall `-0,0586`.
- Chunks F2 giảm `0,0204`.

## Kết luận

Parent window dài giúp xác suất hit của từng chunk tăng rõ rệt, nhưng phần đuôi rank 65–98 chứa quá nhiều ground-truth coverage để loại bỏ. F2 vẫn ưu tiên recall nên precision tăng không bù được recall mất đi.

Giữ Exp47 làm champion. Không nộp Exp49 top-48: Exp48 đã cho thấy cắt ở top-64 vượt quá điểm gãy, nên cắt sâu hơn gần như chắc chắn tiếp tục regression. Hướng tiếp theo phải giữ toàn bộ 98 candidate chunks và chỉ merge/cluster các evidence dư thừa.
