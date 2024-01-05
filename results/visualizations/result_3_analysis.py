from results.visualizations.plots.fancy_scatter_plot_mean import FancyScatterPlotMean
from results.visualizations.plots.plot_utils import get_identifiers
from results.visualizations.plots.subgrouped_bar_plot_mean import SubGroupedBarPlotMean


def subgrouped_bar_plot_mean_change_repr_by_v_per_repo():
    title = "Mean Accuracy By K per Repository Split by Vectorization"
    plot_name = "subgrouped_bar_plot_mean_change_repr_by_v_per_repo"
    filter_criteria = {
        "window_size": 10,
        "k": 1,
    }
    group_criteria = {
        "term_strategy": ["diff_text", "meta_ast_text"],
        "repository_identifier": get_identifiers(),
    }
    subgroup_criteria = {"embeddings_concept": ["tf", "tf_idf"]}
    # blue, orange, red and green
    colors = ["#4E79A7", "#F28E2B", "#E15759", "#59A14F"]
    subgrouped_bar_plot_mean = SubGroupedBarPlotMean(
        title,
        plot_name,
        filter_criteria,
        group_criteria,
        colors,
        subgroup_criteria,
        2,
        2,
        "C",
        "V",
    )
    subgrouped_bar_plot_mean.plot()


def fancy_scatter_plot_mean_diff_text_by_v_by_t():
    title = "Mean Accuracy By Window Size per Repository Split by Vectorization"
    plot_name = "fancy-scatter-plot-diff-text-by-v-by-t"
    filter_criteria = {"term_strategy": "diff_text", "k": 1, "window_size": 10}
    group_criteria = {
        "embeddings_concept": ["tf", "tf_idf"],
        "repository_identifier": get_identifiers(),
    }
    subgroup_criteria = {
        "embeddings_strategy": [
            "tf-embedding--standard-tokenizer",
            "tf-embedding--subword-tokenizer",
        ]
    }
    # blue and orange
    colors = ["#4E79A7", "#F28E2B"]
    fancy_scatter_plot_mean = FancyScatterPlotMean(
        title,
        plot_name,
        filter_criteria,
        group_criteria,
        colors,
        subgroup_criteria,
        2,
        2,
        "V",
        "T",
    )
    fancy_scatter_plot_mean.plot()


def fancy_scatter_plot_mean_src_text_by_v_by_t():
    title = "Mean Accuracy By Window Size per Repository Split by Vectorization"
    plot_name = "fancy-scatter-plot-src-text-by-v-by-t"
    filter_criteria = {"term_strategy": "meta_ast_text", "k": 1, "window_size": 10}
    group_criteria = {
        "embeddings_concept": ["tf", "tf_idf"],
        "repository_identifier": get_identifiers(),
    }
    subgroup_criteria = {
        "embeddings_strategy": [
            "tf-embedding--standard-tokenizer",
            "tf-embedding--subword-tokenizer",
        ]
    }
    # blue and orange
    colors = ["#4E79A7", "#F28E2B"]
    fancy_scatter_plot_mean = FancyScatterPlotMean(
        title,
        plot_name,
        filter_criteria,
        group_criteria,
        colors,
        subgroup_criteria,
        2,
        2,
        "V",
        "T",
    )
    fancy_scatter_plot_mean.plot()


if __name__ == "__main__":
    subgrouped_bar_plot_mean_change_repr_by_v_per_repo()
    fancy_scatter_plot_mean_diff_text_by_v_by_t()
    fancy_scatter_plot_mean_src_text_by_v_by_t()