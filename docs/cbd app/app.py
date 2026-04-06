from assets.imports import *
from assets.utils import spider_chart, sankey_chart, plot_prob_bar_with_callout, fig_to_base64_img
from assets.patient_form import patient_input_form, test_results_table, abbreviations_notes, shared_component_style

number_samples_if_models = {'MRCP': 2342,'EUS': 2342,'ERCP':  2342,'IOC': 2342}
ci_if = {'MRCP': [0,0], 'EUS': [0,0],'ERCP': [0,0], 'IOC': [0,0]}

cost_values = {
    'MRCP': [1215.08, 3620.92],
    'EUS': [2986.58,3566.92],
    'ERCP': [4451,0],
    'IOC': [600,4451]
}

# Load all model files from the "Models" folder
list_of_files = [f for f in os.listdir('./Models') if f.endswith('.pkl')]  # Get all model files
models = {f: joblib.load(f'./Models/{f}') for f in list_of_files}  # Load the models into a dictionary

with open('./assets/chosen_features_label.txt', 'r') as file:
    chosen_features_label_read = [line[:-1] if line.endswith('\n') else line for line in file]  # Remove only the newline, not spaces

with open('./assets/abbreviation.json', 'r') as file:
    column_abb = json.load(file)





# Initialize the Dash app
app = dash.Dash(__name__)
app.layout = html.Div(
    style={'backgroundColor': '#f5f7fa', 'padding': '20px'},
    children=[
        dcc.Store(id='prediction-store', data={'initial_prediction': 0}),

        # Title with underline
        html.Div([
            html.H1(
                "Patient Prediction Dashboard",
                style={
                    'textAlign': 'center',
                    'color': '#2c3e50',
                    'fontFamily': 'Segoe UI, Arial, sans-serif',
                    'fontWeight': '700',
                    'fontSize': '36px',
                    'marginBottom': '1px',
                    'marginTop': '10px',
                    'letterSpacing': '1px',
                    'textShadow': '1px 1px 2px rgba(0,0,0,0.1)',
                    'width': '100%',
                }
            ),
            html.Div(
                style={
                    'height': '4px',
                    'backgroundColor': '#2980b9',
                    'marginBottom': '5px',
                    'borderRadius': '10px'
                }
            )
        ]),

        html.Div(
            style={'display': 'flex', 'flexDirection': 'row'},
            children=[
                # Left: Patient description form
                html.Div([
            patient_input_form,
            html.Div(
                style={
                    # 'flex': '0',
                    # 'maxWidth': '30%',
                    'marginTop': '20px',
                    'paddingTop': '20px',
                    'borderTop': '1px solid #ccc',
                    'textAlign': 'center',
                    'fontFamily': 'Arial, sans-serif',
                    'color': '#2c3e50',
                },
                children=[
                    html.P("Helpful Calculators:", style={'fontWeight': 'bold', 'fontSize': 'clamp(14px, 2vw, 18px)'}),
                    html.A(" Tokyo Guidelines for Acute Cholecystitis", 
                           href="https://www.mdcalc.com/calc/10130/tokyo-guidelines-acute-cholecystitis-2018", 
                           target="_blank", 
                           style={'display': 'block', 'margin': '5px', 'color': '#2980b9'}),
                    html.A(" Tokyo Guidelines for Acute Cholangitis", 
                           href="https://www.mdcalc.com/calc/10142/tokyo-guidelines-acute-cholangitis-2018", 
                           target="_blank", 
                           style={'display': 'block', 'margin': '5px', 'color': '#2980b9'}),
                    html.A("Charlson Comorbidity Index (CCI)", 
                           href="https://www.mdcalc.com/calc/3917/charlson-comorbidity-index-cci", 
                           target="_blank", 
                           style={'display': 'block', 'margin': '5px', 'color': '#2980b9'})
                ]
            )
        ], style={'flex': '2',
                  'maxWidth': '4px',
                  'minWidth': '350px',
                  }),

                # Middle: Dashboard content
                html.Div(
                    style={
                            'flex': '2',  # ← Grows as screen gets bigger
                            'backgroundColor': 'white',
                            'padding': '20px',
                            'borderRadius': '10px',
                            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
                            'fontFamily': 'Arial, sans-serif',
                            'display': 'flex',
                            'flexDirection': 'column',
                            'justifyContent': 'flex-start',
                            'boxSizing': 'border-box'
                        },
                    children=[
                        # Prediction card
                        html.Div(
                            style={
                                # 'flex': '1',
                                'backgroundColor': 'white',
                                'padding': '20px',
                                'borderRadius': '10px',
                                'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
                                'fontFamily': 'Arial, sans-serif',
                                # 'marginTop': '100px',
                                'marginBottom': '10px',
                            },
                            children=[
                                html.H2(
                                    "Prediction",
                                    style={
                                        'textAlign': 'center',
                                        'color': '#2c3e50',
                                        'fontFamily': 'Arial, sans-serif',
                                        'marginTop': '2px',
                                        'fontSize': '24px',
                                        'fontWeight': 'bold',
                                        # 'backgroundColor': 'green' 
                                    }
                                ),
                                html.Div(
                                    id='initial-predictions-output',
                                    style={
                                        'padding': '5px',
                                        'fontSize': '16px',
                                        'color': '#34495e',
                                        'fontFamily': 'Arial, sans-serif',
                                        'textAlign': 'center'
                                    },
                                    children=" "
                                ),
                                html.H3(
                                    "The suggested next step in management is:",
                                    style={
                                        'textAlign': 'center',
                                        'color': '#34495e',
                                        'fontFamily': 'Arial, sans-serif',
                                        'marginBottom': '20px'
                                    }
                                ),
                                html.Div(
                                    id='main_plot_place_hoder',
                                    className='prediction-card',
                                    children=[
                                        html.Img(id='pred_plot', style={'display': 'none'})
                                    ],
                                    style={
                                        'width': '100%',
                                        'height': 'auto',
                                        'borderRadius': '10px',
                                        'boxShadow': '0 4px 6px rgba(0, 100, 0, 1)',
                                        # 'marginTop': '100px'
                                    }
                                ),
                            ],
                            
                        ),
                        html.Div(
                                style={
                                    'marginTop': '20px',
                                    'padding': '15px',
                                    'backgroundColor': '#f8f9fa',
                                    'borderRadius': '8px',
                                    'fontSize': '14px',
                                    'color': '#2c3e50',
                                    'lineHeight': '1.6'
                                },
                                children=[
                                    html.Ul([
                                        html.Li("ASGE 2019 guidelines recommend all patients with cholangitis undergo ERCP as clinically appropriate."),
                                        html.Li("In cases with a high predicted probability of choledocholithiasis, ERCP may be considered as the next step in management if EUS is unavailable."),
                                        html.Li("Recommendations provided by this tool should be adapted based on available resources and always used in conjunction with clinical judgment.")
                                    ], style={'paddingLeft': '20px', 'margin': '0'}),

                                    html.Div(
                                        "Management recommendations informed by:\n"
                                        "1. Buxbaum JL, Abbas Fehmi SM, Sultan S, et al. ASGE guideline on the role of endoscopy in the evaluation and management of choledocholithiasis. "
                                        "Gastrointest Endosc. 2019;89(6):1075-1105.e15. doi:10.1016/j.gie.2018.10.001\n"
                                        "2. Huerta-Reyna R, Guevara-Torres L, Martínez-Jiménez MA, et al. Development and validation of a predictive model for choledocholithiasis. "
                                        "World J Surg. 2024;48(7):1730-1738. doi:10.1002/wjs.12206\n"
                                        "3. Sonnenberg A, Enestvedt BK, Bakis G. Management of Suspected Choledocholithiasis: A Decision Analysis for Choosing the Optimal Imaging Modality. "
                                        "Dig Dis Sci. 2016;61(2):603-609. doi:10.1007/s10620-015-3882-7",
                                        style={
                                            'marginTop': '15px',
                                            'fontSize': '13px',
                                            'color': '#7f8c8d',
                                            'whiteSpace': 'pre-line'
                                        }
                                    )
                                ]
                            )
                        ]
                ),
                # RIGHT SIDE: Test results table# RIGHT SIDE: Image
                        html.Div(
                            children=[html.Img(
                            src='/assets/pic1.png',
                            style={
                                **shared_component_style,
                                # 'height': 'auto',
                                'borderRadius': '10px',
                                'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
                            }
                        ),test_results_table, abbreviations_notes],
                            style={
                                                        'flex': '0',
                                                        # 'maxWidth': '30%',
                                                        # 'display': 'flex',
                                                        'minWidth': '20%',
                                                        'flexDirection': 'column',
                                                        # 'justifyContent': 'flex-start',
                                                        'justifyContent': 'flex-end',
                                                        'alignItems': 'center',
                                                        'gap': '20px',
                                                        'padding': '10px',
                                                        'fontSize': 'clamp(14px, 2vw, 18px)'
                                                        }
                        )
            ]
        ),
        # Bottom Links Section
        
    ]
)


