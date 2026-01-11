import traceback
from transformers import AutoModel
import numpy as np

class Embedding:
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            print("Creating new Embedding instance")
            cls._instance = super().__new__(cls)
            
            try:
                print("Initializing pipeline...")
                cls._model = AutoModel.from_pretrained("jinaai/jina-embeddings-v2-base-code", trust_remote_code=True).to("cuda:0")
                print("Embedding model initialized successfully")
            except Exception as e:
                print(f"Pipeline initialization failed: {e}")
                raise
        return cls._instance
    
    def __init__(self):
        pass
    
    def get_embedding(self, text):
        """Get embedding for text"""
        try:
            if text is None:
                print("Warning: Input text is None")
                return None
                
            if not isinstance(text, str):
                print(f"Warning: Input text type is not string, but {type(text)}")
                text = str(text)
                
            if not text.strip():
                print("Warning: Input text is empty")
                return None
            
            return self._model.encode([text])[0].tolist()
            
        except Exception as e:
            print(f"Error getting embedding: {e}")
            print(f"Model status: {self._model}")
            print(traceback.format_exc())
            return None

    def _cos_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def text_similarity(self, text1, text2):
        """Calculate similarity between two texts"""
        vec1 = self.get_embedding(text1)
        vec2 = self.get_embedding(text2)
        return self._cos_similarity(vec1, vec2)
