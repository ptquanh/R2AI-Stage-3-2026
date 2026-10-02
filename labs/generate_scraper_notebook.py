import nbformat as nbf

nb = nbf.v4.new_notebook()

nb.cells.append(nbf.v4.new_markdown_cell("""\
# Async Web Scraper (Kaggle Standalone)
Notebook này được tự động sinh ra từ mã nguồn `src/data_collection/async_scraper.py`. 
Nó chứa toàn bộ logic cào dữ liệu đa luồng (aiohttp) và 2 tầng lọc phễu thông minh. 
Bạn có thể dễ dàng chạy trực tiếp trên Kaggle để tận dụng tối đa CPU của nền tảng này!
"""))

nb.cells.append(nbf.v4.new_code_cell("""\
# Cài đặt các thư viện cần thiết
!pip install -q aiohttp trafilatura pandas pyarrow nest_asyncio
"""))

# Đọc mã nguồn của async_scraper.py
with open("src/data_collection/async_scraper.py", "r", encoding="utf-8") as f:
    code = f.read()

# Lấy toàn bộ hàm và class (Cắt bỏ đoạn argparse ở phần if __name__ == "__main__")
code_blocks = code.split('if __name__ == "__main__":')
core_logic = code_blocks[0]

# Tạo block code cho Notebook
notebook_code = core_logic + """
# ==========================================
# CẤU HÌNH KAGGLE (THAY ĐỔI Ở ĐÂY)
# ==========================================
# Đường dẫn file links_corpus.parquet bạn upload lên Kaggle
INPUT_LINKS = "/kaggle/input/ten-dataset-cua-ban/links_corpus.parquet"

# Thư mục chứa các file Parquet tải về
OUTPUT_DIR = "/kaggle/working/corpus_text"

# Cấu hình Chunking / Batch
BATCH_SIZE = 10000
START_BATCH = 0
MAX_BATCHES = 5  # Chạy thử 5 batch (50k URLs). Kaggle có limit 12 tiếng, hãy điều chỉnh con số này!

# Để sử dụng đa luồng (AsyncIO) trong Jupyter Notebook (vốn đã có sẵn event loop đang chạy),
# chúng ta phải dùng nest_asyncio để patch event loop.
if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    
    # Bắt đầu chạy cào dữ liệu
    asyncio.run(main(
        input_file=INPUT_LINKS,
        output_dir=OUTPUT_DIR,
        batch_size=BATCH_SIZE,
        start_batch=START_BATCH,
        max_batches=MAX_BATCHES
    ))
"""

nb.cells.append(nbf.v4.new_code_cell(notebook_code))

nb.cells.append(nbf.v4.new_markdown_cell("""\
## Hướng dẫn xuất dữ liệu
Khi Cell trên hoàn thành, toàn bộ các file `.parquet` (dữ liệu sạch) và `dropped_urls.csv` (dữ liệu rác bị loại) sẽ nằm gọn trong thư mục `/kaggle/working/corpus_text`.
Bạn có thể lưu (Commit/Save Version) toàn bộ phiên bản này lại để sử dụng Output làm Dataset cho bước Training/BM25!
"""))

with open('labs/02_async_scraper.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
    
print("Đã tạo thành công labs/02_async_scraper.ipynb!")
