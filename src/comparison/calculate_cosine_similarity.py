import random

import torch.nn.functional as F
from sklearn.metrics.pairwise import cosine_similarity


def calculate_cosine_similarity(embedding1, embedding2, embedding_strategy):
    if embedding_strategy == "tf_embedding_strategy" or "tf_idf_embedding_strategy":
        similarity = cosine_similarity(embedding1, embedding2)

    elif  embedding_strategy == "codebert_embedding_strategy":
        similarity = F.cosine_similarity(embedding1, embedding2, dim=2)

    elif embedding_strategy == "codebert_summed_embedding_strategy":
        similarity = F.cosine_similarity(embedding1, embedding2, dim=1)

    # TODO remove
    similarity = random.random()
    return similarity
#
#
# if __name__ == "__main__":
#     matrix1 = np.array([[1, 2, 3],
#                         [4, 5, 6],
#                         [7, 8, 9]])
#
#     # Example NumPy matrix 2
#     matrix2 = np.array([[9, 8, 7],
#                         [6, 5, 4],
#                         [3, 2, 1]])
#     print(calculate_cosine_similarity(matrix1, matrix2, "tf_embedding_strategy"))