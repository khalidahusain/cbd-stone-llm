# Coding Conventions

**Analysis Date:** 2026-04-05

## Naming Patterns

**Files:**
- Python module files: `snake_case.py` (e.g., `app.py`, `utils.py`, `patient_form.py`)
- CSS files: `snake_case.css` (e.g., `css.css`, `toggle.css`)
- JSON config files: `snake_case.json` (e.g., `abbreviation.json`)
- Jupyter notebooks: `snake_case.ipynb` (e.g., `batch.ipynb`)

**Functions:**
- Dash callbacks: `snake_case` (e.g., `toggle_cholangitis`, `enable_us_toggle`, `update_model_predictions`, `clear_inputs`)
- Utility functions: `snake_case` (e.g., `spider_chart`, `sankey_chart`, `plot_prob_bar_with_callout`, `fig_to_base64_img`)
- Boolean conversion helpers use inline logic: `"YES" if condition else "NO"`

**Variables:**
- Module-level constants: `UPPERCASE_WITH_UNDERSCORES` (e.g., not observed in codebase)
- Function parameters and local variables: `snake_case` (e.g., `n_clicks`, `cholangitis`, `patient_imputed`, `cost_0`)
- Dictionary keys use strings matching form/UI semantics: `'Sex'`, `'Cholangitis'`, `'AST'`, `'CBD stone on Abd US'`

**Types:**
- Plotly Graph Objects: Import as `go` (e.g., `import plotly.graph_objects as go`)
- Dash components: Import from `dash` (e.g., `from dash import html, dcc, Input, Output, State`)
- Pandas DataFrames: Use `df` or descriptive names like `patient_df`, `patient_imputed`
- Numpy arrays: Use `np` alias

## Code Style

**Formatting:**
- No explicit formatter config detected (PEP 8 convention followed implicitly)
- Line length appears unconstrained (some lines exceed 100 characters)
- Indentation: 4 spaces (Python standard)

**Linting:**
- No linting config files detected (`.eslintrc`, `.pylintrc` absent)
- No type hints observed in codebase

**Comments and Inline Documentation:**
- Inline comments explain non-obvious logic: `# Get all model files`, `# Remove only the newline, not spaces`
- Comment style: `# Single space after hash`
- Commented code blocks left in place for reference (e.g., lines 448-485 in `app.py`)
- Commented-out code used for experimental features (spider charts, sankey diagrams)

## Import Organization

**Order:**
1. External framework imports: `dash`, `dash_daq`, `plotly`
2. Data science libraries: `pandas`, `numpy`, `sklearn`
3. Standard library utilities: `os`, `json`, `joblib`
4. Visualization: `matplotlib.pyplot`
5. IO utilities: `BytesIO`, `base64`, `FigureCanvas`

**Examples from `app.py`:**
```python
from assets.imports import *
from assets.utils import spider_chart, sankey_chart, plot_prob_bar_with_callout, fig_to_base64_img
from assets.patient_form import patient_input_form, test_results_table, abbreviations_notes, shared_component_style
```

**Examples from `imports.py`:**
```python
import dash
import dash_daq as daq
from dash import dcc, html, Input, Output, State
from dash import no_update
import plotly.express as px
from sklearn.impute import KNNImputer
import pandas as pd
import numpy as np
import os
import joblib
import plotly.graph_objects as go
import json
import matplotlib.pyplot as plt
```

**Path Aliases:**
- Not observed; relative imports used (`from assets.utils import ...`)

## Error Handling

**Patterns:**
- No explicit try-except blocks observed in main application code
- File I/O assumes files exist (no error handling for missing files):
  ```python
  with open('./assets/chosen_features_label.txt', 'r') as file:
      chosen_features_label_read = [line[:-1] if line.endswith('\n') else line for line in file]
  ```
- Data validation uses conditional checks: `if n_clicks > 0 and sex and age:` to prevent invalid predictions
- Invalid gender values filtered using boolean mask without exception handling (in `batch.ipynb`)

**Validation:**
- Toggle states validated via modulo arithmetic: `n % 2 == 1` for binary states
- Empty form fields detected with: `if value and 'done' in value`
- Output validation uses assertions: `assert 0 <= prob <= 100` in `plot_prob_bar_with_callout()`

## Logging

**Framework:** Not used; no logging configuration detected

**Patterns:**
- Debug output uses commented print statements: `# print('cholangitis:', cholangitis)`
- Batch notebook displays data via implicit DataFrame output (Jupyter convention)
- No structured logging or log levels observed

## Comments

**When to Comment:**
- Explain non-intuitive string processing: `# Remove only the newline, not spaces`
- Clarify file loading intent: `# Get all model files`, `# Load the models into a dictionary`
- Denote commented experimental code: `# for _ , model_name in enumerate(model_names):`

**Documentation:**
- No docstrings observed (functions lack descriptions)
- Comments appear inline rather than above function definitions
- CSS classes documented via HTML comments (e.g., `# Form row layout`)

## Function Design

**Size:** 
- Small callbacks (5-12 lines): `toggle_cholangitis`, `toggle_pancreatitis`, `enable_us_toggle`
- Medium callbacks (15-30 lines): `clear_inputs`
- Large callbacks (100+ lines): `update_model_predictions` (169 lines, handles form input → prediction pipeline)

**Parameters:**
- Dash callbacks use @app.callback decorator with State/Input unpacking
- Function signatures match callback outputs exactly: 13 State inputs for `update_model_predictions`
- Optional parameters use default values: `plot_prob_bar_with_callout(prob, figsize=(10, 2))`

**Return Values:**
- Callback return values match Output tuples: `[initial, {'initial_prediction': initial_pred}, main_plot_place_hoder, table_rows, table_style]`
- List comprehensions for dynamic content: `[html.Tr([...]) for test in ['IOC', 'MRCP', 'ERCP', 'EUS']]`
- Conditional returns: `if cholangitis == "YES": return blurred_image else: return normal_image`

## Module Design

**Exports:**
- `app.py`: Exports `app` object (main Dash application)
- `utils.py`: Exports visualization functions: `spider_chart`, `sankey_chart`, `plot_prob_bar_with_callout`, `fig_to_base64_img`
- `patient_form.py`: Exports form component: `patient_input_form`, `test_results_table`, `abbreviations_notes`, `shared_component_style`
- `imports.py`: Star import pattern: `from assets.imports import *` (imports all pandas/dash/sklearn dependencies)

**Barrel Files:**
- `imports.py` acts as centralized import barrel, imported via star in `app.py`
- All utility functions imported explicitly: `from assets.utils import spider_chart, sankey_chart, ...`

## Layout and CSS Conventions

**Inline Styles:**
- Extensive use of inline style dictionaries for React components (Dash html/dcc)
- CSS properties use camelCase: `'backgroundColor'`, `'marginTop'`, `'borderRadius'`
- Color scheme: Hex codes (`'#2c3e50'`, `'#2980b9'`, `'#27ae60'`)
- Flexbox for layout: `'display': 'flex'`, `'flexDirection': 'row'`

**CSS Classes:**
- Form styling: `.form-row`, `.form-label`
- Component styling: `.prediction-card_prob`, `.toggle`, `.toggle-on`, `.toggle-off`, `.toggle-text`, `.toggle-circle`
- Animations: `@keyframes popIn` with scale and opacity transitions

---

*Convention analysis: 2026-04-05*
