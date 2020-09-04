from datetime import timedelta

import settings
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from functools import lru_cache
from threading import Timer
import sys
from datetime import datetime


# Reboot the container every day
def killme():
    sys.exit(0)


today = datetime.today()
killdate = today.replace(day=today.day+1, hour=0,
                         minute=0, second=0, microsecond=0)
delta_t = killdate - today
print(delta_t)
Timer(delta_t.seconds, killme).start()


# Download data
data = pd.read_csv(settings.CSV_URL, index_col='data', parse_dates=True,
                   usecols=['nuovi_positivi', 'totale_positivi', 'variazione_totale_positivi',
                            'terapia_intensiva', 'deceduti', 'data', 'stato'],)
assert((data['stato'] == 'ITA').all())


# Preprocess data
nm = data['deceduti'].values
nm_diff = np.insert(nm[1:] - nm[:-1], obj=0, values=nm[0])
data['variazione_deceduti'] = nm_diff

vtp_avg = data['variazione_totale_positivi'].resample('W').mean()
np_avg = data['nuovi_positivi'].resample('W').mean()
totp_avg = data['totale_positivi'].resample('W').mean()
ti_avg = data['terapia_intensiva'].resample('W').mean()
nm_avg = data['variazione_deceduti'].resample('W').mean()
vtp_avg.index = np_avg.index = totp_avg.index = nm_avg.index = ti_avg.index = vtp_avg.index - \
    timedelta(days=2)

# Build figures
# Totale positivi
totp_fig = go.Figure()
totp_fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data['totale_positivi'],
        name='Dati giornalieri'
    ))
totp_fig.update_traces(mode='lines+markers',
                       marker=dict(size=5))
totp_fig.add_trace(
    go.Bar(
        x=totp_avg.index,
        y=totp_avg.values,
        name='Media settimanale'
    ))
totp_fig.update_layout(bargap=0)

# Nuovi positivi
np_fig = go.Figure()
np_fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data['nuovi_positivi'],
        name='Dati giornalieri'
    ))
np_fig.update_traces(mode='lines+markers',
                     marker=dict(size=5))
np_fig.add_trace(
    go.Bar(
        x=np_avg.index,
        y=np_avg.values,
        name='Media settimanale'
    ))
np_fig.update_layout(bargap=0)

# Variazione totale positivi
vtp_fig = go.Figure()
vtp_fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data['variazione_totale_positivi'],
        name='Dati giornalieri'
    ))
vtp_fig.update_traces(mode='lines+markers',
                      marker=dict(size=5))
vtp_fig.add_trace(
    go.Bar(
        x=vtp_avg.index,
        y=vtp_avg.values,
        name='Media settimanale'
    ))
vtp_fig.update_layout(bargap=0)

# Terapia intensiva
ti_fig = go.Figure()
ti_fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data['terapia_intensiva'],
        name='Dati giornalieri'
    ))
ti_fig.update_traces(mode='lines+markers',
                     marker=dict(size=5))
ti_fig.add_trace(
    go.Bar(
        x=ti_avg.index,
        y=ti_avg.values,
        name='Media settimanale'
    ))
ti_fig.update_layout(bargap=0)

# Deceduti
nm_fig = go.Figure()
nm_fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data['variazione_deceduti'],
        name='Dati giornalieri'
    ))
nm_fig.update_traces(mode='lines+markers',
                     marker=dict(size=5))
nm_fig.add_trace(
    go.Bar(
        x=nm_avg.index,
        y=nm_avg.values,
        name='Media settimanale'
    ))
nm_fig.update_layout(bargap=0)

# Set of plots
plots = {
    'totp': dcc.Graph(id='totp', figure=totp_fig),
    'np': dcc.Graph(id='np', figure=np_fig),
    'vtp': dcc.Graph(id='vtp', figure=vtp_fig),
    'ti': dcc.Graph(id='ti', figure=ti_fig),
    'nm': dcc.Graph(id='nm', figure=nm_fig)
}

# Run GUI
server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server, external_scripts=[
                'https://www.googletagmanager.com/gtag/js?id=UA-177060824-1'])

app.title = 'Situazione COVID-19 in Italia'
app.layout = html.Div(children=[
    html.Embed('''<!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=UA-177060824-1"></script>
    <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'UA-177060824-1');
    </script>
    '''),
    html.H1(app.title),
    dcc.Tabs(id='tabs', value='totp', children=[
        dcc.Tab(label='Totale positivi', value='totp'),
        dcc.Tab(label='Nuovi positivi', value='np'),
        dcc.Tab(label='Variazione positivi', value='vtp'),
        dcc.Tab(label='Posti occupati in terapia intensiva', value='ti'),
        dcc.Tab(label='Numero di morti', value='nm')
    ]),
    html.Div(id='tabs-content'),
    html.Footer([
        html.P(['Fonte dati: ', html.A(settings.REPO_DATA, href=settings.REPO_DATA),
                ' (', html.A(
                    'CC-BY-4.0', href='https://creativecommons.org/licenses/by/4.0/deed.it'), ')',
                '. Codice app: ', html.A(
                    settings.REPO_CODE, href=settings.REPO_CODE),
                ' (', html.A(
            'GNU AGPL', href='https://raw.githubusercontent.com/Davide95/covid-dash-ita/master/LICENSE'), ')']),
    ])
])


@lru_cache
@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    return plots[tab]


if __name__ == '__main__':
    app.run_server(debug=settings.DEBUG, host='0.0.0.0')
