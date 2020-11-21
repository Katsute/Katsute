import codecs
import os
import sys

import yaml
import githubUtility

import imgkit
from PIL import Image
from github import Github
from liquid import Liquid
from pyvirtualdisplay import Display

from datetime import datetime
from pytz import timezone


def main():
    # init
    if not sys.argv[1]:
        print("Failed to update file (no oauth token provided)")

    github = Github(sys.argv[1])
    user   = github.get_user()
    req    = github.get_rate_limit().core.remaining
    now    = datetime.utcnow()
    print("Request Available:", req)

    config = yaml.load(open("config.yml", 'r'), Loader=yaml.FullLoader)

    display = None if len(sys.argv) >= 3 else Display(size=(1920, 1080)).start()
    if display:
        print("Loaded virtual display")

# image
    map_statistics = githubUtility.get_statistics(
        user            = user,
        private         = config['include_private_repos'],
        hide_languages  = config['hide_languages'],
        max_languages   = config['max_languages'],
        hide_repos      = config['hide_repos']
    )

    css = codecs.open("templates/style.css", 'r', encoding="utf-8").read()

    # contributions
    str_file = "contributions"
    str_template = codecs.open("templates/contributions.html", 'r', encoding="utf-8").read()
    str_html = Liquid(str_template, statistics=map_statistics['statistics'], css=css).render()
    __html2image(str_html, str_file, options=config['render']['options'])

    # languages
    str_file = "languages"
    str_template = codecs.open("templates/languages.html", 'r', encoding="utf-8").read()
    str_html = Liquid(str_template, languages=map_statistics['languages'], css=css).render()
    __html2image(str_html, str_file, options=config['render']['options'], threshold=config['render']['chroma_threshold'])

# readme
    codecs.open("README.md", 'w', encoding="utf-8").write(codecs.open("README.template.md", 'r', encoding="utf-8").read())  # skip below
    '''
    str_template = codecs.open("README.template.md", 'r', encoding="utf-8").read()

    # {{ activity }}

    named_user = github.get_user(github.get_user().login)
    str_activity = ""
    for i in range(config['max_history']):
        event = named_user.get_public_events()[i]
        str_activity += \
            ('\n' if i > 0 else '') + \
            " - " + githubUtility.getEventAsMarkdown(github, event, now, config['max_lines']).replace('\n', "\n  ")  # indent list

    # {{ updated }}
    eastern     = timezone('US/Eastern')
    localized   = datetime.now(eastern)
    sdf         = '%B %d, %Y at %I:%M %p (EST)'
    str_updated = localized.strftime(sdf)

    # parse
    str_output = Liquid(str_template, activity=str_activity, updated=str_updated).render()
    codecs.open("README.md", 'w', encoding="utf-8").write(str_output)
    '''
# cleanup
    if display:
        display.stop()

    print("Requests Remaining:", github.get_rate_limit().core.remaining)
    print("Requests Used:", req - github.get_rate_limit().core.remaining)

    return


# noinspection SpellCheckingInspection
def __html2image(str_html, str_file, config=None, options=None, threshold=0):
    imgkit.from_string(str_html, str_file, config=config, options=options)
    if os.path.exists(f"{str_file}.png"):
        os.remove(f"{str_file}.png")
    os.rename(str_file, f"{str_file}.png")  # wkhtmltoimg doesn't work with file extensions for some reason
    __remove_color(f"{str_file}.png", 0, 255, 0, threshold)
    return


def __remove_color(img_path, r, g, b, threshold=0):
    img  = Image.open(img_path)
    img  = img.convert("RGBA")
    data = img.getdata()

    new = []
    for item in data:
        if \
                r-threshold <= item[0] <= r+threshold and \
                g-threshold <= item[1] <= g+threshold and \
                b-threshold <= item[2] <= b+threshold:
            new.append((255, 255, 255, 0))
        else:
            new.append(item)

    img.putdata(new)
    img.save(img_path, "PNG")


if __name__ == "__main__":
    main()

