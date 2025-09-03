"""
Basic Security and Validation for Health Data
Production-ready security measures for hackathon context
"""

import re
import hashlib
import uuid
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd

class HealthDataSecurity:
    """Basic security measures for health data processing"""
    
    # File size limits (in bytes)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_FILES_PER_SESSION = 10
    
    # Data validation patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$')
    
    # Sensitive data patterns to detect and mask
    SENSITIVE_PATTERNS = {
        'ssn': re.compile(r'\b\d{3}-?\d{2}-?\d{4}\b'),
        'credit_card': re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
        'phone': PHONE_PATTERN,
        'email': EMAIL_PATTERN
    }
    
    def __init__(self):
        self.session_limits = {}
        self.rate_limits = {}
    
    def validate_file_upload(self, filename: str, content: bytes, session_id: str) -> Dict:
        """
        Validate file upload for security and size limits
        
        Returns:
            Dict with validation results
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check file size
        if len(content) > self.MAX_FILE_SIZE:
            validation_result['valid'] = False
            validation_result['errors'].append(f"File too large: {len(content)} bytes (max: {self.MAX_FILE_SIZE})")
        
        # Check file extension
        if not filename.lower().endswith('.csv'):
            validation_result['warnings'].append("File should be a CSV file")
        
        # Check session limits
        if session_id in self.session_limits:
            if self.session_limits[session_id] >= self.MAX_FILES_PER_SESSION:
                validation_result['valid'] = False
                validation_result['errors'].append("Too many files uploaded for this session")
        else:
            self.session_limits[session_id] = 0
        
        # Check for suspicious content
        content_str = content.decode('utf-8', errors='ignore')
        suspicious_patterns = self._detect_suspicious_content(content_str)
        if suspicious_patterns:
            validation_result['warnings'].extend(suspicious_patterns)
        
        if validation_result['valid']:
            self.session_limits[session_id] += 1
        
        return validation_result
    
    def sanitize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Sanitize DataFrame to remove or mask sensitive information
        """
        sanitized_df = df.copy()
        
        for column in sanitized_df.columns:
            if sanitized_df[column].dtype == 'object':  # String columns
                sanitized_df[column] = sanitized_df[column].astype(str).apply(
                    lambda x: self._mask_sensitive_data(x) if pd.notna(x) else x
                )
        
        return sanitized_df
    
    def _detect_suspicious_content(self, content: str) -> List[str]:
        """Detect potentially suspicious content in uploaded files"""
        warnings = []
        
        # Check for script tags or executable content
        if re.search(r'<script|javascript:|eval\(|exec\(', content, re.IGNORECASE):
            warnings.append("File contains potentially executable content")
        
        # Check for SQL injection patterns
        if re.search(r'(union|select|insert|delete|drop|update).*from', content, re.IGNORECASE):
            warnings.append("File contains SQL-like patterns")
        
        # Check for excessive special characters
        special_char_ratio = len(re.findall(r'[^\w\s]', content)) / len(content)
        if special_char_ratio > 0.3:
            warnings.append("File contains high ratio of special characters")
        
        return warnings
    
    def _mask_sensitive_data(self, text: str) -> str:
        """Mask sensitive data patterns in text"""
        masked_text = text
        
        for pattern_name, pattern in self.SENSITIVE_PATTERNS.items():
            if pattern.search(masked_text):
                masked_text = pattern.sub(f'[MASKED_{pattern_name.upper()}]', masked_text)
        
        return masked_text
    
    def generate_session_token(self) -> str:
        """Generate a secure session token"""
        return str(uuid.uuid4())
    
    def hash_sensitive_data(self, data: str) -> str:
        """Hash sensitive data for storage"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def validate_data_types(self, df: pd.DataFrame, expected_schema: Dict) -> Dict:
        """
        Validate DataFrame against expected schema
        
        Args:
            df: DataFrame to validate
            expected_schema: Expected column types and constraints
            
        Returns:
            Validation results
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        for column, expected_type in expected_schema.items():
            if column not in df.columns:
                validation_result['warnings'].append(f"Missing expected column: {column}")
                continue
            
            # Check data type
            actual_type = str(df[column].dtype)
            if expected_type not in actual_type:
                validation_result['warnings'].append(
                    f"Column {column}: expected {expected_type}, got {actual_type}"
                )
            
            # Check for null values in required columns
            if 'required' in expected_schema.get(column, {}) and df[column].isnull().any():
                validation_result['errors'].append(f"Required column {column} contains null values")
        
        validation_result['valid'] = len(validation_result['errors']) == 0
        
        return validation_result
    
    def create_audit_log(self, session_id: str, action: str, details: Dict) -> Dict:
        """Create audit log entry for security tracking"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'session_id': session_id,
            'action': action,
            'details': details,
            'ip_address': '127.0.0.1',  # Would be real IP in production
            'user_agent': 'Metabolic-BioTwin/1.0'
        }
    
    def check_rate_limit(self, session_id: str, action: str) -> bool:
        """Check if action is within rate limits"""
        now = datetime.utcnow()
        key = f"{session_id}:{action}"
        
        if key not in self.rate_limits:
            self.rate_limits[key] = []
        
        # Remove old entries (older than 1 hour)
        self.rate_limits[key] = [
            timestamp for timestamp in self.rate_limits[key]
            if now - timestamp < timedelta(hours=1)
        ]
        
        # Check limits based on action
        limits = {
            'upload': 10,  # 10 uploads per hour
            'process': 20,  # 20 processing requests per hour
            'insight': 50   # 50 insight requests per hour
        }
        
        limit = limits.get(action, 10)
        
        if len(self.rate_limits[key]) >= limit:
            return False
        
        self.rate_limits[key].append(now)
        return True
