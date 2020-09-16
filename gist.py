import sys
import datetime

from github import Github, InputFileContent

# configuration
g_boolean_include_private = True
g_arr_hide_lang = ["HTML", "JavaScript", "CSS"]


# first arg is python compile; second arg is oauth
def main():
    g = Github(sys.argv[1])
    user = g.get_user()
    int_userid = user.id
    date_year = datetime.datetime.combine(datetime.date(datetime.date.today().year, 1, 1), datetime.time.min)

    map_lang = dict()
    int_commits = int_pulls = int_issues = int_contributions = 0

    for repo in user.get_repos(type="all"):
        if g_boolean_include_private and repo.private:
            continue

        # contributions
        if repo.owner.id != int_userid:
            int_contributions += 1  # no ++ :(
        # issues
        int_issues += repo.get_issues(since=date_year, state="all", creator=user.name).totalCount
        # pulls
        for pull in repo.get_pulls(state="all"):
            if pull.user.id == user.id and pull.updated_at >= date_year:
                int_pulls += 1
        # commits
        int_user_commits = repo.get_commits(author=user.name).totalCount
        int_commits += int_user_commits

        # language statistics
        double_contrib = int_user_commits / repo.get_commits().totalCount  # what % of commits is made by this user
        for lang, count in repo.get_languages().items():
            if not (lang in g_arr_hide_lang):  # remove hidden config
                if not (lang in map_lang.keys()):
                    map_lang[lang] = count * double_contrib
                else:
                    map_lang[lang] += count * double_contrib

    # statistics gist
    map_stats = {
        'Total Commits': int_commits,
        'Total PRs': int_pulls,
        'Total Issues': int_issues,
        'Contributed to': int_contributions
    }

    str_gist = ""
    for k, v in map_stats.items():
        str_gist += f"{k + ':':20}{v}\n"

    for gist in user.get_gists():
        for name, file in gist.files.items():
            if file.filename == "📊 GitHub Stat":
                gist.edit(files={file.filename: InputFileContent(content=str_gist)})

    print(str_gist)
    # lang gist
    double_total = sum(map_lang.values())
    map_lang = sorted(map_lang.items(), key=lambda x: x[1], reverse=True)

    str_gist = ""

    for i in map_lang:
        lang, percent = i[0], float(i[1]) * 100 / double_total
        int_bar = int(percent/100*20)
        str_bar = ('█' * int_bar) + ('░' * (20-int_bar))

        str_gist += f"{lang:15}{str_bar:25}{percent:05.2f}%\n"

    for gist in user.get_gists():
        for name, file in gist.files.items():
            if file.filename == "📊 Top Languages":
                gist.edit(files={file.filename: InputFileContent(content=str_gist)})
    print(str_gist)
    return


if __name__ == "__main__":
    main()