@app.callback(
    Output('toggle-cholangitis', 'className'),
    Output('toggle-text-cholangitis', 'children'),
    Input('toggle-cholangitis', 'n_clicks')
)
def toggle_cholangitis(n):
    is_on = n % 2 == 1
    return "toggle toggle-on" if is_on else "toggle toggle-off", "YES" if is_on else "NO"

@app.callback(
    Output('toggle-pancreatitis', 'className'),
    Output('toggle-text-pancreatitis', 'children'),
    Input('toggle-pancreatitis', 'n_clicks')
)
def toggle_pancreatitis(n):
    is_on = n % 2 == 1
    return "toggle toggle-on" if is_on else "toggle toggle-off", "YES" if is_on else "NO"

@app.callback(
    Output('toggle-cholecystitis', 'className'),
    Output('toggle-text-cholecystitis', 'children'),
    Input('toggle-cholecystitis', 'n_clicks')
)
def toggle_cholecystitis(n):
    is_on = n % 2 == 1
    return "toggle toggle-on" if is_on else "toggle toggle-off", "YES" if is_on else "NO"



@app.callback(
    Output('us-toggle-wrapper', 'style'),
    Input('abd-us-check', 'value'),
    prevent_initial_call=True
)
def enable_us_toggle(value):
    if value and 'done' in value:
        return {
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'space-between',
            'marginTop': '10px',
            'opacity': '1.0',
            'pointerEvents': 'auto'
        }
    return {
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'space-between',
        'marginTop': '10px',
        'opacity': '0.5',
        'pointerEvents': 'none'
    }

