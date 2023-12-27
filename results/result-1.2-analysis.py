from results.grouped_bar_plot_mean import GroupedBarPlotMean
from results.plot_utils import get_identifiers
from results.scatter_plot_mean_std import ScatterPlotMeanStd


def scatter_plot_mean_and_std_src_text_k_1_w_10():
    title = "Source Code Files - Textual Representation"
    plot_name = "scatter-plot-src-text-mean-std-k-1-w-10.svg"
    term_strategy = "meta_ast_text"
    meta_strategy = "ast-lg"
    colors = ["#FF1493", "#9370DB"]
    scatter_plot = ScatterPlotMeanStd(
        title, plot_name, term_strategy, meta_strategy, colors
    )
    scatter_plot.plot()


def scatter_plot_mean_and_std_src_code_k_1_w_10():
    title = "Source Code Files - Code Representation"
    plot_name = "scatter-plot-src-code-mean-std-k-1-w-10.svg"
    term_strategy = "meta_ast_code"
    meta_strategy = "ast-lg"
    colors = ["#FF1493", "#9370DB"]
    scatter_plot_mean_std = ScatterPlotMeanStd(
        title, plot_name, term_strategy, meta_strategy, colors
    )
    scatter_plot_mean_std.plot()


def grouped_bar_plot_mean_src_text_by_k_per_repo():
    title = (
        "Code Differences - Textual Representation \n Mean Accuracy By K per Repository"
    )
    plot_name = "grouped-bar-plot-src-text-by-k-per-repo"
    filter_criteria = {
        "term_strategy": "meta_ast_text",
        "meta_strategy": "ast-lg",
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


def grouped_bar_plot_mean_src_text_by_w_per_repo():
    title = "Code Differences - Textual Representation \n Mean Accuracy By Window Size per Repository"
    plot_name = "grouped-bar-plot-src-text-by-w-per-repo"
    filter_criteria = {
        "term_strategy": "meta_ast_text",
        "meta_strategy": "ast-lg",
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


if __name__ == "__main__":
    # scatter_plot_mean_and_std_src_text_k_1_w_10()
    # scatter_plot_mean_and_std_src_code_k_1_w_10()
    # grouped_bar_plot_mean_src_text_by_w_per_repo()
    grouped_bar_plot_mean_src_text_by_k_per_repo()
