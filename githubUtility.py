import datetime as datetime
import re


# noinspection PyPep8Naming
def getStatistics(config):
    gh_user = config['gh_user']
    boolean_includePrivate = config['include_private']
    arr_hideLang = config['hide_lang']

    int_user_id = gh_user.id

    date_init_year = datetime.datetime.combine(datetime.date(datetime.date.today().year, 1, 1), datetime.time.min)

    map_lang_contrib = {}
    map_stats = {
        "commits"      : 0,
        "pulls"        : 0,
        "issues"       : 0,
        "contributions": 0
    }

    for repo in gh_user.get_repos():
        if repo.private and not boolean_includePrivate:
            continue

        # contributions
        if repo.owner.id != int_user_id:
            map_stats['contributions'] += 1  # no ++ :(
        # issues
        map_stats['issues'] += repo.get_issues(since=date_init_year, state="all", creator=gh_user.name).totalCount
        # pulls
        for pull in repo.get_pulls(state="all"):
            if pull.user.id == gh_user.id and pull.updated_at >= date_init_year:
                map_stats['pulls'] += 1
        # commits
        map_stats['commits'] += repo.get_commits(since=date_init_year, author=gh_user.name).totalCount

        # language statistics
        double_contrib = repo.get_commits(author=gh_user.name).totalCount / repo.get_commits().totalCount  # what % of commits is made by this user
        for lang, count in repo.get_languages().items():
            if not (lang in arr_hideLang):  # remove hidden config
                if not (lang in map_lang_contrib.keys()):
                    map_lang_contrib[lang] = count * double_contrib
                else:
                    map_lang_contrib[lang] += count * double_contrib

    double_total     = sum(map_lang_contrib.values())
    map_lang_contrib = sorted(map_lang_contrib.items(), key=lambda x: x[1], reverse=True)

    map_lang = []

    for i in map_lang_contrib:
        map_lang.append({
            "name": i[0],
            "percent": int((float(i[1]) * 100 / double_total) * 100) / 100  # as two point float
        })

    return {
        'languages' : map_lang,
        'statistics': map_stats
    }


