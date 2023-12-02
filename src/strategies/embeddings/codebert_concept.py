from typing import Any

import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer

from src.strategies.defs import ContentStrategies, CacheStrategy, IEmbeddingConcept

cb_model = AutoModel.from_pretrained("microsoft/codebert-base")
cb_tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")


class CodeBertEmbeddingStrategy:
    def __init__(self):
        self.name = "codebert-embedding"
        self._cache = {}

    def init(self):
        self._cache = {}

    def get_embedding(self, code) -> Any:
        embedding = self._cache.get(code)
        if embedding is None:
            embedding = self._create_embedding(code)
            self._cache[code] = embedding
        return embedding

    def _create_embedding(self, code, max_seq_length=512) -> Any:
        code_tokens = cb_tokenizer.tokenize(code, truncation=True)
        total_tokens = len(code_tokens) + 2  # 3 if SEP token added
        if total_tokens > max_seq_length:
            print("TRUNCATION!")
            keep = int(max_seq_length - 2)  # 3 if SEP token added
            code_tokens = code_tokens[:keep]
        tokens = [cb_tokenizer.cls_token] + code_tokens + [cb_tokenizer.eos_token]
        tokens_ids = cb_tokenizer.convert_tokens_to_ids(tokens[1:])
        embeddings = cb_model(torch.tensor(tokens_ids)[None, :])[0]
        return embeddings

    def calculate_similarity(self, embedding1, embedding2):
        embedding1 = embedding1[0]
        embedding2 = embedding2[0]
        size_diff = abs(embedding1.size(0) - embedding2.size(0))
        if embedding1.size(0) > embedding2.size(0):
            embedding2 = F.pad(embedding2, (0, 0, 0, size_diff))
        elif embedding2.size(0) > embedding1.size(0):
            embedding1 = F.pad(embedding1, (0, 0, 0, size_diff))
        similarity = F.cosine_similarity(
            embedding1.reshape(-1), embedding2.reshape(-1), dim=0
        ).item()
        return similarity

    def get_tokens(self, text: str) -> [str]:
        return ["no tokens for codebert"]


class CodeBertConcept(IEmbeddingConcept):
    name = "codebert"

    def __init__(self):
        self.embedding_strategies = []
        self.content_strategies = ContentStrategies.CodeBERT
        self.cache_strategy = CacheStrategy.Npy
        self.embedding_strategies.append(CodeBertEmbeddingStrategy)
