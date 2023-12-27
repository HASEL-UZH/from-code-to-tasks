import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from results.scatter_plot_mean_std import ScatterPlotMeanStd
from src.core.logger import log

plt.rcParams["font.family"] = "Helvetica"


def get_data(k, w, term_strategy):
    combined_data = pd.DataFrame()
    current_directory = os.getcwd()
    csv_files = [
        file for file in os.listdir(current_directory) if file.endswith(".csv")
    ]
    for csv_file in csv_files:
        file_path = os.path.join(os.getcwd(), csv_file)
        df = pd.read_csv(file_path)
        filtered_data = df[
            (df["k"] == k)
            & (df["window_size"] == w)
            & (df["term_strategy"] == term_strategy)
        ]
        combined_data = combined_data._append(filtered_data, ignore_index=True)
    return combined_data


def get_formatted_identifier(identifier):
    format = {
        "iluwatar__java-design-patterns": "java-design-patterns",
        "reactive_x___rx_java": "RxJava",
        "eugenp__tutorials": "tutorials",
        "airbnb__lottie-android": "lottie-android",
        "bumptech__glide": "glide",
        "apolloconfig__apollo": "apollo",
        "selenium_hq__selenium": "selenium",
        "alibaba__nacos": "nacos",
    }
    return format[identifier]


def scatter_plot_mean_and_std_diff_k_1_w_10():
    title = "Code Differences"
    plot_name = "scatter-plot-diff-mean-std-k-1-w-10.svg"
    term_strategy = "diff_text"
    colors = ["#FF1493", "#9370DB"]
    scatter_plot = ScatterPlotMeanStd(title, plot_name, term_strategy, colors=colors)
    scatter_plot.plot()


def plot_mean_diff_k_1_3_5(k_colors=None):
    k_values = [5, 3, 1]
    window_size = 10
    term_strategy = "diff_text"

    data_by_k = {k: get_data(k, window_size, term_strategy) for k in k_values}
    combined_data = pd.concat(
        [pd.DataFrame(data).assign(k=k) for k, data in data_by_k.items()]
    )
    formatted_identifiers = combined_data["repository_identifier"].map(
        get_formatted_identifier
    )
    grouped_data = (
        combined_data.groupby([formatted_identifiers, "k"])["mean"].mean().unstack()
    )

    default_colors = ["#FF5733", "#33FF57", "#5733FF"]
    color_mapping = dict(zip(k_values, k_colors or default_colors))

    plt.figure(figsize=(12, 8))
    width = 0.2
    for i, k in enumerate(k_values):
        color = color_mapping.get(k, "#CCCCCC")
        positions = np.arange(len(grouped_data.index)) + width * (i - 1)
        plt.bar(
            x=positions,
            height=grouped_data[k].values,
            width=width,
            color=color,
            label=f"K={k}",
        )

    plt.xlabel("Repository")
    plt.ylabel("Mean")
    plt.title("Code Differences\nMean per Repository for K=1, K=3, K=5 and W=10")
    plt.xticks(np.arange(len(grouped_data.index)), grouped_data.index)
    plt.legend(title="Top-K")
    plt.savefig("plot-diff-mean-k-1-3-5-w-10-grouped.svg", format="svg")

    plt.show()

    for k in k_values:
        means_for_k = grouped_data[k].dropna().values
        mean_k = np.mean(means_for_k)
        std_k = np.std(means_for_k)
        var_k = np.var(means_for_k)
        log.info(
            f"Approach: k={k}, window_size=10, term_strategy=diff, Mean: {mean_k:.2f}, Std: {std_k:.2f}, Var: {var_k:.2f}"
        )


def plot_mean_diff_w_10_20_50(w_colors=None):
    k = 1
    w_values = [10, 20, 50]
    term_strategy = "diff_text"

    data_by_w = {w: get_data(k, w, term_strategy) for w in w_values}
    combined_data = pd.concat(
        [pd.DataFrame(data).assign(w=w) for w, data in data_by_w.items()]
    )
    formatted_identifiers = combined_data["repository_identifier"].map(
        get_formatted_identifier
    )
    grouped_data = (
        combined_data.groupby([formatted_identifiers, "window_size"])["mean"]
        .mean()
        .unstack()
    )

    default_colors = ["#FF5733", "#33FF57", "#5733FF"]
    color_mapping = dict(zip(w_values, w_colors or default_colors))

    plt.figure(figsize=(12, 8))
    width = 0.2
    for i, w in enumerate(w_values):
        color = color_mapping.get(w, "#CCCCCC")
        positions = np.arange(len(grouped_data.index)) + width * (i - 1)
        plt.bar(
            x=positions,
            height=grouped_data[w].values,
            width=width,
            color=color,
            label=f"W={w}",
        )

    plt.xlabel("Repository")
    plt.ylabel("Mean")
    plt.title("Code Differences\nMean per Repository for W=10, W=20, W=50 and K=1")
    plt.xticks(np.arange(len(grouped_data.index)), grouped_data.index)
    plt.legend(title="Window Size")
    plt.savefig("plot-diff-mean-k-1-w-10-20-50.svg", format="svg")

    plt.show()

    for w in w_values:
        means_for_w = grouped_data[w].dropna().values
        mean_w = np.mean(means_for_w)
        std_w = np.std(means_for_w)
        var_w = np.var(means_for_w)
        log.info(
            f"Approach: k={k}, window_size={w}, term_strategy=diff, "
            f"Mean: {mean_w:.2f}, Std: {std_w:.2f}, Var: {var_w:.2f}"
        )


if __name__ == "__main__":
    # plot_mean_diff_k_1_3_5()
    # plot_mean_and_std_diff_k_1_w_10()
    # plot_mean_diff_w_10_20_50()
    scatter_plot_mean_and_std_diff_k_1_w_10()
