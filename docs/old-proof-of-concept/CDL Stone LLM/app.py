import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go

from dummy_chat import respond_to_user

# ---------------- Initial data ---------------- #

INITIAL_HISTORY = [
    {
        "role": "assistant",
        "content": (
            "Hi, I am a custom LLM assistant to help you assist with "
            "assessing common bile duct stone risk. "
        ),
    }
]

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


# ---------------- Helper functions for UI ---------------- #

def render_message(msg):
    is_user = msg["role"] == "user"
    alignment = "end" if is_user else "start"
    bubble_color = "primary" if is_user else "light"

    return html.Div(
        dbc.Card(
            dbc.CardBody(
                html.P(msg["content"], className="mb-0"),
            ),
            color=bubble_color,
            inverse=is_user,
            className="shadow-sm",
            style={"maxWidth": "80%"},
        ),
        className=f"d-flex justify-content-{alignment} mb-2",
    )


def build_probability_card(pred):
    if not pred:
        return dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Prediction", className="mb-2"),
                    html.P(
                        "No prediction yet. Ask about a patient to see results.",
                        className="mb-0",
                    ),
                ]
            ),
            className="mb-3",
        )

    prob = pred["probability"]
    return dbc.Card(
        dbc.CardBody(
            [
                html.H5("Prediction", className="mb-3"),
                html.Div(
                    f"The probability of a stone in the CBD is {prob:.2f}%.",
                    className="fw-bold mb-2",
                ),
                html.Div(
                    f"The suggested next step in management is: {pred['next_step']}",
                    className="mb-0",
                ),
            ]
        ),
        color="success",
        inverse=True,
        className="mb-3",
    )


def build_risk_bar(pred):
    """
    Build a static-style risk bar similar to the design mock, using pure HTML/CSS
    instead of a Plotly graph. This avoids layout/resizing loops.
    """
    # Base container when no prediction yet
    if not pred:
        return dbc.Card(
            dbc.CardBody(
                html.Div(
                    "The suggested next step in management will appear here once a prediction is available.",
                    className="text-center text-muted",
                )
            ),
            className="mt-3",
        )

    prob = pred["probability"]
    next_step = pred["next_step"]
    bands = pred["bands"]

    # Compute widths for each band and the tick marks (0, 10, 44, 90, 100)
    segments = []
    total_width = 100.0
    colors = ["#c7f0b3", "#a8e6a3", "#7bc96f", "#4aaf50"]

    for (color, (label, (start, end))) in zip(colors, bands.items()):
        width_pct = end - start
        segments.append(
            html.Div(
                label,
                style={
                    "flex": f"0 0 {width_pct}%",
                    "textAlign": "center",
                    "lineHeight": "40px",
                    "fontWeight": "500",
                    "backgroundColor": color,
                },
            )
        )

    # Tick labels at band boundaries
    boundaries = [0.0]
    for (start, end) in bands.values():
        boundaries.append(end)
    # Ensure uniqueness and sorting
    boundaries = sorted(set(boundaries))

    tick_labels = []
    for b in boundaries:
        tick_labels.append(
            html.Div(
                f"{int(b)}%",
                style={
                    "position": "absolute",
                    "left": f"{b}%",
                    "bottom": 0,
                    "transform": "translateX(-50%) translateY(100%)",
                    "fontSize": "0.8rem",
                },
            )
        )

    # Pointer showing the suggested next step
    pointer = html.Div(
        [
            html.Div(
                next_step,
                style={
                    "backgroundColor": "#4CAF50",
                    "color": "white",
                    "padding": "4px 10px",
                    "borderRadius": "12px",
                    "fontWeight": "700",
                    "fontSize": "0.9rem",
                    "textAlign": "center",
                },
            ),
            html.Div(
                "▼",
                style={
                    "textAlign": "center",
                    "marginTop": "-6px",
                    "fontSize": "1rem",
                    "color": "#4CAF50",
                },
            ),
        ],
        style={
            "position": "absolute",
            "top": "-40px",
            "left": f"{prob}%",
            "transform": "translateX(-50%)",
        },
    )

    bar = html.Div(
        [
            # Pointer and ticks are absolutely positioned over the bar
            pointer,
            *tick_labels,
            # The actual banded bar
            html.Div(
                segments,
                style={
                    "display": "flex",
                    "height": "40px",
                    "borderRadius": "8px",
                    "overflow": "hidden",
                    "border": "1px solid #7cbf5b",
                },
            ),
        ],
        style={
            "position": "relative",
            "paddingTop": "16px",
            "paddingBottom": "32px",  # room for tick labels plus extra spacing
            "marginTop": "0.75rem",
        },
    )

    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    "The suggested next step in management is:",
                    className="fw-bold mb-2 text-center",
                ),
                bar,
            ],
            style={
                "paddingBottom": "40px"  # extra space at bottom for cleaner look
            },
        ),
        className="mt-3",
    )


