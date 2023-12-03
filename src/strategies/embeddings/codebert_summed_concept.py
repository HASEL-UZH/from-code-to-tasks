from typing import Any

import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer

from src.strategies.defs import ContentStrategies, CacheStrategy, IEmbeddingConcept
from src.strategies.embeddings.codebert_npy_cache import CodeBertNpyCache

cb_model = AutoModel.from_pretrained("microsoft/codebert-base")
cb_tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")


class CodeBertSummedEmbeddingStrategy:
    def __init__(self):
        self.name = "codebert-summed-embedding"
        self._cache = CodeBertNpyCache("codebert-standard")

    def get_embedding(self, code) -> Any:
        embedding = self._cache.get_embedding_from_cache(code)
        if embedding is None:
            embedding = self._create_embedding(code)
            self._cache.save_embedding_to_cache(code, embedding)
        return embedding

    def _create_embedding(self, code, max_seq_length=512) -> Any:
        code_tokens = cb_tokenizer.tokenize(code, truncation=True)
        total_tokens = len(code_tokens) + 2  # 3 if SEP token added
        if total_tokens > max_seq_length:
            keep = int(max_seq_length - 2)  # 3 if SEP token added
            code_tokens = code_tokens[:keep]
        tokens = [cb_tokenizer.cls_token] + code_tokens + [cb_tokenizer.eos_token]
        tokens_ids = cb_tokenizer.convert_tokens_to_ids(tokens[1:])
        embeddings = cb_model(torch.tensor(tokens_ids)[None, :])[0]
        summed_embeddings = torch.sum(embeddings, dim=1)
        return summed_embeddings

    def calculate_similarity(self, embedding1, embedding2):
        similarity = (F.cosine_similarity(embedding1, embedding2, dim=1)).item()
        return similarity

    def get_tokens(self, text: str) -> [str]:
        return ["no tokens for codebert summed"]


class CodeBertSummedConcept(IEmbeddingConcept):
    name = "codebert-summed"

    def __init__(self):
        self.embedding_strategies = [CodeBertSummedEmbeddingStrategy()]
        self.content_strategies = ContentStrategies.CodeBERT
        self.cache_strategy = CacheStrategy.Npy
