from dash import Dash
from dash import Input
from dash import Output
from dash import dcc
from dash import html
import json
import pandas as pd
import plotly.express as px
import pycountry
import requests

# Requesting JSON Data

url = 'https://www.ag-grid.com/example-assets/olympic-winners.json'

try:
    r = requests.get(url)
except:
    print("Error requesting the JSON.")

json_file = json.loads(r.text)

# Dataframe used on the bar graph
country_medals = pd.DataFrame(json_file, columns = ["country","sport","gold","silver","bronze","total"])

# Grouping and renaming column name
countrymedals_grouped = country_medals.groupby(["country","sport"]).sum()
countrymedals_grouped = countrymedals_grouped.reset_index()
countrymedals_grouped.rename(columns={'total': 'Total Medals'}, inplace=True)


# Dataframe used on the sunburst graph
athlete_data = pd.DataFrame(json_file, columns = ["athlete", "country","sport","gold","silver","bronze","total","year"])

# Grouping data
athlete_grouped = athlete_data.groupby(["country","sport","year"]).sum()
athlete_grouped = athlete_grouped.reset_index()


# Dataframe used on World Map Graph
map_data = pd.DataFrame(json_file, columns = ["country","year","sport","gold","silver","bronze","total"])

# Grouping data
map_grouped = map_data.groupby(["country","year"]).sum()
map_grouped = map_grouped.reset_index()
map_grouped = map_grouped.sort_values(by=['year'])



sunburst_fig = px.sunburst(athlete_data, path=['year', 'sport', 'athlete'], values='total', color="sport",maxdepth=-1)
bar_fig = px.bar(countrymedals_grouped, x="sport", y="Total Medals", barmode='group',title="Teste Medals by Sport",color='Total Medals')


# Getting unique countries loop
countries = []
country_list = country_medals.country.unique()
for country in country_list:
  countries.append(country)


# Getting alpha codes to use on World Map graph
country_dict = {}
for country in country_list:
  country_stats =  pycountry.countries.get(name=country)
  try:
    country_dict[country] = country_stats.alpha_3
  except:
    country_dict[country] = None

# Adding Alpha Code column to the dataframe
for index, row in map_grouped.iterrows():
    map_grouped.at[index,'Alpha Code'] = country_dict[row["country"]]



app = Dash(__name__)


# Drawing graphs
bar_fig = px.bar(countrymedals_grouped, "sport", y="Total Medals", barmode='group',title="Medals by Sport",color='Total Medals')

sunburst_fig = px.sunburst(athlete_data, path=["year",'sport', 'athlete'], values='total', color="sport")

country_graph = px.scatter_geo(map_grouped, locations="Alpha Code", color="country",
                     hover_name="country", size="total",
                     projection="natural earth", animation_frame="year",
                     title="Country Medals")

country_graph.update_layout(title_text="Country Medals", title_x=0.5)

colors = {
    'background': '#111111',
    'text': 'black'
}

# Defining HTML texts and style
app.layout = html.Div([

    html.Div([
         html.H1('Olympics Visualization Dashboard',
                 style={
            'textAlign': 'center',
            'color': colors['text']
            }),

        html.Div(children='''
            You can change the country by filtering below.

            ''',
            style={
            'textAlign': 'center',
            'color': colors['text']
            }),

        dcc.Dropdown(countries, 'Brazil', id='demo-dropdown'),

        dcc.Graph(
            id='sunburst_graph',
            figure=bar_fig
        ),

        dcc.Graph(
            id='bar_graph',
            figure=sunburst_fig
        ),

        dcc.Graph(
            id='map_graph',
            figure=country_graph
        )
        ])


])


# Functions used to update the graphs after the interaction with filters/buttons

@app.callback(
    Output('sunburst_graph', component_property="figure"),
    Input('demo-dropdown', 'value')
)
def update_sunburst_graph(value):
    filtered_data = athlete_data[athlete_data['country'] == value]
    sunburst_fig = px.sunburst(filtered_data, path=["year",'sport', 'athlete'],title="{0} Athletes by Country and Sport".format(value) ,values='total', color="sport",maxdepth=-1)
    sunburst_fig.update_layout(title_text="{0} Athletes by Country and Sport".format(value), title_x=0.5, width=800, height=800)

    return sunburst_fig


@app.callback(
    Output('bar_graph', component_property="figure"),
    Input('demo-dropdown', 'value')
)
def update_bar_graph(value):
    filtered_data = countrymedals_grouped[countrymedals_grouped['country'] == value]
    bar_fig = px.bar(filtered_data, x="sport", y="Total Medals", barmode='group',title="{0} Medals by Sport".format(value), color='Total Medals')
    bar_fig.update_layout(title_text="{0} Medals by Sport".format(value), title_x=0.5)

    return bar_fig



if __name__ == '__main__':
    app.run_server(debug=True)
