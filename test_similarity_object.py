import statistics


def calculate_evaluation_metrics(k, similarity_objects):
    top_k_accuracies = []
    for sample_object in similarity_objects:
        total_embeddings = 0
        correct_predictions = 0

        # Iterate through each key in the sample_object
        for key in sample_object:
            from collections import defaultdict

            highest_scores = sorted(
                sample_object[key].items(), key=lambda x: x[1][0], reverse=True
            )

            # Create a dictionary to store keys with their corresponding scores
            key_scores = defaultdict(list)
            for k, v in highest_scores:
                key_scores[v[0]].append(k)

            # Determine the keys with the k highest scores (including multiple if scores are the same)
            k_highest_score_keys = [
                k for score, keys in key_scores.items() for k in keys
            ][:k]

            if key in k_highest_score_keys:
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


def get_top_k_folders(data, k):
    grouped_data = {}
    for folder, value in data.items():
        if value not in grouped_data:
            grouped_data[value] = [folder]
        else:
            grouped_data[value].append(folder)
    result_dict = {}
    for key, folders in grouped_data.items():
        number, folder = key
        if number not in result_dict:
            result_dict[number] = []
        result_dict[number].extend(folders)
    top_k_keys = list(result_dict.keys())[:k]
    result_folders = []
    for key, folders in result_dict.items():
        if key in top_k_keys:
            for folder in folders:
                result_folders.append(folder)
    return result_folders


if __name__ == "__main__":
    # Example usage:
    data = {
        "folder_1": (0.85, "a"),
        "folder_2": (0.85, "a"),
        "folder_3": (0.85, "b"),
        "folder_4": (0.6, "c"),
    }
    k = 1

    x = get_top_k_folders(data, k)

    similarity_dict = [
        {
            "folder_1": {
                "folder_1": (0.85, "a"),
                "folder_2": (0.85, "a"),
                "folder_3": (0.80, "b"),
            },
            "folder_2": {
                "folder_1": (0.8, "b"),
                "folder_2": (0.7, "a"),
                "folder_3": (0.6, "c"),
            },
            "folder_code_diff_3": {
                "folder_1": (0.8, "f"),
                "folder_2": (0.8, "e"),
                "folder_3": (0.8, "d"),
            },
        },
        {
            "folder_1": {
                "folder_1": (0.85, "a"),
                "folder_2": (0.85, "a"),
                "folder_3": (0.80, "b"),
            },
            "folder_2": {
                "folder_1": (0.8, "b"),
                "folder_2": (0.7, "a"),
                "folder_3": (0.6, "c"),
            },
            "folder_3": {
                "folder_1": (0.8, "f"),
                "folder_2": (0.8, "e"),
                "folder_3": (0.7, "d"),
            },
        },
    ]
    evaluation_metrics = calculate_evaluation_metrics(1, similarity_dict)
    print(evaluation_metrics)
