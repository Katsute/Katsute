import codecs, re, sys
from datetime import datetime

from github import Github

history = 5


# first arg is python compile; second arg is oauth
def main():
    g = Github(sys.argv[1])
    user = g.get_user(g.get_user().login)

    # last 10 activities
    len = 0
    str_newline = '\n'
    str_list = ""
    now = datetime.utcnow()
    for event in user.get_public_events():
        if len == history: break
        if not event.public: continue
        len += 1
        str_list += f"{str_newline if len > 0 else ''} - {eventAsString(event, now).replace(str_newline, str_newline + '  ')}"

    print(str_list)

    str_template = codecs.open("README.template.md", "r", encoding="utf-8").read() \
        .replace("{{ activity }}", str_list)
    codecs.open("README.md", "w", encoding="utf-8").write(str_template)

    return


int_max_lines = 4


def eventAsString(event, now):  # no switch statements :(
    payload = event.payload
    str_repo_name = f"[{event.repo.name}]({event.repo.html_url})"
    ago = f" *`{getTimePassed(event.created_at, now)} ago`*"
    if event.type == "CommitCommentEvent":
        comment = payload["comment"]
        return f"Commented on commit [{comment['commit']['sha'][0:7]}]({comment.html_url}) " \
               f"in repository {str_repo_name} {ago}" + \
               quote(comment['body'], event.repo.html_url)
    elif event.type == "CreateEvent" or event.type == "DeleteEvent":
        str_name = payload['ref']
        return f"{'Created' if event.type == 'CreateEvent' else 'Deleted'} {payload['ref_type']} " \
               f"[{str_name}]({event.repo.html_url}/tree/{str_name}) in repository " + \
               str_repo_name + ago
    elif event.type == "ForkEvent":
        return f"Forked repository {str_repo_name} {ago}"
    elif event.type == "GollumEvent":
        return f"Updated {payload['pages'].size()} wiki pages " \
               f"in repository {str_repo_name} {ago}"
    elif event.type == "IssueCommentEvent":
        comment = payload['comment']
        return f"Commented on issue [{payload['issue']['title']} (#{payload['issue']['number']})]({payload['comment']['html_url']}) " \
               f"from repository {str_repo_name} {ago}" + \
               quote(comment['body'], event.repo.html_url)
    elif event.type == "IssuesEvent":
        arr_pull_state = ["opened", "closed", "reopened"]
        arr_pull_assign = ["assigned", "unassigned"]

        str_pull_and_repo = f"[{payload['issue']['title']} (#{payload['issue']['number']})]({payload['issue']['html_url']}) " \
                            f"from repository {str_repo_name}"
        str_action = payload["action"]
        if contains(arr_pull_state, str_action):
            return f"{str_action.capitalize()} issue {str_pull_and_repo} {ago}"
        elif contains(arr_pull_assign, str_action):
            return f"{str_action.capitalize()} {payload['assignee']['name']} " \
                   f"{'to' if str_action == 'assigned' else 'from'} " \
                   f"issue {str_pull_and_repo} {ago}"
        else:  # label
            return f"{'Added' if str_action == 'labeled' else 'Removed'} label {payload['label']['name']}" \
                   f"{'to' if str_action == 'labeled' else 'from'} " \
                   f"issue {str_pull_and_repo} {ago}"
    elif event.type == "MemberEvent":
        return f"{payload['action'].capitalize()} [{payload['member']['name']}]({payload['member']['html_url']}) " \
               f"{'to' if payload['action'] == 'added' else 'in'} " \
               f"repository {str_repo_name} {ago}"
    elif event.type == "PublicEvent":
        return f"Set repository {str_repo_name} to public {ago}"
    elif event.type == "PullRequestEvent":
        arr_pull_state = ["opened", "closed", "reopened"]
        arr_pull_assign = ["assigned", "unassigned"]
        arr_pull_labeled = ["labeled", "unlabeled"]
        arr_pull_review = ["review_requested", "review_request_removed"]

        str_pull_and_repo = f"[{payload['pull_request']['title']} (#{payload['pull_request']['number']})]({payload['pull_request']['html_url']}) " \
                            f"in repository {str_repo_name}"
        str_action = payload["action"]
        if contains(arr_pull_state, str_action):
            return f"{str_action.capitalize()} pull request {str_pull_and_repo} {ago}"
        elif contains(arr_pull_assign, str_action):
            return f"{str_action.capitalize()} {payload['assignee']['name']} " \
                   f"{'to' if str_action == 'assigned' else 'from'} " \
                   f"pull request {str_pull_and_repo} {ago}"
        elif contains(arr_pull_labeled, str_action):
            return f"{'Added' if str_action == 'labeled' else 'Removed'} label {payload['label']['name']}" \
                   f"{'to' if str_action == 'labeled' else 'from'} " \
                   f"pull request {str_pull_and_repo} {ago}"
        elif contains(arr_pull_review, str_action):
            return f"{'Requested review' if str_action == 'review_requested' else 'Redacted review request'} for {str_action.capitalize()} pull request {str_pull_and_repo} {ago}"
        else:  # synchronize (with master)
            return f"Synchronized {str_pull_and_repo} with default branch {ago}"

    elif event.type == "PullRequestReviewCommentEvent":
        comment = payload['comment']
        return f"Commented on pull request {payload['issue']['title']} ([#{payload['issue']['number']})]({payload['comment']['html_url']}) " \
               f"in repository {str_repo_name} {ago}" + \
               quote(comment['body'], event.repo.html_url)
    elif event.type == "PushEvent":
        commit = payload['commits'][0]
        message = commit['message']
        return f"Added commit [{commit['sha'][0:7]}]({event.repo.html_url}/commit/{commit['sha']}) " \
               f"to branch [{payload['ref'][11:]}]({event.repo.html_url}/tree/{payload['ref'][11:]}) " + \
               f"in repository {str_repo_name} {ago}" + \
               quote(message, event.repo.html_url)
    elif event.type == "ReleaseEvent":
        return f"{payload['action'].capitalize()} release {payload['release']['name']} in {str_repo_name} {ago}"
    elif event.type == "SponsorshipEvent":
        return f"Sponsored {str_repo_name} {ago}"
    elif event.type == "WatchEvent":
        return f"Starred repository {str_repo_name} {ago}"
    else:
        return f"*No template has been created for {event.type}*"  # wtf?


