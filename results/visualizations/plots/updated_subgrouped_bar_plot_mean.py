import os

from matplotlib import patches as mpatches
from matplotlib import pyplot as plt

from results.visualizations.plots.plot_utils import (
    get_data,
    get_formatted_identifier,
    get_formatted_label,
    get_formatted_value,
)
from src.core.logger import log
from src.core.workspace_context import get_results_dir


class UpdatedSubGroupedBarPlotMean:
    def __init__(
        self,
        title,
        plot_name,
        filter_criteria,
        group_criteria,
        colors,
        subgroup_criteria=None,
        group_amount=3,
        subgroup_amount=2,
        group_name="",
        subgroup_name="",
    ):
        self.title = title
        self.plot_name = plot_name
        self.filter_criteria = filter_criteria
        self.group_criteria = group_criteria
        self.colors = colors
        self.subgroup_criteria = subgroup_criteria
        self.group_amount = group_amount
        self.subgroup_amount = subgroup_amount
        self.group_name = group_name
        self.subgroup_name = subgroup_name

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
            self.filter_criteria, self.group_criteria, self.subgroup_criteria
        )
        plt.figure(figsize=(8, 6))
        width = 0.3
        unique_legend_item = set()
        tick_positions = []
        tick_labels = []
        color_matching = {}

        combinations = []

        for group_key, group_values in self.group_criteria.items():
            for i, group_value in enumerate(group_values):
                for subgroup_key, subgroup_values in self.subgroup_criteria.items():
                    for j, subgroup_value in enumerate(subgroup_values):
                        # Check if there is a row with the corresponding values
                        if any(
                            (group_value == row[group_key])
                            and (subgroup_value == row[subgroup_key])
                            for _, row in data.iterrows()
                        ):
                            combinations.append((group_value, subgroup_value))

        for k, repo_identifier in enumerate(repository_order):
            group_df = data[data["repository_identifier"] == repo_identifier]
            if "meta_ast_strategy" in self.group_criteria:
                custom_order = {"ast-sm": 0, "ast-md": 1, "ast-lg": 2}
                group_df["sorting_order"] = group_df["meta_ast_strategy"].map(
                    custom_order
                )
                group_df = group_df.sort_values(by="sorting_order")
                group_df = group_df.drop("sorting_order", axis=1)
            group_center = k + (3 - 1) / 2

            self.group_criteria = {
                key: value
                for key, value in self.group_criteria.items()
                if key != "repository_identifier"
            }
            for group_key, group_values in self.group_criteria.items():
                x = -1
                for i, group_value in enumerate(group_values):
                    for subgroup_key, subgroup_values in self.subgroup_criteria.items():
                        for j, subgroup_value in enumerate(subgroup_values):
                            if (group_value, subgroup_value) not in combinations:
                                continue
                            x += 1
                            print(f"{x} {(group_value, subgroup_value)}")
                            filtered_data = group_df[
                                (group_df[group_key] == group_value)
                                & (group_df[subgroup_key] == subgroup_value)
                            ]
                            mean_value = filtered_data["Mean"].mean()
                            color = self.colors[x]
                            position = group_center + width * (x - 5 - 1) / 2

                            plt.bar(
                                x=position,
                                height=mean_value,
                                width=width / 2,
                                color=color,
                                label=f"{group_value} {subgroup_value}",
                            )
                            unique_legend_item.add((group_value, subgroup_value))
                            if (group_value, subgroup_value) not in color_matching:
                                color_matching[(group_value, subgroup_value)] = color

            tick_positions.append(group_center - 0.6)
            tick_labels.append(f"{get_formatted_identifier(repo_identifier)}")
        plt.tight_layout()
        plt.subplots_adjust(left=0.08, bottom=0.14)
        plt.xlabel("Repository")
        plt.ylabel("Accuracy")
        plt.ylim(0, 1)
        plt.xticks(tick_positions, tick_labels)
        self.group_criteria.update(self.subgroup_criteria)

        plt.legend(
            loc="upper left",
            title=f"{get_formatted_label(self.group_name)}, {get_formatted_label(self.subgroup_name)}",
            handles=[mpatches.Patch(color=color_matching[i]) for i in color_matching],
            labels=(
                [
                    f"{self.group_name}={get_formatted_value(i[0])}, {self.subgroup_name}={get_formatted_value(i[1])}"
                    for i in color_matching
                ]
            ),
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
            for subgroup_value, subgroup_df in group_df.groupby(
                list(self.subgroup_criteria.keys())[0]
            ):
                mean_value = subgroup_df["Mean"].mean()
                std_value = subgroup_df["Mean"].std()
                var_value = subgroup_df["Mean"].var()

                log.info(
                    f"{get_formatted_label(list(self.group_criteria.keys())[0])}: {group_value}, {get_formatted_label(list(self.subgroup_criteria.keys())[0])}: {subgroup_value}, Mean: {mean_value:.4f}, Std: {std_value:.2f}, Var: {var_value:.2f}"
                )
