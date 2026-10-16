import os
import sys
import time
import argparse
import pandas as pd
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.stdout.reconfigure(encoding='utf-8')

SYSTEM_PROMPT_ZH = (
    "You are an expert medical translator. Translate the given Vietnamese patient inquiry "
    "or clinical query into Simplified Chinese accurately. Maintain all symptoms, anatomical terms, "
    "drug names, and clinical conditions. Output ONLY the translated Chinese text without explanations, "
    "notes, or commentary."
)

SYSTEM_PROMPT_EN = (
    "You are an expert medical translator. Translate the given Vietnamese patient inquiry "
    "or clinical query into concise professional English. "
    "Accurately preserve all symptoms, anatomical structures, drug names, dosages, clinical signs, and medical terminology. "
    "Output ONLY the translated English text without any explanations, notes, introductory phrases, or commentary."
)

def parse_args():
    parser = argparse.ArgumentParser(description="Offline Multilingual Translator for Queries (VI -> ZH & EN).")
    parser.add_argument("--model", type=str, default="Qwen/Qwen2.5-1.5B-Instruct",
                        help="Hugging Face model ID (default: Qwen/Qwen2.5-1.5B-Instruct)")
    parser.add_argument("--input", type=str, default="data/raw/btc_provided/query.parquet",
                        help="Input query parquet file")
    parser.add_argument("--output", type=str, default="data/raw/btc_provided/query_translated.parquet",
                        help="Output parquet file containing id, query, query_zh, query_en")
    parser.add_argument("--batch_size", type=int, default=16,
                        help="Inference batch size (default: 16)")
    parser.add_argument("--max_new_tokens", type=int, default=256,
                        help="Max generated tokens per query (default: 256)")
    return parser.parse_args()

def translate_column(df, model, tokenizer, target_col, system_prompt, batch_size, max_new_tokens, output_path):
    total = len(df)
    missing_indices = [i for i, row in df.iterrows() if not (pd.notna(row.get(target_col)) and str(row[target_col]).strip())]
    print(f"\n--- BẮT ĐẦU DỊCH CỘT {target_col.upper()} ---")
    print(f"Tổng số query: {total} | Còn thiếu cần dịch: {len(missing_indices)}")

    if not missing_indices:
        print(f"Cột {target_col} đã hoàn thành đầy đủ 100%!")
        return df

    t0 = time.time()
    for b_start in range(0, len(missing_indices), batch_size):
        b_indices = missing_indices[b_start:b_start + batch_size]
        batch_rows = [df.iloc[idx] for idx in b_indices]

        batch_prompts = []
        for row in batch_rows:
            messages = [
                {"role": "system", "content": system_prompt},
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
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

        input_len = inputs["input_ids"].shape[1]
        generated_tokens = outputs[:, input_len:]
        decoded = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)

        for idx, trans_text in zip(b_indices, decoded):
            clean_text = trans_text.strip()
            df.at[idx, target_col] = clean_text

        done_count = min(b_start + batch_size, len(missing_indices))
        elapsed = time.time() - t0
        speed = done_count / max(elapsed, 0.001)
        eta = (len(missing_indices) - done_count) / max(speed, 0.001)
        print(f"   [{done_count}/{len(missing_indices)}] {target_col.upper()} | "
              f"Tiến độ: {done_count/len(missing_indices)*100:.1f}% | Tốc độ: {speed:.1f} q/s | ETA: {eta:.0f}s", flush=True)

        if done_count % 50 == 0 or done_count == len(missing_indices):
            df.to_parquet(output_path, index=False)

    df.to_parquet(output_path, index=False)
    print(f"Hoàn thành dịch {target_col.upper()} trong {time.time() - t0:.2f}s.")
    return df

def main():
    args = parse_args()
    print("=" * 70)
    print("🌐 MULTILINGUAL OFFLINE TRANSLATOR (VI -> ZH & EN)")
    print(f"   Model: {args.model}")
    print(f"   Input base queries: {args.input}")
    print(f"   Output target: {args.output}")
    print(f"   Batch size: {args.batch_size}")
    print("=" * 70)

    # Base dataset
    df_base = pd.read_parquet(args.input)
    if "query_zh" not in df_base.columns:
        df_base["query_zh"] = ""
    if "query_en" not in df_base.columns:
        df_base["query_en"] = ""

    # Merge any existing progress
    if os.path.exists(args.output):
        try:
            df_exist = pd.read_parquet(args.output)
            id_to_zh = dict(zip(df_exist["id"], df_exist.get("query_zh", [""] * len(df_exist))))
            id_to_en = dict(zip(df_exist["id"], df_exist.get("query_en", [""] * len(df_exist))))

            df_base["query_zh"] = df_base["id"].map(lambda x: id_to_zh.get(x, "")).fillna("")
            df_base["query_en"] = df_base["id"].map(lambda x: id_to_en.get(x, "")).fillna("")
            print(f"Đã nạp tiến độ cũ: {sum(df_base['query_zh'] != '')} ZH, {sum(df_base['query_en'] != '')} EN.")
        except Exception as e:
            print(f"[!] Lỗi khi nạp file output cũ: {e}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Đang tải model {args.model} lên {device}...", flush=True)
    t_load = time.time()
    tokenizer = AutoTokenizer.from_pretrained(args.model, padding_side="left")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dtype = torch.float16 if device == "cuda" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype).to(device)
    model.eval()
    print(f"Model đã sẵn sàng ({time.time() - t_load:.2f}s).", flush=True)

    # 1. Translate Chinese
    df_base = translate_column(
        df=df_base,
        model=model,
        tokenizer=tokenizer,
        target_col="query_zh",
        system_prompt=SYSTEM_PROMPT_ZH,
        batch_size=args.batch_size,
        max_new_tokens=args.max_new_tokens,
        output_path=args.output
    )

    # 2. Translate English
    df_base = translate_column(
        df=df_base,
        model=model,
        tokenizer=tokenizer,
        target_col="query_en",
        system_prompt=SYSTEM_PROMPT_EN,
        batch_size=args.batch_size,
        max_new_tokens=args.max_new_tokens,
        output_path=args.output
    )

    print("\n" + "=" * 70)
    print(f"✅ TẤT CẢ 1,200 CÂU HỎI ĐÃ ĐƯỢC DỊCH HOÀN TẤT VÀ LƯU VÀO {args.output}!")
    print("=" * 70)

    # Sample display
    for i in range(min(3, len(df_base))):
        row = df_base.iloc[i]
        print(f"\n[SAMPLE {i+1}] (ID: {row['id']}):")
        print(f"  🇻🇳 VI: {row['query'][:120]}...")
        print(f"  🇨🇳 ZH: {str(row['query_zh'])[:120]}...")
        print(f"  🇬🇧 EN: {str(row['query_en'])[:120]}...")
    print("=" * 70, flush=True)

if __name__ == "__main__":
    main()
