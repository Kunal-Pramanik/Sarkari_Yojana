# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL: str = "llama-3.1-8b-instant"
    
    MAX_HISTORY_TURNS: int = 10 
    
    INDEX_PATH: str = "." 
    CHUNKS_PATH: str = "schemes_meta.json" 
    
    EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    TOP_K_RETRIEVAL: int = 3
    SIMILARITY_THRESHOLD: float = 0.35

    # Web search
    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")
    SEARCH_CONFIDENCE_THRESHOLD: float = 16.0  # Below this → trigger web search
    MAX_SEARCH_RESULTS: int = 2

config = Config()