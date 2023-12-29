import os

from matplotlib import pyplot as plt

from results.visualizations.plots.plot_utils import (
    get_data,
    get_formatted_label,
    get_formatted_item,
    get_formatted_identifier,
)
from src.core.logger import log
from src.core.workspace_context import get_results_dir


class FancyScatterPlotMean:
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
        data = get_data(
            self.filter_criteria, self.group_criteria, self.subgroup_criteria
        )
        plt.figure(figsize=(12, 8))
        width = 0.2
        grouped_data = data.groupby("repository_identifier")
        unique_legend_item = set()
        tick_positions = []
        tick_labels = []

        for k, (repo_identifier, group_df) in enumerate(grouped_data):
            if "meta_ast_strategy" in self.group_criteria:
                custom_order = {"ast-sm": 0, "ast-md": 1, "ast-lg": 2}
                group_df["sorting_order"] = group_df["meta_ast_strategy"].map(
                    custom_order
                )
                group_df = group_df.sort_values(by="sorting_order")
                group_df = group_df.drop("sorting_order", axis=1)
            group_center = k + (len(group_df) / 2 - 1) / 2

            self.group_criteria = {
                key: value
                for key, value in self.group_criteria.items()
                if key != "repository_identifier"
            }

            for group_key, group_values in self.group_criteria.items():
                for i, group_value in enumerate(group_values):
                    for subgroup_key, subgroup_values in self.subgroup_criteria.items():
                        for j, subgroup_value in enumerate(subgroup_values):
                            subgroup_width = width / 3
                            filtered_data = group_df[
                                (group_df[group_key] == group_value)
                                & (group_df[subgroup_key] == subgroup_value)
                            ]
                            mean_value = filtered_data["Mean"].mean()

                            color = self.colors[j]
                            shapes = ["^", "s", "o"]
                            shape_dict = dict(zip(group_values, shapes))
                            shape = shape_dict.get(group_value)

                            position = group_center + width * (
                                i - (len(group_df) / 2 - 1) / 2
                            )

                            if k == 0 and group_value == 10:
                                print(
                                    f"{subgroup_value} xpos {position + i * subgroup_width} "
                                )

                            plt.scatter(
                                x=position + i * subgroup_width,
                                y=mean_value,
                                color=color,
                                marker=shape,
                                s=100,
                                label=f"{get_formatted_item(group_value)} {get_formatted_item(subgroup_value)}",
                            )

                            unique_legend_item.add((group_value, subgroup_value))

            tick_positions.append(group_center)
            tick_labels.append(f"{get_formatted_identifier(repo_identifier)}")
        plt.tight_layout()
        plt.subplots_adjust(left=0.06, bottom=0.09)
        plt.xlabel("Repository")
        plt.ylabel("Mean")
        plt.xticks(tick_positions, tick_labels)
        plt.legend(
            loc="upper center",
            title=f"{get_formatted_label(self.group_name)}, {get_formatted_label(self.subgroup_name)}",
            labels=sorted(
                [
                    f"{self.group_name}={get_formatted_item(l_item[0])}, {self.subgroup_name}={get_formatted_item(l_item[1])}"
                    for l_item in unique_legend_item
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
                    f"{get_formatted_label(list(self.group_criteria.keys())[0])}: {group_value}, {get_formatted_label(list(self.subgroup_criteria.keys())[0])}: {subgroup_value}, Mean: {mean_value:.2f}, Std: {std_value:.2f}, Var: {var_value:.2f}"
                )

                for repo, repo_group in subgroup_df.groupby("repository_identifier"):
                    mean_value_repo = repo_group["Mean"].mean()
                    std_value_repo = repo_group["Mean"].std()
                    var_value_repo = repo_group["Mean"].var()
            log.info(
                f"Repository: {get_formatted_identifier(repo)}, {get_formatted_label(list(self.group_criteria.keys())[0])}: {group_value}, {get_formatted_label(list(self.subgroup_criteria.keys())[0])}: Mean: {mean_value_repo:.2f}, Std: {std_value_repo:.2f}, Var: {var_value_repo:.2f}"
            )
