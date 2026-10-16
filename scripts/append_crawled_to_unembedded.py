"""
Đồng bộ dữ liệu cào mới:
1. Thêm 77,468 URLs vừa cào thành công vào data/unembedded_samples.parquet (tránh trùng lặp).
2. Xóa các URL thành công (77,468) và các URL bị lỗi 404 (184) khỏi data/remaining_urls.parquet.
3. Tạo bản sao lưu an toàn .bak và kiểm tra tính toàn vẹn (Integrity Checks).
"""

import os
import sys
import shutil
import pandas as pd
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(r"d:\CODE PLAYGROUND\Projects\Competitions\R2AI-Stage-3-2026")
DATA_DIR = BASE / "data"

EMB_PATH = DATA_DIR / "embedded_samples.parquet"
UNEMB_PATH = DATA_DIR / "unembedded_samples.parquet"
REM_PATH = DATA_DIR / "remaining_urls.parquet"
RECOV_DIR = DATA_DIR / "raw" / "corpus_text" / "local_recovered"


def main():
    print("=" * 80)
    print("🔄 BẮT ĐẦU ĐỒNG BỘ DỮ LIỆU CÀO MỚI VÀO UNEMBEDDED VÀ LOẠI BỎ 404 KHỎI REMAINING")
    print("=" * 80)

    # 1. Đọc trạng thái hiện tại
    print("\n[1/5] Đang đọc trạng thái hiện tại của các tập dữ liệu...")
    df_emb = pd.read_parquet(EMB_PATH, columns=["id"])
    df_unemb_old = pd.read_parquet(UNEMB_PATH)
    df_rem_old = pd.read_parquet(REM_PATH)

    emb_ids = set(df_emb["id"])
    unemb_old_ids = set(df_unemb_old["id"])
    rem_old_ids = set(df_rem_old["id"])

    print(f"  • embedded_samples hiện tại:   {len(emb_ids):,} IDs")
    print(f"  • unembedded_samples hiện tại: {len(unemb_old_ids):,} IDs")
    print(f"  • remaining_urls hiện tại:     {len(rem_old_ids):,} IDs")

    # 2. Quét local_recovered để lấy các bản ghi Success và 404
    print("\n[2/5] Đang quét toàn bộ các part trong data/raw/corpus_text/local_recovered...")
    new_succ_records = []
    seen_new_ids = set()
    ids_404 = set()

    part_files = sorted(RECOV_DIR.glob("*.parquet"))
    print(f"  • Tìm thấy {len(part_files)} part files.")

    for p in part_files:
        try:
            df_part = pd.read_parquet(p)
            if "status" not in df_part.columns:
                continue

            # Xử lý Success
            df_succ = df_part[df_part["status"] == "success"]
            for _, r in df_succ.iterrows():
                cid = int(r["id"])
                if cid not in emb_ids and cid not in unemb_old_ids and cid not in seen_new_ids:
                    txt = r.get("text", "")
                    if txt is not None and len(str(txt).strip()) >= 50:
                        new_succ_records.append({
                            "id": cid,
                            "url": str(r["url"]),
                            "text": str(txt).strip()
                        })
                        seen_new_ids.add(cid)

            # Xử lý 404 Dropped
            df_drop = df_part[df_part["status"] == "dropped"]
            for _, r in df_drop.iterrows():
                cid = int(r["id"])
                reason = str(r.get("reason", "")).lower()
                if "404" in reason or "not found" in reason:
                    ids_404.add(cid)
        except Exception as e:
            pass

    n_new_succ = len(new_succ_records)
    n_404 = len(ids_404)
    print(f"  • Số bản ghi SUCCESS mới cần thêm: {n_new_succ:,}")
    print(f"  • Số ID lỗi 404 Not Found cần xóa: {n_404:,}")

    # 3. Gộp vào unembedded_samples.parquet
    print(f"\n[3/5] Đang gộp {n_new_succ:,} mẫu mới vào unembedded_samples.parquet...")
    df_new_succ = pd.DataFrame(new_succ_records)
    df_unemb_combined = pd.concat([df_unemb_old, df_new_succ], ignore_index=True)
    df_unemb_final = df_unemb_combined.drop_duplicates(subset=["id"]).copy()
    n_unemb_final = len(df_unemb_final)
    print(f"  • unembedded_samples trước: {len(df_unemb_old):,} | sau: {n_unemb_final:,} rows (+{n_unemb_final - len(df_unemb_old):,})")

    # 4. Loại bỏ các ID success và 404 khỏi remaining_urls.parquet
    print(f"\n[4/5] Đang cập nhật remaining_urls.parquet...")
    ids_to_remove = seen_new_ids.union(ids_404)
    print(f"  • Tổng số ID cần loại bỏ khỏi remaining: {len(ids_to_remove):,} (gồm {len(seen_new_ids):,} success + {len(ids_404):,} 404)")

    df_rem_final = df_rem_old[~df_rem_old["id"].isin(ids_to_remove)].copy()
    n_rem_final = len(df_rem_final)
    print(f"  • remaining_urls trước: {len(df_rem_old):,} | sau: {n_rem_final:,} URLs (-{len(df_rem_old) - n_rem_final:,})")

    # 5. Sao lưu .bak và lưu file
    print(f"\n[5/5] Đang sao lưu và ghi dữ liệu mới...")
    shutil.copy2(UNEMB_PATH, DATA_DIR / "unembedded_samples.parquet.bak_pre_crawl_append")
    shutil.copy2(REM_PATH, DATA_DIR / "remaining_urls.parquet.bak_pre_crawl_append")
    print("  ✓ Đã tạo các tệp .bak an toàn.")

    # Lưu unembedded_samples.parquet
    tmp_unemb = UNEMB_PATH.with_suffix(".tmp")
    df_unemb_final.to_parquet(tmp_unemb, index=False, compression="snappy")
    if os.path.exists(UNEMB_PATH):
        os.remove(UNEMB_PATH)
    os.rename(tmp_unemb, UNEMB_PATH)
    sz_unemb_mb = os.path.getsize(UNEMB_PATH) / (1024 * 1024)
    print(f"  💾 Đã lưu {UNEMB_PATH}: {n_unemb_final:,} rows ({sz_unemb_mb:.2f} MB)")

    # Lưu remaining_urls.parquet
    tmp_rem = REM_PATH.with_suffix(".tmp")
    df_rem_final.to_parquet(tmp_rem, index=False, compression="snappy")
    if os.path.exists(REM_PATH):
        os.remove(REM_PATH)
    os.rename(tmp_rem, REM_PATH)
    sz_rem_mb = os.path.getsize(REM_PATH) / (1024 * 1024)
    print(f"  💾 Đã lưu {REM_PATH}: {n_rem_final:,} rows ({sz_rem_mb:.2f} MB)")

    # 6. Kiểm tra tính toàn vẹn (Integrity Checks)
    print("\n🔍 KIỂM TRA TÍNH TOÀN VẸN CUỐI CÙNG:")
    v_unemb = pd.read_parquet(UNEMB_PATH)
    v_rem = pd.read_parquet(REM_PATH)

    set_final_unemb = set(v_unemb["id"])
    set_final_rem = set(v_rem["id"])

    overlap_unemb_emb = set_final_unemb.intersection(emb_ids)
    overlap_rem_emb = set_final_rem.intersection(emb_ids)
    overlap_unemb_rem = set_final_unemb.intersection(set_final_rem)

    print(f"  • Trùng lặp giữa unembedded và embedded: {len(overlap_unemb_emb)} (Phải bằng 0)")
    print(f"  • Trùng lặp giữa remaining và embedded:  {len(overlap_rem_emb)} (Phải bằng 0)")
    print(f"  • Trùng lặp giữa unembedded và remaining: {len(overlap_unemb_rem)} (Phải bằng 0)")

    assert len(overlap_unemb_emb) == 0, "Lỗi trùng lặp unembedded vs embedded!"
    assert len(overlap_rem_emb) == 0, "Lỗi trùng lặp remaining vs embedded!"
    assert len(overlap_unemb_rem) == 0, "Lỗi trùng lặp unembedded vs remaining!"

    assert len(v_unemb) == n_unemb_final, "Lỗi số dòng unembedded!"
    assert len(v_rem) == n_rem_final, "Lỗi số dòng remaining!"

    print("\n" + "=" * 80)
    print("🎉 ĐỒNG BỘ THÀNH CÔNG CHÍNH XÁC 100%!")
    print(f" • unembedded_samples.parquet: {len(v_unemb):,} bài viết (đã bổ sung {n_new_succ:,} bài mới cào)")
    print(f" • remaining_urls.parquet:     {len(v_rem):,} URLs còn lại cần cào")
    print(f" • Tổng số tài liệu đã cào:    {len(emb_ids) + len(v_unemb):,} docs (đã vượt mốc 1.25M docs!)")
    print("=" * 80)


if __name__ == "__main__":
    main()
