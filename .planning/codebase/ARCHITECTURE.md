# Architecture

**Analysis Date:** 2026-04-05

## Pattern Overview

**Overall:** Medical prediction web application with multi-layer architecture combining UI framework, ML model inference, and visualization components.

**Key Characteristics:**
- Monolithic Dash web application serving as unified UI and API
- Pre-trained ML models (scikit-learn) loaded at startup for inference
- Interactive form-based patient data collection with real-time prediction
- Visualization-driven decision support output

## Layers

**Presentation Layer:**
- Purpose: Interactive web UI for patient data entry and results display
- Location: `docs/cbd app/app.py` (main Dash layout and callbacks)
- Contains: Dash components (html.Div, dcc.Input, dcc.Dropdown), form layouts, styling
- Depends on: Plotly (visualization), Dash callbacks (state management)
- Used by: End users (physicians) accessing the web dashboard

**Component Assembly Layer:**
- Purpose: Modular component definitions for reusable UI elements
- Location: `docs/cbd app/assets/patient_form.py`
- Contains: Patient input form structure, test results table template, abbreviation reference
- Depends on: Dash HTML/core components
- Used by: Main app.py layout for composition

**Visualization & Utility Layer:**
- Purpose: Chart generation and image encoding for prediction results display
- Location: `docs/cbd app/assets/utils.py`
- Contains: `spider_chart()`, `sankey_chart()`, `plot_prob_bar_with_callout()`, `fig_to_base64_img()`
- Depends on: Matplotlib, Plotly, NumPy
- Used by: Callback functions to transform model output into displayable graphics

**Import/Dependency Aggregation Layer:**
- Purpose: Centralized import management for all major libraries
- Location: `docs/cbd app/assets/imports.py`
- Contains: Dash, scikit-learn, pandas, plotly, joblib imports
- Depends on: External packages (see environment.yml)
- Used by: app.py via wildcard import

**Model Inference Layer:**
- Purpose: Load and execute pre-trained ML models for prediction
- Location: Models loaded in `docs/cbd app/app.py` (lines 15-17)
- Contains: Joblib-serialized scikit-learn models in `docs/cbd app/Models/` directory
- Models included:
  - `initial.pkl`: Primary choledocholithiasis probability predictor
  - `iterative_imputer.pkl`: KNN-based missing value imputation
  - `model_predict_if_ercp.pkl`: Conditional probability if ERCP performed
  - `model_predict_if_eus.pkl`: Conditional probability if EUS performed
  - `model_predict_if_mrcp.pkl`: Conditional probability if MRCP performed
  - `model_predict_if_ioc.pkl`: Conditional probability if IOC performed
- Depends on: joblib for deserialization, scikit-learn models
- Used by: Prediction callback

**Data & Configuration Layer:**
- Purpose: Store feature metadata, abbreviations, clinical guidelines
- Location: `docs/cbd app/assets/` directory
- Contains: 
  - `chosen_features_label.txt`: Clinical definitions and data dictionary
  - `abbreviation.json`: Medical term abbreviations
  - `toggle.css`, `css.css`: Styling rules
  - `pic1.png`: Clinical reference image
- Depends on: File system
- Used by: App initialization and display

**Batch Processing Pipeline (Optional):**
- Purpose: Off-line batch prediction for CSV datasets
- Location: `docs/Batch_pred/`
- Contains: `batch.ipynb`, models, feature definitions
- Note: Jupyter notebook-based, separate from main web app

## Data Flow

**Interactive Prediction Flow:**

1. **User Input Capture**
   - User enters patient demographics (sex, age, Charlson index) in `patient_input_form`
   - User enters lab values (AST, ALT, ALP, Total Bilirubin) via `dcc.Input` components
   - User toggles clinical conditions (cholangitis, pancreatitis, cholecystitis) via custom toggle buttons
   - User checks imaging completion (Abd US, CT) and indicates stone findings via checkboxes/toggles

2. **State Aggregation**
   - Callback `update_model_predictions()` collects all form state via `State()` inputs
   - Form values stored in dictionary: `patient_data` (line 423-437)

3. **Data Transformation**
   - Patient data converted to pandas DataFrame
   - String values converted: `YES/NO → 1/0`, `Male/Female → 1/0`
   - Missing values imputed via `iterative_imputer.pkl` transform

4. **Model Inference**
   - Imputed patient data passed to `initial.pkl` classifier
   - `predict_proba()` returns [prob_no_stone, prob_stone]
   - Probability scaled to percentage (0-100)

