# Technology Stack

**Analysis Date:** 2026-04-05

## Languages

**Primary:**
- Python 3.11.2 - All application code, machine learning, and web framework

## Runtime

**Environment:**
- Conda environment `cbd` configured in `docs/environment.yml`
- Development tested on Linux environment (jupyter.dasl.jhsph.edu)
- Deployment target: Johns Hopkins web server (jupyter.dasl.jhsph.edu:1035)

**Package Manager:**
- pip 25.0.1 (managed within Conda)
- Conda 3.11.2 environment specification
- Lockfile: `docs/environment.yml` provides reproducible dependency versions

## Frameworks

**Core Web Framework:**
- Dash 3.0.1 - Web application framework for interactive UI
  - Location: `docs/cbd app/app.py`
  - Components: dash_daq 0.6.0 for UI controls
  - Callbacks: Reactive UI component binding

**Visualization:**
- Plotly 6.0.1 - Interactive chart generation
  - Radar/spider charts via `plotly.graph_objects`
  - Sankey diagrams for decision flow
  - Bar charts with annotations
- Matplotlib 3.10.3 - Static figure generation
  - Matplotlib backend set to 'Agg' for server-side rendering
  - Used for probability bar chart with gradient
  - Conversion to base64 for embedding in HTML

**Machine Learning:**
- scikit-learn 1.5.2 - ML models and imputation
  - `KNNImputer` from `sklearn.impute` for handling missing values
  - Model loading via joblib
  - Classification via probability predictions

## Key Dependencies

**Critical:**
- joblib 1.4.2 - Serialization/deserialization of trained models
  - All 6 model files (.pkl) loaded at startup
  - Location: `docs/cbd app/Models/` contains initial.pkl and conditional models

**Data Processing:**
- pandas 2.2.3 - Data manipulation and DataFrame operations
  - Patient data assembly and transformation
  - Model input preparation
  - CSV output for batch predictions

- numpy 1.26.4 - Numerical computations
  - Probability calculations and rounding
  - Confidence interval calculations
  - Array indexing for predictions

**Infrastructure:**
- Flask 3.0.3 - WSGI application server (dependency of Dash)
- Werkzeug 3.0.6 - WSGI utilities
- Click 8.1.8 - CLI utilities
- Requests 2.32.3 - HTTP library (potentially for future API integrations)

**Visualization Support:**
- Plotly 6.0.1 - Chart rendering library
- Kiwisolver 1.4.8 - Constraint solving for matplotlib
- Contourpy 1.3.2 - Contour calculations
- Fonttools 4.59.0 - Font handling
- Pillow 11.3.0 - Image processing

**Data/Time Utilities:**
- python-dateutil 2.9.0.post0 - Date parsing
- pytz 2025.2 - Timezone handling
- tzdata 2025.2 - Timezone database

**Web Standards:**
- Jinja2 3.1.6 - HTML templating (Flask dependency)
- ItsDangerous 2.2.0 - Secure data signing (Flask dependency)
- MarkupSafe 3.0.2 - Safe string handling

**Library Utilities:**
- typing-extensions 4.13.0 - Type hint backports
- certifi 2025.1.31 - Root CA certificates
- charset-normalizer 3.4.1 - Character encoding detection
- idna 3.10 - Internationalized domain names
- urllib3 2.3.0 - HTTP library foundation
- six 1.17.0 - Python 2/3 compatibility
- retrying 1.3.4 - Retry logic
- scipy 1.15.2 - Scientific computing (scikit-learn dependency)
- threadpoolctl 3.6.0 - Thread pool control (scikit-learn dependency)

**Optional/Legacy:**
- narwhals 1.32.1 - Dataframe interchange library (likely unused)
- nest-asyncio 1.6.0 - Asyncio nesting (likely unused)
- blinker 1.9.0 - Signal library

## Configuration

**Environment:**
- Conda environment specified in `docs/environment.yml`
- Application initialized as Dash app: `app = dash.Dash(__name__)`
- Server configuration hard-coded in `docs/cbd app/app.py` line 585:
  - Host: `jupyter.dasl.jhsph.edu`
  - Port: `1035`

**Build:**
- No build step required
- Models precompiled and pickled in `docs/cbd app/Models/`
- Static assets served from `docs/cbd app/assets/` (JSON, images)

## Platform Requirements

**Development:**
- Python 3.11.2
- Conda environment manager
- Access to trained model files (.pkl files)
- Feature configuration files (chosen_features_label.txt)

**Production:**
- Johns Hopkins server infrastructure
- Linux environment (jupyter.dasl.jhsph.edu)
- Network port 1035 accessible
- Permission to read model files from disk
- Enough disk space for pickle files (~600KB total)

---

*Stack analysis: 2026-04-05*
