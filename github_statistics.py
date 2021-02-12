import datetime as datetime

from github import Github
from github.AuthenticatedUser import AuthenticatedUser
from github.GithubException import UnknownObjectException
from typing import List, Set, Dict

from github.Repository import Repository


class Statistics:
    commits: int = 0
    contributions: int = 0
    issues: int = 0
    pulls: int = 0
    stars: int = 0
    followers: int = 0
    languages: Dict[str, float] = {}


def get_statistics(
        token: str,
        include_private: bool = False,
        hide_languages: List[str] = None,
        hide_repositories: List[int] = None):
    if hide_repositories is None:
        hide_repositories = []
    if hide_languages is None:
        hide_languages = []

    github: Github = Github(token)
    user: AuthenticatedUser = github.get_user()
    username: str = user.name
    user_id: int = user.id

    req: int = github.get_rate_limit().core.remaining
    print("Request Available:", req)

    date_init_year: datetime = datetime.datetime.combine(datetime.date(datetime.date.today().year, 1, 1),
                                                         datetime.time.min)

    annual: Statistics = Statistics()
    all_time: Statistics = Statistics()

    repositories: Set[int] = set()
    contributed: Set[int] = set()

    for issue in github.search_issues('', author=username):
        repo: Repository = issue.repository
        if repo.id in hide_repositories:
            continue
        repositories.add(repo.id)

        if repo.owner.id != user_id and repo.id not in contributed and issue.created_at >= date_init_year:
            contributed.add(repo.id)
            annual.contributions += 1

        try:  # if pull
            issue.as_pull_request()
            all_time.pulls += 1
            if issue.created_at >= date_init_year:
                annual.pulls += 1
        except UnknownObjectException:  # if issue
            all_time.issues += 1
            if issue.created_at >= date_init_year:
                annual.issues += 1

    for repo in user.get_repos("all" if include_private else "public"):
        if repo.id not in hide_repositories:
            repositories.add(repo.id)
            if not repo.fork:
                all_time.stars += repo.stargazers_count
            if repo.owner.id != user.id and repo.id not in contributed:
                contributed.add(repo.id)
                annual.contributions += 1

    for repository in repositories:
        repo: Repository = github.get_repo(repository)

        def commits(since: datetime = None):
            if since:
                total_user_commits: int = repo.get_commits(author=user.name, since=since).totalCount
                total_repo_commits: int = max(repo.get_commits(since=since).totalCount, 1)
            else:
                total_user_commits: int = repo.get_commits(author=user.name).totalCount
                total_repo_commits: int = max(repo.get_commits().totalCount, 1)

            # % of commits by user
            percent_commits: float = total_user_commits / total_repo_commits

            if percent_commits <= .01:  # skip if contribution is negligible (<1%)
                return

            stat: Statistics = annual if since else all_time

            for lang, count in {k: v for k, v in repo.get_languages().items() if k not in hide_languages}.items():
                if lang not in stat.languages:
                    stat.languages[lang] = count * percent_commits
                else:
                    stat.languages[lang] += count * percent_commits

            stat.commits += total_user_commits

        commits()
        commits(date_init_year)

    def to_percentage(languages: dict):
        total: float = sum(languages.values())

        percentage_languages: Dict[str, float] = {k : round(v / max(total, 1) * 100, 2) for k, v in languages.items()}

        return {k: v for k, v in sorted(percentage_languages.items(), key=lambda item: item[1], reverse=True)}

    annual.languages = to_percentage(annual.languages)
    all_time.languages = to_percentage(all_time.languages)

    all_time.followers = user.get_followers().totalCount
    all_time.contributions = len(contributed)

    print("Requests Remaining:", github.get_rate_limit().core.remaining)
    print("Requests Used:", req - github.get_rate_limit().core.remaining)
    print("Resets At:", github.get_rate_limit().core.reset)

    return annual, all_time
