#!/usr/bin/env python3
"""
FastAPI Backend for Air Quality Monitoring Dashboard
Provides REST API endpoints for real-time monitoring, predictions, and DDS
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

app = FastAPI(title="Air Quality Monitoring API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data and models
print("Loading data and models...")
try:
    sensor_df = pd.read_csv('../data/sensor_data.csv')
    sensor_df['timestamp'] = pd.to_datetime(sensor_df['timestamp'])
    
    with open('../data/ward_info.json', 'r') as f:
        ward_info = json.load(f)
    
    # Load ML models
    from models.train_models import AQIPredictionModel, PollutionSourceClassifier
    aqi_predictor = AQIPredictionModel.load('../models/aqi_predictor.pkl')
    source_classifier = PollutionSourceClassifier.load('../models/source_classifier.pkl')
    
    print("✓ Data and models loaded successfully")
except Exception as e:
    print(f"⚠ Warning: Could not load models - {e}")
    aqi_predictor = None
    source_classifier = None

# Pydantic models
class WardData(BaseModel):
    ward_id: int
    ward_name: str
    latitude: float
    longitude: float
    aqi: int
    aqi_category: str
    pm25: float
    pm10: float
    no2: float
    so2: float
    co: float
    o3: float
    temperature: float
    humidity: float
    wind_speed: float
    timestamp: str

class HealthAdvisory(BaseModel):
    ward_id: int
    ward_name: str
    aqi: int
    category: str
    health_message: str
    recommendations: List[str]
    risk_level: str

class PolicyRecommendation(BaseModel):
    ward_id: int
    ward_name: str
    pollution_source: str
    severity: str
    recommended_actions: List[str]
    priority: str

# Decision Support System Rules
def generate_health_advisory(aqi: int, category: str, ward_name: str, ward_id: int) -> HealthAdvisory:
    """Generate health advisory based on AQI level"""
    
    if aqi <= 50:
        health_message = "Air quality is satisfactory. Enjoy outdoor activities!"
        recommendations = [
            "No health precautions needed",
            "Good time for outdoor exercise",
            "Safe for all age groups"
        ]
        risk_level = "Low"
    
    elif aqi <= 100:
        health_message = "Air quality is acceptable. Minimal impact for most people."
        recommendations = [
            "Unusually sensitive people should limit prolonged outdoor exertion",
            "Generally safe for outdoor activities",
            "Monitor for symptoms if sensitive"
        ]
        risk_level = "Low"
    
    elif aqi <= 200:
        health_message = "Sensitive groups may experience health effects."
        recommendations = [
            "Children, elderly, and people with respiratory issues should limit prolonged outdoor exertion",
            "Wear N95 masks if outdoors for extended periods",
            "Keep windows closed during peak pollution hours",
            "Use air purifiers indoors if available"
        ]
        risk_level = "Moderate"
    
    elif aqi <= 300:
        health_message = "Everyone may begin to experience health effects."
        recommendations = [
            "Avoid prolonged outdoor activities",
            "Sensitive groups should remain indoors",
            "Wear N95 masks when going outside",
            "Use air purifiers and keep windows closed",
            "Monitor children and elderly closely"
        ]
        risk_level = "High"
    
    elif aqi <= 400:
        health_message = "Health alert: Everyone may experience serious health effects."
        recommendations = [
            "Avoid all outdoor activities",
            "Stay indoors with air purifiers running",
            "Wear N95 masks if you must go outside",
            "Seek medical attention if experiencing breathing difficulties",
            "Schools should consider closure or online classes"
        ]
        risk_level = "Very High"
    
    else:  # > 400
        health_message = "Health warning of emergency conditions. Emergency level!"
        recommendations = [
            "EMERGENCY: Stay indoors at all times",
            "Seal windows and doors",
            "Use air purifiers continuously",
            "Seek immediate medical attention for any respiratory distress",
            "Schools and offices should close",
            "Only essential travel permitted"
        ]
        risk_level = "Emergency"
    
    return HealthAdvisory(
        ward_id=ward_id,
        ward_name=ward_name,
        aqi=aqi,
        category=category,
        health_message=health_message,
        recommendations=recommendations,
        risk_level=risk_level
    )

def generate_policy_recommendation(ward_id: int, ward_name: str, aqi: int, 
                                  pollution_source: str) -> PolicyRecommendation:
    """Generate policy recommendations based on pollution source and severity"""
    
    # Determine severity
    if aqi <= 100:
        severity = "Low"
        priority = "Monitor"
    elif aqi <= 200:
        severity = "Moderate"
        priority = "Medium"
    elif aqi <= 300:
        severity = "High"
        priority = "High"
    else:
        severity = "Severe"
        priority = "Critical"
    
    # Source-specific recommendations
    action_map = {
        'traffic': [
            "Implement odd-even vehicle restrictions",
            "Increase public transportation frequency",
            "Deploy traffic police for better flow management",
            "Consider congestion pricing during peak hours",
            "Promote work-from-home for offices in the area"
        ],
        'construction': [
            "Order mandatory water sprinkling at construction sites",
            "Enforce dust control measures (covering materials, barriers)",
            "Conduct compliance inspections within 24 hours",
            "Issue stop-work notices for non-compliant sites",
            "Require construction vehicles to be covered"
        ],
        'industrial': [
            "Inspect industrial emission controls",
            "Issue notices to non-compliant factories",
            "Consider temporary production restrictions",
            "Monitor stack emissions continuously",
            "Verify pollution control equipment operation"
        ],
        'biomass_burning': [
            "Deploy rapid response teams to detect burning",
            "Issue immediate stop-burning notices",
            "Increase patrolling in the area",
            "Launch awareness campaigns",
            "Impose penalties for violators"
        ],
        'residential': [
            "Promote clean cooking fuel usage",
            "Distribute awareness materials",
            "Provide subsidies for LPG connections",
            "Monitor domestic heating sources",
            "Conduct door-to-door campaigns"
        ]
    }
    
    # Get recommendations for the pollution source
    actions = action_map.get(pollution_source, [
        "Conduct detailed investigation",
        "Deploy mobile monitoring units",
        "Increase surveillance in the area"
    ])
    
    # Limit actions based on severity
    if severity == "Low":
        actions = actions[:2]
    elif severity == "Moderate":
        actions = actions[:3]
    elif severity == "High":
        actions = actions[:4]
    # Severe gets all actions
    
    return PolicyRecommendation(
        ward_id=ward_id,
        ward_name=ward_name,
        pollution_source=pollution_source,
        severity=severity,
        recommended_actions=actions,
        priority=priority
    )

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Air Quality Monitoring API", "version": "1.0.0", "status": "running"}

@app.get("/api/wards")
async def get_wards():
    """Get all ward information"""
    return ward_info

@app.get("/api/current_data")
async def get_current_data(ward_id: Optional[int] = None):
    """Get current air quality data for all wards or specific ward"""
    try:
        # Get latest timestamp
        latest_time = sensor_df['timestamp'].max()
        
        # Filter for latest data
        if ward_id:
            current_data = sensor_df[
                (sensor_df['timestamp'] == latest_time) & 
                (sensor_df['ward_id'] == ward_id)
            ]
        else:
            current_data = sensor_df[sensor_df['timestamp'] == latest_time]
        
        if len(current_data) == 0:
            raise HTTPException(status_code=404, detail="No data found")
        
        # Convert to dict
        result = current_data.to_dict('records')
        
        # Convert timestamp to string
        for record in result:
            record['timestamp'] = record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ward/{ward_id}/history")
async def get_ward_history(ward_id: int, hours: int = 24):
    """Get historical data for a specific ward"""
    try:
        # Get latest timestamp
        latest_time = sensor_df['timestamp'].max()
        start_time = latest_time - timedelta(hours=hours)
        
        # Filter data
        history = sensor_df[
            (sensor_df['ward_id'] == ward_id) &
            (sensor_df['timestamp'] >= start_time)
        ].sort_values('timestamp')
        
        if len(history) == 0:
            raise HTTPException(status_code=404, detail="No history found")
        
        result = history.to_dict('records')
        for record in result:
            record['timestamp'] = record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ward/{ward_id}/prediction")
async def predict_aqi(ward_id: int, hours: int = 6):
    """Predict future AQI for a ward"""
    try:
        if aqi_predictor is None:
            raise HTTPException(status_code=503, detail="Prediction model not loaded")
        
        # Get latest data for the ward
        latest_data = sensor_df[sensor_df['ward_id'] == ward_id].sort_values('timestamp').iloc[-1]
        
        # Prepare features
        current_time = datetime.now()
        features = [
            latest_data['pm25'],
            latest_data['pm10'],
            latest_data['no2'],
            latest_data['so2'],
            latest_data['co'],
            latest_data['o3'],
            latest_data['temperature'],
            latest_data['humidity'],
            latest_data['wind_speed'],
            current_time.hour,
            current_time.weekday()
        ]
        
        # Get predictions
        predictions = aqi_predictor.predict_next_hours(features, hours=hours)
        
        return {
            'ward_id': ward_id,
            'ward_name': latest_data['ward_name'],
            'current_aqi': int(latest_data['aqi']),
            'predictions': predictions,
            'generated_at': current_time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ward/{ward_id}/source_analysis")
async def analyze_pollution_source(ward_id: int):
    """Analyze pollution source for a ward"""
    try:
        if source_classifier is None:
            raise HTTPException(status_code=503, detail="Classification model not loaded")
        
        # Get latest data
        latest_data = sensor_df[sensor_df['ward_id'] == ward_id].sort_values('timestamp').iloc[-1]
        
        # Prepare features
        current_time = datetime.now()
        features = [
            latest_data['pm25'],
            latest_data['pm10'],
            latest_data['no2'],
            latest_data['so2'],
            latest_data['co'],
            latest_data['o3'],
            latest_data['temperature'],
            latest_data['humidity'],
            latest_data['wind_speed'],
            current_time.hour
        ]
        
        # Classify
        predicted_source, probabilities = source_classifier.classify(features)
        
        return {
            'ward_id': ward_id,
            'ward_name': latest_data['ward_name'],
            'aqi': int(latest_data['aqi']),
            'predicted_source': predicted_source,
            'source_probabilities': probabilities,
            'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hotspots")
async def get_hotspots(threshold: int = 200):
    """Get current pollution hotspots"""
    try:
        # Get latest data
        latest_time = sensor_df['timestamp'].max()
        latest_data = sensor_df[sensor_df['timestamp'] == latest_time]
        
        # Find hotspots
        hotspots = latest_data[latest_data['aqi'] >= threshold].sort_values('aqi', ascending=False)
        
        result = []
        for _, row in hotspots.iterrows():
            result.append({
                'ward_id': int(row['ward_id']),
                'ward_name': row['ward_name'],
                'aqi': int(row['aqi']),
                'category': row['aqi_category'],
                'latitude': float(row['latitude']),
                'longitude': float(row['longitude']),
                'pollution_source': row['pollution_source']
            })
        
        return {
            'threshold': threshold,
            'count': len(result),
            'hotspots': result,
            'timestamp': latest_time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health_advisory/{ward_id}", response_model=HealthAdvisory)
async def get_health_advisory(ward_id: int):
    """Get health advisory for a specific ward"""
    try:
        # Get latest data
        latest_data = sensor_df[sensor_df['ward_id'] == ward_id].sort_values('timestamp').iloc[-1]
        
        advisory = generate_health_advisory(
            aqi=int(latest_data['aqi']),
            category=latest_data['aqi_category'],
            ward_name=latest_data['ward_name'],
            ward_id=ward_id
        )
        
        return advisory
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/policy_recommendations/{ward_id}", response_model=PolicyRecommendation)
async def get_policy_recommendations(ward_id: int):
    """Get policy recommendations for a specific ward"""
    try:
        # Get latest data
        latest_data = sensor_df[sensor_df['ward_id'] == ward_id].sort_values('timestamp').iloc[-1]
        
        recommendation = generate_policy_recommendation(
            ward_id=ward_id,
            ward_name=latest_data['ward_name'],
            aqi=int(latest_data['aqi']),
            pollution_source=latest_data['pollution_source']
        )
        
        return recommendation
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard_summary")
async def get_dashboard_summary():
    """Get overall dashboard summary statistics"""
    try:
        # Get latest data
        latest_time = sensor_df['timestamp'].max()
        latest_data = sensor_df[sensor_df['timestamp'] == latest_time]
        
        # Calculate statistics
        summary = {
            'timestamp': latest_time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_wards': len(latest_data),
            'average_aqi': round(latest_data['aqi'].mean(), 1),
            'max_aqi': int(latest_data['aqi'].max()),
            'min_aqi': int(latest_data['aqi'].min()),
            'category_distribution': latest_data['aqi_category'].value_counts().to_dict(),
            'hotspot_count': len(latest_data[latest_data['aqi'] >= 200]),
            'critical_wards': len(latest_data[latest_data['aqi'] >= 300]),
            'worst_ward': {
                'ward_id': int(latest_data.loc[latest_data['aqi'].idxmax(), 'ward_id']),
                'ward_name': latest_data.loc[latest_data['aqi'].idxmax(), 'ward_name'],
                'aqi': int(latest_data['aqi'].max())
            },
            'best_ward': {
                'ward_id': int(latest_data.loc[latest_data['aqi'].idxmin(), 'ward_id']),
                'ward_name': latest_data.loc[latest_data['aqi'].idxmin(), 'ward_name'],
                'aqi': int(latest_data['aqi'].min())
            }
        }
        
        return summary
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting Air Quality Monitoring API Server...")
    print("📊 Dashboard will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
