# Script entrypoints

Chỉ giữ trong thư mục này các entrypoint có thể chạy lại hoặc còn thuộc pipeline hiện hành.

## Submission và đánh giá

- `generate_best_submission.py`: sinh submission từ cấu hình tốt nhất đã chốt.
- `generate_true_union_submission.py`: hợp nhất candidate/submission có kiểm soát.
- `validate_submission.py`: kiểm tra schema và invariants trước khi nộp.
- `validate_evidence_submission.py`: kiểm tra evidence/chunk coverage.
- `verify_data_state.py`: snapshot trạng thái corpus/index/registry.

## Index và embedding

- `rebuild_clean_index.py`, `streaming_index_rebuild.py`: rebuild index.
- `merge_embedded_artifact.py`, `merge_recovered_artifacts.py`: merge artifact có kiểm tra.
- `sync_embedded_zip_registry.py`: đồng bộ embedded/unembedded registry.
- `build_faiss_index.py`: FAISS build.
- `prepare_qwen3_embedding_kaggle.py`, `prepare_qwen3_doc_retrieval.py`: chuẩn bị Qwen3.
- `build_qwen3_secondary_index.py`: secondary dense index.

## Retrieval kiến trúc mới

- `build_bm25_document_index.py`: BM25 document index.
- `build_bm25_translation_treatment.py`: treatment dùng query dịch.
- `build_icd10_query_routes.py`, `build_icd10_passage_routes.py`: ICD-10 soft routing.
- `package_exp130_bm25_dense_kaggle_inputs.py`: đóng gói input cho cascade Kaggle.
- `create_translation_production_kaggle_notebook.py`: tái tạo notebook dịch production.

## Corpus recovery

- `crawl_local_fast.py`: crawler chính.
- `reconcile_remaining_urls.py`: đối soát remaining URLs.
- `audit_local_recovered_final.py`: audit recovery.
- `recover_commoncrawl_hits.py`, `recover_pharmacity_api.py`, `recover_publisher_frontends.py`: recovery theo nguồn.

## Quy ước

- Thí nghiệm chỉ dùng một lần phải ghi kết quả vào `docs/experiments_log/`, sau đó chuyển code sang `archive/`.
- Logic được dùng từ hai entrypoint trở lên nên chuyển vào `src/` và có test.
- Không tạo thêm script `generate_expNNN_*.py` cho sweep nhỏ; dùng một generator tham số hóa hoặc cấu hình dữ liệu.
