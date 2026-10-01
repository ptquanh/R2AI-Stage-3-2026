import re
from typing import List, Dict, Any

class SemanticChunker:
    """
    Trình cắt văn bản theo ngữ nghĩa (Semantic Chunker).
    Nguyên lý: 
    - Ưu tiên cắt theo đoạn văn (paragraph) được phân cách bởi 2 dấu xuống dòng (\n\n).
    - Nếu đoạn quá dài, tiếp tục cắt theo câu (dấu chấm, chấm hỏi, chấm than).
    - Cố gắng gộp các đoạn/câu ngắn lại với nhau cho đến khi đạt giới hạn max_tokens.
    """
    def __init__(self, max_tokens: int = 1024, token_overlap: int = 100):
        self.max_tokens = max_tokens
        self.token_overlap = token_overlap
        # Dùng tỷ lệ xấp xỉ: 1 token ~ 0.75 từ (đối với tiếng Việt/Anh)
        self.max_words = int(self.max_tokens * 0.75)
        self.overlap_words = int(self.token_overlap * 0.75)

    def count_words(self, text: str) -> int:
        """Đếm số lượng từ trong text."""
        return len(text.split())

    def split_into_sentences(self, text: str) -> List[str]:
        """Tách văn bản thành các câu dựa trên dấu câu."""
        # Biểu thức chính quy cắt theo dấu chấm, chấm hỏi, chấm than (hỗ trợ cả tiếng Việt và Trung)
        sentences = re.split(r'(?<=[.!?。！？])\s+', text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def chunk_document(self, doc_id: str, text: str, url: str = "") -> List[Dict[str, Any]]:
        """
        Cắt 1 văn bản dài thành nhiều chunk nhỏ.
        Returns: Danh sách các Dictionary chứa nội dung chunk và metadata.
        """
        if not text:
            return []

        # Tách theo đoạn văn (\n\n hoặc \n)
        paragraphs = re.split(r'\n\s*\n', text.strip())
        
        chunks = []
        current_chunk_words = []
        current_word_count = 0
        
        def add_chunk(words_list):
            chunk_text = ' '.join(words_list).strip()
            if chunk_text:
                chunks.append({
                    "chunk_id": f"{doc_id}_{len(chunks)}",
                    "doc_id": doc_id,
                    "url": url,
                    "content": chunk_text,
                    "word_count": self.count_words(chunk_text)
                })

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_words = para.split()
            para_word_count = len(para_words)

            # Trường hợp lý tưởng: Đoạn văn hiện tại có thể gộp vào chunk đang gom
            if current_word_count + para_word_count <= self.max_words:
                current_chunk_words.extend(para_words)
                current_word_count += para_word_count
            else:
                # Nếu chunk đang gom đã có data, thì lưu nó lại trước
                if current_chunk_words:
                    add_chunk(current_chunk_words)
                    # Giữ lại một phần overlap (đuôi của chunk trước làm đầu của chunk sau)
                    overlap_slice = current_chunk_words[-self.overlap_words:] if self.overlap_words > 0 else []
                    current_chunk_words = overlap_slice
                    current_word_count = len(current_chunk_words)

                # Sau khi lưu chunk cũ, kiểm tra xem đoạn văn mới này có QUÁ KHỔ không?
                if para_word_count > self.max_words:
                    # Bắt buộc phải băm đoạn văn này thành từng câu
                    sentences = self.split_into_sentences(para)
                    for sentence in sentences:
                        sent_words = sentence.split()
                        sent_len = len(sent_words)
                        
                        if current_word_count + sent_len > self.max_words and current_chunk_words:
                            add_chunk(current_chunk_words)
                            overlap_slice = current_chunk_words[-self.overlap_words:] if self.overlap_words > 0 else []
                            current_chunk_words = overlap_slice
                            current_word_count = len(current_chunk_words)
                            
                        current_chunk_words.extend(sent_words)
                        current_word_count += sent_len
                else:
                    # Nếu đoạn mới không quá khổ, đưa vào chunk mới
                    current_chunk_words.extend(para_words)
                    current_word_count += para_word_count

        # Lưu chunk cuối cùng nếu còn sót
        if current_chunk_words:
            add_chunk(current_chunk_words)

        return chunks

# Test thử nếu chạy file trực tiếp
if __name__ == "__main__":
    sample_text = "Đây là một bài báo y khoa siêu dài. " * 100
    chunker = SemanticChunker(max_tokens=100) # Thử giới hạn 100 tokens ~ 75 từ
    results = chunker.chunk_document(doc_id="DOC_001", text=sample_text, url="https://example.com")
    
    print(f"Tổng số chunks: {len(results)}")
    for i, res in enumerate(results[:2]):
        print(f"\n--- Chunk {i} ({res['word_count']} words) ---")
        print(res['content'][:150] + "...")
