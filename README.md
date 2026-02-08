# Metabolic BioTwin

**Personal Metabolic Decision Engine** — glucose & prediabetes focus

Transform your health data into actionable, personalized insights for metabolic and glucose decisions. This is **decision support only**, not medical diagnosis or treatment.

## 🎥 Demo Video
Watch the platform in action: [Metabolic BioTwin Demo](https://drive.google.com/file/d/1qbvrvOXfvnrXi7sJ7am_7vKdCSJ3toow/view?usp=sharing)

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/pkumar1025/Metabolic-BioTwin.git
   cd Metabolic-BioTwin
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

4. **Open your browser**
   Navigate to `http://localhost:8000`

### Optional: LLM-generated insight text (Gemini)
Insight cards can show personalized intervention and success text instead of fixed templates.

1. Get a free API key: [Google AI Studio](https://aistudio.google.com/app/apikey) → Create API key.
2. Set the environment variable before running the app:
   ```bash
   export GEMINI_API_KEY=your_key_here
   ```
   Or add it to a `.env` file if you use one.
3. Optional: override the model with `GEMINI_MODEL` (default: `gemini-2.5-flash`).

If `GEMINI_API_KEY` is not set, the app uses fallback text and works as before.

## How to Use

### Option 1: Demo Data (Recommended for first-time users)
1. Click "Get Started with Demo Data" on the homepage
2. Explore the 4 dashboard tabs with pre-loaded sample data
3. Navigate between Health Trends, Meals, AI Insights, and Predictions tabs

### Option 2: Upload Your Own Data
1. Prepare CSV files with your health data (see supported formats below)
2. Click "Upload Your Data" and select your CSV files
3. The system will automatically process and analyze your data
4. Access the same 4 dashboard tabs with your personal data

### Additional Features
- **Health Score API**: Available via `/api/health-score` endpoint
- **Correlations API**: Available via `/api/correlations` endpoint
- *Note: These features have complete backend implementations but are not yet integrated into the dashboard UI*

## Supported Data Formats

### Required CSV Files
Upload any combination of these data types:

**Meals Data** (`meals.csv`)
```csv
date,time,carbs_g,protein_g,fat_g,fiber_g,calories
2024-01-01,08:00,45,20,15,8,350
2024-01-01,13:00,60,25,20,12,450
```

**Sleep Data** (`sleep.csv`)
```csv
date,sleep_hours,hrv,rhr
2024-01-01,7.5,45,65
2024-01-02,8.0,50,60
```

**Activity Data** (`activity.csv`)
```csv
date,steps,workout_min,hydration_l
2024-01-01,8500,30,2.5
2024-01-02,9200,45,3.0
```

**Vitals Data** (`vitals.csv`)
```csv
date,fg_fast_mgdl,weight,bp_systolic,bp_diastolic
2024-01-01,95,70.5,120,80
2024-01-02,92,70.2,118,78
```

### Flexible Column Names
The system automatically recognizes various column naming conventions:
- `date`, `Date`, `DATE`, `meal_date`, `timestamp`
- `carbs_g`, `carbs`, `carbohydrates`, `carbs_grams`
- `sleep_hours`, `sleep_duration`, `total_sleep`, `hours_slept`
- And many more...

## Dashboard Features

### 1. Health Trends
- Interactive time-series visualizations
- Correlated view of sleep, activity, nutrition, and vitals over time
- Zoom/pan functionality for detailed analysis

### 2. Meals
- Detailed nutrition analysis with streamlined data table
- Meal-by-meal breakdown with glucose response predictions
- Color-coded status indicators and AI-driven insights
- Export functionality for meal data

### 3. AI Insights
- Data-driven actionable recommendations (decision support only, not diagnosis)
- Causal relationships and correlation discoveries
- Statistical analysis with confidence intervals
- Personalized insights for glucose and metabolic decisions

### 4. Predictions
- ML-powered forecasting for glucose response
- Scenario modeling for different health choices
- Risk assessment and recommendations
- Interactive prediction charts

## Additional API Features

*Note: The following features have backend APIs available but are not yet integrated into the dashboard UI:*

### Health Score API
- Multi-dimensional health assessment across glucose, sleep, recovery, nutrition, and activity
- Trend analysis and personalized recommendations
- Component breakdown and scoring

### Correlations API
- Hidden relationship discovery between health metrics
- Time-lagged correlation analysis
- Statistical significance testing

## Technical Details

### Architecture
- **Backend**: FastAPI with Python 3.8+
- **Frontend**: Plotly Dash for interactive visualizations
- **ML**: Scikit-learn for machine learning models
- **Data Processing**: Pandas for data manipulation

### AI/ML Implementation
- **Machine Learning**: Scikit-learn for predictive modeling (Random Forest, Linear Regression)
- **Statistical Analysis**: SciPy for correlation analysis and statistical significance testing
- **Data Processing**: Pandas and NumPy for data manipulation and feature engineering
- **Causal Inference**: Custom implementation of doubly robust estimation for treatment effects (runs locally)
- **Insight card text (optional)**: With `GEMINI_API_KEY` set, intervention and success copy for the four AI Insight cards is generated by Google’s Gemini API from your analysis results; otherwise fixed fallback text is used. All numbers and card logic are computed locally; only the short narrative text is optionally sent to Gemini.

### Key AI Features
- **Causal Inference**: Doubly robust estimation for treatment effects
- **Correlation Discovery**: Statistical analysis of health metric relationships
- **Predictive Modeling**: Random Forest for glucose response prediction
- **Anomaly Detection**: Rolling median + MAD for outlier identification
- **Health Scoring**: Multi-dimensional health assessment

## Troubleshooting

### Common Issues

**Port already in use**
```bash
# Use a different port
python -m uvicorn app.main:app --reload --port 8001
```

**Missing dependencies**
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

**Data not loading**
- Ensure CSV files have proper headers
- Check that date columns are in a recognized format
- Verify file size is under 10MB per file

### Getting Help
- Check the console output for error messages
- Ensure all required columns are present in your CSV files
- Try the demo data first to verify the system is working
