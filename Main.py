import sys

from pandas import DataFrame

import yaml
import GitHubStatistics
import Chart as ch
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as ply

required = dict(
    weekday_commits = False,
    weekday_repo_commits = False,
    year_languages = False,
    all_languages = False
)

def main(args: list):
    size = len(args)

    if size < 1:
        print("Failed to update file (no oauth token provided)")
        return

    token = str(args[0])
    config = yaml.load(open("config.yml", 'r'), Loader=yaml.FullLoader)

    #annual_statistics, all_time_statistics = GitHubStatistics.get_statistics(
    #    token,
    #    include_private=config['include_private_repositories'],
    #    hide_repositories=config['hide_repositories'],
    #    hide_languages=config['hide_languages']
    #)
    all_time_statistics = GitHubStatistics.Statistics()
    all_time_statistics.languages = {
        "Java": .859,
        "Python": .0556,
        "HTML": .052,
        "Liquid": .0174,
        "JavaScript": .0044,
    }

    df = DataFrame(all_time_statistics.languages.items(), columns=["Language", "Usage"])

    languages = all_time_statistics.languages
    size = len(languages)
    fig = go.Figure(data=[go.Bar(
        x=list(languages.values()),
        y=list(languages.keys()),
        text=list(languages.values()),
        texttemplate="%{text:.2%}",
        textposition="auto",
        width=.4,
        orientation='h'
    )])
    fig = ply.read_json("json/horizontal_chart.json")
    fig.add_trace(go.Bar(
        x=list(languages.values()),
        y=list(languages.keys()),
        text=list(languages.values()),
        texttemplate="%{text:.2%}",
        textposition="auto",
        width=.4,
        orientation='h'
    ))
    fig.write_image(file="generated/all_time_languages_bar.svg")

    df = DataFrame(dict(r=all_time_statistics.languages.values(), theta=all_time_statistics.languages.keys()))
    fig = px.line_polar(df, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself')
    fig.write_image(file="generated/all_time_languages_radar.svg")

    return


if __name__ == "__main__":
    main(sys.argv[1:])
