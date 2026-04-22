import json
from pathlib import Path
from typing import Optional, Union
from app.core.config import KB_PATH

class KBService:
    def __init__(self, kb_path: Union[str, Path] = KB_PATH):
        kb_file = Path(kb_path)
        with kb_file.open("r", encoding="utf-8") as f:
            self.kb = json.load(f)
    
    def search_kb(self, query: str, top_k: int = 5, filters: Optional[dict] = None) -> dict:
        """
        Busca en la KB usando weighted keyword matching.
        """
        query_tokens = self._tokenize(query)
        scores = []
        
        for doc in self.kb:
            # Aplicar filtros
            if filters:
                if "audience" in filters and doc.get("audience") != filters["audience"]:
                    continue
                if "tags" in filters:
                    if not any(tag in doc.get("tags", []) for tag in filters["tags"]):
                        continue
            
            # Calcular score
            title_tokens = self._tokenize(doc["title"])
            content_tokens = self._tokenize(doc["content"])
            tag_tokens = doc.get("tags", [])
            
            title_match = sum(1 for t in query_tokens if t in title_tokens)
            content_match = sum(1 for t in query_tokens if t in content_tokens)
            tag_match = sum(1 for t in query_tokens if t in tag_tokens)
            
            # Pesos: title > tags > content
            score = (title_match * 3 + tag_match * 2 + content_match * 1) / max(len(query_tokens), 1)
            
            if score > 0:
                scores.append((score, doc))
        
        # Sort by score, limit to top_k
        scores.sort(key=lambda x: x[0], reverse=True)
        top_docs = scores[:min(top_k, 10)]
        
        results = []
        for score, doc in top_docs:
            snippet = doc["content"][:150] + "..." if len(doc["content"]) > 150 else doc["content"]
            results.append({
                "id": doc["id"],
                "title": doc["title"],
                "score": round(score, 2),
                "snippet": snippet,
                "tags": doc.get("tags", [])
            })
        
        return {"results": results}
    
    def _tokenize(self, text: str) -> set:
        """
        Tokenización simple: lowercase + split.
        """
        return set(text.lower().split())