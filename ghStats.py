import datetime


# noinspection PyPep8Naming
def getStatistics(config):
    gh_user                = config['gh_user']
    boolean_includePrivate = config['include_private']
    arr_hideLang           = config['hide_lang']
    
    int_user_id = gh_user.id

    date_init_year  = datetime.datetime.combine(datetime.date(datetime.date.today().year, 1, 1), datetime.time.min)
    date_init_today = datetime.datetime.combine(datetime.date.today(), datetime.time())

    map_lang_contrib = {}
    map_stats = {
        "commits"            : 0,
        "commits_today"      : 0,
        "pulls"              : 0,
        "pulls_today"        : 0,
        "issues"             : 0,
        "issues_today"       : 0,
        "contributions"      : 0
    }

    for repo in gh_user.get_repos():
        if repo.private and not boolean_includePrivate:
            continue
            
        # contributions
        if repo.owner.id != int_user_id:
            map_stats['contributions'] += 1  # no ++ :(
        # issues
        map_stats['issues'] += repo.get_issues(since=date_init_year, state="all", creator=gh_user.name).totalCount
        map_stats['issues_today'] += repo.get_issues(since=date_init_today, state="all", creator=gh_user.name).totalCount
        # pulls
        for pull in repo.get_pulls(state="all"):
            if pull.user.id == gh_user.id and pull.updated_at >= date_init_year:
                map_stats['pulls'] += 1
                if pull.updated_at >= date_init_today:
                    map_stats['pulls_today'] += 1
        # commits
        map_stats['commits'] += repo.get_commits(author=gh_user.name).totalCount
        map_stats['commits_today'] += repo.get_commits(author=gh_user.name,since=date_init_today).totalCount

        # language statistics
        double_contrib = map_stats['commits'] / repo.get_commits().totalCount  # what % of commits is made by this gh_User
        for lang, count in repo.get_languages().items():
            if not (lang in arr_hideLang):  # remove hidden config
                if not (lang in map_lang_contrib.keys()):
                    map_lang_contrib[lang] = count * double_contrib
                else:
                    map_lang_contrib[lang] += count * double_contrib

    # lang gist
    double_total = sum(map_lang_contrib.values())
    map_lang_contrib = sorted(map_lang_contrib.items(), key=lambda x: x[1], reverse=True)

    map_lang = {}

    for i in map_lang_contrib:
        map_lang[i[0]] = float(i[1]) * 100 / double_total

    # str_gist += f"{lang:11}{str_bar} {percent:05.2f}%\n"

    return {
        'languages': map_lang,
        'statistics': map_stats
    }


def getProgessBar(percent, size):
    int_bar = int((percent/100)*20)
    return ('█' * int_bar) + ('░' * (size - int_bar))

