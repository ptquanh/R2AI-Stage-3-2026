# R2AI Stage 3 — retrieval system

Repository này chứa pipeline crawl, index, retrieval và sinh submission cho R2AI Stage 3.

## Bắt đầu ở đây

1. Đọc [kế hoạch hiện hành](docs/r2ai_score_improvement_plan.md).
2. Tra cứu kết quả đã nộp trong [experiments log](docs/experiments_log.md) và `docs/experiments_log/`.
3. Xem [danh mục script](scripts/README.md) trước khi chạy một pipeline.
4. Chạy `pytest -q` trước và sau thay đổi có ảnh hưởng retrieval/index.

## Pipeline đang hoạt động

- Production translation: `notebooks/16_translation_production_2xt4_kaggle.ipynb`
- BM25 → dense passage cascade: `notebooks/14_bm25_dense_passage_cascade_kaggle.ipynb`
- Full-corpus embedding: `notebooks/12_qwen3_embedding_full_kaggle.ipynb`
- BGE-M3 chunk/index build: `notebooks/10_semantic_chunk_bgem3_kaggle.ipynb`
- Submission control: `scripts/generate_best_submission.py`
- Validation: `scripts/validate_submission.py`, `scripts/validate_evidence_submission.py`

## Nguyên tắc tổ chức

- `src/`: logic tái sử dụng; không đặt script thí nghiệm ở đây.
- `scripts/`: entrypoint có thể chạy lại và phục vụ pipeline hiện hành.
- `notebooks/`: notebook production hoặc benchmark còn giá trị.
- `docs/experiments_log/`: provenance từng submission; không dùng làm kế hoạch hiện hành.
- `data/`: corpus, index và artifacts sinh ra; phần lớn được ignore khỏi Git.
- `archive/`: mã one-off đã nghỉ hưu, chỉ giữ để truy vết/khôi phục.

Không xóa hoặc rebuild `data/raw/` và `data/indices/` nếu chưa kiểm tra coverage, `doc_id` và backup.
