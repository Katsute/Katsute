from datetime import date

from GitHubStatistics import Statistics
from card.card import Card

MAGNITUDE = ['', 'K', 'M', 'B', 'T']


def format_num(num: int):
    if num <= 999:
        return num
    else:
        m = 0
        while num >= 1_000:
            m += 1
            num /= 1_000
        return '%.2f%s' % (num, MAGNITUDE[m])


class StatisticsCard(Card):

    def __init__(self, statistics: Statistics, all_time: bool):
        super().__init__(
            "All Time Statistics" if all_time else f"Annual Statistics ({date.today().year})",
            "templates/statistics.liquid",
            statistics=dict(
                Commits         = format_num(statistics.commits),
                Issues          = format_num(statistics.issues),
                PRs             = format_num(statistics.pulls),
                Contributions   = format_num(statistics.contributions)
            ),
            all_time=dict(
                Stars = statistics.stars,
                Followers = statistics.followers
            ) if all_time else {},
            css="""
                .stat{
                    font: 600 14px 'Segoe UI', "Helvetica Neue", Sans-Serif; fill: #333;
                }
                """
        )

        self.increase_height(len(self.args["statistics"]) * 25)
        return
