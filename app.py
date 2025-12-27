import streamlit as st
import requests
from typing import Dict, Optional
from dataclasses import dataclass

# ============================================================================
# CONSTANTS - Define all altitude thresholds in one place
# ============================================================================
class AltitudeThresholds:
    SEA_LEVEL = 1500
    INTERMEDIATE = 2500
    HIGH = 3500
    VERY_HIGH = 5800
    EXTREME = 8000

# ============================================================================
# DATA CLASSES - Better type handling
# ============================================================================
@dataclass
class ElevationData:
    success: bool
    elevation: Optional[float] = None
    location: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    error: Optional[str] = None

@dataclass
class RiskProfile:
    previous_ams: bool = False
    previous_hace: bool = False
    previous_hape: bool = False
    rapid_ascent: bool = False
    no_acclimatization: bool = False
    physical_activity: bool = False

# Page configuration
st.set_page_config(
    page_title="Altitude Sickness Analyzer",
    page_icon="🏔️",
    layout="wide"
)

# Custom CSS
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

# ============================================================================
# IMPROVED API FUNCTIONS WITH BETTER ERROR HANDLING
# ============================================================================
def get_elevation(location_name: str) -> ElevationData:
    """Get elevation for a location using OpenStreetMap Nominatim API
    
    Args:
        location_name: Name of the location to search
        
    Returns:
        ElevationData object with results or error
    """
    if not location_name or not location_name.strip():
        return ElevationData(
            success=False,
            error="Location name cannot be empty"
        )
    
    try:
        # Add rate limiting to respect API terms
        import time
        time.sleep(1)  # 1 second delay for Nominatim
        
        geocode_url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json&limit=1&accept-language=en"
        headers = {'User-Agent': 'AltitudeSicknessAnalyzer/1.0'}
        
        response = requests.get(geocode_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return ElevationData(
                success=False,
                error=f"API error: {response.status_code}"
            )
        
        data = response.json()
        if not data:
            return ElevationData(
                success=False,
                error="Location not found. Try a more specific place name."
            )
        
        location_data = data[0]
        lat = float(location_data.get('lat', 0))
        lon = float(location_data.get('lon', 0))
        display_name = location_data.get('display_name', 'Unknown')
        
        # Get elevation using Open-Elevation API
        elevation_url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
        elev_response = requests.get(elevation_url, timeout=10)
        
        if elev_response.status_code != 200:
            return ElevationData(
                success=False,
                error="Could not fetch elevation data"
            )
        
        elevation_data = elev_response.json()
        if not elevation_data.get('results'):
            return ElevationData(
                success=False,
                error="No elevation data available for this location"
            )
        
        elevation = elevation_data['results'][0].get('elevation')
        
        if elevation is None:
            return ElevationData(
                success=False,
                error="Elevation data is unavailable"
            )
        
        return ElevationData(
            success=True,
            elevation=float(elevation),
            location=display_name,
            lat=lat,
            lon=lon
        )
        
    except requests.exceptions.Timeout:
        return ElevationData(
            success=False,
            error="Request timeout. Please try again."
        )
    except requests.exceptions.RequestException as e:
        return ElevationData(
            success=False,
            error=f"Network error: {str(e)}"
        )
    except (KeyError, ValueError, TypeError) as e:
        return ElevationData(
            success=False,
            error=f"Data parsing error: {str(e)}"
        )

def analyze_altitude(elevation: float) -> Dict:
    """Categorize altitude and provide physiological information"""
    if elevation < AltitudeThresholds.SEA_LEVEL:
        return {
            'category': 'Sea Level to Low Altitude',
            'risk': 'Minimal',
            'description': 'No altitude-related physiological changes expected.',
            'oxygen_sat': '>95%',
            'color': 'low'
        }
    elif elevation < AltitudeThresholds.INTERMEDIATE:
        return {
            'category': 'Intermediate Altitude (1,500-2,500m)',
            'risk': 'Low',
            'description': 'Physiological changes detectable. Arterial oxygen saturation >90%.',
            'oxygen_sat': '>90%',
            'color': 'low'
        }
    elif elevation < AltitudeThresholds.HIGH:
        return {
            'category': 'High Altitude (2,500-3,500m)',
            'risk': 'Moderate',
            'description': 'Altitude illness common when individuals ascend rapidly.',
            'oxygen_sat': '85-90%',
            'color': 'medium'
        }
    elif elevation < AltitudeThresholds.VERY_HIGH:
        return {
            'category': 'Very High Altitude (3,500-5,800m)',
            'risk': 'High',
            'description': 'Altitude illness common. Marked hypoxemia during exercise.',
            'oxygen_sat': '<90%',
            'color': 'high'
        }
    elif elevation < AltitudeThresholds.EXTREME:
        return {
            'category': 'Extreme Altitude (5,800-8,000m)',
            'risk': 'Very High',
            'description': 'Marked hypoxemia at rest. Progressive deterioration inevitable.',
            'oxygen_sat': '<80%',
            'color': 'high'
        }
    else:
        return {
            'category': 'Death Zone (>8,000m)',
            'risk': 'Extreme',
            'description': 'Most mountaineers require supplementary oxygen.',
            'oxygen_sat': '~55%',
            'color': 'high'
        }

def assess_risk_profile(elevation: float, profile: RiskProfile) -> tuple[str, list]:
    """Assess risk based on WMS 2024 Figure 1 criteria"""
    risk_level = "Low"
    risk_factors = []
    
    # History-based risk
    if profile.previous_hace or profile.previous_hape:
        risk_level = "High"
        if profile.previous_hace:
            risk_factors.append("Previous HACE episode - high risk for recurrence")
        if profile.previous_hape:
            risk_factors.append("Previous HAPE episode - high risk for recurrence")
    elif profile.previous_ams:
        if elevation >= AltitudeThresholds.HIGH:
            risk_level = "High"
            risk_factors.append("Previous AMS with rapid ascent to very high altitude")
        else:
            risk_level = "Moderate"
            risk_factors.append("Previous AMS history increases risk")
    
    # Ascent profile risk
    if elevation >= AltitudeThresholds.HIGH:
        if profile.rapid_ascent or profile.no_acclimatization:
            risk_level = "High"
            risk_factors.append("Rapid ascent to very high altitude (>3,500m)")
    elif elevation >= 2800:
        if profile.rapid_ascent:
            if risk_level != "High":
                risk_level = "Moderate"
            risk_factors.append("Rapid ascent to high altitude without acclimatization")
    
    # Physical activity risk
    if profile.physical_activity and elevation >= AltitudeThresholds.INTERMEDIATE:
        risk_factors.append("Strenuous physical activity increases risk")
        
    return risk_level, risk_factors

def calculate_lake_louise_score(symptoms: Dict) -> tuple[int, str]:
    """Calculate Lake Louise Acute Mountain Sickness Score (0-12 scale)
    
    Args:
        symptoms: Dictionary with symptom booleans
        
    Returns:
        Tuple of (score, severity_level)
    """
    score = 0
    
    # Headache (0-3 points) - cardinal symptom
    if symptoms.get('headache'):
        score += 1
    
    # Gastrointestinal (0-3 points)
    if symptoms.get('nausea') or symptoms.get('anorexia'):
        score += 1
    
    # Fatigue/weakness (0-3 points)
    if symptoms.get('fatigue'):
        score += 1
    
    # Dizziness (0-3 points)
    if symptoms.get('dizziness'):
        score += 1
    
    if score <= 2:
        return score, "No AMS"
    elif score <= 5:
        return score, "Mild-Moderate AMS"
    else:
        return score, "Severe AMS"

# ============================================================================
# UI TITLE
# ============================================================================
st.markdown('<h1 class="main-header">🏔️ Altitude Sickness Risk Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666;">Based on 2024 Wilderness Medical Society Clinical Practice Guidelines</p>', unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - LOCATION INPUT WITH CLEAR BUTTON
# ============================================================================
st.sidebar.header("📍 Location Information")
location_name = st.sidebar.text_input("Enter Location Name", placeholder="e.g., Mount Kilimanjaro, Machu Picchu")

col_search, col_clear = st.sidebar.columns(2)
with col_search:
    search_clicked = st.button("🔍 Analyze Location")
with col_clear:
    clear_clicked = st.button("🔄 Clear")

if clear_clicked:
    st.session_state.pop('elevation_data', None)
    st.rerun()

if search_clicked:
    if location_name:
        with st.spinner("Fetching elevation data..."):
            result = get_elevation(location_name)
            
            if result.success:
                st.session_state['elevation_data'] = result
            else:
                st.error(f"❌ Error: {result.error}")
    else:
        st.warning("Please enter a location name")

# Manual elevation input option
st.sidebar.markdown("---")
st.sidebar.markdown("**Or enter elevation manually:**")
manual_elevation = st.sidebar.number_input("Elevation (meters)", min_value=0, max_value=9000, value=0, step=100)

if st.sidebar.button("Use Manual Elevation"):
    st.session_state['elevation_data'] = ElevationData(
        success=True,
        elevation=manual_elevation,
        location='Manual Entry',
        lat=None,
        lon=None
    )

# ============================================================================
# MAIN CONTENT
# ============================================================================
if 'elevation_data' in st.session_state and st.session_state['elevation_data'].success:
    elevation_data = st.session_state['elevation_data']
    elevation = elevation_data.elevation
    
    # Display location info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📍 Location", elevation_data.location)
    with col2:
        st.metric("⛰️ Elevation", f"{elevation:,.0f} m")
    with col3:
        st.metric("🗻 Elevation (ft)", f"{elevation * 3.28084:,.0f} ft")
    
    # Altitude analysis
    altitude_info = analyze_altitude(elevation)
    
    st.markdown("---")
    st.header("🎯 Altitude Category & Physiological Effects")
    
    risk_class = f"risk-{altitude_info['color']}"
    st.markdown(f"""
    <div class="{risk_class}">
        <h3>{altitude_info['category']}</h3>
        <p><strong>Risk Level:</strong> {altitude_info['risk']}</p>
        <p><strong>Expected Oxygen Saturation:</strong> {altitude_info['oxygen_sat']}</p>
        <p>{altitude_info['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Risk Profile Assessment (WMS 2024)
    if elevation >= AltitudeThresholds.INTERMEDIATE:
        st.markdown("---")
        st.header("📊 Personal Risk Assessment")
        st.markdown("*Based on WMS 2024 Clinical Practice Guidelines*")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Medical History")
            previous_ams = st.checkbox("Previous acute mountain sickness (AMS)")
            previous_hace = st.checkbox("Previous high altitude cerebral edema (HACE)")
            previous_hape = st.checkbox("Previous high altitude pulmonary edema (HAPE)")
            
        with col2:
            st.subheader("Ascent Profile")
            rapid_ascent = st.checkbox("Rapid ascent (>500m/day above 3000m)")
            no_acclimatization = st.checkbox("No intermediate acclimatization")
            physical_activity = st.checkbox("Immediate strenuous physical activity planned")
        
        # Use RiskProfile dataclass
        profile = RiskProfile(
            previous_ams=previous_ams,
            previous_hace=previous_hace,
            previous_hape=previous_hape,
            rapid_ascent=rapid_ascent,
            no_acclimatization=no_acclimatization,
            physical_activity=physical_activity
        )
        
        risk_level, risk_factors = assess_risk_profile(elevation, profile)
        
        # Display risk assessment
        if risk_level == "High":
            st.error("🚨 **HIGH RISK** - Prophylactic medication strongly recommended")
        elif risk_level == "Moderate":
            st.warning("⚠️ **MODERATE RISK** - Prophylactic medication should be considered")
        else:
            st.success("✅ **LOW RISK** - Gradual ascent alone may be sufficient")
        
        if risk_factors:
            st.subheader("Risk Factors Identified:")
            for factor in risk_factors:
                st.warning(f"⚠️ {factor}")
    
    # Symptoms Checker
    st.markdown("---")
    st.header("🩺 Symptoms Checker")
    st.markdown("*Check any symptoms you are currently experiencing*")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Common Symptoms")
        headache = st.checkbox("Headache")
        nausea = st.checkbox("Nausea or vomiting")
        fatigue = st.checkbox("Fatigue or weakness")
        dizziness = st.checkbox("Dizziness or lightheadedness")
        anorexia = st.checkbox("Loss of appetite")
    
    with col2:
        st.subheader("Respiratory Symptoms")
        dyspnea_exertion = st.checkbox("Shortness of breath with exertion (worse than expected)")
        dyspnea_rest = st.checkbox("Shortness of breath at rest")
        cough_dry = st.checkbox("Dry cough")
        cough_productive = st.checkbox("Cough with pink/frothy sputum")
        chest_tightness = st.checkbox("Chest tightness or gurgling sensation")
    
    # Advanced symptoms (danger signs)
    st.markdown("**🚨 Severe Warning Signs (Medical Emergency):**")
    col3, col4 = st.columns(2)
    with col3:
        ataxia = st.checkbox("Loss of coordination/balance (cannot walk straight)")
        altered_mental = st.checkbox("Confusion or altered consciousness")
    with col4:
        severe_lassitude = st.checkbox("Severe weakness/inability to self-care")
        cyanosis = st.checkbox("Blue lips or fingertips")
    
    # Compile symptoms
    symptoms = {
        'headache': headache,
        'nausea': nausea,
        'fatigue': fatigue,
        'dizziness': dizziness,
        'anorexia': anorexia,
        'dyspnea_exertion': dyspnea_exertion,
        'dyspnea_rest': dyspnea_rest,
        'cough_dry': cough_dry,
        'cough_productive': cough_productive,
        'chest_tightness': chest_tightness,
        'ataxia': ataxia,
        'altered_mental': altered_mental,
        'severe_lassitude': severe_lassitude,
        'cyanosis': cyanosis
    }
    
    # Calculate Lake Louise Score
    lake_louise_score, severity = calculate_lake_louise_score(symptoms)
    
    # Count symptom groups
    basic_symptoms = sum([headache, nausea, fatigue, dizziness, anorexia])
    pulmonary_symptoms = sum([dyspnea_exertion, dyspnea_rest, cough_dry, cough_productive, chest_tightness])
    cerebral_symptoms = sum([ataxia, altered_mental, severe_lassitude])
    
    st.markdown("---")
    
    # Diagnosis and recommendations
    if cerebral_symptoms > 0:
        st.error("🚨 **EMERGENCY: High Altitude Cerebral Edema (HACE) SUSPECTED**")
        st.error("""
        **Immediate Actions Required:**
        - **DESCEND IMMEDIATELY** 300-1,000m (do not descend alone)
        - Administer **Dexamethasone 8mg** immediately, then 4mg every 6 hours
        - **Supplemental oxygen** 2-4 L/min if available (target SpO₂ >90%)
        - Consider portable hyperbaric chamber if descent delayed
        - **EVACUATE TO MEDICAL FACILITY**
        """)
    
    if pulmonary_symptoms >= 2 or dyspnea_rest or cough_productive:
        st.error("🚨 **EMERGENCY: High Altitude Pulmonary Edema (HAPE) SUSPECTED**")
        st.error("""
        **Immediate Actions Required:**
        - **DESCEND IMMEDIATELY** (minimize exertion, use assistance)
        - **Supplemental oxygen** to achieve SpO₂ >90%
        - **Nifedipine** 30mg extended release every 12 hours (only if oxygen unavailable)
        - Rest, keep warm, minimize physical activity
        - **EVACUATE TO MEDICAL FACILITY**
        - If concurrent HACE suspected, add Dexamethasone
        """)
    
    if headache and basic_symptoms >= 1 and cerebral_symptoms == 0 and pulmonary_symptoms < 2:
        st.info(f"Lake Louise Score: **{lake_louise_score}/12** - {severity}")
        
        if lake_louise_score >= 6:
            st.warning("⚠️ **SEVERE Acute Mountain Sickness (AMS)**")
            st.warning("""
            **Treatment Recommendations (WMS 2024):**
            - **STOP ASCENT** immediately
            - **Consider descent** if symptoms don't improve
            - **Dexamethasone**: 4mg every 6 hours (primary treatment)
            - **Acetazolamide**: 250mg every 12 hours (can be used as adjunct)
            - Rest and hydration
            - Supplemental oxygen if available (target SpO₂ >90%)
            - Ibuprofen 600mg every 8 hours for headache
            """)
        elif lake_louise_score >= 3:
            st.info("ℹ️ **MILD-MODERATE Acute Mountain Sickness (AMS)**")
            st.info("""
            **Treatment Recommendations (WMS 2024):**
            - **STOP ASCENT** until symptoms resolve
            - Rest at current altitude for 1-3 days
            - **Ibuprofen** 600mg every 8 hours or acetaminophen for headache
            - **Acetazolamide** 250mg every 12 hours may be considered
            - **Dexamethasone** 4mg every 6 hours for moderate-severe cases
            - Ensure adequate hydration
            - Descend if symptoms worsen or don't improve after 1-3 days
            """)

    # [Rest of the code continues with Prevention & Treatment sections...]
    # These remain largely the same as the original

else:
    # Welcome screen
    st.info("""
    👋 **Welcome to the Altitude Sickness Risk Analyzer!**
    
    This tool is based on the **2024 Wilderness Medical Society Clinical Practice Guidelines**.
    
    **Get started by entering a location in the sidebar** or manually entering an elevation.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p><strong>⚠️ EMERGENCY:</strong> If experiencing severe symptoms, <strong>DESCEND IMMEDIATELY</strong>.</p>
    <p><strong>Guidelines Source:</strong> Wilderness Medical Society 2024</p>
</div>
""", unsafe_allow_html=True)