import streamlit as st
import requests
from datetime import datetime

# -------------------------------
# Page configuration
# -------------------------------
st.set_page_config(
    page_title="Altitude Sickness Analyzer",
    page_icon="🏔️",
    layout="wide"
)

# -------------------------------
# Custom CSS
# -------------------------------
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .risk-high {
        background-color: #ffcccc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ff0000;
    }
    .risk-medium {
        background-color: #fff4cc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ffaa00;
    }
    .risk-low {
        background-color: #ccffcc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #00aa00;
    }
    .guideline-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# Title
# -------------------------------
st.markdown('<h1 class="main-header">🏔️ Altitude Sickness Risk Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666;">Based on 2024 Wilderness Medical Society Clinical Practice Guidelines</p>', unsafe_allow_html=True)

# -------------------------------
# Helper Functions
# -------------------------------
@st.cache_data(show_spinner=False)
def get_elevation(location_name: str):
    """Get elevation for a location using OpenStreetMap + Open-Elevation API"""
    try:
        geocode_url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json&limit=1&accept-language=en"
        headers = {'User-Agent': 'AltitudeSicknessAnalyzer/1.0'}
        response = requests.get(geocode_url, headers=headers, timeout=10)

        if response.status_code == 200 and response.json():
            data = response.json()[0]
            lat, lon = data['lat'], data['lon']
            display_name = data['display_name']

            elevation_url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
            elev_response = requests.get(elevation_url, timeout=10)

            if elev_response.status_code == 200:
                elevation = elev_response.json()['results'][0]['elevation']
                return {
                    'success': True,
                    'elevation': elevation,
                    'location': display_name,
                    'lat': lat,
                    'lon': lon
                }

        return {'success': False, 'error': 'Location not found'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def analyze_altitude(elevation: int):
    """Categorize altitude and provide physiological information"""
    if elevation < 1500:
        return {"category": "Sea Level to Low Altitude", "risk": "Minimal", "oxygen_sat": ">95%", "color": "low",
                "description": "No altitude-related physiological changes expected."}
    elif elevation < 2500:
        return {"category": "Intermediate Altitude (1,500-2,500m)", "risk": "Low", "oxygen_sat": ">90%", "color": "low",
                "description": "Physiological changes detectable. Illness rare but possible with rapid ascent."}
    elif elevation < 3500:
        return {"category": "High Altitude (2,500-3,500m)", "risk": "Moderate", "oxygen_sat": "85-90%", "color": "medium",
                "description": "Altitude illness common with rapid ascent. Gradual ascent recommended."}
    elif elevation < 5800:
        return {"category": "Very High Altitude (3,500-5,800m)", "risk": "High", "oxygen_sat": "<90%", "color": "high",
                "description": "Marked hypoxemia during exercise. Maximum altitude of permanent habitation."}
    elif elevation < 8000:
        return {"category": "Extreme Altitude (5,800-8,000m)", "risk": "Very High", "oxygen_sat": "<80%", "color": "high",
                "description": "Progressive deterioration despite acclimatization. Permanent survival not possible."}
    else:
        return {"category": "Death Zone (>8,000m)", "risk": "Extreme", "oxygen_sat": "~55%", "color": "high",
                "description": "Rapid deterioration inevitable. Supplemental oxygen required."}

# -------------------------------
# Sidebar Inputs
# -------------------------------
st.sidebar.header("📍 Location Information")
location_name = st.sidebar.text_input("Enter Location Name", placeholder="e.g., Mount Kilimanjaro, Machu Picchu")

if st.sidebar.button("🔍 Analyze Location"):
    if location_name:
        with st.spinner("Fetching elevation data..."):
            result = get_elevation(location_name)
            st.session_state['elevation_data'] = result
    else:
        st.warning("Please enter a location name")

st.sidebar.markdown("---")
manual_elevation = st.sidebar.number_input("Elevation (meters)", min_value=0, max_value=9000, value=0, step=100)
if st.sidebar.button("Use Manual Elevation"):
    st.session_state['elevation_data'] = {
        'success': True,
        'elevation': manual_elevation,
        'location': 'Manual Entry',
        'lat': None,
        'lon': None
    }

# -------------------------------
# Main Content
# -------------------------------
if 'elevation_data' in st.session_state and st.session_state['elevation_data'].get('success'):
    elevation_data = st.session_state['elevation_data']
    elevation = elevation_data['elevation']

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("📍 Location", elevation_data['location'])
    col2.metric("⛰️ Elevation", f"{elevation:,.0f} m")
    col3.metric("🗻 Elevation (ft)", f"{elevation * 3.28084:,.0f} ft")

    # Altitude Analysis
    st.markdown("---")
    st.header("🎯 Altitude Category & Physiological Effects")
    altitude_info = analyze_altitude(elevation)
    risk_class = f"risk-{altitude_info['color']}"

    st.markdown(f"""
    <div class="{risk_class}">
        <h3>{altitude_info['category']}</h3>
        <p><strong>Risk Level:</strong> {altitude_info['risk']}</p>
        <p><strong>Expected Oxygen Saturation:</strong> {altitude_info['oxygen_sat']}</p>
        <p>{altitude_info['description']}</p>
    </div>
    """, unsafe_allow_html=True)

    # TODO: Continue with risk profile, symptoms checker, treatment guidelines
    # (Your original logic can be plugged back here, but now with safer medication phrasing)
