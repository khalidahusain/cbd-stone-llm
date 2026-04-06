<!-- GSD:project-start source:PROJECT.md -->
## Project

**CBD Stone LLM — Conversational Clinical Decision Support**

A conversational, LLM-powered clinical decision support system for assessing the probability of common bile duct (CBD) stones (choledocholithiasis). Clinicians describe a patient case in natural language; an LLM extracts structured clinical variables, passes them to a validated machine learning model, and returns both a natural language explanation and an interpretable clinical dashboard showing risk stratification, recommended interventions, and cost analysis. Built for gastroenterologists and physicians at Johns Hopkins.

**Core Value:** The ML model is the source of truth for clinical predictions — the LLM orchestrates input extraction and explanation but never generates or overrides clinical decisions.

### Constraints

- **Frontend stack**: React (Vite) + TypeScript — no Python UI frameworks (Dash/Streamlit)
- **Backend stack**: Python + FastAPI — serves ML model and orchestrates OpenAI API calls
- **LLM**: GPT-4o-mini via OpenAI API — API key stored server-side only
- **ML Model**: Existing scikit-learn GBM models (.pkl) — used as-is, no retraining
- **Deployment**: Local network, port 450 — public hosting deferred to later
- **Architecture**: LLM is orchestrator only, never decision-maker — model outputs are authoritative
- **YAML config**: Model features, types, ranges defined in YAML — LLM reads this to know what to extract
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python 3.11.2 - All application code, machine learning, and web framework
## Runtime
- Conda environment `cbd` configured in `docs/environment.yml`
- Development tested on Linux environment (jupyter.dasl.jhsph.edu)
- Deployment target: Johns Hopkins web server (jupyter.dasl.jhsph.edu:1035)
- pip 25.0.1 (managed within Conda)
- Conda 3.11.2 environment specification
- Lockfile: `docs/environment.yml` provides reproducible dependency versions
## Frameworks
- Dash 3.0.1 - Web application framework for interactive UI
- Plotly 6.0.1 - Interactive chart generation
- Matplotlib 3.10.3 - Static figure generation
- scikit-learn 1.5.2 - ML models and imputation
## Key Dependencies
- joblib 1.4.2 - Serialization/deserialization of trained models
- pandas 2.2.3 - Data manipulation and DataFrame operations
- numpy 1.26.4 - Numerical computations
- Flask 3.0.3 - WSGI application server (dependency of Dash)
- Werkzeug 3.0.6 - WSGI utilities
- Click 8.1.8 - CLI utilities
- Requests 2.32.3 - HTTP library (potentially for future API integrations)
- Plotly 6.0.1 - Chart rendering library
- Kiwisolver 1.4.8 - Constraint solving for matplotlib
- Contourpy 1.3.2 - Contour calculations
- Fonttools 4.59.0 - Font handling
- Pillow 11.3.0 - Image processing
- python-dateutil 2.9.0.post0 - Date parsing
- pytz 2025.2 - Timezone handling
- tzdata 2025.2 - Timezone database
- Jinja2 3.1.6 - HTML templating (Flask dependency)
- ItsDangerous 2.2.0 - Secure data signing (Flask dependency)
- MarkupSafe 3.0.2 - Safe string handling
- typing-extensions 4.13.0 - Type hint backports
- certifi 2025.1.31 - Root CA certificates
- charset-normalizer 3.4.1 - Character encoding detection
- idna 3.10 - Internationalized domain names
- urllib3 2.3.0 - HTTP library foundation
- six 1.17.0 - Python 2/3 compatibility
- retrying 1.3.4 - Retry logic
- scipy 1.15.2 - Scientific computing (scikit-learn dependency)
- threadpoolctl 3.6.0 - Thread pool control (scikit-learn dependency)
- narwhals 1.32.1 - Dataframe interchange library (likely unused)
- nest-asyncio 1.6.0 - Asyncio nesting (likely unused)
- blinker 1.9.0 - Signal library
## Configuration
- Conda environment specified in `docs/environment.yml`
- Application initialized as Dash app: `app = dash.Dash(__name__)`
- Server configuration hard-coded in `docs/cbd app/app.py` line 585:
- No build step required
- Models precompiled and pickled in `docs/cbd app/Models/`
- Static assets served from `docs/cbd app/assets/` (JSON, images)
## Platform Requirements
- Python 3.11.2
- Conda environment manager
- Access to trained model files (.pkl files)
- Feature configuration files (chosen_features_label.txt)
- Johns Hopkins server infrastructure
- Linux environment (jupyter.dasl.jhsph.edu)
- Network port 1035 accessible
- Permission to read model files from disk
- Enough disk space for pickle files (~600KB total)
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns
- Python module files: `snake_case.py` (e.g., `app.py`, `utils.py`, `patient_form.py`)
- CSS files: `snake_case.css` (e.g., `css.css`, `toggle.css`)
- JSON config files: `snake_case.json` (e.g., `abbreviation.json`)
- Jupyter notebooks: `snake_case.ipynb` (e.g., `batch.ipynb`)
- Dash callbacks: `snake_case` (e.g., `toggle_cholangitis`, `enable_us_toggle`, `update_model_predictions`, `clear_inputs`)
- Utility functions: `snake_case` (e.g., `spider_chart`, `sankey_chart`, `plot_prob_bar_with_callout`, `fig_to_base64_img`)
- Boolean conversion helpers use inline logic: `"YES" if condition else "NO"`
- Module-level constants: `UPPERCASE_WITH_UNDERSCORES` (e.g., not observed in codebase)
- Function parameters and local variables: `snake_case` (e.g., `n_clicks`, `cholangitis`, `patient_imputed`, `cost_0`)
- Dictionary keys use strings matching form/UI semantics: `'Sex'`, `'Cholangitis'`, `'AST'`, `'CBD stone on Abd US'`
- Plotly Graph Objects: Import as `go` (e.g., `import plotly.graph_objects as go`)
- Dash components: Import from `dash` (e.g., `from dash import html, dcc, Input, Output, State`)
- Pandas DataFrames: Use `df` or descriptive names like `patient_df`, `patient_imputed`
- Numpy arrays: Use `np` alias
## Code Style
- No explicit formatter config detected (PEP 8 convention followed implicitly)
- Line length appears unconstrained (some lines exceed 100 characters)
- Indentation: 4 spaces (Python standard)
- No linting config files detected (`.eslintrc`, `.pylintrc` absent)
- No type hints observed in codebase
- Inline comments explain non-obvious logic: `# Get all model files`, `# Remove only the newline, not spaces`
- Comment style: `# Single space after hash`
- Commented code blocks left in place for reference (e.g., lines 448-485 in `app.py`)
- Commented-out code used for experimental features (spider charts, sankey diagrams)
## Import Organization
- Not observed; relative imports used (`from assets.utils import ...`)
## Error Handling
- No explicit try-except blocks observed in main application code
- File I/O assumes files exist (no error handling for missing files):
- Data validation uses conditional checks: `if n_clicks > 0 and sex and age:` to prevent invalid predictions
- Invalid gender values filtered using boolean mask without exception handling (in `batch.ipynb`)
- Toggle states validated via modulo arithmetic: `n % 2 == 1` for binary states
- Empty form fields detected with: `if value and 'done' in value`
- Output validation uses assertions: `assert 0 <= prob <= 100` in `plot_prob_bar_with_callout()`
## Logging
- Debug output uses commented print statements: `# print('cholangitis:', cholangitis)`
- Batch notebook displays data via implicit DataFrame output (Jupyter convention)
- No structured logging or log levels observed
## Comments
- Explain non-intuitive string processing: `# Remove only the newline, not spaces`
- Clarify file loading intent: `# Get all model files`, `# Load the models into a dictionary`
- Denote commented experimental code: `# for _ , model_name in enumerate(model_names):`
- No docstrings observed (functions lack descriptions)
- Comments appear inline rather than above function definitions
- CSS classes documented via HTML comments (e.g., `# Form row layout`)
## Function Design
- Small callbacks (5-12 lines): `toggle_cholangitis`, `toggle_pancreatitis`, `enable_us_toggle`
- Medium callbacks (15-30 lines): `clear_inputs`
- Large callbacks (100+ lines): `update_model_predictions` (169 lines, handles form input → prediction pipeline)
- Dash callbacks use @app.callback decorator with State/Input unpacking
- Function signatures match callback outputs exactly: 13 State inputs for `update_model_predictions`
- Optional parameters use default values: `plot_prob_bar_with_callout(prob, figsize=(10, 2))`
- Callback return values match Output tuples: `[initial, {'initial_prediction': initial_pred}, main_plot_place_hoder, table_rows, table_style]`
- List comprehensions for dynamic content: `[html.Tr([...]) for test in ['IOC', 'MRCP', 'ERCP', 'EUS']]`
- Conditional returns: `if cholangitis == "YES": return blurred_image else: return normal_image`
## Module Design
- `app.py`: Exports `app` object (main Dash application)
- `utils.py`: Exports visualization functions: `spider_chart`, `sankey_chart`, `plot_prob_bar_with_callout`, `fig_to_base64_img`
- `patient_form.py`: Exports form component: `patient_input_form`, `test_results_table`, `abbreviations_notes`, `shared_component_style`
- `imports.py`: Star import pattern: `from assets.imports import *` (imports all pandas/dash/sklearn dependencies)
- `imports.py` acts as centralized import barrel, imported via star in `app.py`
- All utility functions imported explicitly: `from assets.utils import spider_chart, sankey_chart, ...`
## Layout and CSS Conventions
- Extensive use of inline style dictionaries for React components (Dash html/dcc)
- CSS properties use camelCase: `'backgroundColor'`, `'marginTop'`, `'borderRadius'`
- Color scheme: Hex codes (`'#2c3e50'`, `'#2980b9'`, `'#27ae60'`)
- Flexbox for layout: `'display': 'flex'`, `'flexDirection': 'row'`
- Form styling: `.form-row`, `.form-label`
- Component styling: `.prediction-card_prob`, `.toggle`, `.toggle-on`, `.toggle-off`, `.toggle-text`, `.toggle-circle`
- Animations: `@keyframes popIn` with scale and opacity transitions
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern Overview
- Monolithic Dash web application serving as unified UI and API
- Pre-trained ML models (scikit-learn) loaded at startup for inference
- Interactive form-based patient data collection with real-time prediction
- Visualization-driven decision support output
## Layers
- Purpose: Interactive web UI for patient data entry and results display
- Location: `docs/cbd app/app.py` (main Dash layout and callbacks)
- Contains: Dash components (html.Div, dcc.Input, dcc.Dropdown), form layouts, styling
- Depends on: Plotly (visualization), Dash callbacks (state management)
- Used by: End users (physicians) accessing the web dashboard
- Purpose: Modular component definitions for reusable UI elements
- Location: `docs/cbd app/assets/patient_form.py`
- Contains: Patient input form structure, test results table template, abbreviation reference
- Depends on: Dash HTML/core components
- Used by: Main app.py layout for composition
- Purpose: Chart generation and image encoding for prediction results display
- Location: `docs/cbd app/assets/utils.py`
- Contains: `spider_chart()`, `sankey_chart()`, `plot_prob_bar_with_callout()`, `fig_to_base64_img()`
- Depends on: Matplotlib, Plotly, NumPy
- Used by: Callback functions to transform model output into displayable graphics
- Purpose: Centralized import management for all major libraries
- Location: `docs/cbd app/assets/imports.py`
- Contains: Dash, scikit-learn, pandas, plotly, joblib imports
- Depends on: External packages (see environment.yml)
- Used by: app.py via wildcard import
- Purpose: Load and execute pre-trained ML models for prediction
- Location: Models loaded in `docs/cbd app/app.py` (lines 15-17)
- Contains: Joblib-serialized scikit-learn models in `docs/cbd app/Models/` directory
- Models included:
- Depends on: joblib for deserialization, scikit-learn models
- Used by: Prediction callback
- Purpose: Store feature metadata, abbreviations, clinical guidelines
- Location: `docs/cbd app/assets/` directory
- Contains: 
- Depends on: File system
- Used by: App initialization and display
- Purpose: Off-line batch prediction for CSV datasets
- Location: `docs/Batch_pred/`
- Contains: `batch.ipynb`, models, feature definitions
- Note: Jupyter notebook-based, separate from main web app
## Data Flow
- Transient form state held in Dash component state (not persistent)
- Clear button resets all inputs to None/0
- Prediction only computed on Calculate button click (prevent_initial_call=True on many callbacks)
- `prediction-store` dcc.Store holds initial_probability for potential future use
## Key Abstractions
- Representation: Dictionary with keys (Sex, Age, Cholangitis, Pancreatitis, Cholecystitis, AST, ALT, ALP, T.Bilirubin, Abd US, CBD stone on Abd US, CBD stone on CT scan, Charlson Comorbidity Index)
- Examples: `docs/cbd app/app.py` lines 423-437
- Pattern: Raw form input → normalized values → feature vector for ML
- Structure: Float between 0-100 representing probability of choledocholithiasis
- Derivatives: Decision category (CCY/MRCP/EUS/ERCP) determined by range boundaries
- Pattern: `plot_prob_bar_with_callout()` maps probability → categorical recommendation
- Hardcoded references embedded in UI (lines 190-209)
- Derived from ASGE 2019, Tokyo Guidelines, academic publications
- Presented as disclaimers that recommendations require clinical judgment
- Matplotlib figure → BytesIO buffer → PNG bytes → base64 string → HTML data URI
- Pattern: `fig_to_base64_img()` (utils.py lines 235-242)
## Entry Points
- Location: `docs/cbd app/app.py` lines 584-585
- Triggers: `python app.py` or Jupyter notebook invocation
- Responsibilities: 
- Location: `docs/Batch_pred/batch.ipynb`
- Triggers: Jupyter notebook execution
- Responsibilities: Load CSV data, apply same preprocessing, batch predict, output results.csv
## Error Handling
- Model loading failure: Unhandled exception will crash app at startup (line 17)
- Missing files: `FileNotFoundError` from os.listdir() (line 16)
- Invalid form input: No validation; relied on input type constraints
- Imputation failure: Assumes iterative_imputer can handle all data types
- Division/NaN: Only explicit guard is `if n_clicks > 0 and sex and age` (line 413) to avoid partial form submission
## Cross-Cutting Concerns
- No structured logging present
- Print statements commented out (line 422: `# print('cholangitis:', cholangitis)`)
- Only console output during execution
- Minimal: Sex dropdown (constrained to Male/Female), age number input
- No range validation on lab values (e.g., AST could be -1000)
- No required field enforcement before Calculate button
- None implemented
- App accessible to all users on network with host:port access
- Hard-coded: Server host, port, sample sizes, cost values
- No environment-based configuration
- Model paths relative to execution directory (`./Models/`)
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
