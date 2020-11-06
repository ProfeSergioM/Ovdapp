import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from app import app
from random import random

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": " #141d26",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Ovdapp", className="display-4"),
        html.Hr(),
        html.P(
            "Todo lo relacionado al monitoreo volcánico instrumental del Ovdas", className="lead"
        ),
        dbc.ButtonGroup(
    [
        dbc.Button("Inicio",id='inicio-button'),
        dbc.Button("Dashboards",id="dashboards-button"),
        dbc.Button("Procesamiento",id='procesamiento-button'),
        dbc.Button("Revisión",id='revision-button'),
        dbc.Button("Reportes",id='reportes-button'),
        dbc.Button("Información de interés",id='info-button')
    ],
    vertical=True,style={'width':'100%'}
),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="contenido", style=CONTENT_STYLE)

layout = html.Div([sidebar, content])


@app.callback(
    Output("contenido", "children"), 
    [Input("inicio-button", "n_clicks"),Input("dashboards-button", "n_clicks"),
     Input("procesamiento-button", "n_clicks"),Input("revision-button", "n_clicks"),Input("reportes-button", "n_clicks"),Input("info-button", "n_clicks")]
)
def on_button_click(n_inicio,n_dashboards,n_procesamiento,n_revision,n_reportes,n_info):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if (button_id == "inicio-button") or (ctx.triggered[0]['prop_id'] =='.'):
        return "Bienvenido!"
    elif button_id == "dashboards-button":
        card_ovdash = dbc.Card([
        dbc.CardImg(src=app.get_asset_url('img/ovdash_thumb.png'), top=True),
        dbc.CardBody([
                html.H4("Ovdash", className="card-title"),
                html.P(
                    "Resumen de actividad volcánica general, usado "
                    "en las pantallas de crisis.",
                    className="card-text",
                ),
                dbc.Button("Ir a la app", color="primary", href='http://172.16.47.23:8080/apps/ovdash'),
            ]),],)
        
        card_orcapp = dbc.Card([
        dbc.CardImg(src=app.get_asset_url('img/orcapp_thumb.png'), top=True),
        dbc.CardBody([
                html.H4("Orcapp", className="card-title"),
                html.P(
                    "Visuaización del proyecto de monitoreo automático "
                    "de actividad sísmica del volcán Orca.",
                    className="card-text",
                ),
                dbc.Button("Ir a la app", color="primary", href='http://172.16.47.23:8080/apps/orcapp'),
            ]),],)

        card_autovdas = dbc.Card([
        dbc.CardImg(src=app.get_asset_url('img/autovdas_thumb.png'), top=True),
        dbc.CardBody([
                html.H4("Autovdas", className="card-title"),
                html.P(
                    "Proyecto de monitoreo automático de señales sísmicas.",
                    className="card-text",
                ),
                dbc.Button("Ir a la app", color="primary", href='http://172.16.47.23:8080/apps/autovdas'),
            ]),],)
        
        card_electriceye = dbc.Card([
        dbc.CardImg(src=app.get_asset_url('img/eleeye_thumb.png'), top=True),
        dbc.CardBody([
                html.H4("Electric Eye", className="card-title"),
                html.P(
                    "Monitoreo de últimos sismos localizados. También permite generar REAVs de estos.",
                    className="card-text",
                ),
                dbc.Button("Ir a la app", color="primary", href='http://172.16.47.23:8080/apps/electriceye'),
            ]),],)
        
        card_sismodb = dbc.Card([
        dbc.CardImg(src=app.get_asset_url('img/sismodb_thumb.png'), top=True),
        dbc.CardBody([
                html.H4("SismoDB", className="card-title"),
                html.P(
                    "Revisión rápida de los datos de sismología "
                    "almacenados en la db del ovdas.",
                    className="card-text",
                ),
                dbc.Button("Ir a la app", color="primary", href='http://172.16.47.23:8080/apps/sismodb'),
            ]),],)        
        contenido = html.Div([dbc.Row([dbc.Col(card_orcapp,width=2),
                                       dbc.Col(card_ovdash,width=2),
                                       dbc.Col(card_autovdas,width=2),
                                       dbc.Col(card_electriceye,width=2),
                                       dbc.Col(card_sismodb,width=2)
                                       
                                       
                                       ])])
        return contenido
    elif button_id == "procesamiento-button":
        card_altcol = dbc.Card(
    [
        dbc.CardImg(src=app.get_asset_url('img/altcol_thumb.png'), top=True),
        dbc.CardBody(
            [
                html.H4("Alturas de columna", className="card-title"),
                html.P(
                    "Procesamiento de imágenes de cámaras IP "
                    "para el cálculo de altura de columnas.",
                    className="card-text",
                ),
                dbc.Button("Ir a la app", color="primary", href='http://172.16.42.160/Altura_Columnas_Php/',target='_blank'),
            ]
        ),
    ],
   
)

        card_apaweb = dbc.Card([
        dbc.CardImg(src=app.get_asset_url('img/apaweb_thumb.png'), top=True),
        dbc.CardBody([
                html.H4("APA - WEB", className="card-title"),
                html.P(
                    "Software principal de procesamiento primario, "
                    "primer paso en el proceso de monitoreo instrumental.",
                    className="card-text",
                ),
                dbc.Button("Ir a la app", color="primary", href='http://172.16.47.22:3000/',target='_blank'),
            ]),],)
        
        contenido = html.Div([dbc.Row([dbc.Col(card_altcol,width=2),
                                       dbc.Col(card_apaweb,width=2)])])
        return contenido
    
    
    elif button_id == "reportes-button":
        
        card_vona = dbc.Card([dbc.CardImg(src=app.get_asset_url('img/vona_thumb.png'), top=True),
        dbc.CardBody([html.H4("Hola VONA", className="card-title"),
                html.P(
                    "Generación de reporte VONA, sobre emisión de  "
                    "columnas significativas para la aeronáutica (.doc).",
                    className="card-text",
                ),
                dbc.Button("Ir a la app", color="primary", href='http://172.16.42.160:100/?random='+str(random()),target='_blank'),
            ]),],)
   
        card_rav = dbc.Card([dbc.CardImg(src=app.get_asset_url('img/rav.png'), top=True),
        dbc.CardBody([html.H4("Hola RAV", className="card-title"),
        html.P(
            "Generación de reporte RAV, Reporte de Actividad  "
            "Mensual. Reporte único para los 45 volcanes (.doc).",
            className="card-text",
        ),
        dbc.Button("Ir a la app", color="primary", href='http://172.16.42.160:200/?random='+str(random()),target='_blank'),
        ]
        ),],)

        card_rad = dbc.Card([dbc.CardImg(src=app.get_asset_url('img/rad_thumb.png?random='+str(random())), top=True),
        dbc.CardBody([html.H4("Hola RAD", className="card-title"),
        html.P(
            "Generación de reporte RAD, Reporte Diario de Actividad  "
            "Reporte único para los 45 volcanes. (.pdf)",
            className="card-text",
        ),
        dbc.Button("Ir a la app", color="primary", href='http://172.16.42.160:300/',target='_blank'),
        ]
        ),],) 

        card_flash = dbc.Card([dbc.CardImg(src=app.get_asset_url('img/flash_thumb.png?random='+str(random())), top=True),
        dbc.CardBody([html.H4("Hola FLASH", className="card-title"),
        html.P(
            "Generación de reporte REAV FLASH, REAV en caso de eventos intespestivos, de rápida emisión (.doc).  ",
            className="card-text",
        ),
        dbc.Button("Ir a la app", color="primary", href='http://172.16.42.160:400/',target='_blank'),
        ]
        ),],) 
        
        contenido = html.Div([dbc.Row([dbc.Col(card_vona,width=2),
                                       dbc.Col(card_rav,width=2),
                                       dbc.Col(card_rad,width=2),
                                       dbc.Col(card_flash,width=2)
                                       
                                       ],
                                      justify='left')])
        return contenido
    elif button_id == "revision-button":
        card_locali6 = dbc.Card([
        dbc.CardImg(src=app.get_asset_url('img/locali6_thumb.png'), top=True),
        dbc.CardBody([
                html.H4("Locali6", className="card-title"),
                html.P(
                    "Revisión de sismicidad localizada, permite "
                    "extraer datos en diversos formatos.",
                    className="card-text",
                ),
                dbc.Button("Ir a la app", color="primary", href='http://172.16.47.23:8080/apps/locali6',target='_blank'),
            ]),],)
        

        
        
        contenido = html.Div([dbc.Row([dbc.Col(card_locali6,width=2)])])
        return contenido
    elif button_id == "info-button":
        card_locali6 = dbc.Card([
        dbc.CardImg(src=app.get_asset_url('img/hangar18_thumb.png'), top=True),
        dbc.CardBody([
                html.H4("Hangar 18", className="card-title"),
                html.P(
                    "Información crítica de monitoreo (Criterios) ",
                    className="card-text",
                ),
                dbc.Button("Ir a la app", color="primary", href='http://172.16.47.23:8080/apps/hangar18',target='_blank'),
            ]),],)
        

        
        
        contenido = html.Div([dbc.Row([dbc.Col(card_locali6,width=2)])])
        return contenido

