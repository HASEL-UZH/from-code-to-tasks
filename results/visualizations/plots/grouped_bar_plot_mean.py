import os

from matplotlib import patches as mpatches
from matplotlib import pyplot as plt

from results.visualizations.plots.plot_utils import (
    get_formatted_identifier,
    get_data,
    get_formatted_label,
    get_formatted_value,
    get_formatted_item,
)
from src.core.logger import log
from src.core.workspace_context import get_results_dir

plt.rcParams["font.family"] = "Helvetica"


class GroupedBarPlotMean:
    def __init__(
        self,
        title,
        plot_name,
        filter_criteria,
        group_criteria,
        colors,
    ):
        self.title = title
        self.plot_name = plot_name
        self.filter_criteria = filter_criteria
        self.group_criteria = group_criteria
        self.colors = colors

    def plot(self):
        repository_order = [
            "iluwatar__java-design-patterns",
            "reactive_x___rx_java",
            "apache__dubbo",
            "eugenp__tutorials",
            "airbnb__lottie-android",
            "bumptech__glide",
            "netty__netty",
            "apolloconfig__apollo",
            "selenium_hq__selenium",
            "alibaba__nacos",
        ]
        data = get_data(
            self.filter_criteria,
            self.group_criteria,
        )
        plt.figure(figsize=(12, 8))
        width = 0.2
        unique_legend_item = set()
        tick_positions = []
        tick_labels = []
        group_name = next(iter(self.group_criteria))
        color_matching = {}

        for k, repo_identifier in enumerate(repository_order):
            group_df = data[data["repository_identifier"] == repo_identifier]
            if "meta_ast_strategy" in self.group_criteria:
                custom_order = {"ast-sm": 0, "ast-md": 1, "ast-lg": 2}
                group_df["sorting_order"] = group_df["meta_ast_strategy"].map(
                    custom_order
                )
                group_df = group_df.sort_values(by="sorting_order")
                group_df = group_df.drop("sorting_order", axis=1)
            group_center = k + (len(group_df) - 1) / 2

            self.group_criteria = {
                key: value
                for key, value in self.group_criteria.items()
                if key != "repository_identifier"
            }
            for group_key, group_values in self.group_criteria.items():
                for i, group_value in enumerate(group_values):
                    filtered_data = group_df[(group_df[group_key] == group_value)]
                    mean_value = filtered_data["Mean"].mean()
                    position = group_center + width * (i - (len(group_df) - 1) / 2)
                    plt.bar(
                        x=position,
                        height=mean_value,
                        width=width,
                        color=self.colors[i],
                        label=f"={group_value}",
                    )
                    unique_legend_item.add(group_value)
                    if group_value not in color_matching:
                        color_matching[group_value] = self.colors[i]

            tick_positions.append(group_center)
            tick_labels.append(f"{get_formatted_identifier(repo_identifier)}")

        plt.tight_layout()
        plt.subplots_adjust(left=0.06, bottom=0.09)
        plt.xlabel("Repository")
        plt.ylabel("Mean")
        plt.ylim(0, 1)
        plt.xticks(tick_positions, tick_labels)
        plt.legend(
            loc="upper center",
            title=get_formatted_label(group_name),
            handles=[mpatches.Patch(color=color_matching[i]) for i in color_matching],
            labels=[
                f"{get_formatted_item(group_name)}={get_formatted_value(i)}"
                for i in color_matching
            ],
        )
        svg_filename = os.path.join(get_results_dir(), f"{self.plot_name}.svg")
        plt.savefig(svg_filename, format="svg")
        plt.show()
        self._log_statistics(data)

    def _log_statistics(self, data):
        log.warn(
            self.title
            + "\n Mean and Standard Deviation per Repository for K=1 and W=10"
        )
        for group_value, group_df in data.groupby(list(self.group_criteria.keys())[0]):
            mean_value = group_df["Mean"].mean()
            std_value = group_df["Mean"].std()
            var_value = group_df["Mean"].var()

            log.info(
                f"{get_formatted_label(list(self.group_criteria.keys())[0])}: {group_value}, Mean: {mean_value:.2f},Std: {std_value:.2f}, Var: {var_value:.2f}"
            )

        for repo, group, mean, std, var in zip(
            data["repository_identifier"],
            data[list(self.group_criteria.keys())[0]],
            data["Mean"],
            data["Std"],
            data["Var"],
        ):
            log.info(
                f"Repository: {get_formatted_identifier(repo)}, {get_formatted_label(list(self.group_criteria.keys())[0])}: {group}, Mean: {mean:.2f}, Std: {std:.2f}, Var: {var:.2f}"
            )
