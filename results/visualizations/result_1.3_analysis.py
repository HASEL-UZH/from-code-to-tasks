from results.visualizations.plots.grouped_bar_plot_mean import GroupedBarPlotMean
from results.visualizations.plots.plot_utils import (
    get_identifiers,
)


def grouped_bar_plot_mean_per_change_repr_text_k_1_w_10_per_repo():
    title = "Change Representation Comparision- Textual Representation \n Mean and Standard Deviation per Repository for K=1 and W=10"
    plot_name = "grouped_bar_plot_mean_per_change_repr_k_1_w_10_per_repo"
    filter_criteria = {
        "k": 1,
        "window_size": 10,
        "embeddings_concept": "tf_idf",
        "embeddings_strategy": "tf-idf-embedding--subword-tokenizer",
    }
    group_criteria = {
        "term_strategy": ["meta_ast_text", "diff_text", "diff_text/meta_ast_text"],
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
    grouped_bar_plot_mean_per_change_repr_text_k_1_w_10_per_repo()
