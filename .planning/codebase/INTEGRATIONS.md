# External Integrations

**Analysis Date:** 2026-04-05

## APIs & External Services

**No External APIs Currently Integrated**

The application is self-contained and does not make outbound API calls. All medical reference links are static hyperlinks in the UI.

**Reference Documentation Links:**
- Tokyo Guidelines for Acute Cholecystitis - https://www.mdcalc.com/calc/10130/tokyo-guidelines-acute-cholecystitis-2018
- Tokyo Guidelines for Acute Cholangitis - https://www.mdcalc.com/calc/10142/tokyo-guidelines-acute-cholangitis-2018
- Charlson Comorbidity Index (CCI) - https://www.mdcalc.com/calc/3917/charlson-comorbidity-index-cci
  - Location: `docs/cbd app/app.py` lines 82-93
  - Context: Helpful links section (no functional integration)

## Data Storage

**Databases:**
- None currently integrated
- No persistent data storage beyond current session
- No database client configured

**File Storage:**
- Local filesystem only
- Model files: `docs/cbd app/Models/`
  - initial.pkl - Primary prediction model
  - iterative_imputer.pkl - Missing value imputation
  - model_predict_if_ercp.pkl - Conditional prediction (currently commented out)
  - model_predict_if_eus.pkl - Conditional prediction (currently commented out)
  - model_predict_if_mrcp.pkl - Conditional prediction (currently commented out)
  - model_predict_if_ioc.pkl - Conditional prediction (currently commented out)
- Configuration files: `docs/cbd app/assets/`
  - chosen_features_label.txt - Model input features
  - abbreviation.json - Column name mapping
  - pic1.png - Anatomical reference image
- Batch prediction output: CSV file written to same directory as notebook

**Caching:**
- None - In-memory only
- Models loaded at application startup via joblib
- Client-side state stored in Dash `dcc.Store` component (prediction-store) with schema `{'initial_prediction': float}`

## Authentication & Identity

**Auth Provider:**
- None
- Application runs on Hopkins internal network (jupyter.dasl.jhsph.edu)
- No user authentication mechanism implemented
- No login system required

**Note:** Access control at Hopkins infrastructure level only

## Monitoring & Observability

**Error Tracking:**
- None configured
- No error reporting service integration

**Logs:**
- Standard output to server console
- Warnings filtered in batch notebook: `warnings.filterwarnings("ignore", category=UserWarning)`
  - Location: `docs/Batch_pred/batch.ipynb`
- No persistent log files configured

## CI/CD & Deployment

**Hosting:**
- Johns Hopkins internal server
- Host: jupyter.dasl.jhsph.edu
- Port: 1035
- Running via Conda environment

**CI Pipeline:**
- None - Manual deployment
- Code version control only (git repo present but no CI configuration)

**Deployment Notes:**
- Direct Python execution: `python docs/cbd app/app.py`
- Conda environment must be activated first
- Models must be in `docs/cbd app/Models/` directory at runtime

## Environment Configuration

**Required env vars:**
- None explicitly required
- Application uses hard-coded server configuration:
  - Host: jupyter.dasl.jhsph.edu
  - Port: 1035

**Secrets location:**
- No secrets management implemented
- No .env file pattern used
- All configuration embedded in Python code

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Data Flow & Integration Points

**User Input Path:**
```
Patient Form (HTML form)
  ↓
Dash Callbacks (app.py lines 246-581)
  ↓
Patient Data Assembly (dict to DataFrame)
  ↓
Missing Value Imputation (iterative_imputer.pkl)
  ↓
Model Prediction (initial.pkl)
  ↓
Visualization (utils.py plotting functions)
  ↓
Base64 Encoding (fig_to_base64_img)
  ↓
HTML/CSS Rendering (patient_form.py, app.py styling)
```

**Batch Prediction Path:**
```
Excel File (check.xlsx)
  ↓
Feature Mapping (abbreviation.json, chosen_features_label.txt)
  ↓
Data Preprocessing (batch.ipynb)
  ↓
Model Prediction (initial.pkl)
  ↓
CSV Export (predictions.csv)
```

## Integration Gaps

**Potential Future Integrations:**
1. **EHR/PACS Integration** - Currently manual data entry
2. **Database Persistence** - No multi-session patient tracking
3. **API Exposure** - Could expose prediction endpoint for other systems
4. **Logging Service** - No audit trail or performance monitoring
5. **Authentication** - No user-level access control
6. **Notification System** - No alert or reporting capabilities

## Data Validation & Security Notes

**Input Validation:**
- Basic type checking on form inputs (number fields for labs)
- Toggle/dropdown selections constrained to predefined options
- Missing values handled via KNN imputation
- No SQL injection risk (no database)
- No file upload functionality

**Model Security:**
- All models are pre-trained and serialized (.pkl files)
- No model re-training from user data
- Read-only access to model files

---

*Integration audit: 2026-04-05*
