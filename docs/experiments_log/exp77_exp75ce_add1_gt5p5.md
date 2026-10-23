# Exp 77 — Add one Exp75 CE passage, score >5,5

## Mục tiêu

Sau regression của Exp75, quay về Exp74 và kiểm tra riêng tác động của một lượng rất nhỏ evidence mới. Giữ nguyên toàn bộ documents và chunks Exp74; mỗi query chỉ được thêm tối đa một scoring passage nguyên văn từ một selected document chưa có evidence, với raw BGE CE score `>5,5`.

## Artifact và audit

- `116/1.200` queries nhận addition; tổng `116` chunks mới.
- CE score min/mean/median/max: `5,5039 / 6,5123 / 6,2383 / 8,8828`.
- Passage dài trung bình `448,52` ký tự, min/max `278/500`.
- Docs khớp Exp74; mọi chunk Exp74 giữ nguyên và theo đúng thứ tự.
- Additions thuộc Docs đã chọn nhưng chưa được đại diện, là substring nguyên văn của source và chỉ dùng official IDs.
- ZIP `99.586.034` bytes, SHA-256 `f251f2a8fed811a68365a4e7572c125e87bb7f56af2c86e78f3d3aaf2ea92b0c`.

## Kết quả BTC

- Final: `0,3221`, hòa Exp74 sau làm tròn.
- Docs F2/P/R: `0,3574 / 0,1813 / 0,6086`, không đổi.
- Chunks F2/P/R: `0,2869 / 0,2399 / 0,3687`.

So với Exp74, Chunk F2 tăng `0,0001`, recall tăng `0,0002`, precision giảm `0,0002`. Tín hiệu dương nhưng rất nhỏ; tiếp tục một bước có kiểm soát với Exp78 threshold `>4,5`, chưa nhảy thẳng xuống threshold thấp nhất.
