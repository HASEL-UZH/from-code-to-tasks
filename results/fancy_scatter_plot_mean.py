from results.plot_utils import get_data


class FancyScatterPlotMean:
    def __init__(
        self,
        title,
        plot_name,
        filter_criteria,
        group_criteria,
        x_axis_criteria,
        legend_criteria,
        subgroup_criteria=None,
        colors=None,
    ):
        self.title = title
        self.plot_name = plot_name
        self.filter_criteria = filter_criteria
        self.group_criteria = group_criteria
        self.x_axis_criteria = x_axis_criteria
        self.legend_criteria = legend_criteria
        self.subgroup_criteria = subgroup_criteria
        self.colors = colors

    def plot(self):
        data = get_data(self.filter_criteria, self.group_criteria)

    def _log_statistics(self, data):
        pass
