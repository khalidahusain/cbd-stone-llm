from dash import html, dcc

shared_component_style = {
    # 'width': '100%',
    'maxWidth': '100%',
    'boxSizing': 'border-box'
}

patient_input_form = html.Div(
    style={
        'backgroundColor': 'white',
        'padding': '20px',
        'borderRadius': '10px',
        'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
        'marginRight': '20px',
        'fontFamily': 'Arial, sans-serif',
        'fontSize': '18px',
        # 'width': '100%',
        # 'maxWidth': '500px',
        # 'minWidth': '300px',
        # 'boxSizing': 'border-box'
    },
    children=[
        html.H3("Patient Description", style={'color': '#34495e', 'textAlign': 'center'}),

        html.Div([
            html.Div("Sex", className='form-label'),
            dcc.Dropdown(
                id='sex-input',
                options=[{'label': s, 'value': s} for s in ['Male', 'Female']],
                placeholder="",
                style={'width': '150px'}
            )
        ], className='form-row'),

        html.Div([
            html.Div("Age", className='form-label'),
            dcc.Input(id='age-input', type='number', placeholder='', style={'width': '80px'})
        ], className='form-row'),

        # Condition Toggles
        html.Div([
            html.Div([
                html.Div("Cholangitis", style={'marginRight': '15px', 'fontWeight': 'bold'}),
                html.Div([
                    html.Div(id="toggle-text-cholangitis", children="NO", className="toggle-text"),
                    html.Div(className="toggle-circle")
                ], id="toggle-cholangitis", className="toggle toggle-off", n_clicks=0)
            ], className='form-row'),

            html.Div([
                html.Div("Acute Pancreatitis", style={'marginRight': '15px', 'fontWeight': 'bold'}),
                html.Div([
                    html.Div(id="toggle-text-pancreatitis", children="NO", className="toggle-text"),
                    html.Div(className="toggle-circle")
                ], id="toggle-pancreatitis", className="toggle toggle-off", n_clicks=0)
            ], className='form-row'),

            html.Div([
                html.Div("Acute Cholecystitis", style={'marginRight': '15px', 'fontWeight': 'bold'}),
                html.Div([
                    html.Div(id="toggle-text-cholecystitis", children="NO", className="toggle-text"),
                    html.Div(className="toggle-circle")
                ], id="toggle-cholecystitis", className="toggle toggle-off", n_clicks=0)
            ], className='form-row'),
        ]),

        # Labs        
        html.Div([
            html.Div([
                html.Span("AST", style={'fontWeight': 'bold'}),
                html.Span(" (U/L)", style={'color': 'gray', 'fontSize': '12px', 'marginLeft': '4px'})
            ], style={'width': '80px'}),
            dcc.Input(id='ast-input', type='number', placeholder='', style={'width': '80px'})
        ], className='form-row'),

        html.Div([
            html.Div([
                html.Span("ALT", style={'fontWeight': 'bold'}),
                html.Span(" (U/L)", style={'color': 'gray', 'fontSize': '12px', 'marginLeft': '4px'})
            ], style={'width': '80px'}),
            dcc.Input(id='alt-input', type='number', placeholder='', style={'width': '80px'})
        ], className='form-row'),

        html.Div([
            html.Div([
                html.Span("ALP", style={'fontWeight': 'bold'}),
                html.Span(" (U/L)", style={'color': 'gray', 'fontSize': '12px', 'marginLeft': '4px'})
            ], style={'width': '80px'}),
            dcc.Input(id='alp-input', type='number', placeholder='', style={'width': '80px'})
        ], className='form-row'),

        html.Div([
            html.Div([
                html.Span("T. Bilirubin", style={'fontWeight': 'bold'}),
                html.Span(" (mg/dL)", style={'color': 'gray', 'fontSize': '12px', 'marginLeft': '4px'})
            ], style={'width': '80px', 'whiteSpace': 'nowrap'}),
            dcc.Input(id='bilirubin-input', type='number', placeholder='', style={'width': '80px'})
        ], className='form-row'),

        # Abd US done checkbox
        html.Div([
            html.Div("Abd US done?", style={'minWidth': '120px', 'fontWeight': 'bold'}),
            dcc.Checklist(
                id='abd-us-check',
                options=[{'label': '', 'value': 'done'}],
                style={'marginLeft': '10px'}
            )
        ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-between', 'marginTop': '10px'}),

        # Toggle for US CBD stone
        html.Div([
            html.Div("CBD stone on US", style={'minWidth': '120px', 'fontWeight': 'bold'}),
            html.Div([
                html.Div(id="toggle-text-us", children="NO", className="toggle-text"),
                html.Div(className="toggle-circle")
            ], id="toggle-us", className="toggle toggle-off", n_clicks=0)
        ], id="us-toggle-wrapper", style={
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'space-between',
            'marginTop': '10px',
            'opacity': '0.5',
            'pointerEvents': 'none'
        }),
        # CT done checkbox
        html.Div([
            html.Div("CT done?", style={'minWidth': '120px', 'fontWeight': 'bold'}),
            dcc.Checklist(
                id='ct-check',
                options=[{'label': '', 'value': 'done'}],
                style={'marginLeft': '10px'}
            )
                    ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-between', 'marginTop': '10px'}),
        
        # Toggle for CT CBD stone
        html.Div([
            html.Div("CBD stone on CT", style={'minWidth': '120px', 'fontWeight': 'bold'}),
            html.Div([
                html.Div(id="toggle-text-ct", children="NO", className="toggle-text"),
                html.Div(className="toggle-circle")
            ], id="toggle-ct", className="toggle toggle-off", n_clicks=0)
        ], id="ct-toggle-wrapper", style={
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'space-between',
            'marginTop': '10px',
            'opacity': '0.5',
            'pointerEvents': 'none'
        }),

        # Charlson Index
        html.Div([
            html.Div("Charlson Index", style={'width': '140px', 'fontWeight': 'bold'}),
            dcc.Input(id='charlson-input', type='number', placeholder='', style={'width': '80px'})
        ], className='form-row'),

        # Buttons
        html.Div(
            style={'marginTop': '20px', 'display': 'flex', 'justifyContent': 'space-between','fontFamily': 'Arial, sans-serif'},
            children=[
                html.Button('Clear', id='clear-button', n_clicks=0, style={
                    'backgroundColor': '#e74c3c',
                    'color': 'white',
                    'border': 'none',
                    'padding': '10px 15px',
                    'borderRadius': '5px',
                    'cursor': 'pointer'
                }),
                html.Button('Calculate', id='calculate-button', n_clicks=0, style={
                    'backgroundColor': '#2ecc71',
                    'color': 'white',
                    'border': 'none',
                    'padding': '10px 15px',
                    'borderRadius': '5px',
                    'cursor': 'pointer'
                }),
            ]
        )
    ]
)


test_results_table = html.Div(
    id='test-results-wrapper',  # <-- NEW ID
    style={
        # 'display': 'none',  # <-- Initially hidden
         **shared_component_style,
        'backgroundColor': 'white',
        'padding': '20px',
        'borderRadius': '10px',
        'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
        'width': '400px',
        'fontFamily': 'Arial, sans-serif',
        'marginTop': '10px'
    },
    children=[
        html.H3("Cost Associated with Interventions", style={
            'textAlign': 'center',
            'color': '#34495e',
            'marginBottom': '20px'
        }),
        html.Table(
            id='test-results-table',  # <-- NEW ID to update content
            style={
                'width': '100%',
                'borderCollapse': 'collapse',
                'fontSize': '15px'
            },
            children=[
                html.Thead([
                    html.Tr([
                        html.Th("Test", style={'padding': '10px', 'borderBottom': '2px solid #ccc', 'textAlign': 'center'}),
                        # html.Th("Positive", style={'padding': '10px', 'borderBottom': '2px solid #ccc', 'textAlign': 'center'}),
                        # html.Th("Negative", style={'padding': '10px', 'borderBottom': '2px solid #ccc', 'textAlign': 'center'}),
                        html.Th("Probability-Weighted Cost", style={'padding': '10px', 'borderBottom': '2px solid #ccc', 'textAlign': 'center'})
                    ])
                ]),
                html.Tbody(id='test-results-body')  # Will update this dynamically
            ]
        )
    ]
)

abbreviations_list = [
    ("Abd US", "abdominal ultrasound"),
    ("ALP", "alkaline phosphatase"),
    ("ALT", "alanine aminotransferase"),
    ("AST", "aspartate aminotransferase"),
    ("CBD", "common bile duct"),
    ("CCY ± IOC", "cholecystectomy with or without intraoperative cholangiogram"),
    ("CT", "computed tomography scan of the abdomen and pelvis"),
    ("ERCP", "endoscopic retrograde cholangiopancreatography"),
    ("EUS", "endoscopic ultrasound"),
    ("IOC", "intraoperative cholangiogram"),
    ("MRCP", "magnetic resonance cholangiopancreatography"),
    ("T. Bilirubin", "total bilirubin")
]

abbreviations_notes = html.Div([
    html.H5(
        html.A("Abbreviations", style={'textDecoration': 'underline'}),
        style={'textAlign': 'center', 'color': '#0066cc', 'marginBottom': '15px','fontFamily': 'Arial, sans-serif',}
    ),
    html.Ul(
        [html.Li(f"{abbr} = {definition}") for abbr, definition in abbreviations_list],
        style={
            'listStyleType': 'none',
            'textAlign': 'left',
            'fontSize': '14px',
            'lineHeight': '1.8',
            **shared_component_style,
            'maxWidth': '700px',
            'margin': '0 auto',
            'padding': '0 20px',
            'border': '1px solid #ddd',
            'borderRadius': '8px',
            'backgroundColor': '#f9f9f9',
            'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'
        }
    )
])


