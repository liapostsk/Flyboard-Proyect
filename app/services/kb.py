import json
import re
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
                audience_filter = filters.get("audience")
                if audience_filter and doc.get("audience") != audience_filter:
                    continue

                # Un filtro de tags vacio se trata como "sin filtro".
                tags_filter = filters.get("tags")
                if isinstance(tags_filter, list) and tags_filter:
                    if not any(
                        self._tag_matches(filter_tag, doc_tag)
                        for filter_tag in tags_filter
                        for doc_tag in doc.get("tags", [])
                    ):
                        continue
            
            # Calcular score
            title_tokens = self._tokenize(doc["title"])
            content_tokens = self._tokenize(doc["content"])
            tag_tokens = [self._normalize_tag(tag) for tag in doc.get("tags", [])]
            
            title_match = sum(1 for t in query_tokens if t in title_tokens)
            content_match = sum(1 for t in query_tokens if t in content_tokens)
            tag_match = sum(1 for t in query_tokens if any(self._tag_matches(t, tag) for tag in tag_tokens))
            
            # Pesos: title > tags > content
            score = (title_match * 3 + tag_match * 2 + content_match * 1) / max(len(query_tokens), 1)
            
            MIN_SCORE = 0.2

            if score >= MIN_SCORE:
                scores.append((score, doc))
        
        # Sort by score, limit to top_k
        scores.sort(key=lambda x: x[0], reverse=True)

        is_troubleshooting = any(
            token in query.lower()
            for token in ["fail", "error", "issue", "troubleshoot"]
        )

        if scores and not is_troubleshooting:
            best_score = scores[0][0]
            scores = [
                (score, doc)
                for score, doc in scores
                if score >= best_score * 0.75
            ]

        top_docs = scores[:min(top_k, 10)]
        
        results = []
        for score, doc in top_docs:
            snippet = self._build_snippet(doc["content"], query_tokens)
            results.append({
                "id": doc["id"],
                "title": doc["title"],
                "score": round(score, 2),
                "snippet": snippet,
                "tags": doc.get("tags", [])
            })
        
        return {"results": results}
    
    def _normalize_token(self, token: str) -> str:
        token = token.lower().strip()

        if len(token) > 4 and token.endswith("ies"):
            token = token[:-3] + "y"
        elif len(token) > 4 and token.endswith("s"):
            token = token[:-1]

        if len(token) > 5 and token.endswith("ed"):
            token = token[:-2]

        return token
    
    def _tokenize(self, text: str) -> set[str]:
        raw_tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
        normalized = [self._normalize_token(token) for token in raw_tokens]

        tokens = set(normalized)

        for i in range(len(normalized) - 1):
            tokens.add(normalized[i] + normalized[i + 1])

        return tokens

    def _normalize_tag(self, tag: str) -> str:
        return tag.strip().lower()

    def _tag_matches(self, left: str, right: str) -> bool:
        left_norm = self._normalize_tag(left)
        right_norm = self._normalize_tag(right)

        if left_norm == right_norm:
            return True

        if len(left_norm) > 3 and len(right_norm) > 3:
            if left_norm.startswith(right_norm) or right_norm.startswith(left_norm):
                return True

        return False

    def _build_snippet(self, content: str, query_tokens: set[str]) -> str:
        """Build a snippet from relevant sentences so important facts are not truncated away."""
        max_length = 400

        if len(content) <= max_length:
            return content

        sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", content) if sentence.strip()]
        if not sentences:
            return content[: max_length - 3].rstrip() + "..."

        relevant_indexes = []
        for index, sentence in enumerate(sentences):
            sentence_tokens = self._tokenize(sentence)
            if any(token in sentence_tokens for token in query_tokens):
                relevant_indexes.append(index)

        if relevant_indexes:
            expanded_indexes = []
            for index in relevant_indexes:
                if index - 1 >= 0:
                    expanded_indexes.append(index - 1)
                expanded_indexes.append(index)
                if index + 1 < len(sentences):
                    expanded_indexes.append(index + 1)

            snippet = " ".join(sentences[index] for index in sorted(set(expanded_indexes)))
        else:
            snippet = sentences[0]

        if len(snippet) > max_length:
            snippet = snippet[: max_length - 3].rstrip() + "..."

        return snippet
    
    def clean_filters(self, filters: Optional[dict]) -> Optional[dict]:
        if not filters:
            return None

        cleaned = {}

        audience = filters.get("audience")
        if audience:
            cleaned["audience"] = audience

        valid_tags = self._all_tags()
        tags = filters.get("tags")

        if isinstance(tags, list):
            normalized_tags = []
            for tag in tags:
                if not isinstance(tag, str):
                    continue

                normalized = self._normalize_tag(tag)
                if normalized in valid_tags:
                    normalized_tags.append(normalized)

            if normalized_tags:
                cleaned["tags"] = normalized_tags

        return cleaned or None

    def _all_tags(self) -> set[str]:
        return {
            self._normalize_tag(tag)
            for doc in self.kb
            for tag in doc.get("tags", [])
        }