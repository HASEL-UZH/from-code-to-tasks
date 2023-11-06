import torch.nn.functional as F
from numpy import dot
from numpy.linalg import norm

from src.strategies.embeddings.embedding_strategies import tf_embedding_strategy, tf_idf_embedding_strategy, \
    codebert_embedding_strategy, codebert_summed_embedding_strategy


def calculate_cosine_similarity(embedding1, embedding2, embedding_strategy):
    if embedding_strategy == tf_embedding_strategy or embedding_strategy == tf_idf_embedding_strategy:
        similarity = dot(embedding1, embedding2)/(norm(embedding1)*norm(embedding2))

    elif  embedding_strategy == codebert_embedding_strategy:
        embedding1 = embedding1[0]
        embedding2 = embedding2[0]
        size_diff = abs(embedding1.size(0) - embedding2.size(0))
        if embedding1.size(0) > embedding2.size(0):
            embedding2 = F.pad(embedding2, (0, 0, 0, size_diff) )
        elif embedding2.size(0) > embedding1.size(0):
            embedding1 = F.pad(embedding1, (0, 0, 0, size_diff) )
        similarity = F.cosine_similarity(embedding1.reshape(-1), embedding2.reshape(-1), dim=0)
        pass

    # reshape
    # dont do zero padding
    elif embedding_strategy == codebert_summed_embedding_strategy:
        similarity = (F.cosine_similarity(embedding1, embedding2, dim=1)).item()

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