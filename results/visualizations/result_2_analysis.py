from results.visualizations.plots.grouped_bar_plot_mean import GroupedBarPlotMean
from results.visualizations.plots.plot_utils import get_identifiers

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
        "embeddings_concept": "tf_idf",
        "embeddings_strategy": "tf-idf-embedding--subword-tokenizer",
    }
    group_criteria = {
        "meta_strategy": ["ast-sm", "ast-md", "ast-lg"],
        "repository_identifier": get_identifiers(),
    }
    # blue, orange and red
    colors = [
        "#4E79A7",
        "#F28E2B",
        "#E15759",
    ]
    grouped_bar_plot_mean = GroupedBarPlotMean(
        title,
        plot_name,
        filter_criteria,
        group_criteria,
        colors,
    )
    grouped_bar_plot_mean.plot()


if __name__ == "__main__":
    grouped_bar_plot_mean_src_text_by_code_el()
