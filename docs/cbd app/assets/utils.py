import numpy as np
import plotly.graph_objects as go
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

def spider_chart(probabilities, confidence_intervals,
                 color_area='rgba(0, 128, 255, 0.2)', color_line='rgba(0, 128, 255, 1)', total=2342):
    
    data_labels = ['MRCP', 'EUS', 'ERCP', 'IOC']
    base_prob_ppl_who_received_procedures = {
        'MRCP': 666/total*100,
        'EUS': 411/total*100,
        'ERCP': 1162/total*100,
        'IOC': 309/total*100
    }

    values = [probabilities[label][1] for label in data_labels]
    value0 = [base_prob_ppl_who_received_procedures[label] for label in data_labels]
    ci_lower = [confidence_intervals[label][0] for label in data_labels]
    ci_upper = [confidence_intervals[label][1] for label in data_labels]

    # Close the loop for radar chart
    values.append(values[0])
    ci_lower.append(ci_lower[0])
    ci_upper.append(ci_upper[0])
    data_labels.append(data_labels[0])
    value0.append(value0[0])

    fig = go.Figure()

    # Confidence band
    fig.add_trace(go.Scatterpolar(
        r=ci_lower,
        theta=data_labels,
        fill=None,
        name='95% CI (Lower)',
        line=dict(color='rgba(0,0,0,0)'),
        hoverinfo='skip',
        showlegend=False
    ))

    fig.add_trace(go.Scatterpolar(
        r=ci_upper,
        theta=data_labels,
        fill='tonext',
        name='95% Confidence Interval',
        line=dict(color='rgba(0,0,0,0)'),
        fillcolor=color_area,
        hoverinfo='skip'
    ))

    # Main probability line
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=data_labels,
        name='Rates of procedures for similar patients',
        line=dict(color=color_line, width=3),
        marker=dict(size=6),
        hovertemplate='%{theta}: %{r:.1f}%'
    ))

    # Base probability line (dashed)
    fig.add_trace(go.Scatterpolar(
        r=value0,
        theta=data_labels,
        name='Reference rate across all patients',
        line=dict(color='black', width=2, dash='dash'),
        marker=dict(size=6),
        hovertemplate='%{theta}: %{r:.1f}%'
    ))

    # Layout styling
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(255,255,255,0)',
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=12),
                gridcolor='lightgrey',
                gridwidth=1,
                linecolor='grey',
                linewidth=1
            ),
            angularaxis=dict(
                tickfont=dict(size=13, family='Arial', color='black')
            )
        ),
        showlegend=True,
        legend=dict(
            font=dict(size=14, color='black'),
            orientation="h",
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='black',
            borderwidth=1,
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=40, r=40, t=40, b=100)
    )

    return fig


def sankey_chart(probabilities):
    data_labels = ['MRCP', 'EUS', 'ERCP', 'IOC']

    # Extract predicted probabilities
    pred_probs = {label: probabilities[label][1] for label in data_labels}

    # Define labels: source + targets
    label_values = [f"{label}<br>{pred_probs[label]:.1f}%" for label in data_labels]
    labels = ['Similar-risk patients'] + label_values

    # All links come from node 0 to each of the targets
    source = [0] * len(data_labels)
    target = list(range(1, len(data_labels) + 1))
    values = [pred_probs[label] for label in data_labels]

    # All links are the same green color
    green_link_color = 'rgba(180, 235, 229, 0.6)'
    link_colors = [green_link_color] * len(data_labels)

    # Node colors: first is left source node (neutral gray), others are the colors at the ends
    node_colors = [
        'rgba(170, 220, 217, 1)',      # Similar-risk patients (subtle greenish gray)
        'rgba(255, 255, 153, 1)',      # IOC: Yellow
        'rgba(204, 204, 255, 1)',      # MRCP: Lavender
        'rgba(255, 153, 153, 1)',      # EUS: Pinkish red
        'rgba(153, 204, 255, 1)'       # ERCP: Blue
    ]

    fig = go.Figure(data=[go.Sankey(
        arrangement="freeform",
        textfont=dict(
            family="Arial",    # or "Courier New", "Helvetica", etc.
            size=14,
            color="black"
            ),
        node=dict(
            pad=20,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=node_colors
        ),
        link=dict(
            source=source,
            target=target,
            value=values,
            color=link_colors
        )
    )])

    return fig


def plot_prob_bar_with_callout(prob, figsize=(10, 2)):
    assert 0 <= prob <= 100
    prob /= 100 
    # Define the regions (start, end, label)
    regions = [
        (0.0, 0.10, "CCY ± IOC"),
        (0.10, 0.44, "MRCP"),
        (0.44, 0.90, "EUS"),
        (0.90, 1.00, "ERCP")
    ]
    start_rgb = np.array([198, 239, 1]) / 255
    end_rgb = np.array([0, 100, 0]) / 255
    gradient = np.linspace(start_rgb, end_rgb, 500).reshape(1, 500, 3) 
    bar_bottom = 0.1
    bar_top = 0.75
    bar_height = bar_top - bar_bottom
    fig, ax = plt.subplots(figsize=figsize)
    
    ax.imshow(gradient, extent=(0, 1, bar_bottom, bar_top), aspect='auto')

    # Add region labels
    for start, end, label in regions:
        ax.text((start + end) / 2, (bar_bottom + bar_top) / 2,
                label, ha='center', va='center', fontsize=12, color='black')
    
    # Dynamically compute vertical line top/bottom
    line_top = bar_top
    line_bottom = bar_bottom - 0.15

    # Plot dynamic vertical lines using ax.plot in data coords
    for boundary in [r[1] for r in regions[:-1]]:
        ax.plot([boundary, boundary], [line_bottom, line_top], color='black', linewidth=2)

    # X-axis style
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.3, 1)
    ax.axis('off')

    # Percent ticks manually added
    tick_fontsize = 16
    for p in [0.10, 0.44, 0.90]:
        ax.text(p, -0.15, f"{int(p * 100)}%", ha='center', va='top', fontsize=tick_fontsize)

    ax.text(0, -0.15, "0%", ha='left', va='top', fontsize=tick_fontsize)
    ax.text(1, -0.15, "100%", ha='right', va='top', fontsize=tick_fontsize)

    # Determine region based on input probability
    region_label = None
    for start, end, label in regions:
        if start <= prob < end:
            region_label = label
            break
    if region_label is None:
        region_label = "Unknown"
        
    gradient_rgb = gradient[0]  # shape: (500, 3)
    gradient_index = int(prob * 499)  # Map prob ∈ [0,1] to [0,499]
    matched_color = gradient_rgb[gradient_index]
    
    # Arrow and label
    ax.annotate(region_label,
                xy=(prob, bar_top - 0.25), xytext=(prob, bar_top + 0.5),
                arrowprops=dict(facecolor='orange', shrink=0.05, width=3, headwidth=8),
                bbox=dict(boxstyle="round,pad=0.4", fc=matched_color, ec="black"),
                ha='center', va='bottom', color='white', fontsize=16, weight='bold')
    
    # ax.set_title("Probability-Based Decision Support", fontsize=12, pad=25)
    plt.tight_layout()
    plt.close()
    return fig

def fig_to_base64_img(fig):
    """Convert a Matplotlib figure to a base64-encoded image URI for Dash display."""
    buf = BytesIO()
    FigureCanvas(fig).print_png(buf)
    buf.seek(0)
    img_bytes = buf.read()
    base64_img = base64.b64encode(img_bytes).decode("ascii")
    return f"data:image/png;base64,{base64_img}"