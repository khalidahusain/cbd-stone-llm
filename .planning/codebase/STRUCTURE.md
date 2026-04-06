# Codebase Structure

**Analysis Date:** 2026-04-05

## Directory Layout

```
CBD-stone-LLM/
├── .git/                          # Git repository metadata
├── .planning/
│   └── codebase/                  # Architecture documentation (this location)
├── docs/
│   ├── cbd app/                   # Main web application
│   │   ├── app.py                 # Dash application entry point
│   │   ├── test_load.py           # Model loading verification script
│   │   ├── assets/                # UI components, utilities, styling
│   │   │   ├── imports.py         # Centralized library imports
│   │   │   ├── patient_form.py    # Form component definitions
│   │   │   ├── utils.py           # Visualization functions
│   │   │   ├── toggle.css         # Toggle button styles
│   │   │   ├── css.css            # General styling
│   │   │   ├── pic1.png           # Clinical reference image
│   │   │   ├── chosen_features_label.txt  # Data dictionary
│   │   │   ├── abbreviation.json  # Medical abbreviations
│   │   │   └── original.txt       # Original feature list
│   │   ├── Models/                # Serialized ML models (joblib .pkl files)
│   │   │   ├── initial.pkl        # Primary classifier
│   │   │   ├── iterative_imputer.pkl   # KNN imputer
│   │   │   ├── model_predict_if_ercp.pkl
│   │   │   ├── model_predict_if_eus.pkl
│   │   │   ├── model_predict_if_mrcp.pkl
│   │   │   └── model_predict_if_ioc.pkl
│   │   └── .ipynb_checkpoints/    # Jupyter checkpoint files
│   ├── Batch_pred/                # Batch prediction pipeline
│   │   ├── batch.ipynb            # Jupyter notebook for batch processing
│   │   ├── initial.pkl            # Duplicate of primary model
│   │   ├── iterative_imputer.pkl  # Duplicate of imputer
│   │   ├── abbs.json              # Abbreviations for batch
│   │   ├── chosen_features_label.txt  # Features for batch
│   │   ├── check.xlsx             # Input data for batch processing
│   │   └── predictions.csv        # Batch prediction output
│   ├── environment.yml            # Conda environment specification
│   ├── email_spec_of_project.txt  # Project requirements document
│   └── DDW 2025 Choledocholithiasis Prediction Model 5-3-25 1.pdf  # Presentation/documentation
```

## Directory Purposes

**`docs/cbd app/`:**
- Purpose: Main interactive web application using Dash framework
- Contains: Application entry point, UI component definitions, utilities, ML models, styling
- Key files: `app.py` (entry), `assets/` (modularity), `Models/` (inference)

**`docs/cbd app/assets/`:**
- Purpose: Modular UI components and supporting utilities
- Contains: Form builders, visualization utilities, CSS styling, data dictionaries
- Key files: 
  - `patient_form.py`: Reusable form component for patient data entry
  - `utils.py`: Chart generation functions (matplotlib/plotly wrappers)
  - `imports.py`: Centralized dependency management
  - `chosen_features_label.txt`: Clinical data definitions (reference document)
  - `abbreviation.json`: Machine-readable abbreviation mapping

**`docs/cbd app/Models/`:**
- Purpose: Store pre-trained scikit-learn ML models
- Contains: Joblib-serialized classifier and preprocessing pipelines
- Loaded at app startup (line 16-17 of app.py)
- Not version-controlled (binary files)

**`docs/Batch_pred/`:**
- Purpose: Offline batch prediction capability for datasets
- Contains: Jupyter notebook pipeline, duplicate models, sample data
- Separate from main web app; used for processing spreadsheets or CSV exports
- Key files: `batch.ipynb` (executable), `check.xlsx` (sample input), `predictions.csv` (sample output)

**`docs/`:**
- Purpose: Project root containing all source code and documentation
- Contains: Web app, batch processing, environment config, project specs
- Key files: `environment.yml` (reproducible environment), PDF presentation (design rationale)

## Key File Locations

**Entry Points:**

- `docs/cbd app/app.py`: Main Dash web application initialization and layout definition (lines 584-585)
  - Imports all components via `from assets.imports import *`
  - Loads models from `./Models/` directory
  - Registers all callbacks for interactivity
  - Starts Flask/Dash server

- `docs/Batch_pred/batch.ipynb`: Jupyter notebook for batch prediction
  - Loads CSV data (referenced: `check.xlsx`)
  - Applies same preprocessing
  - Outputs predictions to `predictions.csv`

**Configuration:**

- `docs/environment.yml`: Conda environment definition
  - Python 3.11.2
  - Key packages: dash==3.0.1, scikit-learn==1.5.2, matplotlib==3.10.3, plotly==6.0.1
  - Reproducible environment setup

- `docs/cbd app/assets/chosen_features_label.txt`: Data dictionary
  - 16-row reference defining each input feature
  - Clinical criteria from Tokyo Guidelines, ASGE standards
  - Labels map directly to form inputs in `patient_form.py`

- `docs/cbd app/assets/abbreviation.json`: JSON mapping of medical abbreviations
  - Referenced in app display (bottom section)
  - Example: `"CBD": "common bile duct"`

**Core Logic:**

