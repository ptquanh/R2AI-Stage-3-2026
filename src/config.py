import os
from dotenv import load_dotenv

# Tải biến môi trường từ file .env (nếu có)
load_dotenv()

class Settings:
    """Lớp quản lý tập trung các cấu hình và biến môi trường (Environment Variables)"""
    
    # NCBI / PubMed API
    NCBI_EMAIL = os.getenv("NCBI_EMAIL", "your_email@example.com")
    NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")
    
    # LLM API
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_URL = os.getenv("GROQ_URL") # Để None để SDK tự lấy mặc định (https://api.groq.com)
    
# Khởi tạo một instance duy nhất (Singleton pattern) để import ở mọi nơi
settings = Settings()
