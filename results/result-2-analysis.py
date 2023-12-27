from results.grouped_bar_plot_mean import GroupedBarPlotMean
from results.plot_utils import get_identifiers

SRC_TEXT = "Source Code Files - Text Representation"
SRC_CODE = "Source Code Files - Code Representation"
ACC_EL = "Mean Accuracy by Code Element Set"


def grouped_bar_plot_mean_src_text_by_code_el():
    title = SRC_TEXT + "\n" + ACC_EL
    plot_name = "grouped-bar-plot-src-text-by-sm-md-lg"
    filter_criteria = {
        "term_strategy": "meta_ast_text",
        "k": 1,
        "window_size": 10,
    }
    group_criteria = {
        "meta_strategy": ["ast_sm", "ast_md", "ast_lg"],
        "repository_identifier": get_identifiers(),
    }
    colors = [
        "#FF5733",
        "#33FF57",
        "#5733FF",
    ]
    x_axis_criteria = "repository_identifier"
    legend_criteria = "meta_strategy"
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


def grouped_bar_plot_mean_src_code_by_code_el():
    title = SRC_CODE + "\n" + ACC_EL
    plot_name = "grouped-bar-plot-src-code-by-sm-md-lg"
    filter_criteria = {
        "term_strategy": "meta_ast_code",
        "k": 1,
        "window_size": 10,
    }
    group_criteria = {
        "meta_strategy": ["ast_sm", "ast_md", "ast_lg"],
        "repository_identifier": get_identifiers(),
    }
    colors = [
        "#FF5733",
        "#33FF57",
        "#5733FF",
    ]
    x_axis_criteria = "repository_identifier"
    legend_criteria = "meta_strategy"
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
    grouped_bar_plot_mean_src_text_by_code_el()
    grouped_bar_plot_mean_src_code_by_code_el()
