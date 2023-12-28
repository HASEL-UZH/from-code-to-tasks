import matplotlib.pyplot as plt

from results.visualizations.plots.plot_utils import get_data, get_formatted_identifier
from src.core.logger import log

plt.rcParams["font.family"] = "Helvetica"


class ScatterPlotMeanStd:
    def __init__(self, title, plot_name, filter_criteria, group_criteria, colors):
        self.title = title
        self.plot_name = plot_name
        self.filter_criteria = filter_criteria
        self.group_criteria = group_criteria
        self.colors = colors

    def plot(self):
        data = get_data(self.filter_criteria, self.group_criteria)

        plt.figure(figsize=(12, 8))
        plt.scatter(
            x=data["repository_identifier"].apply(get_formatted_identifier),
            y=data["Mean"],
            color=self.colors[0],
            label="Mean",
        )
        plt.errorbar(
            data.index,
            data["Mean"],
            yerr=data["Std"],
            fmt="none",
            capsize=5,
            color=self.colors[1],
            label="Standard Deviation",
        )

        plt.xlabel("Repository")
        plt.ylabel("Mean")
        plt.title(
            self.title
            + "\n Mean and Standard Deviation per Repository for K=1 and W=10"
        )
        plt.legend(
            loc="lower right",
        )
        plt.savefig(self.plot_name, format="svg")
        plt.savefig(self.plot_name, format="png")
        plt.show()

        for repo, mean, std, var in zip(
            data["repository_identifier"],
            data["Mean"],
            data["Std"],
            data["Var"],
        ):
            log.info(
                f"Repository: {repo}, Mean: {mean:.2f}, Std: {std:.2f}, Var: {var:.2f}"
            )
