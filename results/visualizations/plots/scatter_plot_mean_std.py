import os

import matplotlib.pyplot as plt

from results.visualizations.plots.plot_utils import get_data, get_formatted_identifier
from src.core.logger import log
from src.core.workspace_context import get_results_dir

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
        plt.tight_layout()
        plt.subplots_adjust(left=0.06, bottom=0.09)
        plt.xlabel("Repository")
        plt.ylabel("Mean")
        plt.legend(
            loc="upper center",
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
        overall_mean = data["Mean"].mean()
        overall_std = data["Mean"].std()
        overall_var = data["Mean"].var()
        log.info(
            f"Overall Mean: {overall_mean:.2f}, Overall Std: {overall_std:.2f}, Overall Var: {overall_var:.2f}"
        )

        for repo, mean, std, var in zip(
            data["repository_identifier"],
            data["Mean"],
            data["Std"],
            data["Var"],
        ):
            log.info(
                f"Repository: {repo}, Mean: {mean:.2f}, Std: {std:.2f}, Var: {var:.2f}"
            )