@app.callback(
    Output('ct-toggle-wrapper', 'style'),
    Input('ct-check', 'value'),
    prevent_initial_call=True
)
def enable_ct_toggle(value):
    if value and 'done' in value:
        return {
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'space-between',
            'marginTop': '10px',
            'opacity': '1.0',
            'pointerEvents': 'auto'
        }
    return {
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'space-between',
        'marginTop': '10px',
        'opacity': '0.5',
        'pointerEvents': 'none'
    }
    
@app.callback(
    Output('toggle-ct', 'className'),
    Output('toggle-text-ct', 'children'),
    Input('toggle-ct', 'n_clicks')
)
def toggle_ct(n):
    is_on = n % 2 == 1
    return "toggle toggle-on" if is_on else "toggle toggle-off", "YES" if is_on else "NO"

@app.callback(
    Output('toggle-us', 'className'),
    Output('toggle-text-us', 'children'),
    Input('toggle-us', 'n_clicks'),
    prevent_initial_call=True
)
def toggle_us(n):
    is_on = n % 2 == 1
    return "toggle toggle-on" if is_on else "toggle toggle-off", "YES" if is_on else "NO"

@app.callback(
    [
        Output('sex-input', 'value'),
        Output('age-input', 'value'),
        Output('toggle-cholangitis', 'n_clicks'),
        Output('toggle-pancreatitis', 'n_clicks'),
        Output('toggle-cholecystitis', 'n_clicks'),
        Output('ast-input', 'value'),
        Output('alt-input', 'value'),
        Output('alp-input', 'value'),
        Output('bilirubin-input', 'value'),
        Output('abd-us-check', 'value'),
        Output('toggle-us', 'n_clicks'),
        Output('toggle-ct', 'n_clicks'),
        Output('charlson-input', 'value')
    ],
    Input('clear-button', 'n_clicks'),
    prevent_initial_call=True
)
def clear_inputs(_):
    return [
        None,  # sex-input
        None,  # age-input (even if invalid text was typed)
        0,     # toggle-cholangitis
        0,     # toggle-pancreatitis
        0,     # toggle-cholecystitis
        None,  # ast-input
        None,  # alt-input
        None,  # alp-input
        None,  # bilirubin-input
        [],    # abd-us-check
        0,     # toggle-us
        0,     # toggle-ct
        None   # charlson-input
    ]







