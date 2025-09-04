# Metabolic BioTwin

AI-Powered Personal Health Intelligence Platform

Transform fragmented health data into actionable, personalized insights through advanced machine learning and causal inference.

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

## How to Use

### Option 1: Demo Data (Recommended for first-time users)
1. Click "Get Started with Demo Data" on the homepage
2. Explore the 6 dashboard tabs with pre-loaded sample data

### Option 2: Upload Your Own Data
1. Prepare CSV files with your health data (see supported formats below)
2. Click "Upload Your Data" and select your CSV files
3. The system will automatically process and analyze your data

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

### 1. Timeline
- Health trends over time
- Correlated visualizations of sleep, activity, nutrition, and vitals

### 2. Meals
- Detailed nutrition analysis
- Meal-by-meal breakdown with glucose response predictions

### 3. Insights
- AI-generated actionable insights
- Causal relationships and correlation discoveries

### 4. Health Score
- Personalized scoring across multiple health dimensions
- Trend analysis and recommendations

### 5. Predictions
- ML-powered forecasting
- Scenario modeling for different health choices

### 6. Correlations
- Hidden relationship discovery
- Statistical analysis with confidence intervals

## Technical Details

### Architecture
- **Backend**: FastAPI with Python 3.8+
- **Frontend**: Plotly Dash for interactive visualizations
- **ML**: Scikit-learn for machine learning models
- **Data Processing**: Pandas for data manipulation

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

## License

MIT License - see LICENSE file for details.