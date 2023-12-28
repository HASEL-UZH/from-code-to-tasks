from results.visualizations.plots.fancy_scatter_plot_mean import FancyScatterPlotMean
from results.visualizations.plots.grouped_bar_plot_mean import GroupedBarPlotMean
from results.visualizations.plots.plot_utils import get_identifiers
from results.visualizations.plots.scatter_plot_mean_std import ScatterPlotMeanStd
from results.visualizations.plots.subgrouped_bar_plot_mean import SubGroupedBarPlotMean

CODE_DIFFERENCES = "Code Differences"


def scatter_plot_mean_and_std_diff_k_1_w_10_per_repo():
    title = CODE_DIFFERENCES
    plot_name = "scatter-plot-diff-mean-std-k-1-w-10.svg"
    filter_criteria = {
        "term_strategy": "diff_text",
        "k": 1,
        "window_size": 10,
    }
    group_criteria = {
        "repository_identifier": get_identifiers(),
    }
    colors = ["#FF1493", "#9370DB"]
    scatter_plot = ScatterPlotMeanStd(
        title, plot_name, filter_criteria, group_criteria, colors=colors
    )
    scatter_plot.plot()


def grouped_bar_plot_mean_diff_text_by_k_per_repo():
    title = CODE_DIFFERENCES + "\n Mean Accuracy By K per Repository"
    plot_name = "grouped-bar-plot-diff-text-by-k-per-repo"
    filter_criteria = {
        "term_strategy": "diff_text",
        "window_size": 10,
    }
    group_criteria = {
        "k": [1, 3, 5],
        "repository_identifier": get_identifiers(),
    }
    colors = [
        "#FF5733",
        "#33FF57",
        "#5733FF",
    ]
    x_axis_criteria = "repository_identifier"
    legend_criteria = "k"
    grouped_bar_plot_mean = GroupedBarPlotMean(
        title,
        plot_name,
        filter_criteria,
        group_criteria,
        x_axis_criteria,
        legend_criteria,
        colors,
    )
    grouped_bar_plot_mean.plot()


def grouped_bar_plot_mean_diff_text_by_w_per_repo():
    title = CODE_DIFFERENCES + "\n Mean Accuracy By Window Size per Repository"
    plot_name = "grouped-bar-plot-diff-text-by-w-per-repo"
    filter_criteria = {
        "term_strategy": "diff_text",
        "k": 1,
    }
    group_criteria = {
        "window_size": [10, 20, 50],
        "repository_identifier": get_identifiers(),
    }
    colors = [
        "#FF5733",
        "#33FF57",
        "#5733FF",
    ]
    x_axis_criteria = "repository_identifier"
    legend_criteria = "window_size"
    grouped_bar_plot_mean = GroupedBarPlotMean(
        title,
        plot_name,
        filter_criteria,
        group_criteria,
        x_axis_criteria,
        legend_criteria,
        colors,
    )
    grouped_bar_plot_mean.plot()


def subgrouped_bar_plot_mean_diff_text_by_k_per_repo():
    title = (
        CODE_DIFFERENCES + "\n Mean Accuracy By K per Repository Split by Vectorization"
    )
    plot_name = "grouped-bar-plot-diff-text-by-w-per-repo"
    filter_criteria = {
        "term_strategy": "diff_text",
        "window_size": 10,
    }
    group_criteria = {
        "k": [1, 3, 5],
        "repository_identifier": get_identifiers(),
    }
    subgroup_criteria = {"embeddings_concept": ["tf", "tf_idf"]}
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
    x_axis_criteria = "repository_identifier"
    legend_criteria = "window_size"
    grouped_bar_plot_mean = SubGroupedBarPlotMean(
        title,
        plot_name,
        filter_criteria,
        group_criteria,
        x_axis_criteria,
        legend_criteria,
        colors,
        subgroup_criteria,
        3,
        2,
        "K",
        "V",
    )
    grouped_bar_plot_mean.plot()


def subgrouped_bar_plot_mean_diff_text_by_w_per_repo():
    title = (
        CODE_DIFFERENCES
        + "\n Mean Accuracy By Window Size per Repository Split by Vectorization"
    )
    plot_name = "grouped-bar-plot-diff-text-by-w-per-repo"
    filter_criteria = {
        "term_strategy": "diff_text",
        "k": 1,
    }
    group_criteria = {
        "window_size": [10, 20, 50],
        "repository_identifier": get_identifiers(),
    }
    subgroup_criteria = {"embeddings_concept": ["tf", "tf_idf"]}
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
    x_axis_criteria = "repository_identifier"
    legend_criteria = "window_size"
    grouped_bar_plot_mean = SubGroupedBarPlotMean(
        title,
        plot_name,
        filter_criteria,
        group_criteria,
        x_axis_criteria,
        legend_criteria,
        colors,
        subgroup_criteria,
        3,
        2,
        "W",
        "V",
    )
    grouped_bar_plot_mean.plot()


def fancy_scatter_plot_mean_diff_text_by_w_per_repo():
    title = (
        CODE_DIFFERENCES
        + "\n Mean Accuracy By Window Size per Repository Split by Vectorization"
    )
    plot_name = "fancy-scatter-plot-diff-text-by-w-per-repo"
    filter_criteria = {
        "term_strategy": "diff_text",
        "k": 1,
    }
    group_criteria = {
        "window_size": [10, 20, 50],
        "repository_identifier": get_identifiers(),
    }
    subgroup_criteria = {"embeddings_concept": ["tf", "tf_idf"]}
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
    x_axis_criteria = "repository_identifier"
    legend_criteria = "window_size"
    fancy_scatter_plot_mean = FancyScatterPlotMean(
        title,
        plot_name,
        filter_criteria,
        group_criteria,
        x_axis_criteria,
        legend_criteria,
        colors,
        subgroup_criteria,
        3,
        2,
        "W",
        "V",
    )
    fancy_scatter_plot_mean.plot()


if __name__ == "__main__":
    scatter_plot_mean_and_std_diff_k_1_w_10_per_repo()