def quote(message, repo_url):
    s2 = re.sub(r'\n\s*\n', '\n', message).replace('\n', '\n> ')
    return '\n > ' + truncate(re.sub(r'#(\d+)', '[#\\1](' + repo_url + '/issues/\\1)', s2.replace('\n', '\n >  ')),
                              int_max_lines) if s2 else ''


def truncate(string, max_lines):
    lines = string.split('\n', 1)
    if len(lines) > max_lines:
        return lines[0] + '\n' + lines[1] + '\n' + lines[2] + '\n' + lines[3]
    else:
        return string


def contains(arr, string):
    for s in arr:
        if s == string:
            return True
    return False


def getTimePassed(time, now):
    passed = int((now - time).total_seconds())
    inYears = int(passed / 31_536_000)
    inMonths = int(passed / 2_628_000)
    inDays = int(passed / 86400)
    inHours = int(passed / 3600)
    inMinutes = int(passed / 60)

    if inYears > 0:
        return f"{inYears} year{'s' if inYears != 1 else ''}"
    elif inMonths > 0:
        return f"{inMonths} month{'s' if inMonths != 1 else ''}"
    elif inDays > 0:
        return f"{inDays} day{'s' if inDays != 1 else ''}"
    elif inHours > 0:
        return f"{inHours} hour{'s' if inHours != 1 else ''}"
    elif inMinutes > 0:
        return f"{inMinutes} minute{'s' if inMinutes != 1 else ''}"
    else:
        return f"{passed} second{'s' if passed != 1 else ''}"


if __name__ == "__main__":
    main()
