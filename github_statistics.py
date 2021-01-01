import datetime as datetime

from github import Github
from github.GithubException import UnknownObjectException


class Statistics:
    commits = 0
    contributions = 0
    issues = 0
    pulls = 0
    stars = 0
    followers = 0
    languages = {}


def get_statistics(
        token: str,
        include_private=False,
        hide_languages: dict = None,
        hide_repositories: dict = None):
    if hide_repositories is None:
        hide_repositories = []
    if hide_languages is None:
        hide_languages = []

    github = Github(token)
    user = github.get_user()
    username = user.name
    user_id = user.id

    req = github.get_rate_limit().core.remaining
    print("Request Available:", req)

    date_init_year = datetime.datetime.combine(datetime.date(datetime.date.today().year, 1, 1), datetime.time.min)

    annual = Statistics()
    all_time = Statistics()

    repositories = set()
    contributed = set()

    for issue in github.search_issues('', author=username):
        repo = issue.repository
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
        repo = github.get_repo(repository)

        def commits(since: datetime = None):
            if since:
                total_user_commits = repo.get_commits(author=user.name, since=since).totalCount
                total_repo_commits = max(repo.get_commits(since=since).totalCount, 1)
            else:
                total_user_commits = repo.get_commits(author=user.name).totalCount
                total_repo_commits = max(repo.get_commits().totalCount, 1)

            # % of commits by user
            percent_commits = total_user_commits / total_repo_commits

            if percent_commits <= .01:  # skip if contribution is negligible (<1%)
                return

            stat = annual if since else all_time

            for lang, count in repo.get_languages().items():
                if lang in hide_languages:
                    continue

                if lang not in stat.languages:
                    stat.languages[lang] = count * percent_commits
                else:
                    stat.languages[lang] += count * percent_commits

            stat.commits += total_user_commits

        commits()
        commits(date_init_year)

    def to_percentage(languages: dict):
        total = sum(languages.values())

        percentage_languages = dict()

        for k, v in languages.items():
            percentage_languages[k] = round(v / max(total, 1) * 100, 2)

        return {k: v for k, v in sorted(percentage_languages.items(), key=lambda item: item[1], reverse=True)}

    annual.languages = to_percentage(annual.languages)
    all_time.languages = to_percentage(all_time.languages)

    all_time.followers = user.get_followers().totalCount
    all_time.contributions = len(repositories)

    print("Requests Remaining:", github.get_rate_limit().core.remaining)
    print("Requests Used:", req - github.get_rate_limit().core.remaining)
    print("Resets At:", github.get_rate_limit().core.reset)

    return annual, all_time
