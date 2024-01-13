from results.visualizations.plots.plot_utils import get_identifiers
from results.visualizations.plots.subgrouped_bar_plot_mean import SubGroupedBarPlotMean
from results.visualizations.plots.updated_subgrouped_bar_plot_mean import (
    UpdatedSubGroupedBarPlotMean,
)


def updated_subgrouped_bar_plot_mean_change_repr_by_v_per_repo():
    title = "Mean Accuracy By K per Repository Split by Vectorization"
    plot_name = "updated_subgrouped_bar_plot_mean_change_repr_by_v_per_repo"
    filter_criteria = {
        "window_size": 10,
        "k": 1,
    }
    group_criteria = {
        "embeddings_concept": ["tf", "tf_idf", "codebert"],
        "repository_identifier": get_identifiers(),
    }
    subgroup_criteria = {
        "term_strategy": ["diff_text", "meta_ast_text", "meta_ast_code"],
    }
    # blue, orange, red and green
    colors = [
        "#4E79A7",
        "#F28E2B",
        "#E15759",
        "#59A14F",
        "#B07AA1",
        "#59A14F",
        "#B07AA1",
        "#59A14F",
        "#E15759",
    ]
    updated_subgrouped_bar_plot_mean = UpdatedSubGroupedBarPlotMean(
        title,
        plot_name,
        filter_criteria,
        group_criteria,
        colors,
        subgroup_criteria,
        3,
        3,
        "V",
        "C",
    )
    updated_subgrouped_bar_plot_mean.plot()


def subgrouped_bar_plot_mean_change_repr_by_v_by_t_per_repo_diff():
    title = "Mean Accuracy By K per Repository Split by Vectorization"
    plot_name = "subgrouped_bar_plot_mean_change_repr_by_v_by_t_per_repo_diff"
    filter_criteria = {"window_size": 10, "k": 1, "term_strategy": "diff_text"}
    group_criteria = {
        "repository_identifier": get_identifiers(),
        "embeddings_concept": ["tf", "tf_idf"],
    }
    subgroup_criteria = {
        "embeddings_strategy": [
            "tf-embedding--standard-tokenizer",
            "tf-embedding--subword-tokenizer",
        ]
    }
    # blue, orange, red and green
    colors = ["#FFBE7D", "#F28E2B", "#A0CBE8", "#4E79A7"]
    subgrouped_bar_plot_mean = SubGroupedBarPlotMean(
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
    subgrouped_bar_plot_mean.plot()


def subgrouped_bar_plot_mean_change_repr_by_v_by_t_per_repo_src():
    title = "Mean Accuracy By K per Repository Split by Vectorization"
    plot_name = "subgrouped_bar_plot_mean_change_repr_by_v_by_t_per_repo_src"
    filter_criteria = {"window_size": 10, "k": 1, "term_strategy": "meta_ast_text"}
    group_criteria = {
        "repository_identifier": get_identifiers(),
        "embeddings_concept": ["tf", "tf_idf"],
    }
    subgroup_criteria = {
        "embeddings_strategy": [
            "tf-embedding--standard-tokenizer",
            "tf-embedding--subword-tokenizer",
        ]
    }
    # blue, orange, red and green
    colors = ["#FFBE7D", "#F28E2B", "#A0CBE8", "#4E79A7"]
    subgrouped_bar_plot_mean = SubGroupedBarPlotMean(
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
    subgrouped_bar_plot_mean.plot()


if __name__ == "__main__":
    subgrouped_bar_plot_mean_change_repr_by_v_by_t_per_repo_diff()
    subgrouped_bar_plot_mean_change_repr_by_v_by_t_per_repo_src()
    updated_subgrouped_bar_plot_mean_change_repr_by_v_per_repo()
