# Exp132 — Chỉ bổ sung missing-doc windows có anchor, width 512

## Thay đổi

Giữ nguyên documents và full-parent chunks của Exp121. Chỉ thêm cửa sổ nguyên văn 512 ký tự cho selected documents thiếu evidence nhưng có offset-cache hoặc stage-1 anchor; loại source-head fallback của Exp131.

## Artifact

- ZIP: `submission_exp132_anchored_missing_w512.zip` — `97.112.640` bytes.
- SHA-256: `c92775cbe3a7ca6d7ef4df6940eb402c408ac27a84f22bc49dcc2f67f43806ca`.
- Thêm `103.483` anchored windows, trung bình `86,24`/query.
- Documents giữ nguyên so với Exp121/Exp122.

## Kết quả BTC

- Final `0,3162`; Docs F2 `0,3586`; Chunks F2 `0,2738`.
- Docs Precision/Recall `0,1816 / 0,6114`.
- Chunks Precision/Recall `0,1499 / 0,4491`.

So với Exp122: Final `-0,0354`, Chunks F2 `-0,0708`, Chunks Precision `-0,1013`, Chunks Recall `-0,0191`; Docs axis bất biến.

## Kết luận

Bỏ source-head fallback cải thiện precision so với Exp131 nhưng không giải quyết vấn đề cốt lõi. Các anchored windows vẫn không đủ chính xác và recall còn thấp hơn Exp122. Không tiếp tục nhánh “một window cho mọi missing doc”.
