import nbformat as nbf

nb = nbf.v4.new_notebook()

nb.cells.append(nbf.v4.new_markdown_cell("""\
# Benchmark RAG Chunking (BM25 Baseline)
Notebook này nhằm mục đích thử nghiệm và so sánh độ hiệu quả (Recall@K) của thuật toán BM25 trên 2 kỹ thuật Chunking:
1. **Sentence-based Chunking (Không có Context)**
2. **Contextual Chunking (Gắn ngữ cảnh First Paragraph)**
3. **True Semantic Chunking (Sử dụng Qwen3-Embedding-8B)**
4. **Structure Chunking (Nhận diện Markdown Headings)**

Tập dữ liệu: `data/raw/corpus_text/corpus_part_00000.parquet` (2,000 bài báo) và 50 câu hỏi từ Dev Set.
Mỗi kịch bản sẽ được đánh giá trên 3 loại Search: **Sparse (BM25)**, **Semantic (Dense)**, và **Hybrid (Kết hợp 50-50)**.
"""))

nb.cells.append(nbf.v4.new_code_cell("""\
# Cài đặt các thư viện cần thiết (Chạy cell này đầu tiên)
!pip install -q pyvi rank_bm25 sentence-transformers pandas pyarrow scikit-learn accelerate bitsandbytes
"""))

nb.cells.append(nbf.v4.new_code_cell("""\
import pandas as pd
import json
import sys
import os
from pyvi import ViTokenizer
from rank_bm25 import BM25Okapi
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ==========================================
# CẤU HÌNH KAGGLE & ĐƯỜNG DẪN
# ==========================================
import os
import sys

# Đổi thành True nếu bạn đang chạy trên Kaggle
IS_KAGGLE = False

if IS_KAGGLE:
    # Lấy token từ Kaggle Secrets để clone repo Private (nếu cần) và HuggingFace
    from kaggle_secrets import UserSecretsClient
    user_secrets = UserSecretsClient()
    
    try:
        github_token = user_secrets.get_secret("GITHUB_TOKEN")
        !git clone https://{github_token}@github.com/ptquanh/R2AI-Stage-3-2026.git /kaggle/working/R2AI-Stage-3-2026
    except Exception as e:
        print("Không tải được GITHUB_TOKEN hoặc clone repo lỗi:", e)
        
    try:
        hf_token = user_secrets.get_secret("HF_TOKEN")
        os.environ["HF_TOKEN"] = hf_token
        # Hoặc dùng huggingface_hub.login(hf_token)
    except Exception as e:
        print("Không tải được HF_TOKEN:", e)
        
    BASE_DIR = "/kaggle/working/R2AI-Stage-3-2026"
    SRC_DIR = f"{BASE_DIR}/src/preprocessing"
    
    # Thư mục Dataset parquet bạn upload lên Kaggle
    PARQUET_DIR = "/kaggle/input/ten-dataset-parquet-cua-ban"
else:
    BASE_DIR = ".."
    SRC_DIR = "../src/preprocessing"
    PARQUET_DIR = f"{BASE_DIR}/data/raw/corpus_text"

# Import Chunker
sys.path.append(os.path.abspath(SRC_DIR))
from chunker import Chunker
"""))

nb.cells.append(nbf.v4.new_code_cell("""\
# Tải Dev Queries và Qrels
with open(f'{BASE_DIR}/data/dev_set/dev_queries.json', 'r', encoding='utf-8') as f:
    dev_queries = json.load(f)
    
qrels = pd.read_csv(f'{BASE_DIR}/data/dev_set/dev_qrels_synthetic_data.csv')

# Tải Corpus: Thay vì quét toàn bộ parquet (có thể chưa cào xong), 
# ta lấy trực tiếp văn bản đáp án từ dev_ground_truth.json
with open(f'{BASE_DIR}/data/dev_set/dev_ground_truth.json', 'r', encoding='utf-8') as f:
    ground_truth = json.load(f)

true_docs = []
for item in ground_truth:
    for chunk in item['relevant_chunks']:
        true_docs.append({
            'id': str(chunk['doc_id']),
            'text': chunk['chunk_text'],
            'url': ''
        })

df_true = pd.DataFrame(true_docs).drop_duplicates(subset=['id'])

# Lấy 10,000 bài báo từ file parquet đầu tiên để làm dữ liệu nhiễu (noise)
# (Trên Kaggle, file này nằm trong PARQUET_DIR)
df_temp = pd.read_parquet(f'{PARQUET_DIR}/corpus_part_00000.parquet')
df_temp['id'] = df_temp['id'].astype(str)
df_noise = df_temp[~df_temp['id'].isin(df_true['id'])].head(2000)

df_corpus = pd.concat([df_true, df_noise]).drop_duplicates(subset=['id']).reset_index(drop=True)

print(f"Đã tạo Benchmark Corpus với tổng {len(df_corpus)} bài báo (Gồm {len(df_true)} đáp án và {len(df_noise)} nhiễu)")
"""))

