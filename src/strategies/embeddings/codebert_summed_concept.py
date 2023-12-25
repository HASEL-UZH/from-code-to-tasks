from typing import Any

import numpy as np
import torch
from sklearn.metrics.pairwise import cosine_similarity
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
        embedding1_0 = embedding1[0]
        embedding2_0 = embedding2[0]

        if embedding1_0.dim() > 1:
            embedding1_0 = torch.sum(embedding1_0, dim=1)

        if embedding2_0.dim() > 1:
            embedding2_0 = torch.sum(embedding2_0, dim=1)

        embedding1_0 = embedding1_0.numpy()
        embedding2_0 = embedding2_0.numpy()
        size_diff = abs(embedding1_0.size - embedding2_0.size)

        if embedding1_0.size > embedding2_0.size:
            embedding2_0 = np.pad(
                embedding2_0,
                (0, size_diff),
                mode="constant",
                constant_values=0,
            )
        elif embedding2_0.size > embedding1_0.size:
            embedding1_0 = np.pad(
                embedding1_0,
                (0, size_diff),
                mode="constant",
                constant_values=0,
            )

        similarity = cosine_similarity(
            embedding1_0.reshape(1, -1),
            embedding2_0.reshape(1, -1),
        )[0, 0]

        return similarity

    def get_tokens(self, text: str) -> [str]:
        return ["no tokens for codebert summed"]


class CodeBertSummedConcept(IEmbeddingConcept):
    name = "codebert-summed"

    def __init__(self):
        self.embedding_strategies = [CodeBertSummedEmbeddingStrategy()]
        self.content_strategies = ContentStrategies.CodeBERT
        self.cache_strategy = CacheStrategy.Npy
