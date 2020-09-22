import codecs, re, sys

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
    for event in user.get_public_events():
        if len == history: break
        if not event.public: continue
        len += 1
        str_list += f"{str_newline if len > 0 else ''} - {eventAsString(event).replace(str_newline, str_newline + '  ')}"

    print(str_list)

    str_template = codecs.open("README.template.md", "r", encoding="utf-8").read()\
        .replace("{{ activity }}", str_list)
    codecs.open("README.md", "w", encoding="utf-8").write(str_template)

    return


int_max_len = 50


def eventAsString(event):  # no switch statements :(
    payload = event.payload
    str_repo_name = f"[{event.repo.name}]({event.repo.html_url})"
    if event.type == "CommitCommentEvent":
        comment = payload["comment"]
        return f"Commented on commit [{comment['commit']['sha'][0:7]}]({comment.html_url}) " \
               f"in repository {str_repo_name}" + \
               quote(comment['body'], event.repo.html_url)
    elif event.type == "CreateEvent" or event.type == "DeleteEvent":
        str_name = payload['ref']
        return f"{'Created' if event.type == 'CreateEvent' else 'Deleted'} {payload['ref_type']} " \
               f"[{str_name}]({event.repo.html_url}/tree/{str_name}) in repository " + \
               str_repo_name
    elif event.type == "ForkEvent":
        return f"Forked repository {str_repo_name}"
    elif event.type == "GollumEvent":
        return f"Updated {payload['pages'].size()} wiki pages " \
               f"in repository {str_repo_name}"
    elif event.type == "IssueCommentEvent":
        comment = payload['comment']
        return f"Commented on issue [{payload['issue']['title']} (#{payload['issue']['number']})]({payload['comment']['html_url']}) " \
               f"from repository {str_repo_name}" + \
               quote(comment['body'], event.repo.html_url)
    elif event.type == "IssuesEvent":
        arr_pull_state = ["opened", "closed", "reopened"]
        arr_pull_assign = ["assigned", "unassigned"]

        str_pull_and_repo = f"[{payload['issue']['title']} (#{payload['issue']['number']})]({payload['issue']['html_url']}) " \
                             f"from repository {str_repo_name}"
        str_action = payload["action"]
        if contains(arr_pull_state, str_action):
            return f"{str_action.capitalize()} issue {str_pull_and_repo}"
        elif contains(arr_pull_assign, str_action):
            return f"{str_action.capitalize()} {payload['assignee']['name']} " \
                   f"{'to' if str_action == 'assigned' else 'from'} " \
                   f"issue {str_pull_and_repo}"
        else:  # label
            return f"{'Added' if str_action == 'labeled' else 'Removed'} label {payload['label']['name']}" \
                   f"{'to' if str_action == 'labeled' else 'from'} " \
                   f"issue {str_pull_and_repo}"
    elif event.type == "MemberEvent":
        return f"{payload['action'].capitalize()} [{payload['member']['name']}]({payload['member']['html_url']}) " \
               f"{'to' if payload['action'] == 'added' else 'in'} " \
               f"repository {str_repo_name}"
    elif event.type == "PublicEvent":
        return f"Set repository {str_repo_name} to public"
    elif event.type == "PullRequestEvent":
        arr_pull_state = ["opened", "closed", "reopened"]
        arr_pull_assign = ["assigned", "unassigned"]
        arr_pull_labeled = ["labeled", "unlabeled"]
        arr_pull_review = ["review_requested", "review_request_removed"]

        str_pull_and_repo = f"[{payload['pull_request']['title']} (#{payload['pull_request']['number']})]({payload['pull_request']['html_url']}) " \
                            f"in repository {str_repo_name}"
        str_action = payload["action"]
        if contains(arr_pull_state, str_action):
            return f"{str_action.capitalize()} pull request {str_pull_and_repo}"
        elif contains(arr_pull_assign, str_action):
            return f"{str_action.capitalize()} {payload['assignee']['name']} " \
                   f"{'to' if str_action == 'assigned' else 'from'} " \
                   f"pull request {str_pull_and_repo}"
        elif contains(arr_pull_labeled, str_action):
            return f"{'Added' if str_action == 'labeled' else 'Removed'} label {payload['label']['name']}" \
                   f"{'to' if str_action == 'labeled' else 'from'} " \
                   f"pull request {str_pull_and_repo}"
        elif contains(arr_pull_review, str_action):
            return f"{'Requested review' if str_action == 'review_requested' else 'Redacted review request'} for {str_action.capitalize()} pull request {str_pull_and_repo}"
        else:  # synchronize (with master)
            return f"Synchronized {str_pull_and_repo} with default branch"

    elif event.type == "PullRequestReviewCommentEvent":
        comment = payload['comment']
        return f"Commented on pull request {payload['issue']['title']} ([#{payload['issue']['number']})]({payload['comment']['html_url']}) " \
               f"in repository {str_repo_name}" + \
               quote(comment['body'], event.repo.html_url)
    elif event.type == "PushEvent":
        commit = payload['commits'][0]
        message = commit['message']
        return f"Added commit [{commit['sha'][0:7]}]({event.repo.html_url}/commit/{commit['sha']}) " \
               f"to repository {str_repo_name}" + \
               quote(message, event.repo.html_url)
    elif event.type == "ReleaseEvent":
        return f"{payload['action'].capitalize()} release {payload['release']['name']} in {str_repo_name}"
    elif event.type == "SponsorshipEvent":
        return f"Sponsored {str_repo_name}"
    elif event.type == "WatchEvent":
        return f"Starred repository {str_repo_name}"
    else:
        return f"*No template has been created for {event.type}*"  # wtf?


def quote(message, repo_url):
    s2 = message.replace('\n', '\n> ')
    return '\n > ' + truncate(re.sub(r'#(\d+)', '[#\\1](' + repo_url + '/issues/\\1)', s2.replace('\n', '\n' + '  ')), int_max_len) if s2 else ''


def truncate(string, max_len):
    s2 = string.replace('\n', '          \n')  # make new lines weighted more
    return s2 if len(s2) <= max_len else s2 + ' ...'


def contains(arr, string):
    for s in arr:
        if s == string:
            return True
    return False

if __name__ == "__main__":
    main()
