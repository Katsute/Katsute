import codecs
import sys

import yaml
from typing import Dict, List

import github_statistics
from card.languages_card import LanguageCard, LanguageCoverageCard
from card.statistics_card import StatisticsCard

required: Dict[str, bool] = dict(
    weekday_commits=False,
    weekday_repo_commits=False,
    year_languages=False,
    all_languages=False
)


def main(args: List[str]):
    size: int = len(args)

    if size < 1:
        print("Failed to update file (no oauth token provided)")
        return

    token: str = str(args[0])
    config: dict = yaml.safe_load(open("config.yml", 'r'), Loader=yaml.FullLoader)

    annual_statistics, all_time_statistics = github_statistics.get_statistics(
        token,
        include_private=config['include_private_repositories'],
        hide_repositories=config['hide_repositories'],
        hide_languages=config['hide_languages']
    )

    codecs.open("generated/statistics_annual.svg", 'w', encoding="utf-8").write(
        StatisticsCard(annual_statistics, False).render())
    codecs.open("generated/statistics.svg", 'w', encoding="utf-8").write(
        StatisticsCard(all_time_statistics, True).render())
    codecs.open("generated/languages.svg", 'w', encoding="utf-8").write(
        LanguageCard(all_time_statistics.languages).render())
    codecs.open("generated/languages_coverage.svg", 'w', encoding="utf-8").write(
        LanguageCoverageCard(all_time_statistics.languages, config["top_languages"]).render())

    return


if __name__ == "__main__":
    main(sys.argv[1:])
