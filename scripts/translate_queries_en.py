import os
import sys
import time
import argparse
import pandas as pd
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.stdout.reconfigure(encoding='utf-8')

SYSTEM_PROMPT = (
    "You are an expert medical translator. Translate the given Vietnamese patient inquiry "
    "or clinical query into concise professional English. "
    "Accurately preserve all symptoms, anatomical structures, drug names, dosages, clinical signs, and medical terminology. "
    "Output ONLY the translated English text without any explanations, notes, introductory phrases, or commentary."
)

def parse_args():
    parser = argparse.ArgumentParser(description="Translate queries from Vietnamese to English for Multilingual Sparse Retrieval.")
    parser.add_argument("--model", type=str, default="Qwen/Qwen2.5-1.5B-Instruct",
                        help="Hugging Face model ID (default: Qwen/Qwen2.5-1.5B-Instruct)")
    parser.add_argument("--input", type=str, default="data/raw/btc_provided/query_translated.parquet",
                        help="Input query parquet file")
    parser.add_argument("--output", type=str, default="data/raw/btc_provided/query_translated.parquet",
                        help="Output parquet file containing id, query, query_zh, query_en")
    parser.add_argument("--batch_size", type=int, default=8,
                        help="Inference batch size (default: 8 for 4GB VRAM safety)")
    parser.add_argument("--max_new_tokens", type=int, default=96,
                        help="Max generated tokens per query (default: 96)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of queries to translate (for testing)")
    return parser.parse_args()

def main():
    args = parse_args()
    print("=" * 65)
    print("🌐 OPTIMIZED MEDICAL QUERY TRANSLATOR (VI -> EN)")
    print(f"   Model: {args.model}")
    print(f"   Input: {args.input}")
    print(f"   Output: {args.output}")
    print(f"   Batch size: {args.batch_size} (optimized for 4GB VRAM)")
    print(f"   Max new tokens: {args.max_new_tokens}")
    print("=" * 65)

    if not os.path.exists(args.input):
        fallback = "data/raw/btc_provided/query.parquet"
        if not os.path.exists(fallback):
            print(f"[!] Không tìm thấy file truy vấn nào!")
            return
        df = pd.read_parquet(fallback)
    else:
        df = pd.read_parquet(args.input)

    if args.limit:
        df = df.head(args.limit)
    total_queries = len(df)
    print(f"Tổng số query cần xử lý: {total_queries}")

    translated_en_map = {}
    if "query_en" in df.columns:
        for row in df.itertuples(index=False):
            val = getattr(row, "query_en", "")
            if pd.notna(val) and str(val).strip():
                translated_en_map[row.id] = str(val).strip()
        print(f"Đã phát hiện {len(translated_en_map)} bản dịch tiếng Anh có sẵn.")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Đang tải model {args.model} lên thiết bị: {device}...", flush=True)
    t_load = time.time()

    tokenizer = AutoTokenizer.from_pretrained(args.model, padding_side="left")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dtype = torch.float16 if device == "cuda" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=dtype,
    ).to(device)
    model.eval()
    print(f"Tải model hoàn tất trong {time.time() - t_load:.2f} giây.", flush=True)

    pending_indices = [i for i, row in df.iterrows() if row['id'] not in translated_en_map]
    print(f"Số query còn lại cần dịch sang EN: {len(pending_indices)} / {total_queries}")

    if not pending_indices:
        print("Tất cả queries đã có bản dịch tiếng Anh!")
    else:
        t0 = time.time()
        for b_start in range(0, len(pending_indices), args.batch_size):
            t_batch_start = time.time()
            b_indices = pending_indices[b_start:b_start + args.batch_size]
            batch_rows = [df.iloc[idx] for idx in b_indices]

            batch_prompts = []
            for row in batch_rows:
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": row['query']}
                ]
                text = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
                batch_prompts.append(text)

            inputs = tokenizer(batch_prompts, return_tensors="pt", padding=True, truncation=True, max_length=1024)
            inputs = {k: v.to(model.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=args.max_new_tokens,
                    do_sample=False,
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )

            input_len = inputs["input_ids"].shape[1]
            generated_tokens = outputs[:, input_len:]
            decoded = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)

            for row, trans_text in zip(batch_rows, decoded):
                clean_en = trans_text.strip()
                translated_en_map[row['id']] = clean_en

            done_count = min(b_start + args.batch_size, len(pending_indices))
            elapsed = time.time() - t0
            speed = done_count / max(elapsed, 0.001)
            eta = (len(pending_indices) - done_count) / max(speed, 0.001)
            b_time = time.time() - t_batch_start

            print(f"   [{done_count}/{len(pending_indices)}] Tiến độ: {done_count/len(pending_indices)*100:.1f}% | "
                  f"Batch time: {b_time:.2f}s | Tốc độ: {speed:.1f} q/s | ETA: {eta:.0f}s", flush=True)

            # Checkpoint every 40 queries or at end
            if done_count % 40 == 0 or done_count == len(pending_indices):
                df_temp = df.copy()
                df_temp["query_en"] = df_temp["id"].map(lambda x: translated_en_map.get(x, ""))
                df_temp.to_parquet(args.output, index=False)

    df_out = df.copy()
    df_out["query_en"] = df_out["id"].map(lambda x: translated_en_map.get(x, ""))
    df_out.to_parquet(args.output, index=False)
    print(f"\n✅ Đã lưu kết quả hoàn chỉnh vào {args.output} (Tổng: {len(df_out)} queries).")

    print("\n=== MẪU DỊCH THUẬT TIẾNG ANH (3 MẪU ĐẦU TIÊN) ===")
    for i in range(min(3, len(df_out))):
        sample = df_out.iloc[i]
        print(f"ID {sample['id']}:")
        print(f"  [VI]: {sample['query'][:120]}...")
        if 'query_zh' in sample:
            print(f"  [ZH]: {str(sample['query_zh'])[:120]}...")
        print(f"  [EN]: {str(sample['query_en'])[:120]}...")
        print("-" * 50)

if __name__ == "__main__":
    main()