# Callback to update the model predictions
@app.callback(
    [
        Output('initial-predictions-output', 'children'),
        Output('prediction-store', 'data'),
        Output('main_plot_place_hoder', 'children'),
        Output('test-results-body', 'children'),
        Output('test-results-wrapper', 'style'),
    ],
    Input('calculate-button', 'n_clicks'),
    [
        State('sex-input', 'value'),
        State('age-input', 'value'),
        State('toggle-cholangitis', 'n_clicks'),
        State('toggle-pancreatitis', 'n_clicks'),
        State('toggle-cholecystitis', 'n_clicks'),
        State('ast-input', 'value'),
        State('alt-input', 'value'),
        State('alp-input', 'value'),
        State('bilirubin-input', 'value'),
        State('abd-us-check', 'value'),
        State('toggle-us', 'n_clicks'),
        State('toggle-ct', 'n_clicks'),
        State('charlson-input', 'value')
    ]
)
def update_model_predictions(n_clicks, sex, age, cholangitis, pancreatitis, cholecystitis, ast, alt, alp, bilirubin, us_check, us_toggle, ct_toggle, charlson):
    secondary_plot = {'MRCP': [0,0], 'EUS': [0,0],'ERCP': [0,0], 'IOC': [0,0]}
    if n_clicks > 0 and sex and age:
        
        # Convert toggle button states to YES/NO
        cholangitis = "YES" if cholangitis % 2 == 1 else "NO"
        pancreatitis = "YES" if pancreatitis % 2 == 1 else "NO"
        cholecystitis = "YES" if cholecystitis % 2 == 1 else "NO"
        us_toggle = "YES" if us_toggle % 2 == 1 else "NO"
        ct_toggle = "YES" if ct_toggle % 2 == 1 else "NO"
        us_check = "YES" if us_check else "NO"
        # print('cholangitis:', cholangitis)
        patient_data = {
        'Sex': sex,
        'Cholangitis': cholangitis,
        'Pancreatitis': pancreatitis,
        'Cholecystitis': cholecystitis,
        'AST': ast,
        'ALT': alt,
        'ALP': alp,
        'T. Bilirubin': bilirubin,
        'Abd US': us_check,
        'CBD stone on Abd US': us_toggle,
        'CBD stone on CT scan': ct_toggle,
        'Charlson Comorbidity Index': charlson,
        'Age': age,
        }
        patient_df = pd.DataFrame([patient_data])
        patient_df = patient_df.replace({"YES": 1, "NO": 0, "Male": 1, "Female": 0}).infer_objects(copy=False)
        patient_imputed = models['iterative_imputer.pkl'].transform(patient_df)
        patient_imputed = pd.DataFrame(patient_imputed, columns=patient_df.columns)
        
        # model_names = list(models.keys())
        prediction_values = {}  # To store model name and predictions
        model = models['initial.pkl']
        prediction = np.round(model.predict_proba(patient_imputed)[0] * 100, 2)
        prediction_values['initial.pkl'] = prediction[1]  # Store prediction for model
