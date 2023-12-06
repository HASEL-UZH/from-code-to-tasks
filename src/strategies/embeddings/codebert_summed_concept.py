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
        # Get the sequence lengths of embeddings
        seq_len1 = embedding1.size(1)
        seq_len2 = embedding2.size(1)

        # Find the maximum sequence length
        max_seq_len = max(seq_len1, seq_len2)

        # Pad the embeddings to have the same sequence length
        pad1 = max_seq_len - seq_len1
        pad2 = max_seq_len - seq_len2

        embedding1_padded = F.pad(embedding1, (0, 0, 0, pad1))
        embedding2_padded = F.pad(embedding2, (0, 0, 0, pad2))

        # Reshape padded tensors to [batch_size, sequence_length * embedding_size]
        embedding1_flat = embedding1_padded.view(embedding1_padded.size(0), -1)
        embedding2_flat = embedding2_padded.view(embedding2_padded.size(0), -1)

        # Calculate cosine similarity using matrix multiplication
        cosine_similarities = F.cosine_similarity(
            embedding1_flat, embedding2_flat, dim=1
        )

        # Calculate mean similarity
        mean_similarity = torch.mean(cosine_similarities).item()

        return mean_similarity

    def get_tokens(self, text: str) -> [str]:
        return ["no tokens for codebert summed"]


class CodeBertSummedConcept(IEmbeddingConcept):
    name = "codebert-summed"

    def __init__(self):
        self.embedding_strategies = [CodeBertSummedEmbeddingStrategy()]
        self.content_strategies = ContentStrategies.CodeBERT
        self.cache_strategy = CacheStrategy.Npy
