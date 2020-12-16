import codecs

from liquid import Liquid


class Card:

    TEMPLATE = codecs.open("templates/card.liquid", 'r', encoding="utf-8").read()

    _args = {
        "width": 495,
        "height": 300 ,  # this must be systematically generated
        "css": {}
    }

    BODY = None

    def __init__(self, title: str, body: str, **kwargs):
        self._args['title'] = title
        self.BODY = codecs.open(body, 'r', encoding="utf-8").read()
        self._args.update(kwargs.copy())
        return

    def render(self):
        return Liquid(
            codecs
                .open("templates/card.liquid", 'r', encoding="utf-8")
                .read()
                .replace("{{ body }}", self.BODY if self.BODY else ''),
            **self._args
        ).render()  # TODO: minify
