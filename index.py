import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import ovdash,orcapp,ovdapp,locali6,autovdas,electriceye,hangar18,holaRAV,sismodb,fastrsam


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='blank-output'),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname is None:
        return 'Loading...'
    elif pathname == '/apps/ovdash':
        return ovdash.layout
    elif pathname == '/apps/orcapp':
        return orcapp.layout
    elif pathname == '/apps/autovdas':
        return autovdas.layout
    elif pathname == '/apps/locali6':
        return locali6.layout
    elif pathname == '/apps/electriceye':
        return electriceye.layout
    elif pathname == '/apps/hangar18':
        return hangar18.layout
    elif pathname == '/apps/holaRAV':
        return holaRAV.layout
    elif pathname == '/apps/sismodb':
        return sismodb.layout
    elif pathname == '/apps/fastrsam':
        return fastrsam.layout
    elif pathname == '/':
        return ovdapp.layout
    else:
        return '404'

app.clientside_callback(
    """
    function(tab_value) {
        if (tab_value === '/apps/ovdash') {
            document.title = 'Ovdapp - Ovdash'
        } else if (tab_value === '/apps/orcapp') {
            document.title = 'Ovdapp - Orcapp'
        } else if (tab_value === '/apps/locali6') {
            document.title = 'Ovdapp - Locali6'
        } else if (tab_value === '/apps/autovdas') {
            document.title = 'Ovdapp - AutOvdas'
        } else if (tab_value === '/apps/electriceye') {
            document.title = 'Ovdapp - Electric Eye'
        } else if (tab_value === '/apps/hangar18') {
            document.title = 'Ovdapp - Hangar 18'
        } else if (tab_value === '/apps/sismodb') {
            document.title = 'Ovdapp - SismoDB'
        } else if (tab_value === '/apps/fastrsam') {
            document.title = 'Ovdapp - fast RSAM'
        }
    }
    }
    """,
    Output('blank-output', 'children'),
    [Input('url', 'pathname')]
)
            

if __name__ == '__main__':
    app.run_server(debug=True,threaded=True)