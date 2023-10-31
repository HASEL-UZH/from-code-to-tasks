import csv
import datetime
import json
import os
import statistics
import string

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def generate_text_object():
    commit_data_folder_path = (
        "0_data_collection/datasets/commit_data_removed_empty_and_only_comments"
    )
    if os.path.exists(commit_data_folder_path) and os.path.isdir(
        commit_data_folder_path
    ):
        text_object = {}
        for folder_name in os.listdir(commit_data_folder_path):
            text_object[folder_name] = {}
            folder_path = os.path.join(commit_data_folder_path, folder_name)
            if os.path.isdir(folder_path):
                commit_change_object_path = os.path.join(
                    folder_path, "commit_change_object.json"
                )
                if os.path.exists(commit_change_object_path):
                    with open(commit_change_object_path, "r") as json_file:
                        commit_change_object = json.load(json_file)
                        code_change_text = commit_change_object.get("code").get("text")
                        pull_request_text = commit_change_object.get("pr").get("text")
                        text_object[folder_name]["pull request"] = pull_request_text
                        text_object[folder_name]["code change"] = code_change_text
    return text_object


def generate_tf_idf_vector(code_change_text, pull_request_text):
    # Create a TfidfVectorizer with a shared vocabulary
    vectorizer = TfidfVectorizer()

    # Fit the vectorizer on both texts to build a shared vocabulary
    vectorizer.fit([code_change_text, pull_request_text])

    # Transform text1 and text2 to TF-IDF vectors using the shared vocabulary
    tfidf_vector_code_change = vectorizer.transform([code_change_text]).toarray()[0]
    tfidf_vector_pull_request = vectorizer.transform([pull_request_text]).toarray()[0]
    return tfidf_vector_code_change, tfidf_vector_pull_request


def generate_tf_vector(code_change_text, pull_request_text):
    # Create a TfidfVectorizer with a shared vocabulary
    vectorizer = CountVectorizer()

    # Fit the vectorizer on both texts to build a shared vocabulary
    vectorizer.fit([code_change_text, pull_request_text])

    # Transform text1 and text2 to TF-IDF vectors using the shared vocabulary
    tf_vector_code_change = vectorizer.transform([code_change_text]).toarray()[0]
    tf_vector_pull_request = vectorizer.transform([pull_request_text]).toarray()[0]
    return tf_vector_code_change, tf_vector_pull_request


def generate_similarity_object(sliding_window_folder, text_object):
    similarity_array = []
    for sliding_window_subfolder in os.listdir(sliding_window_folder):
        print("current sliding window " + sliding_window_subfolder)
        sliding_window_subfolder_path = os.path.join(
            sliding_window_folder, sliding_window_subfolder
        )
        similarity_dict = {}
        try:
            for folder_code_diff in os.listdir(sliding_window_subfolder_path):
                code_change_text = text_object[folder_code_diff]["code change"]
                similarity_dict[folder_code_diff] = {}

                for folder_pull_request in os.listdir(sliding_window_subfolder_path):
                    try:
                        pull_request_text = text_object[folder_pull_request][
                            "pull request"
                        ]

                        # Call the generate_tf_vector or generate_tf_idf_vector and calculate_cosine_similarity functions
                        (
                            code_change_vector,
                            pull_request_vector,
                        ) = generate_tf_idf_vector(code_change_text, pull_request_text)
                        cosine_similarity = calculate_cosine_similarity(
                            code_change_vector, pull_request_vector
                        )
                        similarity_dict[folder_code_diff][
                            folder_pull_request
                        ] = cosine_similarity
                    except KeyError:
                        print(
                            "KeyError: Text not found in text_object for code or pull request"
                        )

        except Exception as e:
            print(f"An error occurred: {str(e)}")
        similarity_array.append(similarity_dict)
    return similarity_array


def calculate_cosine_similarity(code_change_vector, pull_request_vector):
    similarity = cosine_similarity([code_change_vector], [pull_request_vector])[0][0]
    return similarity


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
        "mean": mean_value,
        "median": median_value,
        "stdev": stdev_value,
        "min": min_value,
        "max": max_value,
    }
    return evaluation_metrics


def save_evaluation_metrics_to_csv(title, description, date, evaluation_metrics):
    header = [
        "Title",
        "Description",
        "Date",
        "Mean",
        "Median",
        "Standard Deviation",
        "Minimum",
        "Maximum",
    ]
    data = [
        [
            title,
            description,
            date,
            evaluation_metrics["mean"],
            evaluation_metrics["median"],
            evaluation_metrics["stdev"],
            evaluation_metrics["min"],
            evaluation_metrics["max"],
        ]
    ]

    if not os.path.exists("2_results"):
        os.makedirs("2_results")
    file_path = os.path.join("2_results", "results.csv")
    file_exists = os.path.exists(file_path)
    with open(file_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(header)
        writer.writerows(data)


def calculate_unique_words_overall(text_object):
    unique_words = set()  # Set to store unique words from all texts

    for key, obj in text_object.items():
        if "pull request" in obj:
            pull_request_text = obj["pull request"]

            # Tokenize text and remove punctuation
            pull_request_words = pull_request_text.lower().split()
            pull_request_words = [
                word.strip(string.punctuation) for word in pull_request_words
            ]

            # Update the unique vocabulary set
            unique_words.update(pull_request_words)

        if "code change" in obj:
            code_change_text = obj["code change"]

            # Tokenize text and remove punctuation
            code_change_words = code_change_text.lower().split()
            code_change_words = [
                word.strip(string.punctuation) for word in code_change_words
            ]

            # Update the unique vocabulary set
            unique_words.update(code_change_words)

    # Calculate the total unique word size and get the unique vocabulary
    total_unique_word_size = len(unique_words)
    return total_unique_word_size, list(unique_words)


if __name__ == "__main__":
    window_size = 20
    sliding_window_folder = (
        f"0_data_collection/datasets/commit_data_sliding_window_{window_size}"
    )
    k = 5
    title = f"ast approach preliminary tf-idf k={k} window size = {window_size}"
    description = "file names, class names, method names (added, deleted, modified)"
    date = datetime.datetime.now().strftime("%d.%m.%y (%H:%M:%S)")

    text_object = generate_text_object()
    total_unique_word_size, unique_words = calculate_unique_words_overall(text_object)
    similarity_object = generate_similarity_object(sliding_window_folder, text_object)

    evaluation_metrics = calculate_evaluation_metrics(k, similarity_object)
    save_evaluation_metrics_to_csv(title, description, date, evaluation_metrics)
