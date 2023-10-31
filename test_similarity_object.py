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


def get_top_k_keys(data, k):
    # Sort the data by the first item of the tuple in descending order
    sorted_data = sorted(data.items(), key=lambda x: x[1][0], reverse=True)

    # Find the value of the k-th largest item
    kth_largest_value = sorted_data[k - 1][1][0]

    # Create a list of keys where the first item in the tuple is greater than or equal to the kth largest value
    top_k_keys = [k for k, v in data.items() if v[0] >= kth_largest_value]

    grouped_data = {}

    for key, value in data.items():
        if value not in grouped_data:
            grouped_data[value] = []
        grouped_data[value].append(key)

    # Convert the tuple keys to their first element
    grouped_data = {k[0]: v for k, v in grouped_data.items()}

    return top_k_keys


if __name__ == "__main__":
    # Example usage:
    data = {"folder_1": (0.85, "a"), "folder_2": (0.85, "a"), "folder_3": (0.8, "b")}
    k = 1

    get_top_k_keys(data, k)

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
    # evaluation_metrics = calculate_evaluation_metrics(1, similarity_dict)
    # print(evaluation_metrics)
