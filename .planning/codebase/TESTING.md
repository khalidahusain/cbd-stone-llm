# Testing Patterns

**Analysis Date:** 2026-04-05

## Test Framework

**Runner:**
- Not formally configured; testing is manual/exploratory
- `test_load.py` exists but contains only a simple load test

**Assertion Library:**
- No test framework detected (pytest, unittest, nose absent)
- Manual assertions via simple conditionals (e.g., `assert 0 <= prob <= 100` in utils)

**Run Commands:**
```bash
python test_load.py                    # Manual verification of model loading
jupyter notebook batch.ipynb           # Exploratory data analysis and batch prediction testing
```

## Test File Organization

**Location:**
- Primary test file: `docs/cbd app/test_load.py` (co-located with application code)
- Exploratory tests: `docs/Batch_pred/batch.ipynb` (notebook-based testing)

**Naming:**
- Test file: `test_load.py` (uses `test_` prefix convention)
- Notebooks: `batch.ipynb` (exploratory analysis rather than formal tests)

**Structure:**
```
docs/cbd app/
├── app.py                           # Main application
├── test_load.py                     # Model loading verification
└── assets/
    ├── utils.py                     # Utility functions
    ├── patient_form.py              # Form components
    └── imports.py                   # Centralized imports
```

## Test Structure

**Current Test Content (`test_load.py`):**
```python
import cloudpickle

with open('initial.pkl', 'rb') as f:
    model_initial = cloudpickle.load(f)
print("Loaded successfully!")
```

**Purpose:** Simple sanity check to verify pickled model can be deserialized without errors.

**Pattern Observations:**
- No test class/suite structure
- Single assertion via print output (informal)
- Direct file I/O without fixtures or setup/teardown
- No test discovery mechanism

## Testing Approach (Observed)

**Manual Testing via Notebooks:**
The codebase uses Jupyter notebooks (`batch.ipynb`) for exploratory testing of the prediction pipeline:

```python
# Load data
df0 = pd.read_excel(bath_path, engine='openpyxl')
df0.rename(columns={...}, inplace=True)

# Data cleaning
valid_gender = df['Sex'].isin(['Male', 'Female'])
invalid_indices = df.index[~valid_gender]
print("Subjects with no gender values specified:", invalid_indices.tolist())

# Model inference
model = joblib.load(os.path.join(model_folder, 'initial.pkl'))
imputer = joblib.load(os.path.join(model_folder, 'iterative_imputer.pkl'))
X_imputed = imputer.transform(X)
pred_probs = model.predict_proba(X_imputed) * 100
```

**Validation Pattern:**
- Data shape verification: Print row/column counts
- Missing value handling: `KNNImputer` applied to handle NaNs
- Output verification: Export to CSV and inspect (`df.to_csv('./predictions.csv', index=False)`)

## Testing Data

**Test Fixtures:**
- Excel file: `check.xlsx` (batch input data)
- Feature list: `chosen_features_label.txt` (column mapping)
- Model files: `initial.pkl`, `iterative_imputer.pkl` (pre-trained models in `./Models/`)

**Batch Testing Pattern (`batch.ipynb`):**
```python
# Load and prepare data
bath_path = './check.xlsx'
feature_path = './chosen_features_label.txt'
model_folder = './'

df0 = pd.read_excel(bath_path, engine='openpyxl')

# Transform categorical variables
df['Sex'] = df['Sex'].replace({'Female': 0, 'Male': 1}).astype('int8')
df.replace({'Yes': 1, 'No': 0}, inplace=True)

# Impute missing values
X_imputed = imputer.transform(X)
X_imputed = pd.DataFrame(X_imputed, columns=X.columns)

# Generate predictions
pred_probs = model.predict_proba(X_imputed) * 100
prob_values = pred_probs[:, 1]
```

## Mocking

**Framework:** Not used

**Data Mocking:**
- Hardcoded test dictionaries for model metadata:
  ```python
  number_samples_if_models = {'MRCP': 2342, 'EUS': 2342, 'ERCP': 2342, 'IOC': 2342}
  ci_if = {'MRCP': [0,0], 'EUS': [0,0], 'ERCP': [0,0], 'IOC': [0,0]}
  cost_values = {
      'MRCP': [1215.08, 3620.92],
      'EUS': [2986.58, 3566.92],
      'ERCP': [4451, 0],
      'IOC': [600, 4451]
  }
  ```

