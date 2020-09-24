import codecs
import re
import sys

from datetime import datetime
from pytz import timezone
from github import Github

import utility

int_history   = 5
int_max_lines = 4


# first arg is python compile; second arg is oauth
def main():
    g    = Github(sys.argv[1])
    user = g.get_user(g.get_user().login)
    now  = datetime.utcnow()

    str_template = codecs.open("README.template.md", "r", encoding="utf-8").read()

    # {{ activity }}

    str_list = ""
    for i in range(int_history):
        event = user.get_public_events()[i]

        str_list += '\n' if i > 0 else ''  # add new line before each except first
        str_list += " - " + eventAsString(event, now).replace('\n', '\n' + ' ')
    str_template = str_template.replace("{{ activity }}", str_list)

    # {{ updated }}

    eastern   = timezone('US/Eastern')
    localized = datetime.now(eastern)
    sdf       = '%B %d, %Y at %I:%M %p (EST)'
    str_template = str_template.replace("{{ updated }}", localized.strftime(sdf))

    # write

    codecs.open("README.md", "w", encoding="utf-8").write(str_template)

    return


# for sake of readability, f-strings can be used even when they are not needed
# (this program is small enough that it won't lose any performance)
# noinspection PyPep8Naming
def eventAsString(event, now):  # no switch statements :(
    payload = event.payload
    # noinspection SpellCheckingInspection
    etype   = event.type

    str_repo_url = event.repo.url

    str_repo_name = f"[{event.repo.name}]({str_repo_url})"
    str_time_ago  = f" *`{getTimePassed(event.created_at, now)} ago`*"

    if etype == "CommitCommentEvent":
        comment = payload["comment"]
        return f"Commented on commit " \
               f"[{comment['commit']['sha'][0:7]}]({comment.html_url}) " \
               f"in repository {str_repo_name} " \
               f"{str_time_ago}" + \
               quote(comment['body'], str_repo_url)
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
               quote(comment['body'], str_repo_url)
    elif etype == "IssuesEvent":
        arr_pull_state  = ["opened", "closed", "reopened"]
        arr_pull_assign = ["assigned", "unassigned"]

        # link around issue name/no.
        str_pull_and_repo = f"[{payload['issue']['title']} (#{payload['issue']['number']})]({payload['issue']['html_url']}) " \
                            f"from repository {str_repo_name}"
        str_action = payload["action"]

        if utility.contains(arr_pull_state, str_action):  # open/closed
            return f"{str_action.capitalize()}" \
                   f"issue {str_pull_and_repo} " \
                   f"{str_time_ago}"
        elif utility.contains(arr_pull_assign, str_action):  # assign/unassign
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
        arr_pull_state   = ["opened", "closed", "reopened"]
        arr_pull_assign  = ["assigned", "unassigned"]
        arr_pull_labeled = ["labeled", "unlabeled"]
        arr_pull_review  = ["review_requested", "review_request_removed"]

        str_pull_and_repo = f"[{payload['pull_request']['title']} (#{payload['pull_request']['number']})]({payload['pull_request']['html_url']}) " \
                            f"in repository {str_repo_name}"
        str_action = payload["action"]
        if utility.contains(arr_pull_state, str_action):  # opened/closed
            return f"{str_action.capitalize()} " \
                   f"pull request {str_pull_and_repo} " \
                   f"{str_time_ago}"
        elif utility.contains(arr_pull_assign, str_action):  # assigned
            return f"{str_action.capitalize()} " \
                   f"{payload['assignee']['name']} " \
                   f"{'to' if str_action == 'assigned' else 'from'} " \
                   f"pull request {str_pull_and_repo} " \
                   f"{str_time_ago}"
        elif utility.contains(arr_pull_labeled, str_action):  # labeled
            return f"{'Added' if str_action == 'labeled' else 'Removed'} label {payload['label']['name']} " \
                   f"{'to' if str_action == 'labeled' else 'from'} " \
                   f"pull request {str_pull_and_repo} " \
                   f"{str_time_ago}"
        elif utility.contains(arr_pull_review, str_action):  # reviewed
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
               quote(comment['body'], str_repo_url)
    elif etype == "PushEvent":
        commit  = payload['commits'][0]
        message = commit['message']
        return f"Added commit [{commit['sha'][0:7]}]({str_repo_url}/commit/{commit['sha']}) " \
               f"to branch [{payload['ref'][11:]}]({str_repo_url}/tree/{payload['ref'][11:]}) " + \
               f"in repository {str_repo_name} {str_time_ago}" + \
               quote(message, str_repo_url)
    elif etype == "ReleaseEvent":
        return f"{payload['action'].capitalize()} " \
               f"release {payload['release']['name']} in " \
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


def quote(message, repo_url):
    s2 = re.sub(r'\n\s*\n', '\n', message).replace('\n', '\n> ')
    return '\n > ' + utility.truncate(re.sub(r'#(\d+)', '[#\\1](' + repo_url + '/issues/\\1)', s2.replace('\n', '\n >  ')),int_max_lines) if s2 else ''


# noinspection PyPep8Naming
def getTimePassed(time, now):
    passed = int((now - time).total_seconds())

    passed = {
        'years'  : int(passed / 31_536_000),
        'months' : int(passed / 2_628_000),
        'days'   : int(passed / 86_400),
        'hours'  : int(passed / 3_600),
        'minutes': int(passed / 60),
        'seconds': passed
    }

    for k, v in passed.items():
        if v > 0 or k == 'seconds':
            return f"{v} {k[:(-1 if v == 1 else len(k))]}"


if __name__ == "__main__":
    main()
