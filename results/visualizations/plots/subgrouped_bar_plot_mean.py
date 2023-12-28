from matplotlib import pyplot as plt

from results.visualizations.plots.plot_utils import (
    get_data,
    get_formatted_identifier,
    get_formatted_label,
    get_formatted_item,
)


class SubGroupedBarPlotMean:
    def __init__(
        self,
        title,
        plot_name,
        filter_criteria,
        group_criteria,
        x_axis_criteria,
        legend_criteria,
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
        self.x_axis_criteria = x_axis_criteria
        self.legend_criteria = legend_criteria
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
        grouped_data = data.groupby(self.x_axis_criteria)
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
            group_center = k + (len(group_df) / self.group_amount - 1) / 2

            self.group_criteria = {
                key: value
                for key, value in self.group_criteria.items()
                if key != "repository_identifier"
            }
            for group_key, group_values in self.group_criteria.items():
                for i, group_value in enumerate(group_values):
                    for subgroup_key, subgroup_values in self.subgroup_criteria.items():
                        for j, subgroup_value in enumerate(subgroup_values):
                            subgroup_width = width / self.subgroup_amount
                            filtered_data = group_df[
                                (group_df[group_key] == group_value)
                                & (group_df[subgroup_key] == subgroup_value)
                            ]
                            mean_value = filtered_data["Mean"].mean()
                            color = self.colors[len(subgroup_values) * i + j]
                            position = group_center + width * (
                                i - (len(group_df) / self.group_amount) / 2
                            )

                            plt.bar(
                                x=position + j * subgroup_width,
                                height=mean_value,
                                width=subgroup_width,
                                color=color,
                                label=f"{group_value} {subgroup_value}",
                            )
                            unique_legend_item.add((group_value, subgroup_value))

            tick_positions.append(group_center)
            tick_labels.append(f"{get_formatted_identifier(repo_identifier)}")

        plt.xlabel("Repository")
        plt.ylabel("Mean")
        plt.title(self.title)
        plt.xticks(tick_positions, tick_labels)
        self.group_criteria.update(self.subgroup_criteria)

        plt.legend(
            loc="upper center",
            title=f"{get_formatted_label(self.group_name)}, {get_formatted_label(self.subgroup_name)}",
            labels=sorted(
                [
                    f"{self.group_name}={get_formatted_item(l_item[0])} {self.subgroup_name}={get_formatted_item(l_item[1])}"
                    for l_item in unique_legend_item
                ]
            ),
        )
        plt.savefig(f"{self.plot_name}.svg", format="svg")
        plt.savefig(f"{self.plot_name}.png", format="png")
        plt.show()
