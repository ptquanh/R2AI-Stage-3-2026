# Exp 90 — Qwen gate rank≤125, score≥0,90

Trạng thái: đã build, chưa có kết quả BTC.

- Baseline: Exp87; top-50 và chunks giữ nguyên.
- Chỉ đổi tối đa một doc/query khi candidate ở stage rank ≤125 và Qwen score ≥0,90.
- 95/1.200 queries thay đổi; trung bình `0,0792` swap/query.
- ZIP: `99.630.164` bytes.

Không dùng điểm suy đoán. Exp90 được giữ làm artifact đối chứng cho selective Qwen gating.
