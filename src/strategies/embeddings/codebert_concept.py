import torch
import torch.nn.functional as F
from pympler import asizeof
from transformers import AutoModel, AutoTokenizer

from src.core.logger import log
from src.strategies.embeddings.defs import ContentStrategies, CacheStrategy

model = AutoModel.from_pretrained("microsoft/codebert-base")
tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")


def _codebert_embedding_strategy(text, max_seq_length=512):
    text_tokens = tokenizer.tokenize(text, truncation=True)
    total_tokens = len(text_tokens) + 2  # 3 if SEP token added
    if total_tokens > max_seq_length:
        print("TRUNCATION!")
        keep_tokens = int(max_seq_length - 2)  # 3 if SEP token added
        text_tokens = text_tokens[:keep_tokens]
    tokens = [tokenizer.cls_token] + text_tokens + [tokenizer.eos_token]
    tokens_ids = tokenizer.convert_tokens_to_ids(tokens[1:])
    embeddings = model(torch.tensor(tokens_ids)[None, :])[0]
    log.debug(
        f"text: {asizeof.asizeof(text)}, tokens: {asizeof.asizeof(tokens_ids)}, embeddings:  {asizeof.asizeof(embeddings)}"
    )
    return embeddings


def _create_strategy():
    def create_embedding(text):
        return _codebert_embedding_strategy(text)

    return create_embedding


def _calculate_cosine_similarity(embedding1, embedding2):
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


def create_codebert_concept():
    strategies = []
    strategies.append({"id": "truncation", "create_embedding": _create_strategy()})
    return {
        "id": "codebert",
        "strategies": strategies,
        "calculate_similarity": _calculate_cosine_similarity,
        "content_strategies": ContentStrategies.CodeBERT,
        "cache_strategy": CacheStrategy.Npy,
    }
