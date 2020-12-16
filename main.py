import codecs
import sys

import yaml
from liquid import Liquid

import GitHubStatistics
from card.languages_card import LanguageCard, LanguageCoverageCard
from card.statistics_card import StatisticsCard

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

    #annual_statistics, all_time_statistics = GitHubStatistics.get_statistics(
    #    token,
    #    include_private=config['include_private_repositories'],
    #    hide_repositories=config['hide_repositories'],
    #    hide_languages=config['hide_languages']
    #)
    all_time_statistics = GitHubStatistics.Statistics()

    all_time_statistics.commits = 1000
    all_time_statistics.contributions = 2500
    all_time_statistics.issues = 23
    all_time_statistics.pulls = 2355
    all_time_statistics.stars = 100
    all_time_statistics.followers = 45

    all_time_statistics.languages = {
        "Java": 85.9,
        "Python": 05.56,
        "HTML": 05.2,
        "Liquid": 01.74,
        "JavaScript": 00.44,
    }

    codecs.open("generated/statistics_annual.svg", 'w', encoding="utf-8").write(StatisticsCard(all_time_statistics, False).render())
    codecs.open("generated/statistics.svg", 'w', encoding="utf-8").write(StatisticsCard(all_time_statistics, True).render())
    codecs.open("generated/languages.svg", 'w', encoding="utf-8").write(LanguageCard(all_time_statistics.languages).render())
    codecs.open("generated/languages_coverage.svg", 'w', encoding="utf-8").write(LanguageCoverageCard(all_time_statistics.languages, config["top_languages"]).render())

    return


if __name__ == "__main__":
    main(sys.argv[1:])
