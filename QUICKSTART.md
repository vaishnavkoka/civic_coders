# 🚀 Quick Start Guide

## Air Quality Monitoring Dashboard

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Modern web browser (Chrome, Firefox, Safari, Edge)

---

## ⚡ Quick Setup (3 commands)

```bash
# 1. Install dependencies
pip install fastapi uvicorn pandas numpy scikit-learn joblib

# 2. Setup (generate data + train models)
./setup.sh

# 3. Start the dashboard
./run.sh
```

Then open `frontend/index.html` in your browser! 🎉

---

## 📋 Detailed Steps

### Step 1: Install Dependencies
```bash
pip install fastapi uvicorn pydantic pandas numpy scikit-learn joblib
```

### Step 2: Generate Data
```bash
cd data
python3 generate_data.py
cd ..
```
**Output:**
- `data/sensor_data.csv` (439,200 records, 56 MB)
- `data/ward_info.json` (50 wards with coordinates)

### Step 3: Train ML Models
```bash
cd models
python3 train_models.py
cd ..
```
**Output:**
- `models/aqi_predictor.pkl` (475 KB)
- `models/source_classifier.pkl` (56 MB)
- `models/hotspots.json`

### Step 4: Start Backend API
```bash
cd backend
python3 api.py
```
API will be available at: **http://localhost:8000**

Leave this terminal running.

### Step 5: Open Dashboard

**Option A:** Direct file open
```bash
# Open frontend/index.html in your browser
open frontend/index.html  # macOS
xdg-open frontend/index.html  # Linux
start frontend/index.html  # Windows
```

**Option B:** Start local web server
```bash
cd frontend
python3 -m http.server 8080
```
Then navigate to: **http://localhost:8080**

---

## ✅ Verify Installation

Run the test script:
```bash
python3 test_api.py
```

You should see 8 successful tests:
- ✓ API is running
- ✓ Dashboard summary retrieved
- ✓ Current data retrieved
- ✓ Prediction retrieved
- ✓ Source analysis retrieved
- ✓ Hotspots retrieved
- ✓ Health advisory retrieved
- ✓ Policy recommendations retrieved

---

## 🌐 Access Points

### Frontend Dashboard
- **File**: `file:///path/to/frontend/index.html`
- **Local server**: `http://localhost:8080`

### Backend API
- **Base URL**: `http://localhost:8000`
- **Interactive docs**: `http://localhost:8000/docs`
- **OpenAPI spec**: `http://localhost:8000/openapi.json`

---

## 🎯 Key Features to Try

### 1. **City Overview**
- View stats cards at the top
- Check average AQI, hotspots, critical wards

### 2. **Interactive Map**
- Click on any ward marker
- Color indicates AQI level (green=good, red=severe)
- Click "View Details" in popup

### 3. **Ward Details**
- Current pollutant levels
- 6-hour AQI forecast
- Pollution source analysis
- Health advisory
- Policy recommendations

### 4. **Hotspots Sidebar**
- Top 5 worst polluted wards
- Click to view details

### 5. **24-Hour Trend**
- Line chart showing historical AQI
- Updates when ward is selected

---

## 📊 Sample API Calls

### Get Dashboard Summary
```bash
curl http://localhost:8000/api/dashboard_summary
```

### Get Current Data for Ward 1
```bash
curl http://localhost:8000/api/current_data?ward_id=1
```

### Get 6-Hour Prediction
```bash
curl http://localhost:8000/api/ward/1/prediction
```

### Get Pollution Source Analysis
```bash
curl http://localhost:8000/api/ward/1/source_analysis
```

### Get Hotspots
```bash
curl http://localhost:8000/api/hotspots
```

### Get Health Advisory
```bash
curl http://localhost:8000/api/health_advisory/1
```

### Get Policy Recommendations
```bash
curl http://localhost:8000/api/policy_recommendations/1
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'X'"
**Solution:** Install missing package
```bash
pip install X
```

### "FileNotFoundError: sensor_data.csv"
**Solution:** Generate data first
```bash
cd data && python3 generate_data.py && cd ..
```

### "FileNotFoundError: aqi_predictor.pkl"
**Solution:** Train models first
```bash
cd models && python3 train_models.py && cd ..
```

### "Address already in use (port 8000)"
**Solution:** Kill existing process or change port
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or edit api.py to use different port
```

### Map not loading
**Solution:** Check internet connection (Leaflet requires CDN)

### CORS errors in browser console
**Solution:** Ensure backend is running on localhost:8000

---

## 🛑 Stopping the Dashboard

1. Stop backend API:
   - Press `Ctrl + C` in the terminal running `api.py`
   - Or: `ps aux | grep api.py` then `kill <PID>`

2. Stop frontend server (if using option B):
   - Press `Ctrl + C` in the terminal running `python3 -m http.server`

---

## 📈 Project Structure

```
Air_quality_dashboard/
├── data/
│   ├── generate_data.py         # Data generator
│   ├── sensor_data.csv          # 439K records
│   └── ward_info.json           # Ward metadata
├── models/
│   ├── train_models.py          # Model training
│   ├── aqi_predictor.pkl        # Trained predictor
│   └── source_classifier.pkl    # Trained classifier
├── backend/
│   └── api.py                   # FastAPI server
├── frontend/
│   └── index.html               # Dashboard UI
├── setup.sh                     # One-click setup
├── run.sh                       # Start dashboard
├── test_api.py                  # API tests
├── requirements.txt             # Python packages
└── README.md                    # Full documentation
```

---

## 📚 Documentation

For detailed documentation, see:
- **Full README**: [README.md](README.md)
- **API Docs**: http://localhost:8000/docs (when running)

---

## 🎓 Understanding the Data

### Ward Profiles
- **Wards 1-10**: Traffic-heavy areas
- **Wards 11-20**: Construction zones
- **Wards 21-30**: Industrial areas
- **Wards 31-40**: Residential neighborhoods
- **Wards 41-50**: Mixed zones

### AQI Categories
| AQI Range | Category | Color |
|-----------|----------|-------|
| 0-50 | Good | Green |
| 51-100 | Satisfactory | Light Green |
| 101-200 | Moderate | Yellow |
| 201-300 | Poor | Orange |
| 301-400 | Very Poor | Red |
| 401-500 | Severe | Dark Red |

### Pollution Sources
1. **Traffic**: Vehicle emissions (PM2.5, NO₂, CO)
2. **Construction**: Dust (PM10, PM2.5)
3. **Industrial**: Factory emissions (NO₂, SO₂)
4. **Biomass Burning**: Smoke (PM2.5, CO)
5. **Residential**: Cooking/heating (mixed)

---

## 💡 Tips

1. **Bookmark the dashboard** for quick access
2. **Auto-refresh** happens every 5 minutes
3. **Click anywhere on the map** to explore different wards
4. **Check API docs** for programmatic access
5. **Use the test script** to verify functionality

---

## 🚀 Next Steps

1. Explore the interactive map
2. Check hotspots and their sources
3. Review health advisories
4. Read policy recommendations
5. Test API endpoints
6. Customize for your city (see README)

---

**Happy Monitoring! 🌍**

For issues or questions, see the full [README.md](README.md).