5. **Visualization Generation**
   - Primary output: `plot_prob_bar_with_callout()` creates matplotlib bar chart with decision regions:
     - 0-10%: CCY ± IOC (cholecystectomy ± intraoperative cholangiogram)
     - 10-44%: MRCP (magnetic resonance cholangiopancreatography)
     - 44-90%: EUS (endoscopic ultrasound)
     - 90-100%: ERCP (endoscopic retrograde cholangiopancreatography)
   - Chart converted to base64 image string for HTML embedding

6. **Conditional Logic**
   - If cholangitis == "YES": Chart overlaid with red warning text (lines 493-534)
   - Otherwise: Chart displayed normally

7. **Cost Calculation**
   - For each test (IOC, MRCP, ERCP, EUS), expected cost calculated
   - Formula: `cost_0 + cost_1 * (initial_prob / 100)` (line 552)
   - Cost values hardcoded in dict (lines 8-13)

8. **Output Rendering**
   - Prediction text: "The probability of a stone in the CBD is {prob}%"
   - Main chart: Base64 image in `html.Img` component
   - Cost table: Dynamically built `html.Table` with test-cost rows
   - Clinical guidelines: Hardcoded reference text

**State Management:**

- Transient form state held in Dash component state (not persistent)
- Clear button resets all inputs to None/0
- Prediction only computed on Calculate button click (prevent_initial_call=True on many callbacks)
- `prediction-store` dcc.Store holds initial_probability for potential future use

## Key Abstractions

**Patient Profile:**
- Representation: Dictionary with keys (Sex, Age, Cholangitis, Pancreatitis, Cholecystitis, AST, ALT, ALP, T.Bilirubin, Abd US, CBD stone on Abd US, CBD stone on CT scan, Charlson Comorbidity Index)
- Examples: `docs/cbd app/app.py` lines 423-437
- Pattern: Raw form input → normalized values → feature vector for ML

**Prediction Result:**
- Structure: Float between 0-100 representing probability of choledocholithiasis
- Derivatives: Decision category (CCY/MRCP/EUS/ERCP) determined by range boundaries
- Pattern: `plot_prob_bar_with_callout()` maps probability → categorical recommendation

**Clinical Guideline Context:**
- Hardcoded references embedded in UI (lines 190-209)
- Derived from ASGE 2019, Tokyo Guidelines, academic publications
- Presented as disclaimers that recommendations require clinical judgment

**Visualization Pipeline:**
- Matplotlib figure → BytesIO buffer → PNG bytes → base64 string → HTML data URI
- Pattern: `fig_to_base64_img()` (utils.py lines 235-242)

## Entry Points

**Web Application:**
- Location: `docs/cbd app/app.py` lines 584-585
- Triggers: `python app.py` or Jupyter notebook invocation
- Responsibilities: 
  - Initialize Dash app
  - Load all ML models from disk
  - Parse feature definitions from .txt file
  - Define complete layout with form and results area
  - Register all callbacks (form validation, prediction, clearing)
  - Start Flask development server on host `jupyter.dasl.jhsph.edu` port 1035

**Batch Processing:**
- Location: `docs/Batch_pred/batch.ipynb`
- Triggers: Jupyter notebook execution
- Responsibilities: Load CSV data, apply same preprocessing, batch predict, output results.csv

## Error Handling

**Strategy:** Minimal explicit error handling; relies on Dash's default behavior

**Patterns:**
- Model loading failure: Unhandled exception will crash app at startup (line 17)
- Missing files: `FileNotFoundError` from os.listdir() (line 16)
- Invalid form input: No validation; relied on input type constraints
- Imputation failure: Assumes iterative_imputer can handle all data types
- Division/NaN: Only explicit guard is `if n_clicks > 0 and sex and age` (line 413) to avoid partial form submission

## Cross-Cutting Concerns

**Logging:** 
- No structured logging present
- Print statements commented out (line 422: `# print('cholangitis:', cholangitis)`)
- Only console output during execution

**Validation:** 
- Minimal: Sex dropdown (constrained to Male/Female), age number input
- No range validation on lab values (e.g., AST could be -1000)
- No required field enforcement before Calculate button

**Authentication:** 
- None implemented
- App accessible to all users on network with host:port access

**Configuration:**
- Hard-coded: Server host, port, sample sizes, cost values
- No environment-based configuration
- Model paths relative to execution directory (`./Models/`)

---

*Architecture analysis: 2026-04-05*
