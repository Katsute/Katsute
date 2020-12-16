import codecs
import re

from liquid import Liquid


class Card:
    MINIFY = re.compile("^\\s+|\\r?\\n")

    TEMPLATE = codecs.open("templates/card.liquid", 'r', encoding="utf-8").read()

    def __init__(self, title: str, body: str, **kwargs):
        self.args = {
            "title": title
        }
        self.args.update({
                             "width": 400,
                             "height": 70,  # this must be systematically generated
                             "css": {}
                         }.copy())
        self.args.update(kwargs.copy())
        self.BODY = codecs.open(body, 'r', encoding="utf-8").read()
        return

    def increase_height(self, height: int):
        self.args['height'] += height
        return

    def render(self):
        return \
            self.MINIFY.sub('',
                            Liquid(
                                codecs.open("templates/card.liquid", 'r', encoding="utf-8")
                                .read()
                                .replace("{{ body }}", self.BODY if self.BODY else ''),
                                **self.args
                            ).render()
                            )
