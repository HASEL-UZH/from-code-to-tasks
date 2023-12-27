from matplotlib import pyplot as plt

from results.plot_utils import (
    get_formatted_label,
    get_formatted_item,
    get_formatted_identifier,
    get_formatted_value,
    get_data,
)
from src.core.logger import log

plt.rcParams["font.family"] = "Helvetica"


class GroupedBarPlotMean:
    def __init__(
        self,
        title,
        plot_name,
        filter_criteria,
        group_criteria,
        x_axis_criteria,
        legend_criteria,
        colors=None,
    ):
        self.title = title
        self.plot_name = plot_name
        self.filter_criteria = filter_criteria
        self.group_criteria = group_criteria
        self.x_axis_criteria = x_axis_criteria
        self.legend_criteria = legend_criteria
        self.colors = colors

    def plot(self):
        data = get_data(
            self.filter_criteria,
            self.group_criteria,
        )

        plt.figure(figsize=(12, 8))
        width = 0.2
        grouped_data = data.groupby(self.x_axis_criteria)

        unique_legend_item = set()

        tick_positions = []
        tick_labels = []

        for i, (repo_identifier, group_df) in enumerate(grouped_data):
            group_center = i + (len(group_df) - 1) / 2
            if "meta_ast_strategy" in self.group_criteria:
                custom_order = {"ast-sm": 0, "ast-md": 1, "ast-lg": 2}
                group_df["sorting_order"] = group_df["meta_ast_strategy"].map(
                    custom_order
                )
                group_df = group_df.sort_values(by="sorting_order")
                group_df = group_df.drop("sorting_order", axis=1)
            for j, (legend_val, row) in enumerate(group_df.iterrows()):
                color = self.colors[j]
                position = group_center + width * (j - (len(group_df) - 1) / 2)
                plt.bar(
                    x=position,
                    height=row["Mean"],
                    width=width,
                    color=color,
                    label=f"={row[self.legend_criteria]}",
                )
                unique_legend_item.add(row[self.legend_criteria])

            tick_positions.append(group_center)
            tick_labels.append(get_formatted_identifier(repo_identifier))

        plt.xlabel("Repository")
        plt.ylabel("Mean")
        plt.title(self.title)
        plt.xticks(tick_positions, tick_labels)
        plt.legend(
            title=get_formatted_label(self.legend_criteria),
            labels=[
                f"{get_formatted_item(self.legend_criteria)}={get_formatted_value(l_item)}"
                for l_item in unique_legend_item
            ],
        )
        plt.savefig(f"{self.plot_name}.svg", format="svg")
        plt.savefig(f"{self.plot_name}.png", format="png")
        plt.show()
        self._log_statistics(data)

    def _log_statistics(self, data):
        for legend_val, group_df in data.groupby(self.legend_criteria):
            for x_axis_val, x_axis_group in group_df.groupby(self.x_axis_criteria):
                mean_val = x_axis_group["Mean"].iloc[0]
                var_val = x_axis_group["Var"].iloc[0]
                std_val = x_axis_group["Std"].iloc[0]
                log.info(
                    f"For {self.x_axis_criteria}={x_axis_val}, {self.legend_criteria}={legend_val}: "
                    f"Mean: {mean_val:.2f}, Variance: {var_val:.2f}, Std Dev: {std_val:.2f}"
                )

        for legend_val, group_df in data.groupby(self.legend_criteria):
            mean_over_all_repos = group_df.groupby("repository_identifier")[
                "Mean"
            ].mean()
            mean_val = mean_over_all_repos.mean()
            var_val = mean_over_all_repos.var()
            std_val = mean_over_all_repos.std()
            log.info(
                f"For {self.legend_criteria}={legend_val} over all repositories: "
                f"Mean: {mean_val:.2f}, Variance: {var_val:.2f}, Std Dev: {std_val:.2f}"
            )