nb.cells.append(nbf.v4.new_markdown_cell("## Hàm Chạy Đánh giá (Sparse, Semantic, Hybrid)"))

nb.cells.append(nbf.v4.new_code_cell("""\
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import torch

from transformers import BitsAndBytesConfig

# Cấu hình lượng tử hóa 4-bit để ép model 8B xuống còn 4GB VRAM!
quantization_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)

# Load Embedding Model dùng chung cho việc đánh giá (Search)
print("Đang tải model Embedding cho Semantic Search (4-bit quantization)...")
eval_model = SentenceTransformer('Qwen/Qwen3-Embedding-8B', model_kwargs={"quantization_config": quantization_config})
# Bắt buộc giới hạn độ dài token để tránh Attention Matrix phình to gây OOM (Cực kỳ quan trọng với các model Context dài như Qwen)
eval_model.max_seq_length = 512

def tokenize(text):
    return ViTokenizer.tokenize(str(text).lower()).split()

def evaluate_retrieval(chunks_df, name=""):
    print(f"\\n--- ĐÁNH GIÁ: {name} ---")
    total = len(dev_queries)
    
    # --- 1. SETUP BM25 (SPARSE) ---
    print("[BM25] Đang Tokenize chunks...")
    tokenized_corpus = [tokenize(text) for text in chunks_df['content']]
    bm25 = BM25Okapi(tokenized_corpus)
    
    # --- 2. SETUP SEMANTIC (DENSE) ---
    print(f"[Semantic] Đang tạo Embeddings cho {len(chunks_df)} chunks...")
    # Ép buộc cắt ngắn string để chặn đứng OOM do tokenizer của Qwen3 không tôn trọng max_seq_length
    safe_texts = [str(text)[:2000] for text in chunks_df['content']]
    corpus_embeddings = eval_model.encode(safe_texts, batch_size=8, show_progress_bar=True)
    
    # Biến đếm kết quả
    bm25_r5, bm25_r10 = 0, 0
    sem_r5, sem_r10 = 0, 0
    hyb_r5, hyb_r10 = 0, 0
    
    print("Đang thực hiện Queries...")
    for q in dev_queries:
        query_id = q['id']
        query_text = q['query']
        # Tìm doc_id thực sự là đáp án
        true_doc_id = str(next(item['relevant_docs'][0] for item in ground_truth if item['id'] == query_id))
        
        # --- SPARSE SEARCH (BM25) ---
        tokenized_query = tokenize(query_text)
        bm25_scores = bm25.get_scores(tokenized_query)
        # Chuẩn hóa BM25
        if np.max(bm25_scores) > 0:
            bm25_norm = (bm25_scores - np.min(bm25_scores)) / (np.max(bm25_scores) - np.min(bm25_scores))
        else:
            bm25_norm = bm25_scores
            
        # --- SEMANTIC SEARCH ---
        query_embedding = eval_model.encode([query_text])[0]
        sem_scores = cosine_similarity([query_embedding], corpus_embeddings)[0]
        # Chuẩn hóa Semantic
        sem_norm = (sem_scores - np.min(sem_scores)) / (np.max(sem_scores) - np.min(sem_scores))
        
        # --- HYBRID SEARCH (Alpha = 0.5) ---
        alpha = 0.5
        hybrid_scores = alpha * bm25_norm + (1 - alpha) * sem_norm
        
        # Hàm tính kết quả chung
        def get_top_docs(scores):
            top_10_indices = np.argsort(scores)[::-1][:10]
            return [chunks_df.iloc[idx]['doc_id'] for idx in top_10_indices]
            
        # Kiểm tra BM25
        top_docs_bm25 = get_top_docs(bm25_scores)
        if true_doc_id in top_docs_bm25[:5]: bm25_r5 += 1
        if true_doc_id in top_docs_bm25: bm25_r10 += 1
            
        # Kiểm tra Semantic
        top_docs_sem = get_top_docs(sem_scores)
        if true_doc_id in top_docs_sem[:5]: sem_r5 += 1
        if true_doc_id in top_docs_sem: sem_r10 += 1
            
        # Kiểm tra Hybrid
        top_docs_hyb = get_top_docs(hybrid_scores)
        if true_doc_id in top_docs_hyb[:5]: hyb_r5 += 1
        if true_doc_id in top_docs_hyb: hyb_r10 += 1
            
    print(f"=============================")
    print(f"KẾT QUẢ: {name}")
    print(f"=============================")
    print(f"[Sparse]   Recall@5: {bm25_r5/total:.2%} | Recall@10: {bm25_r10/total:.2%}")
    print(f"[Semantic] Recall@5: {sem_r5/total:.2%} | Recall@10: {sem_r10/total:.2%}")
    print(f"[Hybrid]   Recall@5: {hyb_r5/total:.2%} | Recall@10: {hyb_r10/total:.2%}")
    print(f"=============================\\n")
"""))


