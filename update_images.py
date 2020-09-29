import codecs
import os
import sys

import imgkit
from PIL import Image
from github import Github
from liquid import Liquid
from pyvirtualdisplay import Display

import githubUtility

int_languages = 8
boolean_include_private = True
arr_hide_lang = ["HTML", "JavaScript", "CSS"]

int_threshold = 130

render_options = {
    "format"    : "png",
    "width"     : 400,
    "quality"   : 100,
}


def main():
    github = Github(sys.argv[1])
    user   = github.get_user()

    req = github.get_rate_limit().core.remaining
    print("Initial requests:", req)

    # create a virtual display if on workflow
    display = None if len(sys.argv) >= 2 and bool(sys.argv[2]) else Display(size=(1920, 1080)).start()

    map_statistics = githubUtility.getStatistics({
        'gh_user'           : user,
        'include_private'   : boolean_include_private,
        'hide_lang'         : arr_hide_lang
    })

    css = codecs.open("templates/style.css", "r", encoding="utf-8").read()

    # <contributions>
    str_file = "contributions"
    str_template = codecs.open("templates/contributions.html", "r", encoding="utf-8").read()
    str_html = Liquid(str_template, statistics=map_statistics['statistics'], css=css).render()

    __HTML2Image(str_html, str_file, options=render_options)
    __removeColor(f"{str_file}.png", 0, 255, 0, int_threshold)

    # <languages>
    str_file = "languages"
    str_template = codecs.open("templates/languages.html", "r", encoding="utf-8").read()
    str_html = Liquid(str_template, languages=map_statistics['languages'], css=css).render()
    __HTML2Image(str_html, str_file, options=render_options)
    __removeColor(f"{str_file}.png", 0, 255, 0, int_threshold)

    # cleanup

    if display:
        display.stop()

    print("Requests remaining:", github.get_rate_limit().core.remaining)
    print("Requests used:", req - github.get_rate_limit().core.remaining)

    return

#
#   Utility methods
#


# noinspection PyPep8Naming,SpellCheckingInspection
def __HTML2Image(str_html, str_file, config=None, options=None):
    imgkit.from_string(str_html, str_file, config=config, options=options)
    if os.path.exists(f"{str_file}.png"):
        os.remove(f"{str_file}.png")
    os.rename(str_file, f"{str_file}.png")  # wkhtmltoimg doesn't work with file extensions for some reason
    __removeColor(f"{str_file}.png", 0, 255, 0, int_threshold)
    return


# noinspection PyPep8Naming
def __removeColor(img_path, r, g, b, threshold=0):
    img = Image.open(img_path)
    img = img.convert("RGBA")
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

