import os

import numpy as np
import torch

from src.core.utils import hash_string
from src.core.workspace_context import get_cache_dir


class CodeBertNpyCache:
    def __init__(self, codebert_embedding_concept):
        self._directory = codebert_embedding_concept

    def save_embedding_to_cache(self, code, embedding):
        code_hash = hash_string(code)
        cache_dir = get_cache_dir()
        npy_file_path = os.path.join(cache_dir, self._directory, f"{code_hash}.npy")
        os.makedirs(os.path.dirname(npy_file_path), exist_ok=True)
        np.save(npy_file_path, embedding.detach().numpy())

    def get_embedding_from_cache(self, code):
        code_hash = hash_string(code)
        cache_dir = get_cache_dir()
        npy_file_path = os.path.join(cache_dir, self._directory, f"{code_hash}.npy")
        if os.path.exists(npy_file_path):
            return torch.tensor(np.load(npy_file_path))
        else:
            return None
