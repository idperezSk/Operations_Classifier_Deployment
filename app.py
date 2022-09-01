from glob import glob
from matplotlib.pyplot import get
import pandas as pd # Libreria para el manejo de Dataframes (Datos estructurados).
import numpy as np  # libreria para el manejo de series o Vectores.
import warnings
warnings.filterwarnings("ignore")

from data.get_data import * # Importo función para obtener los datos de los ultimos 2 minutos (60 registros)

from dash import html, dash, dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import plotly.express as px

data_record = get_data(60)

## APP
app = dash.Dash(__name__)
app.title = "Live operations detections"

app.layout = html.Div(
    children=[
        html.H1('Real Time Rig 23 SierraCol'),
        dcc.Graph(id='carga_gancho_plot'),
        dcc.Graph(id='posicion_bloque_plot'),
        dcc.Interval(
            id ='interval_component',
            interval = 10*1000,
            n_intervals = 0)
    ]
)


# Update components when the interval gets fired
@app.callback([Output('carga_gancho_plot', 'figure'), Output('posicion_bloque_plot', 'figure')], Input('interval_component', 'n_intervals'))
def update_graph_live1(n):
    global data_record
    data_record = update_data(data_record)
    fig1 = px.line(data_record, x='fecha_hora', y= 'carga_gancho', color='Ops')
    fig2 = px.line(data_record, x='fecha_hora', y= 'posicion_bloque')
    return fig1, fig2

if __name__ == '__main__':
    app.run(debug=False)
