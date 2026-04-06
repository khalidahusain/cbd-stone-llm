# Codebase Concerns

**Analysis Date:** 2026-04-05

## Security Issues

**Pickle Model Loading - Arbitrary Code Execution Risk:**
- Issue: Using `joblib.load()` to load `.pkl` model files from `./Models/` directory without validation. Pickle is fundamentally unsafe and can execute arbitrary Python code during deserialization.
- Files: 
  - `docs/cbd app/app.py` (lines 15-17)
  - `docs/cbd app/test_load.py` (uses `cloudpickle.load()`)
  - `docs/Batch_pred/batch.ipynb` (loads models with `joblib.load()`)
- Impact: Critical - Any compromised pickle file in Models directory could lead to full system compromise. Supply chain attack vector if models are downloaded or shared.
- Fix approach: Replace pickle with safer serialization formats (ONNX, joblib with protocol='dask', or JSON-based formats). If pickle must be used, implement cryptographic signing and integrity verification. Restrict file permissions on Models directory.

**Hardcoded Host and Port:**
- Issue: Production host and port hardcoded in application entry point
- Files: `docs/cbd app/app.py` (line 585): `app.run(host='jupyter.dasl.jhsph.edu', port=1035)`
- Impact: High - Makes it impossible to run app in different environments without code modification. Exposes internal infrastructure hostname.
- Fix approach: Move host/port to environment variables with sensible defaults. Use `os.getenv('DASH_HOST', '0.0.0.0')` and `os.getenv('DASH_PORT', 8050)`.

**Missing Input Validation:**
- Issue: No validation on numeric inputs (age, lab values, Charlson index) before passing to model
- Files: `docs/cbd app/app.py` (lines 411-437: `update_model_predictions` callback)
- Impact: High - Invalid values (negative numbers, impossibly high values, non-numeric strings) could cause silent failures, crash model inference, or return nonsensical predictions
- Fix approach: Add input validation in callback. Check:
  - Age: 0-150 range
  - Lab values (AST, ALT, ALP): reasonable biological ranges (0-5000 for transaminases)
  - Bilirubin: 0-20 mg/dL
  - Charlson Index: 0-40
  Add error messages returned to UI when validation fails.

**Unsafe File Path Operations:**
- Issue: File paths constructed using relative paths (`'./Models'`, `'./assets/chosen_features_label.txt'`)
- Files: 
  - `docs/cbd app/app.py` (lines 16-23)
  - `docs/Batch_pred/batch.ipynb` (file paths)
- Impact: Medium - App will fail if not run from correct directory. Potential directory traversal if user input is incorporated into file paths (though not currently).
- Fix approach: Use absolute paths computed relative to script location using `os.path.dirname(__file__)` or `pathlib.Path(__file__).parent`.

## Tech Debt

**Large Monolithic Main File:**
- Issue: `docs/cbd app/app.py` contains 584 lines with all layout definition, callbacks, data loading, and business logic mixed together
- Files: `docs/cbd app/app.py`
- Impact: Medium - Difficult to maintain, test, and modify. Callback functions are tightly coupled to UI definition.
- Fix approach: Separate concerns:
  - `callbacks.py`: All Dash callbacks
  - `layout.py`: Dashboard layout and component structure
  - `models.py`: Model loading and prediction logic
  - `validators.py`: Input validation functions

**Commented-Out Code Blocks:**
- Issue: Multiple large blocks of commented-out code left in production
- Files: `docs/cbd app/app.py` (lines 448-463: commented initial_style; lines 469-485: large commented-out loop for secondary predictions)
- Impact: Low - Creates confusion about intent, clutters codebase, suggests incomplete refactoring
- Fix approach: Remove all commented-out code. If functionality was intentionally disabled, either:
  1. Remove it entirely, or
  2. Create a feature flag (environment variable) to toggle it on/demand
  3. Document in README or git commit why it was disabled

