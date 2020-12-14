import sys

from pandas import DataFrame

import yaml
import GitHubStatistics
import Chart as ch
import plotly.express as px
import plotly.graph_objects as go

required = dict(
    weekday_commits = False,
    weekday_repo_commits = False,
    year_languages = False,
    all_languages = False
)


def main(args: list):
    size = len(args)

    if size < 1:
        print("Failed to update file (no oauth token provided)")
        return

    token = str(args[0])
    config = yaml.load(open("config.yml", 'r'), Loader=yaml.FullLoader)

    annual_statistics, all_time_statistics = GitHubStatistics.get_statistics(
        token,
        include_private=config['include_private_repositories'],
        hide_repositories=config['hide_repositories'],
        hide_languages=config['hide_languages']
    )

    l1 = ch.RadarChart() \
        .generate(DataFrame(all_time_statistics.languages)) \
        .save_to_file("out.svg")

    return


if __name__ == "__main__":
    main(sys.argv[1:])
