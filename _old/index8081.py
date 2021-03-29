import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import electriceye

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
    elif pathname == '/apps/electriceye':
        return electriceye.layout
    else:
        return '404'

app.clientside_callback(
    """
    function(tab_value) {
        if (tab_value === '/apps/electriceye') {
            document.title = 'Ovdapp - Electric Eye'
        } 
    }
    
    """,
    Output('blank-output', 'children'),
    [Input('url', 'pathname')]
)
            

if __name__ == '__main__':
    app.run_server(debug=True,threaded=True)