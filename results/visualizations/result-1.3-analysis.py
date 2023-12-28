import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from results.visualizations.plots.plot_utils import get_formatted_identifier
from src.core.logger import log

plt.rcParams["font.family"] = "Helvetica"


def get_data(k, w, term_strategy, meta_strategy):
    combined_data = pd.DataFrame()
    current_directory = os.getcwd()
    csv_files = [
        file for file in os.listdir(current_directory) if file.endswith(".csv")
    ]
    for csv_file in csv_files:
        file_path = os.path.join(os.getcwd(), csv_file)
        df = pd.read_csv(file_path)

        if meta_strategy is None:
            filtered_data = df[
                (df["k"] == k)
                & (df["window_size"] == w)
                & (df["term_strategy"] == term_strategy)
                # Questionable
                # & (df["embeddings_concept"] == "tf_idf")
                # & (df["embeddings_strategy"] == "tf-idf-embedding--subword-tokenizer")
            ]
        else:
            # Use meta_strategy condition
            filtered_data = df[
                (df["k"] == k)
                & (df["window_size"] == w)
                & (df["term_strategy"] == term_strategy)
                & (df["meta_strategy"] == meta_strategy)
                # Questionable
                # & (df["embeddings_concept"] == "tf_idf")
                # & (df["embeddings_strategy"] == "tf-idf-embedding--subword-tokenizer")
            ]
        combined_data = combined_data._append(filtered_data, ignore_index=True)
    return combined_data


def get_formatted_strategy(strategy):
    format = {
        "diff_text": "Code Differences",
        "meta_ast_text": "Source Code Files",
        "diff_text/meta_ast_text": "Combined",
    }
    return format[strategy]


def plot_mean_by_strategy():
    k = 1
    window_size = 10
    strategies = [
        ("diff_text", None),
        ("meta_ast_text", "ast-lg"),
        ("diff_text/meta_ast_text", "None/ast-lg"),
    ]
    data_by_strategy = {
        get_formatted_strategy(strategy[0]): get_data(
            k, window_size, strategy[0], strategy[1]
        )
        for strategy in strategies
    }

    combined_data = pd.concat(
        [
            pd.DataFrame(data).assign(strategy=strategy)
            for strategy, data in data_by_strategy.items()
        ]
    )
    formatted_identifiers = combined_data["repository_identifier"].map(
        get_formatted_identifier
    )
    grouped_data = (
        combined_data.groupby([(formatted_identifiers), "strategy"])["mean"]
        .mean()
        .reset_index()
    )
    data = grouped_data.values

    means_for_diff = data[data[:, 1].astype(str) == "Code Differences", 2].astype(float)
    means_for_src = data[data[:, 1].astype(str) == "Source Code Files", 2].astype(float)
    means_for_combined = data[data[:, 1].astype(str) == "Combined", 2].astype(float)

    plt.figure(figsize=(12, 8))
    sns.barplot(
        x="repository_identifier",
        y="mean",
        hue="strategy",
        data=grouped_data,
        palette="Set3",  # You can choose a different color palette
    )

    plt.xlabel("Repository")
    plt.ylabel("Mean")
    plt.title("Mean per Repository for Different Strategies")
    plt.legend(title="Strategy")
    plt.savefig("plot-mean-by-strategy.svg", format="svg")

    plt.show()
    mean_diff = np.mean(means_for_diff)
    mean_src = np.mean(means_for_src)
    mean_combined = np.mean(means_for_combined)
    std_diff = np.std(means_for_diff)
    std_src = np.std(means_for_src)
    std_combined = np.std(means_for_combined)
    var_diff = np.var(means_for_diff)
    var_src = np.var(means_for_src)
    var_combined = np.var(means_for_combined)
    log.info(
        f"Approach: k=1, window_size=10, strategy=diff, Mean: {mean_diff:.2f}, Std: {std_diff:.2f}, Var: {var_diff:.2f}"
    )
    log.info(
        f"Approach: k=1, window_size=10, strategy=src, Mean: {mean_src:.2f}, Std: {std_src:.2f}, Var: {var_src:.2f}"
    )
    log.info(
        f"Approach: k=1, window_size=10, strategy=combined, Mean: {mean_combined:.2f}, Std: {std_combined:.2f}, Var: {var_combined:.2f}"
    )


if __name__ == "__main__":
    plot_mean_by_strategy()
