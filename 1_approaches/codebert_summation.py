import csv
import datetime
import json
import statistics
import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer
from sklearn.metrics.pairwise import cosine_similarity
import os

model = AutoModel.from_pretrained("microsoft/codebert-base")
tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")

def generate_embeddings():
    embeddings_object = {"code_emb": {}, "pr_emb": {}}
    commit_data_folder_path = "../0_data_collection/datasets/commit_data_removed_empty_and_only_comments"
    if os.path.exists(commit_data_folder_path) and os.path.isdir(commit_data_folder_path):
        for folder_name in os.listdir(commit_data_folder_path):
            folder_path = os.path.join(commit_data_folder_path, folder_name)
            if os.path.isdir(folder_path):
                commit_info_path = os.path.join(folder_path, "commit_info.json")
                if os.path.exists(commit_info_path):
                    with open(commit_info_path, "r") as json_file:
                        commit_info_data = json.load(json_file)
                        pull_request_value = commit_info_data.get("pull request")
                        pull_request_embedding = generate_pull_request_embedding(pull_request_value).detach().numpy()
                        # Save the pull_request_embedding as an npy file in the same folder
                        pull_request_npy_file_path = os.path.join(folder_path, "pull_request_summation_embedding.npy")
                        np.save(pull_request_npy_file_path, pull_request_embedding)
                        embeddings_object["pr_emb"][folder_name] = pull_request_npy_file_path  # Store the npy file path
                        # Get code diff embedding
                        diff_file_paths = []
                        for file in os.listdir(folder_path):
                            if file.endswith(".diff"):
                                diff_file_path = os.path.join(folder_path, file)
                                diff_file_paths.append(diff_file_path)
                        added_code, deleted_code = split_code_diff(diff_file_paths)
                        code_embedding = generate_code_diff_embedding(added_code, deleted_code).detach().numpy()
                        # Save the code_embedding as an npy file in the same folder
                        code_npy_file_path = os.path.join(folder_path, "code_summation_embedding.npy")
                        np.save(code_npy_file_path, code_embedding)
                        embeddings_object["code_emb"][folder_name] = code_npy_file_path  # Store the npy file path
    print(embeddings_object)
    return embeddings_object

def generate_similarity_object():
    similarity_array = []
    commit_data_folder = "../0_data_collection/datasets/commit_data_removed_empty_and_only_comments"
    sliding_window_folder = "../0_data_collection/datasets/commit_data_sliding_window"
    for sliding_window_subfolder in os.listdir(sliding_window_folder):
        sliding_window_subfolder_path = os.path.join(sliding_window_folder, sliding_window_subfolder)
        similarity_dict = {}
        for folder_code_diff in os.listdir(sliding_window_subfolder_path):
            folder_path_code_diff = os.path.join(commit_data_folder, folder_code_diff)
            code_embedding_file = os.path.join(folder_path_code_diff, "code_summation_embedding.npy")
            if os.path.exists(code_embedding_file):
                code_embedding = np.load(code_embedding_file)
            similarity_dict[folder_code_diff] = {}
            for folder_pull_request in os.listdir(sliding_window_subfolder_path):
                folder_path_pull_request = os.path.join(commit_data_folder, folder_pull_request)
                pull_request_embedding_file = os.path.join(folder_path_pull_request, "pull_request_summation_embedding.npy")
                if os.path.exists(pull_request_embedding_file):
                    pull_request_embedding = np.load(pull_request_embedding_file)
                cosine_similarity = calculate_cosine_similarity(code_embedding, pull_request_embedding)
                similarity_dict[folder_code_diff][folder_pull_request]= cosine_similarity
        similarity_array.append(similarity_dict)
    return similarity_array

def generate_pull_request_embedding(pull_request):
    # Tokenize the task descriptions
    task_description_tokens = tokenizer.tokenize(pull_request)
   # Adding CLS token, SEP token and EOS token
    tokens = [tokenizer.cls_token]+task_description_tokens+[tokenizer.eos_token]
    #Convert tokens to IDs
    tokens_ids = tokenizer.convert_tokens_to_ids(tokens[1:])
   # Create embeddings
    task_description_embeddings=model(torch.tensor(tokens_ids)[None,:])[0]
    summed_embeddings = torch.sum(task_description_embeddings, dim=1)
    return summed_embeddings

def generate_code_diff_embedding(added_code, deleted_code, max_seq_length=512):
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
    code_embedding_np = code_embedding.reshape(1, -1)
    task_description_embedding_np = task_description_embedding.reshape(1, -1)
    similarity = cosine_similarity(code_embedding_np, task_description_embedding_np)
    similarity_value = similarity[0, 0]
    return similarity_value

def calculate_evaluation_metrics(k, similarity_objects):
    top_k_accuracies = []
    for sample_object in similarity_objects:
        total_embeddings = 0
        correct_predictions = 0
        # Iterate through each key in the sample_object
        for key in sample_object:
            # Get the top k highest scores
            highest_scores = sorted(sample_object[key].values(), reverse=True)[:k]
            same = sample_object[key][key]
            # Check if the correct prediction is among the top k highest scores
            if same in highest_scores:
                correct_predictions += 1
            total_embeddings += 1
        # Calculate top-k accuracy and append to the top_k_accuracies list
        top_k_accuracy = correct_predictions / total_embeddings
        top_k_accuracies.append(top_k_accuracy)
    mean_value = statistics.mean(top_k_accuracies)
    median_value = statistics.median(top_k_accuracies)
    stdev_value = statistics.stdev(top_k_accuracies)
    min_value = min(top_k_accuracies)
    max_value = max(top_k_accuracies)
    evaluation_metrics = {
        'mean': mean_value,
        'median': median_value,
        'stdev': stdev_value,
        'min': min_value,
        'max': max_value
    }
    return evaluation_metrics

def save_evaluation_metrics_to_csv(title, description, date, evaluation_metrics):
    header = ['Title', 'Description', 'Date','Mean', 'Median', 'Standard Deviation', 'Minimum', 'Maximum']
    data = [[title, description, date, evaluation_metrics['mean'], evaluation_metrics['median'],evaluation_metrics['stdev'], evaluation_metrics['min'], evaluation_metrics['max']]]
    # Check if the '2_results' folder exists, create it if not
    if not os.path.exists('../2_results'):
        os.makedirs('../2_results')
    # Define the file path for the 'results.csv' file in '2_results' folder
    file_path = os.path.join('../2_results', 'results.csv')
    # Check if the file exists, if not create it and write the header
    file_exists = os.path.exists(file_path)
    with open(file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(header)  # Write the header if the file is created
        # Write the data row
        writer.writerows(data)

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


if __name__=="__main__":
    title = 'codebert summation k=5'
    description = 'embeddings of all tokens are summed using torch.sum'
    date = datetime.datetime.now().strftime('%d.%m.%y (%H:%M:%S)')
    #embeddings_object = generate_embeddings()
    similarity_objects = generate_similarity_object()
    k = 5
    evaluation_metrics = calculate_evaluation_metrics(k, similarity_objects)
    save_evaluation_metrics_to_csv(title, description, date, evaluation_metrics)
