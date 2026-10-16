"""
Đồng bộ các mẫu cào thành công từ data/raw/corpus_text/local_recovered:
1. Trích xuất các mẫu thành công (status == 'success' và text > 10 ký tự).
2. Lọc bỏ các ID đã có trong embedded_samples và unembedded_samples.
3. Thêm các mẫu thành công mới vào cuối data/unembedded_samples.parquet.
4. Xóa chính xác các ID thành công khỏi data/remaining_urls.parquet (giữ nguyên các URL lỗi để retry).
5. Kiểm tra toàn vẹn dữ liệu chặt chẽ và ghi file an toàn (atomic replace).
"""

import os
import sys
import glob
import time
import shutil
import pandas as pd
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE = Path("d:/CODE PLAYGROUND/Projects/Competitions/R2AI-Stage-3-2026")
DATA_DIR = BASE / "data"

UNEMB_PATH = DATA_DIR / "unembedded_samples.parquet"
EMB_PATH = DATA_DIR / "embedded_samples.parquet"
REM_PATH = DATA_DIR / "remaining_urls.parquet"
RECOVERED_DIR = DATA_DIR / "raw" / "corpus_text" / "local_recovered"


def main():
    print("=" * 80)
    print("🚀 ĐỒNG BỘ CÁC MẪU CÀO THÀNH CÔNG VÀO UNEMBEDDED VÀ CẬP NHẬT REMAINING URLS")
    print("=" * 80)
    t0 = time.time()

    # 1. Đọc danh sách ID hiện tại từ embedded và unembedded
    print("\n🔍 [1/5] Đang nạp danh sách ID hiện tại...")
    df_emb = pd.read_parquet(EMB_PATH, columns=["id"])
    emb_ids = set(df_emb["id"])
    print(f"  • embedded_samples.parquet:   {len(emb_ids):,} mẫu")

    df_unemb = pd.read_parquet(UNEMB_PATH)
    initial_unemb_count = len(df_unemb)
    unemb_ids = set(df_unemb["id"])
    print(f"  • unembedded_samples.parquet: {initial_unemb_count:,} mẫu")

    existing_ids = emb_ids | unemb_ids
    print(f"  • Tổng ID đã quản lý:         {len(existing_ids):,}")

    # 2. Đọc các mẫu thành công từ local_recovered
    print(f"\n📂 [2/5] Đang quét các file trong {RECOVERED_DIR}...")
    files = sorted(glob.glob(str(RECOVERED_DIR / "*.parquet")))
    print(f"  • Tìm thấy {len(files):,} file parquet.")

    success_records = []
    for f in files:
        try:
            df = pd.read_parquet(f)
            if "status" in df.columns:
                succ = df[df["status"] == "success"]
            else:
                succ = df

            if len(succ) > 0:
                succ = succ[["id", "url", "text"]].dropna(subset=["id", "text"])
                succ = succ[succ["text"].str.strip().str.len() > 10]
                if len(succ) > 0:
                    success_records.append(succ)
        except Exception as e:
            print(f"  ⚠️ Lỗi đọc file {Path(f).name}: {e}")

    if not success_records:
        print("  ❌ Không tìm thấy bản ghi thành công nào!")
        return

    df_succ_all = pd.concat(success_records, ignore_index=True)
    df_succ_all["id"] = df_succ_all["id"].astype("int64")
    df_succ_all["url"] = df_succ_all["url"].astype(str)
    df_succ_all["text"] = df_succ_all["text"].astype(str)

    # Khử trùng lặp giữa các đợt cào, giữ bản ghi mới nhất
    df_succ_all = df_succ_all.drop_duplicates(subset=["id"], keep="last")
    total_succ_unique = len(df_succ_all)
    all_succ_ids = set(df_succ_all["id"])
    print(f"  ✅ Tổng số ID unique cào thành công trong local_recovered: {total_succ_unique:,}")

    # Lọc các ID thực sự mới (chưa có trong embedded hoặc unembedded)
    new_to_add = df_succ_all[~df_succ_all["id"].isin(existing_ids)].copy()
    n_new = len(new_to_add)
    print(f"  🎯 Số mẫu thành công MỚI cần thêm vào unembedded: {n_new:,}")

    # 3. Thêm vào cuối unembedded_samples.parquet
    print(f"\n📦 [3/5] Đang thêm {n_new:,} mẫu mới vào cuối {UNEMB_PATH.name}...")
    if n_new > 0:
        updated_unemb = pd.concat([df_unemb, new_to_add], ignore_index=True)
        # Đảm bảo không trùng lặp
        updated_unemb = updated_unemb.drop_duplicates(subset=["id"], keep="first")
        final_unemb_count = len(updated_unemb)

        # Lưu an toàn qua file temp
        unemb_temp = DATA_DIR / "unembedded_samples_temp.parquet"
        updated_unemb.to_parquet(unemb_temp, index=False, compression="snappy")
        os.replace(unemb_temp, UNEMB_PATH)
        print(f"  ✅ Đã lưu {UNEMB_PATH.name}: {initial_unemb_count:,} -> {final_unemb_count:,} (+{n_new:,} mẫu)")
        assert final_unemb_count == initial_unemb_count + n_new, "Lỗi số lượng mẫu unembedded không khớp!"
    else:
        print("  ℹ️ Không có mẫu mới nào cần thêm vào unembedded.")
        final_unemb_count = initial_unemb_count

    # 4. Xóa các ID thành công trong remaining_urls.parquet
    print(f"\n🗑️ [4/5] Đang xóa các ID thành công khỏi {REM_PATH.name}...")
    if REM_PATH.exists():
        df_rem = pd.read_parquet(REM_PATH)
        initial_rem_count = len(df_rem)
        print(f"  • Số URLs trong {REM_PATH.name} trước khi xóa: {initial_rem_count:,}")

        # Xóa các ID thành công (gồm tất cả ID đã cào thành công hoặc đã có trong corpus)
        success_ids_to_remove = all_succ_ids | existing_ids
        if n_new > 0:
            success_ids_to_remove.update(new_to_add["id"])

        mask_to_remove = df_rem["id"].isin(success_ids_to_remove)
        n_removed = mask_to_remove.sum()
        df_rem_filtered = df_rem[~mask_to_remove].copy()
        final_rem_count = len(df_rem_filtered)

        # Lưu an toàn qua file temp
        rem_temp = DATA_DIR / "remaining_urls_temp.parquet"
        df_rem_filtered.to_parquet(rem_temp, index=False, compression="snappy")
        os.replace(rem_temp, REM_PATH)
        print(f"  ✅ Đã loại bỏ {n_removed:,} URLs thành công khỏi {REM_PATH.name}.")
        print(f"  • Số URLs còn lại cần cào: {initial_rem_count:,} -> {final_rem_count:,} (-{n_removed:,})")
    else:
        print(f"  ⚠️ Không tìm thấy file {REM_PATH.name}!")
        final_rem_count = 0

    # 5. Kiểm tra toàn vẹn hệ thống
    print("\n🛡️ [5/5] Kiểm tra toàn vẹn hệ thống sau khi đồng bộ...")
    chk_unemb = pd.read_parquet(UNEMB_PATH, columns=["id"])
    chk_emb = pd.read_parquet(EMB_PATH, columns=["id"])
    chk_rem = pd.read_parquet(REM_PATH, columns=["id"])

    assert len(chk_unemb) == chk_unemb["id"].nunique(), "Phát hiện duplicate trong unembedded_samples!"
    assert len(chk_emb) == chk_emb["id"].nunique(), "Phát hiện duplicate trong embedded_samples!"
    assert len(set(chk_unemb["id"]) & set(chk_emb["id"])) == 0, "Phát hiện overlap giữa unembedded và embedded!"
    assert len(set(chk_rem["id"]) & set(chk_unemb["id"])) == 0, "Phát hiện URL còn lại nằm trong unembedded!"
    assert len(set(chk_rem["id"]) & set(chk_emb["id"])) == 0, "Phát hiện URL còn lại nằm trong embedded!"
    print("  ✅ Tất cả kiểm tra toàn vẹn ĐẠT 100%!")

    elapsed = time.time() - t0
    print("\n" + "=" * 80)
    print(f"🎉 HOÀN THÀNH ĐỒNG BỘ DỮ LIỆU XUẤT SẮC TRONG {elapsed:.2f}s!")
    print(f" • unembedded_samples.parquet: {final_unemb_count:,} mẫu (+{n_new:,})")
    print(f" • embedded_samples.parquet:   {len(chk_emb):,} mẫu")
    print(f" • remaining_urls.parquet:    {final_rem_count:,} URLs còn lại (-{n_removed:,})")
    print(f" • Tổng tài liệu toàn hệ thống:{final_unemb_count + len(chk_emb):,} mẫu")
    print("=" * 80)


if __name__ == "__main__":
    main()