**Model Files Not Version Controlled:**
- Issue: Large pickle files (`.pkl`) stored in directories that may not be consistently deployed
- Files: `docs/cbd app/Models/` and `docs/Batch_pred/` (6 model files totaling ~400KB)
- Impact: Medium - Model versions can become out of sync, no audit trail of model changes, difficult to reproduce results
- Fix approach: 
  - Store models in a dedicated model registry/repository (MLflow, DVC, S3)
  - Document model versions and training dates
  - Implement model versioning strategy
  - Create `.gitignore` to prevent accidental model commits

## Input Validation and Error Handling Gaps

**No Try-Except Blocks:**
- Issue: Zero exception handling in main app.py. Any error in callbacks will crash the application silently on the backend.
- Files: `docs/cbd app/app.py` (entire `update_model_predictions` callback, lines 386-581)
- Impact: High - Users get hung UI with no error message. Difficult to debug production issues.
- Fix approach: Wrap callback logic in try-except blocks:
  ```python
  def update_model_predictions(...):
      try:
          # existing logic
      except ValueError as e:
          return html.Div(f"Invalid input: {str(e)}", style={'color': 'red'})
      except Exception as e:
          logging.error(f"Prediction error: {e}")
          return html.Div("An unexpected error occurred. Please contact support.")
  ```

**Missing Required Field Validation:**
- Issue: Callback checks only if `sex and age` are truthy (line 413), but doesn't validate format or range
- Files: `docs/cbd app/app.py` (line 413)
- Impact: Medium - Form can be submitted with incomplete/invalid data
- Fix approach: Validate all required fields explicitly with clear error messages for missing fields

**No Logging:**
- Issue: No logging framework. Uses only `print()` statement (commented out on line 422)
- Files: `docs/cbd app/app.py` (line 422: `# print('cholangitis:', cholangitis)`)
- Impact: Medium - No audit trail, difficult to debug production issues, can't trace patient predictions for validation
- Fix approach: Implement logging with `logging` module:
  ```python
  import logging
  logging.basicConfig(level=logging.INFO)
  logger = logging.getLogger(__name__)
  logger.info(f"Prediction generated for patient: {patient_data}")
  ```

## Data Flow and State Management Issues

**Unnamed CSV Output:**
- Issue: Batch prediction script writes results to `predictions.csv` without timestamp or metadata
- Files: `docs/Batch_pred/batch.ipynb` (line outputs to `./predictions.csv`)
- Impact: Medium - Multiple batch runs overwrite previous results. No audit trail of when predictions were made.
- Fix approach: Include timestamp in output filename: `predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv`

**Hardcoded Cost Values:**
- Issue: Medical cost values hardcoded in app source code (line 8-13)
- Files: `docs/cbd app/app.py` (lines 8-13)
- Impact: Medium - Cost data cannot be updated without code changes. No version history of cost updates.
- Fix approach: Move to configuration file (`costs.json`) loaded at startup. Include data source and effective date.

**No Data Persistence for Predictions:**
- Issue: Web app predictions are stored only in browser session memory (`dcc.Store`), not persisted
- Files: `docs/cbd app/app.py` (line 34: `dcc.Store(id='prediction-store', data={'initial_prediction': 0})`)
- Impact: Medium - No record of patient predictions for audit/validation. Cannot retrieve past predictions.
- Fix approach: Add database backing (SQLite, PostgreSQL) to store predictions with patient identifier, timestamp, and model version.

## Performance Issues

**Inefficient Model Loading:**
- Issue: All models are loaded at startup (line 17), even if not all are used. Each load causes full deserialization.
- Files: `docs/cbd app/app.py` (lines 15-17)
- Impact: Low-Medium - Slow startup time, high memory footprint. Only `initial.pkl` is actively used; secondary models are commented out.
- Fix approach: Lazy-load models on first use. Or if only using `initial.pkl` and `iterative_imputer.pkl`, explicitly load only those:
  ```python
  models = {
      'initial.pkl': joblib.load('./Models/initial.pkl'),
      'iterative_imputer.pkl': joblib.load('./Models/iterative_imputer.pkl')
  }
  ```

**Redundant Imputer Transform:**
- Issue: Imputer is loaded and transformed for every prediction. Could be cached.
- Files: `docs/cbd app/app.py` (line 440: done every callback)
- Impact: Low - Minimal performance impact but wasteful when same patient input patterns appear
- Fix approach: Cache imputation results by input hash for 1-hour TTL

