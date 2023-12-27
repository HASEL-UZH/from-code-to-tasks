import matplotlib.pyplot as plt

from results.plot_utils import get_data, get_formatted_identifier
from src.core.logger import log

plt.rcParams["font.family"] = "Helvetica"


class ScatterPlotMeanStd:
    def __init__(
        self, title, plot_name, term_strategy, meta_strategy=None, colors=None
    ):
        self.title = title
        self.plot_name = plot_name
        self.term_strategy = term_strategy
        self.meta_strategy = meta_strategy
        self.colors = colors or ["#FF1493", "#9370DB"]

    def plot(self):
        combined_data = get_data(1, 10, self.term_strategy, self.meta_strategy)
        formatted_identifiers = combined_data["repository_identifier"].map(
            get_formatted_identifier
        )
        group_data = (
            combined_data.groupby(formatted_identifiers)["mean"]
            .agg(["mean", "std"])
            .reset_index()
        )

        plt.figure(figsize=(8, 6))
        plt.scatter(
            x=group_data["repository_identifier"],
            y=group_data["mean"],
            color=self.colors[0],
            label="Means",
        )
        plt.errorbar(
            group_data.index,
            group_data["mean"],
            yerr=group_data["std"],
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
        plt.legend()
        plt.savefig(self.plot_name, format="svg")
        plt.savefig(self.plot_name, format="png")
        plt.show()

        for repo, mean, std in zip(
            group_data["repository_identifier"],
            group_data["mean"],
            group_data["std"],
        ):
            log.info(f"Repository: {repo}, Mean: {mean:.2f}, Std: {std:.2f}")
