import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

class SemanticSearchEngine:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SemanticSearchEngine, cls).__new__(cls)
            cls._instance._init_engine()
        return cls._instance
        
    def _init_engine(self):
        self.model = None
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"Error loading model: {e}")
                self.model = None
                
    def search(self, query: str, products: list, top_k: int = 10):
        if not products:
            return []
            
        if self.model is None or not HAS_SENTENCE_TRANSFORMERS:
            # Fallback to basic substring matching
            query_lower = query.lower()
            results = []
            for p in products:
                score = 0.0
                if query_lower in p.name.lower():
                    score += 0.8
                if p.sku and query_lower in p.sku.lower():
                    score += 0.5
                if score > 0:
                    results.append({
                        "product_id": p.id,
                        "product_name": p.name,
                        "sku": p.sku,
                        "selling_price": p.selling_price,
                        "quantity_left": p.quantity_left,
                        "similarity_score": score
                    })
            results.sort(key=lambda x: x["similarity_score"], reverse=True)
            return results[:top_k]
            
        # Semantic search
        product_names = [p.name for p in products]
        product_embeddings = self.model.encode(product_names)
        query_embedding = self.model.encode([query])
        
        similarities = cosine_similarity(query_embedding, product_embeddings)[0]
        
        results = []
        for idx, score in enumerate(similarities):
            p = products[idx]
            results.append({
                "product_id": p.id,
                "product_name": p.name,
                "sku": p.sku,
                "selling_price": p.selling_price,
                "quantity_left": p.quantity_left,
                "similarity_score": float(score)
            })
            
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_k]

search_engine = SemanticSearchEngine()