## Accessibility Concerns

**No ARIA Labels:**
- Issue: Toggle buttons, inputs, and complex UI components lack accessibility labels
- Files: 
  - `docs/cbd app/assets/patient_form.py` (toggle buttons, checkboxes without ARIA labels)
  - `docs/cbd app/app.py` (complex layout divs with `aria-label` missing)
- Impact: Medium - Screen reader users cannot understand form purpose or navigate effectively
- Fix approach: Add ARIA attributes:
  ```python
  dcc.Checklist(
      id='abd-us-check',
      aria-label="Abdominal ultrasound performed",
      # ...
  )
  ```

**Color-Only Indicators:**
- Issue: Prediction output uses only color to indicate risk level (green/yellow/red regions in bar chart). Not accessible to colorblind users.
- Files: `docs/cbd app/assets/utils.py` (lines 168-173: color regions for CCY/MRCP/EUS/ERCP)
- Impact: Medium - Colorblind users cannot distinguish clinical recommendations
- Fix approach: Add text labels AND icons in addition to colors

**Missing Alternative Text:**
- Issue: Static image `/assets/pic1.png` has no alt text (line 217)
- Files: `docs/cbd app/app.py` (line 217)
- Impact: Low-Medium - Screen reader users cannot access image content
- Fix approach: Add descriptive alt text: `alt="Clinical pathology diagram showing cholangitis evaluation"`

**Non-Responsive Layout:**
- Issue: Fixed-width form and output panels (e.g., `minWidth: '350px'`, `width: '400px'`) break on small screens
- Files: 
  - `docs/cbd app/app.py` (line 98: `minWidth: '350px'`)
  - `docs/cbd app/assets/patient_form.py` (line 193: `width: '400px'`)
- Impact: Medium - Mobile users see horizontal scrolling, unusable on phones
- Fix approach: Replace fixed widths with `max-width` and use CSS flexbox/grid breakpoints for mobile

## Known Bugs

**UI State Inconsistency - Toggle Buttons:**
- Issue: Toggle buttons can get out of sync between visual state (CSS class) and underlying data (n_clicks)
- Files: `docs/cbd app/app.py` (toggle callbacks lines 247-342)
- Symptoms: UI shows "NO" but backend thinks it's "YES", or vice versa. Happens if user rapidly clicks.
- Trigger: Click toggle button rapidly multiple times, then submit form
- Workaround: Refresh browser page to reset state

**Phantom Form Values After Clear:**
- Issue: Calling `clear_inputs` sets `value=None` but some dropdown values may persist due to Dash callback ordering
- Files: `docs/cbd app/app.py` (lines 359-377: clear_inputs callback)
- Symptoms: After clicking "Clear", some fields still contain old values
- Trigger: 1) Enter values, 2) Click "Clear", 3) Click "Calculate" - old values appear in some cases
- Workaround: Manually clear each field

**Missing Null Handling in Batch Processing:**
- Issue: Batch prediction doesn't handle missing values in all columns gracefully
- Files: `docs/Batch_pred/batch.ipynb` (cell 8e69fbac: converts NaN to various values inconsistently)
- Symptoms: Some batch predictions fail silently; NaN values imputed as 0 instead of using imputer
- Trigger: Run batch with missing Cholangitis or Pancreatitis values
- Current handling: Imputer transforms data but upstream NaN handling is fragile

**Static Image Path Dependency:**
- Issue: Dashboard hardcodes path to `/assets/pic1.png` which may not exist or load
- Files: `docs/cbd app/app.py` (line 217)
- Symptoms: Missing image with broken image icon
- Trigger: Image file moved or deleted; app run from different directory
- Current state: File path is relative, will break if app.py moved to different directory

## Fragile Areas