- `docs/cbd app/app.py` (lines 247-582): Callback functions
  - Toggle callbacks: `toggle_cholangitis()`, `toggle_pancreatitis()`, `toggle_cholecystitis()`, `toggle_us()`, `toggle_ct()` (lines 247-341)
  - Form control callbacks: `enable_us_toggle()`, `enable_ct_toggle()` (lines 276-322)
  - Clear form callback: `clear_inputs()` (lines 343-377)
  - Main prediction callback: `update_model_predictions()` (lines 386-581)

- `docs/cbd app/assets/utils.py`: Visualization functions
  - `spider_chart()` (lines 10-108): Radar chart for procedure probabilities
  - `sankey_chart()` (lines 111-161): Flow diagram visualization
  - `plot_prob_bar_with_callout()` (lines 164-233): Main probability bar chart
  - `fig_to_base64_img()` (lines 235-242): Image encoding for HTML embedding

- `docs/cbd app/assets/patient_form.py`: UI component definitions
  - `patient_input_form` (lines 9-181): Complete form with all inputs
  - `test_results_table` (lines 184-223): Table template for cost display
  - `abbreviations_notes` (lines 240-262): Reference list display

**Testing:**

- `docs/cbd app/test_load.py`: Simple model loading verification
  - Confirms `initial.pkl` deserializes correctly with cloudpickle
  - No automated test suite present

**Styling:**

- `docs/cbd app/assets/toggle.css` (57 lines): Custom toggle button styles
  - Classes: `.toggle`, `.toggle-on`, `.toggle-off`, `.toggle-text`, `.toggle-circle`
  - Transition effects on state change

- `docs/cbd app/assets/css.css`: General application styling
  - Form row layouts, button styles, container styling
  - Not fully reviewed (referenced but not read)

**Assets:**

- `docs/cbd app/assets/pic1.png`: Clinical reference image displayed in right sidebar
- `docs/cbd app/assets/original.txt`: Backup or original feature list

## Naming Conventions

**Files:**

- Python modules: snake_case (e.g., `patient_form.py`, `iterative_imputer.pkl`)
- Model files: Descriptive lowercase with underscores (e.g., `model_predict_if_ercp.pkl`, `initial.pkl`)
- Data files: Feature-descriptive lowercase (e.g., `chosen_features_label.txt`)
- Styling: snake_case CSS class definitions matching component purpose

**Directories:**

- Functional grouping: PascalCase for top-level domains (e.g., `Models/`, `Batch_pred/`)
- Sub-modules: lowercase (e.g., `assets/`, `.ipynb_checkpoints/`)

**Component IDs (Dash):**

- HTML element IDs: kebab-case (e.g., `sex-input`, `toggle-cholangitis`, `main_plot_place_hoder`)
- Store IDs: kebab-case (e.g., `prediction-store`)
- Pattern: Short, descriptive, related to form field purpose

**Python Variables & Functions:**

- Functions: snake_case (e.g., `toggle_cholangitis()`, `update_model_predictions()`, `plot_prob_bar_with_callout()`)
- Class instances: camelCase (e.g., `patient_input_form`)
- Model dictionaries: snake_case (e.g., `patient_data`, `secondary_plot`, `prediction_values`)
- Hard-coded data: UPPER_SNAKE_CASE for constants (e.g., cost_values, number_samples_if_models, ci_if)

## Where to Add New Code

**New Feature (Clinical Predictor):**
- Primary code: Add new callback in `docs/cbd app/app.py` following pattern of `update_model_predictions()`
- New model file: Place trained .pkl in `docs/cbd app/Models/`
- New form input: Add input definition to `docs/cbd app/assets/patient_form.py`
- New output visualization: Add helper function to `docs/cbd app/assets/utils.py`
- Update data dictionary: Add row to `docs/cbd app/assets/chosen_features_label.txt`

**New Component/Module:**
- Reusable UI element: Define as variable in `docs/cbd app/assets/patient_form.py`
- Reusable utility function: Add to `docs/cbd app/assets/utils.py`
- Keep utilities separate from main app logic for importability

**Utilities/Helpers:**
- Shared functions: `docs/cbd app/assets/utils.py` (visualization) or new file `docs/cbd app/assets/helpers.py`
- Configuration data: Store in JSON/TXT files in `docs/cbd app/assets/`, load in app.py initialization
- Style additions: Extend `docs/cbd app/assets/css.css` or create feature-specific `.css` file

**Batch Processing:**
- Extend `docs/Batch_pred/batch.ipynb` with new processing cells
- Duplicate relevant models to `docs/Batch_pred/` for self-contained execution
- Output results follow `predictions.csv` format

## Special Directories

**`docs/cbd app/Models/`:**
- Purpose: ML model storage
- Generated: No (pre-trained offline)
- Committed: Typically yes (binary .pkl files, ~700KB total)
- Load method: Joblib in app.py line 17 via dictionary comprehension
- Note: Models are versioned by date in filename convention (e.g., implicit from training runs)

**`docs/cbd app/.ipynb_checkpoints/`:**
- Purpose: Jupyter automatic checkpoint directory
- Generated: Yes (auto-created by Jupyter)
- Committed: No (typically in .gitignore)
- Contains: Backup versions of app.py, utils.py, etc.

**`docs/Batch_pred/`:**
- Purpose: Offline prediction pipeline
- Generated: Output files (predictions.csv)
- Committed: .ipynb and .pkl files yes; generated CSVs typically no
- Isolation: Complete copy of models to avoid dependency on main app directory

---

*Structure analysis: 2026-04-05*
