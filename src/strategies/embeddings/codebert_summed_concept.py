import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained("microsoft/codebert-base")
tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")


def _codebert_summed_embedding_strategy(text, max_seq_length=512):
    text_tokens = tokenizer.tokenize(text, truncation=True)
    total_tokens = len(text_tokens) + 2 #3 if SEP token added
    if total_tokens > max_seq_length:
        print("TRUNCATION!")
        keep_tokens = int(max_seq_length - 2) #3 if SEP token added
        text_tokens = text_tokens[:keep_tokens]
    tokens = [tokenizer.cls_token] + text_tokens + [tokenizer.eos_token]
    tokens_ids = tokenizer.convert_tokens_to_ids(tokens[1:])
    embeddings = model(torch.tensor(tokens_ids)[None,:])[0]
    summed_embeddings = torch.sum(embeddings, dim=1)
    return summed_embeddings


def _create_strategy():
    def create_embedding(text):
        return _codebert_summed_embedding_strategy(text)
    return create_embedding


def _calculate_cosine_similarity(embedding1, embedding2):
    similarity = (F.cosine_similarity(embedding1, embedding2, dim=1)).item()
    return similarity


def create_codebert_summed_concept():
    strategies = []
    strategies.append({
        "id" : "truncation",
        "create_embedding" : _create_strategy()
    })
    return {
        "id" : "codebert_summed",
        "strategies": strategies,
        "calculate_similarity" : _calculate_cosine_similarity
    }