def build_cost_table(pred):
    if not pred:
        return html.Div()

    rows = [
        html.Tr(
            [
                html.Td(row["test"]),
                html.Td(f"${row['cost']:,.2f}"),
            ]
        )
        for row in pred["costs"]
    ]

    table = dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Test"),
                        html.Th("Probability weighted cost"),
                    ]
                )
            ),
            html.Tbody(rows),
        ],
        bordered=True,
        hover=True,
        size="sm",
    )

    return dbc.Card(
        [
            dbc.CardHeader("Cost associated with interventions"),
            dbc.CardBody(table),
        ],
        className="mt-3",
    )


# ---------------- Layout ---------------- #

app.layout = dbc.Container(
    [
        dcc.Store(id="chat-history", data=INITIAL_HISTORY),
        dcc.Store(id="prediction-store", data=None),
        dcc.Store(id="scroll-trigger"),

        html.H3("CBD Stone Risk Assistant (prototype)", className="mt-4 mb-3"),

        dbc.Row(
            [
                # Left column: chat
                dbc.Col(
                    [
                        html.Div(
                            id="chat-window",
                            children=[render_message(m) for m in INITIAL_HISTORY],
                            style={
                                "border": "1px solid #dee2e6",
                                "borderRadius": "0.5rem",
                                "padding": "1rem",
                                "height": "calc(100vh - 220px)",
                                "overflowY": "auto",
                                "backgroundColor": "#f8f9fa",
                            },
                        ),
                        dbc.InputGroup(
                            [
                                dcc.Input(
                                    id="user-input",
                                    type="text",
                                    placeholder="Type your question and press Enter...",
                                    n_submit=0,
                                    style={"width": "100%"},
                                ),
                                dbc.Button(
                                    "Send",
                                    id="send-button",
                                    color="primary",
                                    n_clicks=0,
                                    style={"marginTop": "0.5rem"},
                                ),
                            ],
                            className="mt-2",
                            style={"flexDirection": "column"},
                        ),
                    ],
                    md=6,
                ),

                # Right column: prediction dashboard
                dbc.Col(
                    [
                        html.Div(id="probability-card"),
                        html.Div(id="risk-bar", style={"marginTop": "0.5rem"}),
                        html.Div(id="cost-table-card"),
                    ],
                    md=6,
                ),
            ],
            className="mt-3",
        ),
    ],
    fluid=True,
)


# ---------------- Callbacks ---------------- #

@app.callback(
    Output("chat-history", "data"),
    Output("prediction-store", "data"),
    Output("user-input", "value"),
    Input("send-button", "n_clicks"),
    Input("user-input", "n_submit"),
    State("user-input", "value"),
    State("chat-history", "data"),
    prevent_initial_call=True,
)
def handle_message(btn_clicks, enter_presses, user_text, history):
    """Handle user input when the button is clicked or Enter is pressed."""
    if not (btn_clicks or enter_presses):
        raise PreventUpdate

    text = (user_text or "").strip()
    if not text:
        raise PreventUpdate

    history = history or []
    history.append({"role": "user", "content": text})

    reply, prediction = respond_to_user(text, history)
    history.append({"role": "assistant", "content": reply})

    # Clear input after sending
    return history, prediction, ""


# --- Split UI refresh into two callbacks: chat and dashboard ---

# Chat-only callback
@app.callback(
    Output("chat-window", "children"),
    Input("chat-history", "data"),
)
def update_chat_window(history):
    """Render chat history only."""
    history = history or []
    messages = [render_message(m) for m in history]
    return messages

# Dashboard-only callback
@app.callback(
    Output("probability-card", "children"),
    Output("risk-bar", "children"),
    Output("cost-table-card", "children"),
    Input("prediction-store", "data"),
)
def update_dashboard(prediction):
    """Render the right-hand prediction dashboard."""
    prob_card = build_probability_card(prediction)
    risk_bar = build_risk_bar(prediction)
    cost_card = build_cost_table(prediction)
    return prob_card, risk_bar, cost_card


# --- Client-side callback to auto-scroll chat window to bottom ---
app.clientside_callback(
    """
    function(history) {
        // Auto-scroll chat window to the bottom whenever history updates
        window.setTimeout(function() {
            var chat = document.getElementById('chat-window');
            if (chat) {
                chat.scrollTop = chat.scrollHeight;
            }
        }, 50);
        // We must return something, but it is unused
        return '';
    }
    """,
    Output("scroll-trigger", "data"),
    Input("chat-history", "data"),
)


if __name__ == "__main__":
    app.run(debug=True)