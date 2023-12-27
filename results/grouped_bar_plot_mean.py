from matplotlib import pyplot as plt

from results.plot_utils import (
    get_data_2,
    get_formatted_label,
    get_formatted_item,
)

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
        data = get_data_2(
            self.filter_criteria,
            self.group_criteria,
        )

        plt.figure(figsize=(4, 3))
        width = 0.2
        grouped_data = data.groupby(self.x_axis_criteria)
        num_legend_items = len(data[self.legend_criteria].unique())
        cmap = plt.cm.get_cmap("viridis", num_legend_items)

        unique_legend_item = set()

        tick_positions = []
        tick_labels = []

        for i, (repo_identifier, group_df) in enumerate(grouped_data):
            group_center = i + (len(group_df) - 1) / 2
            for j, (legend_val, row) in enumerate(group_df.iterrows()):
                color = cmap(j)
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
            tick_labels.append(legend_val)

        plt.xlabel("Repository")
        plt.ylabel("Mean")
        plt.title(self.title)
        plt.xticks(tick_positions, tick_labels)
        plt.legend(
            title=get_formatted_label(self.legend_criteria),
            labels=[
                f"{get_formatted_item(self.legend_criteria)}={l_item}"
                for l_item in unique_legend_item
            ],
        )
        plt.savefig(f"{self.plot_name}.svg", format="svg")
        plt.savefig(f"{self.plot_name}.png", format="png")
        plt.show()
