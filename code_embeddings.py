from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

def create_code_embeddings_added_deleted(codebert_model, added_code, deleted_code):
    # Initialize the tokenizer
    tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")

    # Tokenize the added and deleted code
    added_tokens = tokenizer(added_code)['input_ids']
    deleted_tokens = tokenizer(deleted_code)['input_ids']

    # Define the separator token ID (you need to obtain the correct ID from the tokenizer)
    separator_token_id = tokenizer.convert_tokens_to_ids('<SEP>')  # Replace '<SEP>' with the correct separator token

    # Concatenate added and deleted tokens with separator token in between
    concatenated_tokens = added_tokens + [separator_token_id] + deleted_tokens

    # Obtain code embeddings
    code_embeddings = codebert_model(torch.tensor(concatenated_tokens)[None, :])[0]

    return code_embeddings

def create_task_description_embeddings (codebert_model, task_description):
    # Initialize the tokenizer
    tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")

    task_description_tokens = tokenizer(task_description)['input_ids']

    # Concatenate added and deleted tokens with separator token in between
    concatenated_tokens = task_description_tokens

    # Obtain code embeddings
    task_description_embeddings = codebert_model(torch.tensor(concatenated_tokens)[None, :])[0]

    return task_description_embeddings

def calculate_cosine_similarity(code_embedding, task_description_embedding):

    size_code_embedding = code_embedding.size()
    size_task_description_embedding = task_description_embedding.size()

    # truncate if necessary
    if size_code_embedding.numel() < size_task_description_embedding.numel():
        task_description_embedding = task_description_embedding[:, :size_code_embedding[1], :]

    elif size_code_embedding.numel() > size_task_description_embedding.numel():
        code_embedding = code_embedding[:, :size_task_description_embedding[1], :]

    # calculate cosine similarity
    code_embedding_np = code_embedding.detach().numpy().reshape(1, -1)
    task_description_embedding_np = task_description_embedding.detach().numpy().reshape(1, -1)

    similarity = cosine_similarity(code_embedding_np, task_description_embedding_np)
    similarity_value = similarity[0, 0]
    return similarity_value


def main():
    model = AutoModel.from_pretrained("microsoft/codebert-base")

    # TODO replace
    added_code = 'ess.broadcastMessage("essentials.banip.notify", tl("playerBanIpAddress", senderName, ipAddress, banReason));'
    deleted_code = 'ess.broadcastMessage("essentials.ban.notify", tl("playerBanIpAddress", senderName, ipAddress, banReason));'
    task_description_correct = "Silent ban messages?"
    task_description_incorrect = "Reduce permission check calls in PlayerCommandSendEvent"

    code_embedding = create_code_embeddings_added_deleted(model, added_code, deleted_code)
    task_description_embedding_correct = create_task_description_embeddings(model, task_description_correct)
    task_description_embedding_incorrect = create_task_description_embeddings(model, task_description_incorrect)
    cosine_similarity_correct = calculate_cosine_similarity(code_embedding, task_description_embedding_correct)
    cosine_similarity_incorrect = calculate_cosine_similarity(code_embedding, task_description_embedding_incorrect)
    print("Cosine similarity correct:", cosine_similarity_correct)
    print("Cosine similarity incorrect:", cosine_similarity_incorrect)

if __name__ == "__main__":
    main()