**No Mock Framework:** Tests interact with real file system and actual model files

## Validation Testing

**Data Validation Observed:**
1. **Gender validation** (`batch.ipynb`):
   ```python
   valid_gender = df['Sex'].isin(['Male', 'Female'])
   invalid_indices = df.index[~valid_gender]
   print("Subjects with no gender values specified:", invalid_indices.tolist())
   df = df.loc[valid_gender].copy()
   ```

2. **Probability bounds assertion** (`utils.py`):
   ```python
   def plot_prob_bar_with_callout(prob, figsize=(10, 2)):
       assert 0 <= prob <= 100
   ```

3. **Form input validation** (`app.py` callback):
   ```python
   if n_clicks > 0 and sex and age:
       # Only process if sex and age are provided
   ```

4. **Conditional rendering** in callbacks:
   ```python
   if value and 'done' in value:
       return enabled_style
   return disabled_style
   ```

## Batch Prediction Testing

**Test Pattern in `batch.ipynb`:**
- Load batch Excel file with multiple patient records
- Apply data cleaning and imputation
- Generate predictions for entire cohort
- Compute next-step recommendations via decision logic:
  ```python
  def next_step(prob, cholangitis_flag):
      if cholangitis_flag == 1:
          return 'ERCP'
      if prob < 10:
          return 'CCY ± IOC'
      elif prob < 44:
          return 'MRCP'
      elif prob < 90:
          return 'EUS'
      else:
          return 'ERCP'
  ```
- Output results to CSV:
  ```python
  df['Predicted Probability of CBD (%)'] = prob_values
  df['Next Step Recommendation'] = [next_step(p, c) for p, c in zip(prob_values, X_imputed['Cholangitis'])]
  df.to_csv('./predictions.csv', index=False)
  ```

## Coverage

**Requirements:** No coverage targets enforced

**Current State:**
- Core model loading: `test_load.py` (trivial coverage)
- Batch pipeline: `batch.ipynb` (manual exploratory testing)
- Interactive prediction: Manual via Dash web UI
- Visualization functions: Tested implicitly via UI callbacks

**Gaps:**
- No unit tests for utility functions (`spider_chart`, `sankey_chart`, `plot_prob_bar_with_callout`)
- No integration tests for Dash callbacks
- No error handling tests (file not found, corrupt model, invalid inputs)
- No tests for edge cases (extreme probability values, missing required fields)

## Test Types

**Unit Tests:**
- Not formally structured
- `test_load.py` serves as single unit test (verifies model deserialization)

**Integration Tests:**
- `batch.ipynb` functions as integration test for full prediction pipeline:
  - Data loading → cleaning → imputation → prediction → output
  - Tests end-to-end flow without UI interaction

**Interactive Testing:**
- Manual web UI testing via Dash application (`app.py`)
- Form submission triggers callback chain:
  1. Input validation (`sex and age` check)
  2. Data transformation (toggle states to YES/NO)
  3. Model inference
  4. Output generation (visualization + cost table)

**Exploratory Testing:**
- Jupyter notebooks used for ad-hoc testing and development
- Data exploration before model integration

## Common Testing Scenarios

**Model Loading:**
```python
# test_load.py pattern
import cloudpickle
with open('initial.pkl', 'rb') as f:
    model_initial = cloudpickle.load(f)
print("Loaded successfully!")
```

**Data Imputation:**
```python
from sklearn.impute import KNNImputer
imputer = joblib.load('iterative_imputer.pkl')
X_imputed = imputer.transform(X)
X_imputed = pd.DataFrame(X_imputed, columns=X.columns)
```

**Probability Conversion:**
```python
# String/binary → numeric conversion
patient_df = patient_df.replace({"YES": 1, "NO": 0, "Male": 1, "Female": 0}).infer_objects(copy=False)

# Modulo arithmetic for toggle states
cholangitis = "YES" if cholangitis % 2 == 1 else "NO"
```

**Output Generation:**
```python
# Expected output structure
return [
    initial_prediction_div,
    {'initial_prediction': initial_pred},
    plot_image,
    table_rows,
    table_style
]
```

---

*Testing analysis: 2026-04-05*