nb.cells.append(nbf.v4.new_markdown_cell("## Kịch bản 1: Không có Context (Tắt Contextual Injection)"))

nb.cells.append(nbf.v4.new_code_cell("""\
chunks_no_context = []
chunker = Chunker(strategy="sentence", max_tokens=256, token_overlap=50)

print("Đang chunking (Không Context)...")
for _, row in df_corpus.iterrows():
    text = str(row['text']) if row['text'] else ""
    if text:
        res = chunker.chunk_document(str(row['id']), text)
        # Giả lập tắt Context: Bỏ đi prefix Context nếu có
        for c in res:
            if '[Context:' in c['content']:
                c['content'] = c['content'].split(']', 1)[-1].strip()
        chunks_no_context.extend(res)

df_chunks_no_ctx = pd.DataFrame(chunks_no_context)
print(f"Tạo được {len(df_chunks_no_ctx)} chunks.")
evaluate_retrieval(df_chunks_no_ctx, "Kịch bản 1: Không có Context")
"""))

nb.cells.append(nbf.v4.new_markdown_cell("## Kịch bản 2: Có Contextual Injection (Kỹ thuật của Anthropic)"))

nb.cells.append(nbf.v4.new_code_cell("""\
chunks_with_context = []
chunker = Chunker(strategy="contextual", max_tokens=256, token_overlap=50)

print("Đang chunking (CÓ Context)...")
for _, row in df_corpus.iterrows():
    text = str(row['text']) if row['text'] else ""
    if text:
        res = chunker.chunk_document(str(row['id']), text)
        chunks_with_context.extend(res)

df_chunks_with_ctx = pd.DataFrame(chunks_with_context)
print(f"Tạo được {len(df_chunks_with_ctx)} chunks.")
evaluate_retrieval(df_chunks_with_ctx, "Kịch bản 2: Có Contextual Injection")
"""))

with open('labs/01_chunking_bm25_benchmark.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print("Done generating notebook (part 2)!")

nb.cells.append(nbf.v4.new_markdown_cell("## Kịch bản 3: True Semantic Chunking (Dùng mô hình Sentence-Transformers)"))

nb.cells.append(nbf.v4.new_code_cell("""\
chunks_semantic = []
# Khởi tạo Semantic Chunker với model Qwen3-Embedding-8B (tái sử dụng eval_model để tránh OOM)
try:
    chunker_sem = Chunker(strategy="semantic", max_tokens=256, token_overlap=50, embedding_model=eval_model)
    
    print("Đang chunking (Semantic Embedding - quá trình này sẽ mất thời gian hơn vì phải tải model)...")
    for _, row in df_corpus.iterrows():
        text = str(row['text']) if row['text'] else ""
        if text:
            chunks = chunker_sem.chunk_document(doc_id=str(row['id']), text=text, url=row['url'])
            chunks_semantic.extend(chunks)
            
    df_chunks_sem = pd.DataFrame(chunks_semantic)
    print(f"Tạo được {len(df_chunks_sem)} semantic chunks.")
    
    evaluate_retrieval(df_chunks_sem, "Kịch bản 3: True Semantic Chunking")
except Exception as e:
    print(f"Lỗi khởi tạo hoặc chạy Semantic Chunker: {e}")
"""))

with open('labs/01_chunking_bm25_benchmark.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

nb.cells.append(nbf.v4.new_markdown_cell("## Kịch bản 4: Structure Chunking (Tiêm Cấu trúc Markdown)"))

nb.cells.append(nbf.v4.new_code_cell("""\
chunks_structure = []
chunker_struct = Chunker(strategy="structure", max_tokens=256, token_overlap=50)

print("Đang chunking (Structure-aware - Tách theo Markdown Headings)...")
for _, row in df_corpus.iterrows():
    text = str(row['text']) if row['text'] else ""
    if text:
        chunks = chunker_struct.chunk_document(doc_id=str(row['id']), text=text, url=row['url'])
        chunks_structure.extend(chunks)
        
df_chunks_struct = pd.DataFrame(chunks_structure)
print(f"Tạo được {len(df_chunks_struct)} structure chunks.")

evaluate_retrieval(df_chunks_struct, "Kịch bản 4: Structure Chunking")
"""))

with open('labs/01_chunking_bm25_benchmark.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print("Done generating notebook (final)!")
