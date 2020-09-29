import codecs
import sys

from datetime import datetime
from github import Github
from liquid import Liquid
from pytz import timezone

import githubUtility

int_history   = 5
int_max_lines = 4

if __name__ == "__main__":
    github = Github(sys.argv[1])
    user   = github.get_user(github.get_user().login)  # get named user (auth user is missing methods)
    now    = datetime.utcnow()

    req    = github.get_rate_limit().core.remaining
    print("Initial requests:", req)

    str_template = codecs.open("README.template.md", "r", encoding="utf-8").read()

    # {{ activity }}

    str_activity = ""
    for i in range(int_history):
        event = user.get_public_events()[i]

        str_activity += '\n' if i > 0 else ''  # add new line between each
        str_activity += " - " + githubUtility.getEventAsMarkdown(github, event, now, int_max_lines).replace('\n', "\n ")  # indent list

    # {{ updated }}

    eastern   = timezone('US/Eastern')
    localized = datetime.now(eastern)
    sdf       = '%B %d, %Y at %I:%M %p (EST)'
    str_updated = localized.strftime(sdf)

    # parse

    str_output = Liquid(str_template, activity=str_activity, updated=str_updated).render()
    codecs.open("README.md", 'w', encoding="utf-8").write(str_output)

    print("Requests remaining:", github.get_rate_limit().core.remaining)
    print("Requests used:", req - github.get_rate_limit().core.remaining)

