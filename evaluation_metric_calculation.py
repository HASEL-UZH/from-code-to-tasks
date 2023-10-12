def calculate_accuracy(sample_object):
    total_embeddings = 0
    correct_predictions = 0

    for key in sample_object:
        highest_score = max(sample_object[key].values())
        if sample_object[key][key] == highest_score:
            correct_predictions += 1

        total_embeddings += 1

    accuracy = correct_predictions / total_embeddings
    return accuracy


def calculate_precision(sample_object):
    true_positives = 0
    false_positives = 0

    for key in sample_object:
        highest_score = max(sample_object[key].values())
        if sample_object[key][key] == highest_score:
            true_positives += 1
        else:
            false_positives += 1

    precision = true_positives / (true_positives + false_positives)
    return precision

def calculate_recall(sample_object):
    total_embeddings = len(sample_object)
    correct_predictions = 0

    for key in sample_object:
        highest_score = max(sample_object[key].values())
        if sample_object[key][key] == highest_score:
            correct_predictions += 1

    # Check for division by zero
    if total_embeddings == 0:
        return 0

    recall = correct_predictions / total_embeddings
    return recall

def calculate_f1_score(sample_object):
    precision = calculate_precision(sample_object)
    recall = calculate_recall(sample_object)

    # Check for division by zero
    if precision + recall == 0:
        return 0

    f1_score = 2 * (precision * recall) / (precision + recall)
    return f1_score

if __name__ == "__main__":
    sample_object = {
        "embedding_0" : {
            "embedding_0": 0.8,
            "embedding_1" : 0.7,
            "embedding_2": 0.6
        },
        "embedding_1": {
            "embedding_0": 0.8,
            "embedding_1": 0.7,
            "embedding_2": 0.6
        },
        "embedding_2": {
            "embedding_0": 0.8,
            "embedding_1": 0.7,
            "embedding_2": 0.9
        }
    }

    accuracy = calculate_accuracy(sample_object)
    print("accuracy " + str(accuracy))

    precision = calculate_precision(sample_object)
    print("precision " + str(precision))

    recall = calculate_recall(sample_object)
    print("recall " + str(recall))

    f1 = calculate_f1_score(sample_object)
    print("f1 " + str(f1))