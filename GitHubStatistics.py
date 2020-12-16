import datetime as datetime

from github import Github


class Statistics:
    contributions = 0
    issues = 0
    pulls = 0
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

    req = github.get_rate_limit().core.remaining
    print("Request Available:", req)

    date_init_year = datetime.datetime.combine(datetime.date(datetime.date.today().year, 1, 1), datetime.time.min)

    annual = Statistics()
    all_time = Statistics()

    repositories = set()
    '''
    for issue in github.search_issues('', author=username, type="issues"):
        repo = issue.repository
        if repo.id in hide_repositories:
            continue
        repositories.add(repo.id)

        pull = issue.pull_request

        if pull:
            all_time.pulls += 1
            if issue.created_at >= date_init_year:
                annual.pulls += 1
        else:
            all_time.issues += 1
            if issue.created_at >= date_init_year:
                annual.issues += 1
    '''
    for repo in user.get_repos("all" if include_private else "public"):
        repositories.add(repo.id)

    for repository in repositories:
        repo = github.get_repo(repository)

        def commits(since: datetime = None):
            # % of commits by user
            percent_commits = \
                repo.get_commits(author=user.name, since=since).totalCount / repo.get_commits(since=since).totalCount \
                    if since else \
                    repo.get_commits(author=user.name).totalCount / repo.get_commits().totalCount

            if percent_commits <= .01:  # skip if contribution is negligible (<1%)
                return

            # assumption is incorrect, there is no outer variable named 'lang'
            # noinspection PyShadowingNames
            for lang, count in repo.get_languages().items():
                if lang in hide_languages:
                    continue

                stat = annual if since else all_time

                if lang not in stat.languages:
                    stat.languages['lang'] = count * percent_commits
                else:
                    stat.languages['lang'] += count * percent_commits

        commits()
        commits(date_init_year)

    # noinspection SpellCheckingInspection
    for langs in [annual.languages, all_time.languages]:
        total = sum(langs.values())
        for lang in langs.keys():  # get language usage as percent
            langs[lang] = round(langs[lang] / total * 100, 2)

    annual.languages = sorted(annual.languages.items(), key=lambda item: item[1])
    all_time.languages = sorted(all_time.languages.items(), key=lambda item: item[1])

    print("Requests Remaining:", github.get_rate_limit().core.remaining)
    print("Requests Used:", req - github.get_rate_limit().core.remaining)

    return annual, all_time
