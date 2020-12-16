import codecs

from card.card import Card


class LanguageCard(Card):

    def __init__(self, languages: dict):
        super().__init__(
            "Most Used Languages",
            "templates/languages.liquid",
            languages = languages,
            css="""
                .stat{
                    font: 600 14px 'Segoe UI', "Helvetica Neue", Sans-Serif; fill: #333;
                }
                """
        )
