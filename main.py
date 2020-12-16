import codecs
import sys

import yaml
from liquid import Liquid

import GitHubStatistics
from card.languages import LanguageCard

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
    all_time_statistics.languages = {
        "Java": 85.9,
        "Python": 05.56,
        "HTML": 05.2,
        "Liquid": 01.74,
        "JavaScript": 00.44,
    }

    codecs.open("generated/languages.svg", 'w', encoding="utf-8").write(LanguageCard(all_time_statistics.languages).render())

    return


if __name__ == "__main__":
    main(sys.argv[1:])
