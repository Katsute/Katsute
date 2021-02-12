import math
from typing import Dict

from card.card import Card


class LanguageCard(Card):

    def __init__(self, languages: Dict[str, float]):
        super().__init__(
            "Most Used Languages",
            "templates/languages.liquid",
            languages=languages,
            css="""
                .stat{
                    font: 600 14px 'Segoe UI', "Helvetica Neue", Sans-Serif; fill: #333;
                }
                """
        )
        self.increase_height(len(languages) * 25)
        return


class LanguageCoverageCard(Card):

    def __init__(self, languages: Dict[str, float], limit: int):
        super().__init__(
            f"Top { limit } Languages",
            "templates/languages_coverage.liquid",
            languages=languages,
            css="""
                .stat{
                    font: 600 14px 'Segoe UI', "Helvetica Neue", Sans-Serif; fill: #333;
                }
                
                circle{
                    fill: #202020;
                    stroke: #FFFFFF;
                    stroke-width: 1;
                }
                
                polyline{
                    stroke: #F3F2F1;
                    stroke-width: .25;
                }
                
                polygon{
                    fill: #2F80ED;
                    fill-opacity: .3;
                    stroke: #2F80ED;
                    stroke-width: 2;
                }
                """
        )
        self.args['height'] = self.args['width']

        # generate axis and poly coords
        limit: int = len(languages) if len(languages) <= limit else limit
        angle: float = 2*math.pi/max(limit, 1)
        offset: float = math.radians(-90)
        radius: float = self.args['width'] / 4

        top: float = list(languages.values())[0]
        axis, taxis, percent = [], [], []
        for i in range(limit):
            co: float = math.cos(i*angle+offset)
            si: float = math.sin(i*angle+offset)

            axis.append({
                'x': radius * co,
                'y': radius * si
            })
            taxis.append({  # text axis
                'x': (radius + 40) * co,
                'y': (radius + 40) * si
            })
            percent.append({
                'x': list(languages.values())[i] / top * radius * co,
                'y': list(languages.values())[i] / top * radius * si
            })
        self.args['axis'] = axis
        self.args['taxis'] = taxis
        self.args['percent'] = percent
        self.args['radius'] = radius

        return