**Patient Form UI - Tight Coupling:**
- Files: `docs/cbd app/assets/patient_form.py` (lines 9-181)
- Why fragile: Layout and state management are tightly coupled. Form fields are defined with hardcoded IDs that are referenced in 10+ callbacks in app.py. Adding/removing form field requires updating multiple files.
- Safe modification: When adding new form fields:
  1. Add input element to `patient_form.py`
  2. Add corresponding Clear callback output to `app.py` line 344-357
  3. Add State to `update_model_predictions` line 395-409
  4. Add to patient_data dict line 423-437
  5. Document in requirements. One missed step breaks the form.
- Test coverage: No automated tests for form state - must manually verify all fields clear/calculate correctly

**Model Loading and Feature Ordering:**
- Files: `docs/cbd app/app.py` (lines 16-20), feature list in `assets/chosen_features_label.txt`
- Why fragile: Feature order must exactly match model training feature order. If features are reordered in feature list, all predictions become wrong silently (no error).
- Safe modification: Never reorder features in `chosen_features_label.txt` without:
  1. Verifying original model training feature order
  2. Updating all references in both app and batch notebook
  3. Retraining model if order changed
- Test coverage: No validation that feature order matches model expectations

**Visualization Functions - Magic Numbers:**
- Files: `docs/cbd app/assets/utils.py` (lines 168-173 in `plot_prob_bar_with_callout`)
- Why fragile: Clinical decision boundaries hardcoded:
  - (0.0, 0.10): "CCY ± IOC"
  - (0.10, 0.44): "MRCP"
  - (0.44, 0.90): "EUS"
  - (0.90, 1.00): "ERCP"
- If clinical guidelines update, these boundaries must change in TWO places:
  1. `utils.py` visualization
  2. `batch.ipynb` `next_step()` function (lines 120-125)
- Risk: Inconsistency between visualization and batch predictions
- Safe modification: Extract to shared config file `decision_thresholds.json` imported by both

## Missing Critical Features

**No Authentication:**
- Problem: Web app is publicly accessible (appears to run on `jupyter.dasl.jhsph.edu`). No user authentication or authorization.
- Blocks: Cannot implement audit logging, cannot restrict access, cannot track which clinician made which prediction
- Impact: Patient data potentially accessible to anyone with network access. Compliance issue for HIPAA-regulated environment.

**No Patient Identifiers:**
- Problem: Form takes no patient ID/medical record number. Predictions cannot be linked back to specific patients.
- Blocks: Cannot validate predictions against actual outcomes. Cannot create audit trail. Cannot support clinical research.

**No Model Versioning:**
- Problem: No way to know which model version generated a prediction. If model is updated, old predictions become non-reproducible.
- Blocks: Cannot validate model accuracy over time. Cannot debug production issues traced to specific model versions.

**No Confidence Intervals or Uncertainty Quantification:**
- Problem: Only point estimates returned. No indication of prediction confidence or model uncertainty.
- Blocks: Clinicians cannot assess reliability of predictions. High-uncertainty predictions get same weight as high-confidence ones.
- Current state: Code exists for confidence intervals (lines 471-485 commented out, `ci_if` variable line 6) but disabled

**No Batch Processing Queue:**
- Problem: Batch notebook is Jupyter notebook, not production-ready. No scheduling, monitoring, or error recovery.
- Blocks: Cannot reliably process large batches. No notification of completion or errors.

## Test Coverage Gaps

**No Automated Tests:**
- What's not tested: Everything. Zero test files for production code.
- Files: No test files found (only `test_load.py` which just loads a model file)
- Risk: Refactoring is dangerous. Regression bugs go undetected. Model changes break silently.
- Priority: High - Production medical prediction tool needs comprehensive testing

**Specific untested areas:**
- Input validation logic (none exists yet)
- Model inference pipeline (prediction_values calculation)
- Imputation correctness
- Toggle state management callbacks
- Cost calculation logic (line 551-552)
- CSV output format for batch

**No Integration Tests:**
- What's missing: End-to-end tests that simulate user input → model prediction → output
- Risk: UI and backend can diverge. Form changes can break callbacks without detection.
- Priority: High

**No Data Validation Tests:**
- What's missing: Tests that invalid/edge-case inputs are handled gracefully
- Risk: Garbage in → garbage out. Silent failures possible.
- Priority: High

---

*Concerns audit: 2026-04-05*
