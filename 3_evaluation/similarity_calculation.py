import os
import json
import time

from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

def similarity_calculation(model, tokenizer):
    similarity_array = []
    current_dir = os.getcwd()
    sliding_window_folder = "0_data_collection/commit_data_sliding_window"

    for sliding_window_subfolder in os.listdir(sliding_window_folder):
        sliding_window_subfolder_path = os.path.join(sliding_window_folder, sliding_window_subfolder)
        task_description_embeddings = {}
        for folder_pull_request in os.listdir(sliding_window_subfolder_path):
            folder_path_pull_request = os.path.join(sliding_window_subfolder_path, folder_pull_request)
            # Get PR embedding
            commit_info_path = os.path.join(folder_path_pull_request, "commit_info.json")
            if os.path.exists(commit_info_path):
                with open(commit_info_path, 'r') as commit_info_file:
                    commit_info_data = json.load(commit_info_file)
                    pull_request_value = commit_info_data.get("pull request")
                    if pull_request_value:
                        pull_request_embedding = generate_pull_request_embedding(model, tokenizer, pull_request_value)
                        task_description_embeddings[folder_pull_request] = pull_request_embedding
            time.sleep(0.3)
        similarity_dict = {}
        for folder_code_diff in os.listdir(sliding_window_subfolder_path):
            folder_path_code_diff = os.path.join(sliding_window_subfolder_path, folder_code_diff)
            if os.path.isdir(folder_path_code_diff):
                print("Folder:", folder_code_diff)
                # Get code diff embedding
                diff_file_paths = []
                for file in os.listdir(folder_path_code_diff):
                    if file.endswith(".diff"):
                        diff_file_path = os.path.join(folder_path_code_diff, file)
                        diff_file_paths.append(diff_file_path)
                added_code, deleted_code = split_code_diff(diff_file_paths)
                code_diff_embedding = generate_code_diff_embedding(model, tokenizer, added_code, deleted_code)
                similarity_dict[folder_code_diff] = {}

                for key, value in task_description_embeddings.items():
                    cosine_similarity = calculate_cosine_similarity(code_diff_embedding, value)
                    similarity_dict[folder_code_diff][key] = cosine_similarity
        similarity_array.append(similarity_dict)
    return similarity_array

def generate_pull_request_embedding(model, tokenizer, pull_request):

    # Tokenize the task descriptions
    task_description_tokens = tokenizer.tokenize(pull_request, truncation=True)
    # Adding CLS token, SEP token and EOS token
    tokens = [tokenizer.cls_token] + task_description_tokens + [tokenizer.eos_token]
    tokens_ids = tokenizer.convert_tokens_to_ids(tokens[1:])
    # Create embeddings
    task_description_embeddings = model(torch.tensor(tokens_ids)[None, :])[0]
    summed_embeddings = torch.sum(task_description_embeddings, dim=1)
    return summed_embeddings

def split_code_diff(diff_files):
    added_lines = ""
    deleted_lines = ""
    for diff_file in diff_files:
        with open(diff_file, 'r') as f:
            for line in f:
                if line.startswith('+'):
                    added_lines += line[1:].strip() + '\n'
                elif line.startswith('-'):
                    deleted_lines += line[1:].strip() + '\n'
    return added_lines, deleted_lines

def generate_code_diff_embedding(model, tokenizer, added_code, deleted_code, max_seq_length=512):
    added_tokens = tokenizer.tokenize(added_code, truncation=True)
    deleted_tokens = tokenizer.tokenize(deleted_code, truncation=True)

    # Truncate tokens if the total length exceeds the maximum sequence length
    total_tokens = len(added_tokens) + len(deleted_tokens) + 3  # 3 for [CLS], [SEP], [EOS]
    if total_tokens > max_seq_length:
        # Calculate how many tokens to keep for each part (added, deleted)
        keep_added_tokens = int((max_seq_length - 3) / 2)
        keep_deleted_tokens = max_seq_length - 3 - keep_added_tokens

        # Truncate tokens accordingly
        added_tokens = added_tokens[:keep_added_tokens]
        deleted_tokens = deleted_tokens[:keep_deleted_tokens]
    # Adding CLS token, SEP token and EOS token
    tokens = [tokenizer.cls_token] + added_tokens + [tokenizer.sep_token] + deleted_tokens + [tokenizer.eos_token]
    # Convert tokens to IDs
    tokens_ids = tokenizer.convert_tokens_to_ids(tokens[1:])
    # Create embeddings
    code_embeddings = model(torch.tensor(tokens_ids)[None, :])[0]
    summed_embeddings = torch.sum(code_embeddings, dim=1)
    return summed_embeddings
def calculate_cosine_similarity(code_embedding, task_description_embedding):
    code_embedding_np = code_embedding.detach().numpy().reshape(1, -1)
    task_description_embedding_np = task_description_embedding.detach().numpy().reshape(1, -1)
    similarity = cosine_similarity(code_embedding_np, task_description_embedding_np)
    similarity_value = similarity[0, 0]
    return similarity_value


if __name__ == '__main__':
    model = AutoModel.from_pretrained("microsoft/codebert-base")
    tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
    similarity_dict = similarity_calculation(model, tokenizer)
    print(similarity_dict)