import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def predict_commit_messages(commit_messages, input_message, num_similar_messages=3):
    # Preprocessing and creating embeddings (using a basic bag-of-words approach)
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(commit_messages)
    input_vector = vectorizer.transform([input_message])

    # Print generated vectors for each commit message
    print("Generated vectors for commit messages:")
    for idx, message in enumerate(commit_messages):
        message_vector = X[idx]
        print(f"Message: {message}")
        print(f"Vector: {message_vector.toarray()}")

    # Print vector for the input message
    print("\nVector for input message:")
    print(f"Message: {input_message}")
    print(f"Vector: {input_vector.toarray()}")

    # Calculate cosine similarity
    cosine_similarities = cosine_similarity(input_vector, X).flatten()

    # Rank similar commit messages
    similar_commit_indices = np.argsort(cosine_similarities)[::-1]

    # Display top similar commit messages
    print("\nTop similar commit messages:")
    for i in range(num_similar_messages):
        index = similar_commit_indices[i]
        print(f"{commit_messages[index]} (Similarity: {cosine_similarities[index]:.2f})")


def main():
    commit_messages = [
        "Implemented user statistics page",
        "Fixed a bug in the login process",
        "Added new feature for user authentication",
        "Updated documentation for API endpoints",
        "Refactored code to improve performance"
    ]

    input_message = "Implemented user profile page"

    predict_commit_messages(commit_messages, input_message)


if __name__ == "__main__":
    main()
