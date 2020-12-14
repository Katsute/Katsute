from abc import abstractmethod
import matplotlib.pyplot as plt
from pandas import DataFrame
from math import pi


class Chart:

    @abstractmethod
    def generate(self, data):
        return self

    # noinspection PyMethodMayBeStatic
    def save_to_file(self, file: str):
        plt.savefig(file, quality=100, format="svg")
        plt.clf()


class RadarChart(Chart):

    def generate(self, data: DataFrame):
        # number of variable
        categories = list(data)[1:]
        size = len(categories)

        # get values
        values = data.loc[0].drop('group').values.flatten().tolist()
        values += values[:1]

        # axis angles
        angles = [n / float(size) * 2 * pi for n in range(size)]
        angles += angles[:1]

        # init spider plot
        ax = plt.subplot(111, polar=True)

        # axe + label
        plt.xticks(angles[:-1], categories, color='grey', size=8)

        # y axis
        ax.set_rlabel_position(0)
        plt.yticks([25, 50, 75], ["25%", "50%", "75%"], color="grey", size=7)
        plt.ylim(0, 40)

        # plot
        ax.plot(angles, values, linewidth=1, linestyle='solid')

        # interior
        ax.fill(angles, values, 'g', alpha=0.1)

        return self
