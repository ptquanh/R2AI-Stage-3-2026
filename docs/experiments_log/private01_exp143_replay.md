# Private01 — replay Exp143 trên bộ 1.200 query BTC xác nhận dùng lại

Ngày chuẩn bị: **02/11/2026**. Hạn private: **23:59 ngày 04/11/2026, UTC+7**. Tối đa 5 lượt cho toàn private. Cập nhật 03/11: người dùng xác nhận **đã nộp 1 lượt**, còn tối đa 4 lượt; chưa cung cấp ID/receipt portal.

**Đính chính 03/11:** private **không công bố điểm trước khi kết thúc**. Thông tin ngày 02/11 về trả điểm từng lượt không còn hiệu lực. Quy tắc lấy **điểm cao nhất** giữ theo xác nhận trước đó; không lập kế hoạch chọn nhánh thắng dựa vào feedback private chưa có. Email BTC yêu cầu bộ thuyết minh, data/model/source/README trước cùng hạn 04/11.

## Trạng thái

- **Build và audit PASS:** `submission_private01_exp143_replay.zip`; người dùng xác nhận đã nộp lượt đầu. **Chưa có điểm private**; chưa kiểm chứng receipt trên portal.
- ZIP **94.478.622 bytes** (<100 MB), SHA256 `14687b27b12a98777daddc290e54e2c25d310743917511866a06cee51e7c4ac3`.
- Đã đối chiếu độc lập đủ **1.200 queries, 183.703 docs, 127.271 chunks**; từng prediction bằng Exp143, không ID ngoài corpus/duplicate. ZIP CRC và source-offset checks pass. ZIP hash khác reference; prediction equality đã kiểm tra riêng, không dựa vào kích thước file hoặc hash của container nén.
- Tests `python -m pytest tests/test_private_champion_replay.py -q`: **3 passed**; kiểm tra query text thay đổi, cache mâu thuẫn/duplicate, schema và corpus IDs.
- Không phải một treatment mới: tái lập selection/packaging của best public theo evaluator mới, dùng inference cache có provenance. Không chạy lại GPU cho cùng input/model.
- Reference Exp143: Final **0.3190**; Docs F2/P/R `0.3731 / 0.2261 / 0.5631`; Chunks F2/P/R `0.2648 / 0.2047 / 0.3510`. Không điền các số này vào cột private.

## Cấu hình và nguồn

- Docs: joint Qwen4B top130 + owner floor; giữ nguyên danh sách của Exp143.
- Chunks: Qwen4B keep90 + bảo toàn nhóm quá dài chưa chấm; Exp142 thêm tối đa 5 missing-owner evidence/query; Exp143 thêm tối đa 3 best-scored P2a source windows/query từ decile chunk dài nhất.
- Reference ZIP SHA256: `039eb431209008b00eeb7b8df76b4d784c20a677c1b375444a167bf19f229649`.
- Query SHA256: `ce13508b893bbd6b9169679d540630bc37eb5950cad08b4d5e0e5d7063670c08`. Người dùng xác nhận BTC dùng lại query; code đối chiếu exact toàn bộ 1.200 ID/text với cache trước build.
- Kiểm tra provenance phát hiện output P2a Parquet khác hash input manifest. Nguyên nhân xác minh từ notebook: ghi lại bằng zstd; `assert_frame_equal(check_exact=True)` đối chiếu toàn bộ rows, columns, dtype và thứ tự với input gốc hash-pinned đã pass. Không bỏ qua mismatch hoặc sửa manifest lịch sử.
- Input P2a SHA256 `febb7a3c8b1f48cc981df21b431685f638f761c17795fcaa53856505cfe9c958`; output Parquet SHA256 `48dba00ac7d89a3b09c6e4a9be291ad97b04d57536fdd656101fa1ac06ca08be`.

## Tái lập và điều kiện phát hành

Chạy `python -m scripts.prepare_private_champion` từ root. Không ghi đè artifact có sẵn; muốn replay lần nữa dùng `--out-prefix` mới.

- Audit độc lập: schema/ID thuộc corpus, query coverage/order, duplicate docs/chunks, CRC, ZIP <100 MB và từng prediction bằng champion.
- Expected: 1.200 queries, 183.703 doc predictions, 127.271 chunks (3.436 spans thêm so với Exp142).
- Source validation kế thừa champion đã audit, cộng kiểm tra offset/hash các spans rebuild; không quét lại toàn bộ source corpus.
- `submission_private01_exp143_replay_audit.json` lưu trạng thái local lúc build ngày 02/11; trường chưa nộp trong audit là snapshot lịch sử, không sửa hồi tố. Ledger này ghi cập nhật người dùng xác nhận đã nộp ngày 03/11; build manifest không phải bằng chứng portal receipt.

## Kết quả private

Chưa công bố. Cần bổ sung ID portal, thời điểm và receipt khi người dùng cung cấp; chỉ ghi bảy metrics sau khi BTC công bố kết quả private. Không tự suy ra score/private labels từ cùng bộ query.

Phân bổ các lượt còn lại theo [kế hoạch hồ sơ/UI/private](../r2ai_score_improvement_plan.md): ưu tiên năm mục email, UI và slide; docs-only/chunks-only/tổ hợp đăng ký trước chỉ chạy nếu không đe dọa deadline, không gọi là tổ hợp winners. Không nộp duplicate chỉ để tiêu đủ lượt.
