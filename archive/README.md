# Retired one-off code

Ngày 2026-10-23, 93 tệp one-off/prototype được chuyển khỏi `scripts/`, `notebooks/`, `tests/` và `scratch/` vào `archive/one_off_code_20261023/`.

Phạm vi gồm:

- generator riêng cho Exp64–Exp135 đã hoàn tất;
- notebook benchmark/reranker đã có kết quả và notebook generator tương ứng;
- local translation prototype đã được thay bằng production notebook;
- các migration/consolidation registry hoặc index đã chạy xong và hard-code artifact cũ;
- crawler, translator và utility đời cũ đã có entrypoint production thay thế;
- một test chỉ phụ thuộc generator Exp75 cũ;
- hai script scratch kiểm tra index.

Không có corpus, index, submission, experiment log hoặc script production nào bị chuyển. Muốn khôi phục, đưa đúng đường dẫn con của tệp từ archive trở lại repository.
