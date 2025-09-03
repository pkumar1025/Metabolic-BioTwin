"""
Flexible Data Processing for Health Data Ingestion
Handles various CSV formats and column naming conventions
"""

import pandas as pd
import numpy as np
import io
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class HealthDataProcessor:
    """Processes and normalizes health data from various sources"""
    
    # Flexible column mapping for different naming conventions
    COLUMN_MAPPINGS = {
        'meals': {
            'date': ['date', 'Date', 'DATE', 'meal_date', 'timestamp'],
            'time': ['time', 'Time', 'TIME', 'meal_time', 'timestamp'],
            'carbs_g': ['carbs_g', 'carbs', 'carbohydrates', 'carbs_grams', 'carb_grams'],
            'protein_g': ['protein_g', 'protein', 'protein_grams', 'prot'],
            'fat_g': ['fat_g', 'fat', 'fat_grams', 'lipids'],
            'fiber_g': ['fiber_g', 'fiber', 'fiber_grams', 'dietary_fiber'],
            'calories': ['calories', 'cal', 'kcal', 'energy', 'energy_kcal']
        },
        'sleep': {
            'date': ['date', 'Date', 'DATE', 'sleep_date', 'night_of'],
            'sleep_hours': ['sleep_hours', 'sleep_duration', 'total_sleep', 'hours_slept', 'duration'],
            'bedtime': ['bedtime', 'sleep_start', 'bed_time', 'sleep_onset'],
            'wake_time': ['wake_time', 'sleep_end', 'wake_up', 'sleep_offset'],
            'sleep_quality': ['sleep_quality', 'quality', 'sleep_score', 'efficiency', 'restfulness']
        },
        'activity': {
            'date': ['date', 'Date', 'DATE', 'activity_date', 'day'],
            'steps': ['steps', 'step_count', 'total_steps', 'daily_steps'],
            'workout_min': ['workout_min', 'exercise_minutes', 'active_minutes', 'workout_duration'],
            'hydration_l': ['hydration_l', 'water_intake', 'fluid_intake', 'water_consumed']
        },
        'vitals': {
            'date': ['date', 'Date', 'DATE', 'measurement_date', 'reading_date'],
            'fg_fast_mgdl': ['fg_fast_mgdl', 'fasting_glucose', 'glucose', 'blood_sugar', 'bg_fasting'],
            'weight': ['weight', 'body_weight', 'mass', 'weight_kg'],
            'bp_systolic': ['bp_systolic', 'systolic', 'systolic_bp', 'blood_pressure_sys'],
            'bp_diastolic': ['bp_diastolic', 'diastolic', 'diastolic_bp', 'blood_pressure_dia']
        }
    }
    
    # Date format patterns to try
    DATE_FORMATS = [
        '%Y-%m-%d',      # 2024-01-15
        '%m/%d/%Y',      # 01/15/2024
        '%d/%m/%Y',      # 15/01/2024
        '%Y-%m-%d %H:%M:%S',  # 2024-01-15 08:30:00
        '%m/%d/%Y %H:%M',     # 01/15/2024 08:30
    ]
    
    # Time format patterns
    TIME_FORMATS = [
        '%H:%M',         # 08:30
        '%I:%M %p',      # 8:30 AM
        '%H:%M:%S',      # 08:30:00
        '%I:%M:%S %p',   # 8:30:00 AM
    ]
    
    def __init__(self):
        self.processed_data = {}
        self.validation_errors = []
        self.data_quality_report = {}
    
    def process_uploaded_files(self, files_data: List[Dict]) -> Tuple[Dict, Dict]:
        """
        Process multiple uploaded files and return normalized data
        
        Args:
            files_data: List of file data with 'content' and 'filename'
            
        Returns:
            Tuple of (processed_data, quality_report)
        """
        self.processed_data = {}
        self.validation_errors = []
        self.data_quality_report = {}
        
        for file_data in files_data:
            try:
                self._process_single_file(file_data)
            except Exception as e:
                logger.error(f"Error processing file {file_data.get('filename', 'unknown')}: {str(e)}")
                self.validation_errors.append({
                    'file': file_data.get('filename', 'unknown'),
                    'error': str(e)
                })
        
        return self.processed_data, self.data_quality_report
    
    def _process_single_file(self, file_data: Dict):
        """Process a single uploaded file"""
        filename = file_data.get('filename', 'unknown')
        content = file_data.get('content')
        
        if not content:
            raise ValueError("No content provided")
        
        # Read CSV
        df = pd.read_csv(io.StringIO(content))
        
        # Detect data type based on columns
        data_type = self._detect_data_type(df.columns)
        
        # Normalize columns
        normalized_df = self._normalize_columns(df, data_type)
        
        # Validate required columns
        self._validate_required_columns(normalized_df, data_type)
        
        # Clean and process data
        cleaned_df = self._clean_data(normalized_df, data_type)
        
        # Store processed data
        self.processed_data[data_type] = cleaned_df
        
        # Generate quality report
        self.data_quality_report[data_type] = self._generate_quality_report(cleaned_df, data_type)
    
    def _detect_data_type(self, columns: List[str]) -> str:
        """Detect the type of health data based on column names"""
        columns_lower = [col.lower() for col in columns]
        
        # Check for meals data
        if any(keyword in ' '.join(columns_lower) for keyword in ['carbs', 'protein', 'fat', 'meal', 'food']):
            return 'meals'
        
        # Check for sleep data
        if any(keyword in ' '.join(columns_lower) for keyword in ['sleep', 'bedtime', 'wake', 'duration']):
            return 'sleep'
        
        # Check for activity data
        if any(keyword in ' '.join(columns_lower) for keyword in ['steps', 'workout', 'exercise', 'activity']):
            return 'activity'
        
        # Check for vitals data
        if any(keyword in ' '.join(columns_lower) for keyword in ['glucose', 'blood', 'pressure', 'weight', 'vital']):
            return 'vitals'
        
        # Default to meals if uncertain
        return 'meals'
    
    def _normalize_columns(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """Normalize column names to standard format"""
        normalized_df = df.copy()
        mappings = self.COLUMN_MAPPINGS.get(data_type, {})
        
        for standard_name, possible_names in mappings.items():
            for col in df.columns:
                if col in possible_names:
                    normalized_df = normalized_df.rename(columns={col: standard_name})
                    break
        
        return normalized_df
    
    def _validate_required_columns(self, df: pd.DataFrame, data_type: str):
        """Validate that required columns are present"""
        required_columns = {
            'meals': ['date', 'time'],
            'sleep': ['date'],
            'activity': ['date'],
            'vitals': ['date']
        }
        
        missing_columns = []
        for required_col in required_columns.get(data_type, []):
            if required_col not in df.columns:
                missing_columns.append(required_col)
        
        if missing_columns:
            raise ValueError(f"Missing required columns for {data_type}: {missing_columns}")
    
    def _clean_data(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """Clean and process the data"""
        cleaned_df = df.copy()
        
        # Standardize date columns
        if 'date' in cleaned_df.columns:
            cleaned_df['date'] = self._parse_dates(cleaned_df['date'])
        
        # Standardize time columns
        if 'time' in cleaned_df.columns:
            cleaned_df['time'] = self._parse_times(cleaned_df['time'])
        
        # Handle numeric columns
        numeric_columns = ['carbs_g', 'protein_g', 'fat_g', 'fiber_g', 'calories', 
                          'sleep_hours', 'steps', 'workout_min', 'hydration_l', 
                          'fg_fast_mgdl', 'weight', 'bp_systolic', 'bp_diastolic']
        
        for col in numeric_columns:
            if col in cleaned_df.columns:
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
        
        # Remove rows with all NaN values
        cleaned_df = cleaned_df.dropna(how='all')
        
        return cleaned_df
    
    def _parse_dates(self, date_series: pd.Series) -> pd.Series:
        """Parse dates with multiple format attempts"""
        for date_format in self.DATE_FORMATS:
            try:
                parsed_dates = pd.to_datetime(date_series, format=date_format, errors='coerce')
                if not parsed_dates.isna().all():
                    return parsed_dates.dt.date
            except:
                continue
        
        # Fallback to pandas auto-parsing
        return pd.to_datetime(date_series, errors='coerce').dt.date
    
    def _parse_times(self, time_series: pd.Series) -> pd.Series:
        """Parse times with multiple format attempts"""
        for time_format in self.TIME_FORMATS:
            try:
                parsed_times = pd.to_datetime(time_series, format=time_format, errors='coerce')
                if not parsed_times.isna().all():
                    return parsed_times.dt.time
            except:
                continue
        
        # Fallback to pandas auto-parsing
        return pd.to_datetime(time_series, errors='coerce').dt.time
    
    def _generate_quality_report(self, df: pd.DataFrame, data_type: str) -> Dict:
        """Generate data quality report"""
        report = {
            'total_rows': len(df),
            'missing_values': df.isnull().sum().to_dict(),
            'data_types': df.dtypes.astype(str).to_dict(),
            'date_range': None,
            'quality_score': 0
        }
        
        # Calculate date range if date column exists
        if 'date' in df.columns and not df['date'].isna().all():
            report['date_range'] = {
                'start': str(df['date'].min()),
                'end': str(df['date'].max())
            }
        
        # Calculate quality score (0-100)
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        report['quality_score'] = max(0, 100 - (missing_cells / total_cells * 100))
        
        return report
    
    def create_daily_summary(self) -> pd.DataFrame:
        """Create daily summary by joining all data types"""
        if not self.processed_data:
            return pd.DataFrame()
        
        # Start with sleep data as base (most consistent)
        daily_df = self.processed_data.get('sleep', pd.DataFrame())
        
        # Merge other data types
        for data_type, df in self.processed_data.items():
            if data_type != 'sleep' and 'date' in df.columns:
                if daily_df.empty:
                    daily_df = df
                else:
                    daily_df = daily_df.merge(df, on='date', how='outer')
        
        # Sort by date
        if 'date' in daily_df.columns:
            daily_df = daily_df.sort_values('date')
            
            # Interpolate numeric columns
            numeric_cols = daily_df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                daily_df[numeric_cols] = daily_df[numeric_cols].interpolate(limit_direction='both')
        
        return daily_df
