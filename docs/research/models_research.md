# Báo cáo Nghiên cứu Model LLM (<= 15B) cho R2AI Stage 3

_Nguồn: Nghiên cứu nội bộ từ User. Cập nhật các model được release trước 01/08/2026._

Dưới đây là bản tổng hợp theo nghĩa **có thể sử dụng để lập shortlist nghiên cứu/deployment**: các _base/foundation model_ hoặc bản chính thức của một họ model, có tổng số tham số $\leq 15$B, đã được công khai **trước 01/08/2026**.

## Phạm vi và quy ước

- **Tính**: checkpoint pretrained/instruct/reasoning/code chính thức; model dense có total params $\leq 15$B; model multimodal được tách nhãn riêng.
- **Không tính mặc định**: fine-tune cộng đồng, Uncensored, Dolphin, Hermes, các quantization, LoRA, merge và distilled checkpoint nếu không phải dòng gốc.
- **MoE**: Tính theo **total parameters**, không dùng active parameters. (Vd: Qwen3-30B-A3B không hợp lệ).
- **Public weights**: Cần kiểm tra license (như Gemma/Llama có hạn chế, Qwen3 là Apache-2.0).

## Shortlist triển khai 2026 cho Pipeline Y khoa

Với công việc thiên về **NLP tiếng Việt, retrieval, medical NER, và benchmark thực chiến**, tập 12 model sau đủ để bao phủ mọi trade-off:

1. **Qwen3-4B**: lựa chọn cân bằng nhất cho inference local, 128K context và reasoning toggle.
2. **Qwen3-8B**: default candidate cho chatbot/RAG tiếng Việt khi có GPU 12–16 GB VRAM ở quant 4-bit.
3. **Qwen3-14B**: candidate chất lượng cao trong giới hạn 15B; cần GPU lớn hơn hoặc quantization mạnh.
4. **Qwen2.5-7B-Instruct**: baseline ổn định, ecosystem mature, rất phù hợp làm ablation.
5. **Qwen2.5-Coder-7B hoặc 14B**: code/RAG agent và tool-use.
6. **DeepSeek-R1-Distill-Qwen-7B/14B**: thêm vào benchmark reasoning (cần kiểm tra hallucination).
7. **Gemma 3 4B hoặc 12B**: nếu cần document image + text hoặc một đối trọng ngoài họ Qwen.
8. **Gemma 4 12B**: candidate multimodal mới trong đúng trần 15B (tháng 06/2026).
9. **Phi-4 14B**: baseline reasoning/quality từ hệ Microsoft.
10. **Phi-4-mini 3.8B**: latency-first, edge hoặc batch extraction.
11. **Mistral Nemo 12B**: lựa chọn 12B có long context, benchmark multilingual/general.
12. **Aya 8B**: điểm đối chứng multilingual (đặc biệt hữu ích khi đánh giá tiếng Trung/Anh ngoài tiếng Việt).

## 4 Tiêu chí Đánh giá Thực tiễn (Benchmark)

1. **Vietnamese general + instruction following**: đo exact-match, pairwise preference và tỷ lệ vi phạm format JSON.
2. **Domain RAG (Medical/Biomedical)**: với citation-required; đo groundedness, citation precision/recall, answer completeness và hallucination rate.
3. **Structured extraction**: NER/normalization (ICD-10, y khoa); đo entity-level F1, schema-valid JSON rate.
4. **Deployment**: token/s, TTFT, peak VRAM, throughput ở context 4K/16K/64K, và chi phí khi Q4/Q5/Q8.
