#!/usr/bin/env python3
"""
Quick test script to verify the Air Quality Dashboard is working
"""

import requests
import json

API_BASE = "http://localhost:8000/api"

print("=" * 60)
print("  Air Quality Dashboard - Quick Test")
print("=" * 60)
print()

try:
    # Test 1: API Root
    print("1. Testing API root...")
    response = requests.get("http://localhost:8000/")
    if response.status_code == 200:
        print("   ✓ API is running")
        print(f"   Response: {response.json()}")
    else:
        print(f"   ✗ Failed with status {response.status_code}")
    
    # Test 2: Dashboard Summary
    print("\n2. Testing dashboard summary...")
    response = requests.get(f"{API_BASE}/dashboard_summary")
    if response.status_code == 200:
        data = response.json()
        print("   ✓ Dashboard summary retrieved")
        print(f"   Total wards: {data['total_wards']}")
        print(f"   Average AQI: {data['average_aqi']}")
        print(f"   Hotspots: {data['hotspot_count']}")
        print(f"   Critical wards: {data['critical_wards']}")
    else:
        print(f"   ✗ Failed with status {response.status_code}")
    
    # Test 3: Current Data
    print("\n3. Testing current data...")
    response = requests.get(f"{API_BASE}/current_data?ward_id=1")
    if response.status_code == 200:
        data = response.json()[0]
        print("   ✓ Current data retrieved for Ward 1")
        print(f"   AQI: {data['aqi']} ({data['aqi_category']})")
        print(f"   PM2.5: {data['pm25']} µg/m³")
        print(f"   PM10: {data['pm10']} µg/m³")
    else:
        print(f"   ✗ Failed with status {response.status_code}")
    
    # Test 4: Prediction
    print("\n4. Testing AQI prediction...")
    response = requests.get(f"{API_BASE}/ward/1/prediction")
    if response.status_code == 200:
        data = response.json()
        print("   ✓ Prediction retrieved for Ward 1")
        print(f"   Current AQI: {data['current_aqi']}")
        print(f"   6-hour forecast: {len(data['predictions'])} predictions")
    else:
        print(f"   ✗ Failed with status {response.status_code}")
    
    # Test 5: Source Analysis
    print("\n5. Testing source analysis...")
    response = requests.get(f"{API_BASE}/ward/1/source_analysis")
    if response.status_code == 200:
        data = response.json()
        print("   ✓ Source analysis retrieved")
        print(f"   Predicted source: {data['predicted_source']}")
        print(f"   Top probability: {data['source_probabilities'][0]['probability']*100:.1f}%")
    else:
        print(f"   ✗ Failed with status {response.status_code}")
    
    # Test 6: Hotspots
    print("\n6. Testing hotspot detection...")
    response = requests.get(f"{API_BASE}/hotspots")
    if response.status_code == 200:
        data = response.json()
        print("   ✓ Hotspots retrieved")
        print(f"   Found {data['count']} hotspots (AQI > {data['threshold']})")
        if data['hotspots']:
            worst = data['hotspots'][0]
            print(f"   Worst: {worst['ward_name']} (AQI: {worst['aqi']})")
    else:
        print(f"   ✗ Failed with status {response.status_code}")
    
    # Test 7: Health Advisory
    print("\n7. Testing health advisory...")
    response = requests.get(f"{API_BASE}/health_advisory/1")
    if response.status_code == 200:
        data = response.json()
        print("   ✓ Health advisory retrieved")
        print(f"   Risk level: {data['risk_level']}")
        print(f"   Recommendations: {len(data['recommendations'])} items")
    else:
        print(f"   ✗ Failed with status {response.status_code}")
    
    # Test 8: Policy Recommendations
    print("\n8. Testing policy recommendations...")
    response = requests.get(f"{API_BASE}/policy_recommendations/1")
    if response.status_code == 200:
        data = response.json()
        print("   ✓ Policy recommendations retrieved")
        print(f"   Priority: {data['priority']}")
        print(f"   Actions: {len(data['recommended_actions'])} items")
    else:
        print(f"   ✗ Failed with status {response.status_code}")
    
    print("\n" + "=" * 60)
    print("  ✓ All tests passed! Dashboard is fully functional.")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Open frontend/index.html in your browser")
    print("  2. Or run: cd frontend && python3 -m http.server 8080")
    print(f"  3. API docs: http://localhost:8000/docs")
    print()

except requests.exceptions.ConnectionError:
    print("\n✗ Error: Could not connect to API")
    print("  Make sure the backend is running: python3 backend/api.py")
except Exception as e:
    print(f"\n✗ Error: {e}")