# noinspection PyPep8Naming
def getEventAsMarkdown(github, event, now, max_lines=4):
    payload = event.payload
    # noinspection SpellCheckingInspection
    etype = event.type

    str_repo_url = github.get_repo(event.repo.id).html_url

    str_repo_name = f"[{event.repo.name}]({str_repo_url})"
    str_time_ago = f" *`{__getTimePassed(event.created_at, now)} ago`*"

    if etype == "CommitCommentEvent":
        comment = payload["comment"]
        return f"Commented on commit " \
               f"[{comment['commit']['sha'][0:7]}]({comment.html_url}) " \
               f"in repository {str_repo_name} " \
               f"{str_time_ago}" + \
               __quote(comment['body'], str_repo_url, max_lines)
    elif etype == "CreateEvent" or etype == "DeleteEvent":
        str_name = payload['ref']
        return f"{'Created' if etype == 'CreateEvent' else 'Deleted'} {payload['ref_type']} " \
               f"[{str_name}]({str_repo_url}/tree/{str_name}) " \
               f"in repository {str_repo_name}" + \
               f"{str_time_ago}"
    elif etype == "ForkEvent":
        return f"Forked repository " \
               f"{str_repo_name} " \
               f"{str_time_ago}"
    elif etype == "GollumEvent":
        return f"Updated {payload['pages'].size()} wiki pages " \
               f"in repository {str_repo_name} " \
               f"{str_time_ago}"
    elif etype == "IssueCommentEvent":
        comment = payload['comment']
        return f"Commented on issue " \
               f"[{payload['issue']['title']} (#{payload['issue']['number']})]({payload['comment']['html_url']}) " \
               f"from repository {str_repo_name} " \
               f"{str_time_ago}" + \
               __quote(comment['body'], str_repo_url, max_lines)
    elif etype == "IssuesEvent":
        arr_pull_state = ["opened", "closed", "reopened"]
        arr_pull_assign = ["assigned", "unassigned"]

        # link around issue name/no.
        str_pull_and_repo = f"[{payload['issue']['title']} (#{payload['issue']['number']})]({payload['issue']['html_url']}) " \
                            f"from repository {str_repo_name}"
        str_action = payload["action"]

        if __arrayContainsString(arr_pull_state, str_action):  # open/closed
            return f"{str_action.capitalize()} " \
                   f"issue {str_pull_and_repo} " \
                   f"{str_time_ago}"
        elif __arrayContainsString(arr_pull_assign, str_action):  # assign/unassign
            return f"{str_action.capitalize()} {payload['assignee']['name']} " \
                   f"{'to' if str_action == 'assigned' else 'from'} " \
                   f"issue {str_pull_and_repo} " \
                   f"{str_time_ago}"
        else:  # label
            return f"{'Added' if str_action == 'labeled' else 'Removed'} label {payload['label']['name']}" \
                   f"{'to' if str_action == 'labeled' else 'from'} " \
                   f"issue {str_pull_and_repo} " \
                   f"{str_time_ago}"
    elif etype == "MemberEvent":
        return f"{payload['action'].capitalize()} " \
               f"[{payload['member']['name']}]({payload['member']['html_url']}) " \
               f"{'to' if payload['action'] == 'added' else 'in'} " \
               f"repository {str_repo_name} " \
               f"{str_time_ago}"
    elif etype == "PublicEvent":
        return f"Set repository {str_repo_name} to public " \
               f"{str_time_ago}"
    elif etype == "PullRequestEvent":
        arr_pull_state = ["opened", "closed", "reopened"]
        arr_pull_assign = ["assigned", "unassigned"]
        arr_pull_labeled = ["labeled", "unlabeled"]
        arr_pull_review = ["review_requested", "review_request_removed"]

        str_pull_and_repo = f"[{payload['pull_request']['title']} (#{payload['pull_request']['number']})]({payload['pull_request']['html_url']}) " \
                            f"in repository {str_repo_name}"
        str_action = payload["action"]
        if __arrayContainsString(arr_pull_state, str_action):  # opened/closed
            return f"{str_action.capitalize()} " \
                   f"pull request {str_pull_and_repo} " \
                   f"{str_time_ago}"
        elif __arrayContainsString(arr_pull_assign, str_action):  # assigned
            return f"{str_action.capitalize()} " \
                   f"{payload['assignee']['name']} " \
                   f"{'to' if str_action == 'assigned' else 'from'} " \
                   f"pull request {str_pull_and_repo} " \
                   f"{str_time_ago}"
        elif __arrayContainsString(arr_pull_labeled, str_action):  # labeled
            return f"{'Added' if str_action == 'labeled' else 'Removed'} label {payload['label']['name']} " \
                   f"{'to' if str_action == 'labeled' else 'from'} " \
                   f"pull request {str_pull_and_repo} " \
                   f"{str_time_ago}"
        elif __arrayContainsString(arr_pull_review, str_action):  # reviewed
            return f"{'Requested review' if str_action == 'review_requested' else 'Redacted review request'} " \
                   f"for {str_action.capitalize()} " \
                   f"pull request {str_pull_and_repo} " \
                   f"{str_time_ago}"
        else:  # synchronize (with master)
            return f"Synchronized {str_pull_and_repo} " \
                   f"with default branch " \
                   f"{str_time_ago}"
    elif etype == "PullRequestReviewCommentEvent":
        comment = payload['comment']
        return f"Commented on pull request {payload['issue']['title']} " \
               f"([#{payload['issue']['number']})]({payload['comment']['html_url']}) " \
               f"in repository {str_repo_name} " \
               f"{str_time_ago}" + \
               __quote(comment['body'], str_repo_url, max_lines)
    elif etype == "PushEvent":
        commit = payload['commits'][0]
        message = commit['message']
        return f"Added commit [{commit['sha'][0:7]}]({str_repo_url}/commit/{commit['sha']}) " \
               f"to branch [{payload['ref'][11:]}]({str_repo_url}/tree/{payload['ref'][11:]}) " + \
               f"in repository {str_repo_name} {str_time_ago}" + \
               __quote(message, str_repo_url, max_lines)
    elif etype == "ReleaseEvent":
        return f"{payload['action'].capitalize()} " \
               f"release [{payload['release']['name']}]({payload['release']['html_url']}) in " \
               f"{str_repo_name} " \
               f"{str_time_ago}"
    elif etype == "SponsorshipEvent":
        return f"Sponsored {str_repo_name} " \
               f"{str_time_ago}"
    elif etype == "WatchEvent":
        return f"Starred repository {str_repo_name} " \
               f"{str_time_ago}"
    else:
        return f"*No template has been created for {etype}*"  # wtf?


#
#   Utility methods
#


# noinspection PyPep8Naming
def __arrayContainsString(arr, string):
    for s in arr:
        if s == string:
            return True
    return False


# noinspection PyPep8Naming
def __capLines(string, max_lines):
    lines = str.splitlines(string)
    if len(lines) > max_lines:
        return lines[0] + '\n' + lines[1] + '\n' + lines[2] + '\n' + lines[3] + '…'
    else:
        return string


def __quote(message, repo_url, max_lines):
    s2 = re.sub(r'\n\s*\n', '\n', message).replace('\n', '\n> ')
    return '\n  > ' + __capLines(re.sub(r'#(\d+)', '[#\\1](' + repo_url + '/issues/\\1)', s2.replace('\n', '\n  >  ')), max_lines) if s2 else ''


# noinspection PyPep8Naming
def __getTimePassed(time, now):
    passed = int((now - time).total_seconds())

    passed = {
        'years': int(passed / 31_536_000),
        'months': int(passed / 2_628_000),
        'days': int(passed / 86_400),
        'hours': int(passed / 3_600),
        'minutes': int(passed / 60),
        'seconds': passed
    }

    for k, v in passed.items():
        if v > 0 or k == 'seconds':
            return f"{v} {k[:(-1 if v == 1 else len(k))]}"

