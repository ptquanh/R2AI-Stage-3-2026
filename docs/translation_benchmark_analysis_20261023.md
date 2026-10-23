# Phân tích benchmark dịch query — 23/10/2026

## Provenance

- `labs/translation_benchmark_nmt.zip`: `147.670` bytes; SHA-256 `4992105c711e62b1f0a3ef8b4321d45498c2b81b53af5fa2d9451883603b445e`.
- `labs/translation_benchmark_llm.zip`: `183.583` bytes; SHA-256 `ea80b1c992fce7b43c1c8454fc1a35431713b345dc82cc26db1001e7483b7e9e`.
- Cả hai ZIP qua CRC; tất cả model được yêu cầu đều hoàn tất, không có model-run failure.
- NMT có `360/360` query-target outputs không rỗng. LLM có `358/360`; hai output rỗng đều thuộc Qwen3-8B tại query ID 219 cho EN và ZH, trạng thái `needs_review` với lỗi `empty` sau khi raw JSON bị cắt.
- Benchmark gồm 60 query cuộc thi phân tầng và 128 cặp MedEV VI→EN có reference. Chỉ số query không phải relevance labels và không dự đoán trực tiếp điểm BTC.

## Kết quả tiếng Anh

| Model | Validator pass | Number recall | Medical-token recall | BGE source cosine | MedEV BLEU | chrF | TER | Runtime (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| VinAI Translate v2 | 0,8500 | 0,9265 | 0,6772 | 0,7713 | **34,7383** | **62,0807** | **57,5993** | 68,75 |
| Qwen3-14B-AWQ | 0,8333 | 0,9137 | 0,6772 | 0,7706 | 26,7558 | 56,6942 | 67,5543 | 3.906,03 |
| Qwen3-8B | 0,8167 | 0,8954 | 0,6717 | 0,7595 | 24,5680 | 52,3346 | 70,6678 | 1.853,57 |
| Qwen3-4B | 0,8000 | 0,8843 | 0,6772 | 0,7679 | 22,2970 | 45,7411 | 73,9041 | 880,47 |
| MADLAD-400-3B-MT | 0,7667 | 0,8487 | 0,6772 | 0,7723 | 25,9913 | 55,6553 | 68,5785 | 707,65 |
| EnViT5 | 0,7333 | 0,7937 | 0,6606 | 0,7612 | 25,9014 | 56,9425 | 75,4199 | 76,78 |
| NLLB-600M | 0,6833 | 0,7432 | 0,6522 | 0,7455 | 23,2555 | 50,5454 | 70,1352 | 99,23 |

VinAI Translate v2 là lựa chọn mặc định cho EN: đứng đầu đồng thời validator, bảo toàn số, BLEU/chrF/TER và nhanh hơn Qwen14 khoảng 57 lần trong run này. Qwen14 hữu ích làm alternate/rescue cho query dài hoặc thuật ngữ khó, không phải default EN toàn bộ corpus.

## Kết quả tiếng Trung và audit định tính

ZH không có reference tương đương MedEV, vì vậy không được chọn model chỉ từ cosine/consensus. Qwen3-14B-AWQ có validator pass `0,55`, number recall `0,5668`, medical-token recall `0,5339`, BGE source cosine `0,7767`; Qwen4/Qwen8 gần nhau ở proxy. MADLAD/NLLB chỉ đạt BGE source cosine khoảng `0,7211/0,7352` và có nhiều lỗi nghĩa trong review.

Audit mẫu cho thấy Qwen14 bảo toàn tốt hơn query dài nhiều chủ thể và thuật ngữ như viêm gan B; Qwen4 có ca dịch “nổi nóng” thành hot flashes và làm sai bệnh danh; Qwen8 bị cắt JSON ở query ID 219 nên EN/ZH parse thành rỗng. NLLB/MADLAD thường xuyên đổi nghĩa thuật ngữ y khoa hoặc đời sống. Qwen14 được chọn làm ZH default có điều kiện, với retry bắt buộc khi output bị cắt/JSON lỗi.

## Quyết định triển khai

1. Sinh EN cho đủ 1.200 query bằng VinAI Translate v2.
2. Sinh ZH bằng Qwen3-14B-AWQ, chia shard nếu cần; tăng token budget động theo độ dài input và retry nếu chưa đóng JSON, reached token limit hoặc validator fail.
3. Qwen14 EN chỉ là rescue/alternate cho query phức tạp hoặc VinAI fail validator; không cộng VinAI và Qwen như hai phiếu độc lập trong cùng language family.
4. Giữ raw VI làm fallback. Không dùng NLLB, MADLAD hoặc Qwen4 làm bản dịch production ở vòng này.
5. Trước khi nộp BTC, rebuild riêng cache BM25 EN/ZH, đo candidate churn/overlap và số membership docs thực sự đổi so với Exp122. Chỉ dùng slot nếu treatment đủ 1.200 query và không phải no-op.

## Giới hạn kết luận

Benchmark chứng minh chất lượng dịch tốt hơn trên MedEV và các validator, không chứng minh retrieval/F2 sẽ tăng. Bài học từ Exp125 cho thấy query transformation có thể giảm Docs F2 nếu dùng trực tiếp. Phép thử leaderboard phải cô lập translation repair, giữ scorer/count/chunk policy control bất biến.
