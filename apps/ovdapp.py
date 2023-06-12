import dash
import dash_bootstrap_components as dbc
from dash import dcc,html
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
                dbc.Button("Ir a la app", color="primary", href='/apps/ovdash'),
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
                dbc.Button("Ir a la app", color="primary", href='/apps/orcapp'),
            ]),],)

        card_autovdas = dbc.Card([
        dbc.CardImg(src=app.get_asset_url('img/autovdas_thumb.png'), top=True),
        dbc.CardBody([
                html.H4("Autovdas", className="card-title"),
                html.P(
                    "Proyecto de monitoreo automático de señales sísmicas.",
                    className="card-text",
                ),
                dbc.Button("Ir a la app", color="primary", href='/apps/autovdas'),
            ]),],)
        
        card_electriceye = dbc.Card([
        dbc.CardImg(src=app.get_asset_url('img/eleeye_thumb.png'), top=True),
        dbc.CardBody([
                html.H4("Electric Eye", className="card-title"),
                html.P(
                    "Monitoreo de últimos sismos localizados. También permite generar REAVs de estos.",
                    className="card-text",
                ),
                dbc.Button("Ir a la app", color="primary", href='/apps/electriceye'),
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
                dbc.Button("Ir a la app", color="primary", href='/apps/sismodb'),
            ]),],)

        card_fastrsam = dbc.Card([
        dbc.CardImg(src=app.get_asset_url('img/fastrsam_thumb.png'), top=True),
        dbc.CardBody([
                html.H4("Fast Rsam", className="card-title"),
                html.P(
                    "RSAM Rápido, permite obtener datos sobre la señal "
                    "sísmica continua por bandas de frecuencia.",
                    className="card-text",
                ),
                dbc.Button("Ir a la app", color="primary", href='/apps/fastrsam'),
            ]),],)
        
        contenido = html.Div([dbc.Row([dbc.Col(card_orcapp,width=3),
                                       dbc.Col(card_ovdash,width=3),
                                       dbc.Col(card_autovdas,width=3)]),
                            dbc.Row([ dbc.Col(card_electriceye,width=3),
                                       dbc.Col(card_sismodb,width=3),
                                       dbc.Col(card_fastrsam,width=3)])
                                      ])

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
                dbc.Button("Ir a la app", color="primary", href='http://altura.ovdas.sernageomin.cl/',target='_blank'),
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
                dbc.Button("Ir a la app", color="primary", href='http://apaweb-zc.sernageomin.cl/',target='_blank'),
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
                dbc.Button("Ir a la app", color="primary", href='http://aplicativos.ovdas.sernageomin.cl:200/',target='_blank'),
            ]),],)
   
        card_heli = dbc.Card([dbc.CardImg(src=app.get_asset_url('img/heli_thumb.png'), top=True),
        dbc.CardBody([html.H4("Helicorderizador", className="card-title"),
        html.P(
            "Generación de helicorders (sismogramas)  "
            "en formato de imagen para visualización rápida ",
            className="card-text",
        ),
        dbc.Button("Ir a la app", color="primary", href='/apps/helicorderizador',target='_blank'),
        ]
        ),],)

        card_rad = dbc.Card([dbc.CardImg(src=app.get_asset_url('img/rad_thumb.png?random='+str(random())), top=True),
        dbc.CardBody([html.H4("Hola RAD", className="card-title"),
        html.P(
            "Generación de reporte RAD, Reporte Diario de Actividad  "
            "Reporte único para los 45 volcanes. (.pdf)",
            className="card-text",
        ),
        dbc.Button("Ir a la app", color="primary", href='http://aplicativos.ovdas.sernageomin.cl:300/',target='_blank'),
        ]
        ),],) 

        card_flash = dbc.Card([dbc.CardImg(src=app.get_asset_url('img/flash_thumb.png?random='+str(random())), top=True),
        dbc.CardBody([html.H4("Hola FLASH", className="card-title"),
        html.P(
            "Generación de reporte REAV FLASH, REAV en caso de eventos intespestivos, de rápida emisión (.doc).  ",
            className="card-text",
        ),
        dbc.Button("Ir a la app", color="primary", href='http://aplicativos.ovdas.sernageomin.cl:100/',target='_blank'),
        ]
        ),],)
        
        card_transparentar = dbc.Card([dbc.CardImg(src=app.get_asset_url('img/transparen_thumb.png?random='+
                                                                         str(random())), top=True),
        dbc.CardBody([html.H4("TRANSPARENTAR", className="card-title"),
        html.P(
            "Lugar donde obtener datos sísmicos en formato "
            ".xslx para solicitudes de transparencia",
            className="card-text",
        ),
        dbc.Button("Ir a la app", color="primary", href='/apps/transparentar',target='_blank'),
        ]
        ),],) 
        
        contenido = html.Div([dbc.Row([dbc.Col(card_vona,width=2),
                                       
                                       dbc.Col(card_rad,width=2),
                                       dbc.Col(card_flash,width=2),
                                       dbc.Col(card_heli,width=2),
                                       dbc.Col(card_transparentar,width=2)
                                       
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
                dbc.Button("Ir a la app", color="primary", href='/apps/locali6',target='_blank'),
            ]),],)
        
        card_nllvsh71 = dbc.Card([
        dbc.CardImg(src=app.get_asset_url('img/nllvsh71_thumb.png'), top=True),
        dbc.CardBody([
                html.H4("NLLvsHypo71", className="card-title"),
                html.P(
                    "Comparación de algoritmos de localización "
                    "NonLinLoc / Hypo71.",
                    className="card-text",
                ),
                dbc.Button("Ir a la app", color="primary", href='/apps/nllvsh71',target='_blank'),
            ]),],)
        
        card_loc3D = dbc.Card([
        dbc.CardImg(src=app.get_asset_url('img/3D_thumb.png'), top=True),
        dbc.CardBody([
                html.H4("Localizaciones 3D", className="card-title"),
                html.P(
                    "Gráficos de localización de eventos "
                    " de burbuja y mapa de calor",
                    className="card-text",
                ),
                dbc.Button("Ir a la app", color="primary", href='http://172.16.47.23:700/',target='_blank'),
            ]),],)

        card_GNSS = dbc.Card([
        dbc.CardImg(src=app.get_asset_url('img/GNSS_thumb.png'), top=True),
        dbc.CardBody([
                html.H4("Líneas de monitoreo GNSS", className="card-title"),
                html.P(
                    "Variación de líneas GNSS "
                    " usadas en monitoreo geodésico",
                    className="card-text",
                ),
                dbc.Button("Ir a la app", color="primary", href='http://172.16.47.23:600/',target='_blank'),
            ]),],)
        
        card_defcon = dbc.Card([
        dbc.CardImg(src=app.get_asset_url('img/defcon_thumb.png'), top=True),
        dbc.CardBody([
                html.H4("DEFCON", className="card-title"),
                html.P(
                    "Historial de alertas técnicas "
                    "decretadas por el Ovdas.",
                    className="card-text",
                ),
                dbc.Button("Ir a la app", color="primary", href='/apps/defcon',target='_blank'),
            ]),],)
        card_estadoEst = dbc.Card([
        dbc.CardImg(src=app.get_asset_url('img/estadoEst_thumb.png'), top=True),
        dbc.CardBody([
                html.H4("Estado de estaciones Simológicas", className="card-title"),
                html.P(
                    "Estado de estaciones Sismológicas"
                    ,
                    className="card-text",
                ),
                dbc.Button("Ir a la app", color="primary", href='http://172.16.47.23:777/',target='_blank'),
            ]),],)
        card_agrupada = dbc.Card([
        dbc.CardImg(src=app.get_asset_url('img/agrupadas_thumb.png'), top=True),
        dbc.CardBody([
                html.H4("Visualizador de eventos agrupados", className="card-title"),
                html.P(
                    "Eventos agrupados en cortos periodos de tiempo"
                    " para evaluación de alta productividad sísmica"
                    ,
                    className="card-text",
                ),
                dbc.Button("Ir a la app", color="primary", href='http://aplicativos.ovdas.sernageomin.cl:400/',target='_blank'),
            ]),],)

        
        contenido = html.Div([dbc.Row([dbc.Col(card_locali6,width=3),
                                       dbc.Col(card_nllvsh71,width=3),
                                       dbc.Col(card_loc3D,width=3),
                                       dbc.Col(card_GNSS,width=3)]),
                              dbc.Row([dbc.Col(card_defcon,width=3),
                                       dbc.Col(card_estadoEst,width=3),
                                       dbc.Col(card_agrupada,width=3)])])
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
                dbc.Button("Ir a la app", color="primary", href='/apps/hangar18',target='_blank'),
            ]),],)
        

        
        
        contenido = html.Div([dbc.Row([dbc.Col(card_locali6,width=2)])])
        return contenido