#         initial_style = {
#     'padding': '20px', 
#     'textAlign': 'center',
#     'borderRadius': '15px', 
#     'backgroundColor': '#27ae60',  
#     'color': 'white',              
#     'marginBottom': '10px',
#     'width': '50%',
#     'marginLeft': 'auto',
#     'marginRight': 'auto',
#     'fontSize': '22px',             
#     'fontWeight': '700',            
#     'boxShadow': '0 8px 12px rgba(0, 0, 0, 0.15)',  
#     'letterSpacing': '1px',         
#     'transition': 'all 0.3s ease-in-out'  # Smooth transition (but no hover effect)
# }
        initial = html.Div(
            f'The probability of a stone in the CBD is {prediction[1]}%',className='prediction-card_prob',
        )
        initial_pred = prediction[1]
        patient_imputed['Initial_prob'] = prediction[1]
        # for _ , model_name in enumerate(model_names):                       
        #     if model_name== 'model_predict_if_ercp.pkl':
        #         prediction = models[model_name].predict_proba(patient_imputed)[0]
        #         secondary_plot['ERCP'] = [prediction[0], prediction[1]]
        #         ci_if['ERCP']=[prediction[1]-1.96*np.sqrt(prediction[1]*(1-prediction[1])/(number_samples_if_models['ERCP'])),prediction[1]+1.96*np.sqrt(prediction[1]*(1-prediction[1])/(number_samples_if_models['ERCP']))]
        #     if model_name== 'model_predict_if_eus.pkl':
        #         prediction = models[model_name].predict_proba(patient_imputed)[0]
        #         secondary_plot['EUS'] = [prediction[0], prediction[1]]
        #         ci_if['EUS']=[prediction[1]-1.96*np.sqrt(prediction[1]*(1-prediction[1])/(number_samples_if_models['EUS'])),prediction[1]+1.96*np.sqrt(prediction[1]*(1-prediction[1])/(number_samples_if_models['EUS']))]
        #     if model_name== 'model_predict_if_mrcp.pkl':
        #         prediction = models[model_name].predict_proba(patient_imputed)[0]
        #         secondary_plot['MRCP'] = [prediction[0], prediction[1]]
        #         ci_if['MRCP']=[prediction[1]-1.96*np.sqrt(prediction[1]*(1-prediction[1])/(number_samples_if_models['MRCP'])),prediction[1]+1.96*np.sqrt(prediction[1]*(1-prediction[1])/(number_samples_if_models['MRCP']))]
        #     if model_name== 'model_predict_if_ioc.pkl':
        #         prediction = models[model_name].predict_proba(patient_imputed)[0]
        #         secondary_plot['IOC'] = [prediction[0], prediction[1]]
        #         ci_if['IOC']=[prediction[1]-1.96*np.sqrt(prediction[1]*(1-prediction[1])/(number_samples_if_models['IOC'])),prediction[1]+1.96*np.sqrt(prediction[1]*(1-prediction[1])/(number_samples_if_models['IOC']))]
        
        # ci_if_100={key: [val * 100 for val in values] for key, values in ci_if.items()}
        # secondary_plot = {key: [val * 100 for val in values] for key, values in secondary_plot.items()}
        # plot_figure = spider_chart(secondary_plot,ci_if_100,color_area='rgba(0, 255, 0, 0.5)',color_line='rgba(255,0, 255, 1)')
        # plot_figure = sankey_chart(secondary_plot)
        plot_figure = plot_prob_bar_with_callout(prediction_values['initial.pkl'])
        plot_figure = fig_to_base64_img(plot_figure)
        if cholangitis == "YES":
            main_plot_place_hoder = html.Div(
                style={
                    'position': 'relative',
                    'width': '100%',
                    'height': 'auto',
                    'borderRadius': '10px',
                    'boxShadow': '0 4px 6px rgba(0, 100, 0, 1)',
                    'overflow': 'hidden'
                },
                children=[
                    # Blurred image
                    html.Img(
                        src=plot_figure,
                        style={
                            'width': '100%',
                            'height': 'auto',
                            'filter': 'blur(4px)',
                            'borderRadius': '10px'
                        }
                    ),
                    # Overlay message
                    html.Div(
                        "ASGE 2019 guidelines recommend all patients with cholangitis undergo ERCP as clinically appropriate.",
                        style={
                            'position': 'absolute',
                            'top': '50%',
                            'left': '50%',
                            'transform': 'translate(-50%, -50%)',
                            'backgroundColor': 'rgba(255, 255, 255, 0.9)',
                            'padding': '15px 20px',
                            'borderRadius': '8px',
                            'color': '#c0392b',
                            'fontWeight': 'bold',
                            'fontSize': '16px',
                            'textAlign': 'center',
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
                            'zIndex': 2
                        }
                    )
                ]
            )
        else:
            main_plot_place_hoder = html.Img(
                src=plot_figure,
                style={
                    'width': '100%',
                    'height': 'auto',
                    'borderRadius': '10px',
                    'boxShadow': '0 4px 6px rgba(0, 100, 0, 1)'
                }
            )
        # options = {'IOC':['Proceed to ERCP.','No further action.'],'MRCP':['Proceed to ERCP.',' Revert to IOC (Option 1).'],'EUS':['Proceed to ERCP.','Revert to IOC (Option 1).'],'ERCP':['Immediate ERCP without prior imaging.','Immediate ERCP without prior imaging.']}
        # Build table rows dynamically from secondary_plot
        table_rows = []
        for test in ['IOC', 'MRCP', 'ERCP', 'EUS']:
            # pos = options[test][0]  # Positive
            # neg = options[test][1]  # Negative
            cost_0, cost_1 = cost_values[test]
            exp_loss = f"${cost_0+cost_1*initial_pred/100:.2f}"
            table_rows.append(
                html.Tr([
                    html.Td(test, style={'textAlign': 'center', 'padding': '10px', 'borderBottom': '2px solid #ccc',
                                         'backgroundColor': '#ecf0f1', 'fontWeight': 'bold'}),
                    # html.Td(pos, style={'textAlign': 'center','border': '1px dashed #ccc'}),
                    # html.Td(neg, style={'textAlign': 'center','border': '1px dashed #ccc'}),
                    html.Td(exp_loss, style={'textAlign': 'center', 'padding': '10px', 'borderBottom': '2px solid #ccc',
                                             'backgroundColor': '#ecf0f1', 'fontWeight': 'bold'})
                ])
            )
        table_style = {
            # 'display': 'block',  # Make it visible
            # 'flex': '0',  # Allow horizontal scrolling if needed
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '10px',
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
            # 'width': '450px',
            # 'maxWidth': '100%',
            'fontFamily': 'Arial, sans-serif',
            'marginTop': '10px',
            'fontSize': 'clamp(14px, 2vw, 18px)'
            # 'borderCollapse': 'collapse',  # Important for clean dashed borders
        }
    
        return initial, {'initial_prediction': initial_pred}, main_plot_place_hoder, table_rows, table_style
    
    default_message = html.Div("Enter patient information and click 'Calculate' to view the results.", style={'textAlign': 'center', 'color': '#95a5a6'})
    return ([default_message] * 3) + [no_update]*2

# Run the Dash app
if __name__ == '__main__':
	app.run(host='jupyter.dasl.jhsph.edu', port=1035)