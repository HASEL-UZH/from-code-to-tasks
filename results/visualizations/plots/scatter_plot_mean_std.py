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

        plt.figure(figsize=(8, 6))
        tick_positions = []
        tick_labels = []
        data = get_data(self.filter_criteria, self.group_criteria)

        # Initialize flags for legend labels
        mean_legend_added = False
        std_legend_added = False

        for k, repo_identifier in enumerate(repository_order):
            group_df = data[data["repository_identifier"] == repo_identifier]
            group_center = k

            plt.scatter(
                x=group_center,
                y=group_df["Mean"],
                color=self.colors[0],
                label="Mean" if not mean_legend_added else "",
            )

            plt.errorbar(
                x=group_center,
                y=group_df["Mean"],
                yerr=group_df["Std"],
                fmt="none",
                capsize=5,
                color=self.colors[1],
                label="Standard Deviation" if not std_legend_added else "",
            )

            tick_positions.append(group_center)
            tick_labels.append(f"{get_formatted_identifier(repo_identifier)}")

            # Set the flags to True after the first iteration
            mean_legend_added = True
            std_legend_added = True

        plt.tight_layout()
        plt.subplots_adjust(left=0.09, bottom=0.12)
        plt.xlabel("Repository")
        plt.ylabel("Mean")
        plt.legend(loc="upper center")
        plt.ylim(0, 1)
        plt.xticks(tick_positions, tick_labels)

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
            f"Overall Mean: {overall_mean:.4f}, Overall Std: {overall_std:.2f}, Overall Var: {overall_var:.2f}"
        )

        for repo, mean, std, var in zip(
            data["repository_identifier"],
            data["Mean"],
            data["Std"],
            data["Var"],
        ):
            log.info(
                f"Repository: {repo}, Mean: {mean:.4f}, Std: {std:.2f}, Var: {var:.2f}"
            )
