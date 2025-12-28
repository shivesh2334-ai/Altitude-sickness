import streamlit as st
import requests
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass, field
from enum import IntEnum
import time
from functools import lru_cache

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================
class Config:
    """Application configuration"""
    APP_TITLE = "Altitude Sickness Risk Analyzer"
    APP_ICON = "🏔️"
    API_TIMEOUT = 10
    NOMINATIM_DELAY = 1  # Seconds between API calls
    USER_AGENT = "AltitudeSicknessAnalyzer/2.0"
    CACHE_TTL = 3600  # 1 hour cache for API calls

class AltitudeThresholds(IntEnum):
    """Altitude thresholds in meters based on WMS 2024 guidelines"""
    SEA_LEVEL = 1500
    INTERMEDIATE = 2500
    HIGH = 3500
    VERY_HIGH = 5800
    EXTREME = 8000

class LakeLouiseThresholds(IntEnum):
    """Lake Louise scoring thresholds"""
    NO_AMS = 2
    MILD_MODERATE = 5

# ============================================================================
# DATA CLASSES
# ============================================================================
@dataclass
class ElevationData:
    """Container for elevation data with validation"""
    success: bool
    elevation: Optional[float] = None
    location: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.success and self.elevation is not None:
            if self.elevation < 0 or self.elevation > 9000:
                self.success = False
                self.error = "Elevation out of valid range (0-9000m)"

@dataclass
class RiskProfile:
    """User's altitude risk profile"""
    previous_ams: bool = False
    previous_hace: bool = False
    previous_hape: bool = False
    rapid_ascent: bool = False
    no_acclimatization: bool = False
    physical_activity: bool = False
    
    def has_severe_history(self) -> bool:
        """Check if user has history of severe altitude illness"""
        return self.previous_hace or self.previous_hape
    
    def has_any_history(self) -> bool:
        """Check if user has any altitude illness history"""
        return self.previous_ams or self.previous_hace or self.previous_hape

@dataclass
class Symptoms:
    """Container for all symptoms with grouping methods"""
    # Basic AMS symptoms
    headache: bool = False
    nausea: bool = False
    fatigue: bool = False
    dizziness: bool = False
    anorexia: bool = False
    
    # Pulmonary symptoms
    dyspnea_exertion: bool = False
    dyspnea_rest: bool = False
    cough_dry: bool = False
    cough_productive: bool = False
    chest_tightness: bool = False
    
    # Cerebral symptoms (danger signs)
    ataxia: bool = False
    altered_mental: bool = False
    severe_lassitude: bool = False
    cyanosis: bool = False
    
    def basic_count(self) -> int:
        """Count basic AMS symptoms"""
        return sum([
            self.headache, self.nausea, self.fatigue, 
            self.dizziness, self.anorexia
        ])
    
    def pulmonary_count(self) -> int:
        """Count pulmonary symptoms"""
        return sum([
            self.dyspnea_exertion, self.dyspnea_rest, self.cough_dry,
            self.cough_productive, self.chest_tightness
        ])
    
    def cerebral_count(self) -> int:
        """Count cerebral symptoms"""
        return sum([
            self.ataxia, self.altered_mental, 
            self.severe_lassitude, self.cyanosis
        ])
    
    def has_emergency(self) -> bool:
        """Check for emergency symptoms"""
        return (self.cerebral_count() > 0 or 
                self.pulmonary_count() >= 2 or 
                self.dyspnea_rest or 
                self.cough_productive)

@dataclass
class AltitudeAnalysis:
    """Results of altitude analysis"""
    category: str
    risk: str
    description: str
    oxygen_sat: str
    color: str
    recommendations: List[str] = field(default_factory=list)

# ============================================================================
# API FUNCTIONS WITH CACHING AND RATE LIMITING
# ============================================================================
@lru_cache(maxsize=100)
def geocode_location(location_name: str) -> Tuple[Optional[float], Optional[float], Optional[str], Optional[str]]:
    """Geocode location with caching
    
    Returns: (lat, lon, display_name, error)
    """
    try:
        time.sleep(Config.NOMINATIM_DELAY)
        
        geocode_url = (
            f"https://nominatim.openstreetmap.org/search"
            f"?q={location_name}&format=json&limit=1&accept-language=en"
        )
        headers = {'User-Agent': Config.USER_AGENT}
        
        response = requests.get(geocode_url, headers=headers, timeout=Config.API_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        if not data:
            return None, None, None, "Location not found. Try a more specific name."
        
        location_data = data[0]
        lat = float(location_data['lat'])
        lon = float(location_data['lon'])
        display_name = location_data.get('display_name', 'Unknown')
        
        return lat, lon, display_name, None
        
    except requests.exceptions.Timeout:
        return None, None, None, "Request timeout. Please try again."
    except requests.exceptions.RequestException as e:
        return None, None, None, f"Network error: {str(e)}"
    except (KeyError, ValueError, TypeError) as e:
        return None, None, None, f"Data parsing error: {str(e)}"

@lru_cache(maxsize=100)
def get_elevation_from_coords(lat: float, lon: float) -> Tuple[Optional[float], Optional[str]]:
    """Get elevation from coordinates with caching
    
    Returns: (elevation, error)
    """
    try:
        elevation_url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
        response = requests.get(elevation_url, timeout=Config.API_TIMEOUT)
        response.raise_for_status()
        
        elevation_data = response.json()
        if not elevation_data.get('results'):
            return None, "No elevation data available"
        
        elevation = elevation_data['results'][0].get('elevation')
        if elevation is None:
            return None, "Elevation data unavailable"
        
        return float(elevation), None
        
    except requests.exceptions.RequestException as e:
        return None, f"Elevation API error: {str(e)}"
    except (KeyError, ValueError, TypeError) as e:
        return None, f"Data parsing error: {str(e)}"

def get_elevation(location_name: str) -> ElevationData:
    """Main function to get elevation for a location"""
    if not location_name or not location_name.strip():
        return ElevationData(success=False, error="Location name cannot be empty")
    
    # Geocode
    lat, lon, display_name, error = geocode_location(location_name.strip())
    if error:
        return ElevationData(success=False, error=error)
    
    # Get elevation
    elevation, error = get_elevation_from_coords(lat, lon)
    if error:
        return ElevationData(success=False, error=error)
    
    return ElevationData(
        success=True,
        elevation=elevation,
        location=display_name,
        lat=lat,
        lon=lon
    )

# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================
def analyze_altitude(elevation: float) -> AltitudeAnalysis:
    """Categorize altitude and provide physiological information"""
    if elevation < AltitudeThresholds.SEA_LEVEL:
        return AltitudeAnalysis(
            category='Sea Level to Low Altitude',
            risk='Minimal',
            description='No altitude-related physiological changes expected.',
            oxygen_sat='>95%',
            color='low',
            recommendations=['Normal activity can be maintained']
        )
    elif elevation < AltitudeThresholds.INTERMEDIATE:
        return AltitudeAnalysis(
            category='Intermediate Altitude (1,500-2,500m)',
            risk='Low',
            description='Physiological changes detectable. Arterial oxygen saturation >90%.',
            oxygen_sat='>90%',
            color='low',
            recommendations=[
                'Monitor for mild symptoms',
                'Stay well hydrated',
                'Gradual ascent recommended'
            ]
        )
    elif elevation < AltitudeThresholds.HIGH:
        return AltitudeAnalysis(
            category='High Altitude (2,500-3,500m)',
            risk='Moderate',
            description='Altitude illness common with rapid ascent.',
            oxygen_sat='85-90%',
            color='medium',
            recommendations=[
                'Ascend gradually (300-500m/day above 3000m)',
                'Include rest days for acclimatization',
                'Consider prophylactic medication if rapid ascent necessary'
            ]
        )
    elif elevation < AltitudeThresholds.VERY_HIGH:
        return AltitudeAnalysis(
            category='Very High Altitude (3,500-5,800m)',
            risk='High',
            description='Altitude illness common. Marked hypoxemia during exercise.',
            oxygen_sat='<90%',
            color='high',
            recommendations=[
                'Mandatory acclimatization required',
                'Ascend 300-500m per day maximum',
                'Include rest day every 3-4 days',
                'Strong consideration for prophylactic medication'
            ]
        )
    elif elevation < AltitudeThresholds.EXTREME:
        return AltitudeAnalysis(
            category='Extreme Altitude (5,800-8,000m)',
            risk='Very High',
            description='Marked hypoxemia at rest. Progressive deterioration inevitable.',
            oxygen_sat='<80%',
            color='high',
            recommendations=[
                'Expert mountaineering experience required',
                'Prophylactic medication strongly recommended',
                'Supplemental oxygen may be necessary',
                'Minimize time at altitude'
            ]
        )
    else:
        return AltitudeAnalysis(
            category='Death Zone (>8,000m)',
            risk='Extreme',
            description='Most mountaineers require supplementary oxygen.',
            oxygen_sat='~55%',
            color='high',
            recommendations=[
                'Supplemental oxygen required for most individuals',
                'Expert medical and mountaineering support essential',
                'Minimize exposure time'
            ]
        )

def assess_risk_profile(elevation: float, profile: RiskProfile) -> Tuple[str, List[str]]:
    """Assess risk based on WMS 2024 criteria"""
    risk_level = "Low"
    risk_factors = []
    
    # Severe history automatically means high risk
    if profile.has_severe_history():
        risk_level = "High"
        if profile.previous_hace:
            risk_factors.append("Previous HACE - high recurrence risk")
        if profile.previous_hape:
            risk_factors.append("Previous HAPE - high recurrence risk")
    
    # Previous AMS with current conditions
    elif profile.previous_ams:
        if elevation >= AltitudeThresholds.HIGH:
            risk_level = "High"
            risk_factors.append("Previous AMS with ascent to very high altitude")
        else:
            risk_level = "Moderate"
            risk_factors.append("Previous AMS history")
    
    # Ascent profile assessment
    if elevation >= AltitudeThresholds.HIGH:
        if profile.rapid_ascent or profile.no_acclimatization:
            if risk_level != "High":
                risk_level = "High"
            risk_factors.append("Rapid ascent to very high altitude without acclimatization")
    elif elevation >= 2800:
        if profile.rapid_ascent and risk_level == "Low":
            risk_level = "Moderate"
            risk_factors.append("Rapid ascent to high altitude")
    
    # Physical activity modifier
    if profile.physical_activity and elevation >= AltitudeThresholds.INTERMEDIATE:
        risk_factors.append("Strenuous activity planned - increases risk")
    
    return risk_level, risk_factors

def calculate_lake_louise_score(symptoms: Symptoms) -> Tuple[int, str]:
    """Calculate Lake Louise AMS Score"""
    score = sum([
        symptoms.headache,
        symptoms.nausea or symptoms.anorexia,
        symptoms.fatigue,
        symptoms.dizziness
    ])
    
    if score <= LakeLouiseThresholds.NO_AMS:
        return score, "No AMS"
    elif score <= LakeLouiseThresholds.MILD_MODERATE:
        return score, "Mild-Moderate AMS"
    else:
        return score, "Severe AMS"

# ============================================================================
# UI STYLING
# ============================================================================
def apply_custom_css():
    """Apply custom CSS styling"""
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 1rem;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 2rem;
        }
        .risk-high {
            background-color: #ffcccc;
            padding: 1.5rem;
            border-radius: 0.5rem;
            border-left: 5px solid #ff0000;
            margin: 1rem 0;
        }
        .risk-medium {
            background-color: #fff4cc;
            padding: 1.5rem;
            border-radius: 0.5rem;
            border-left: 5px solid #ffaa00;
            margin: 1rem 0;
        }
        .risk-low {
            background-color: #ccffcc;
            padding: 1.5rem;
            border-radius: 0.5rem;
            border-left: 5px solid #00aa00;
            margin: 1rem 0;
        }
        .guideline-box {
            background-color: #e8f4f8;
            padding: 1.5rem;
            border-radius: 0.5rem;
            border-left: 5px solid #1f77b4;
            margin: 1rem 0;
        }
        .emergency-box {
            background-color: #ffe6e6;
            padding: 1.5rem;
            border-radius: 0.5rem;
            border: 2px solid #ff0000;
            margin: 1rem 0;
        }
        .metric-container {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

# ============================================================================
# UI COMPONENTS
# ============================================================================
def render_elevation_metrics(elevation_data: ElevationData):
    """Render elevation metrics in a clean layout"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📍 Location", elevation_data.location or "Unknown")
    with col2:
        st.metric("⛰️ Elevation", f"{elevation_data.elevation:,.0f} m")
    with col3:
        st.metric("🗻 Elevation", f"{elevation_data.elevation * 3.28084:,.0f} ft")

def render_altitude_analysis(analysis: AltitudeAnalysis):
    """Render altitude category analysis"""
    st.header("🎯 Altitude Category & Physiological Effects")
    
    risk_class = f"risk-{analysis.color}"
    st.markdown(f"""
        <div class="{risk_class}">
            <h3>{analysis.category}</h3>
            <p><strong>Risk Level:</strong> {analysis.risk}</p>
            <p><strong>Expected Oxygen Saturation:</strong> {analysis.oxygen_sat}</p>
            <p>{analysis.description}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if analysis.recommendations:
        with st.expander("📋 General Recommendations", expanded=True):
            for rec in analysis.recommendations:
                st.write(f"• {rec}")

def render_risk_profile_form(elevation: float) -> Optional[RiskProfile]:
    """Render risk profile assessment form"""
    if elevation < AltitudeThresholds.INTERMEDIATE:
        return None
    
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
        physical_activity = st.checkbox("Immediate strenuous activity planned")
    
    return RiskProfile(
        previous_ams=previous_ams,
        previous_hace=previous_hace,
        previous_hape=previous_hape,
        rapid_ascent=rapid_ascent,
        no_acclimatization=no_acclimatization,
        physical_activity=physical_activity
    )

def render_symptoms_form() -> Symptoms:
    """Render symptoms checker form"""
    st.header("🩺 Symptoms Checker")
    st.markdown("*Check any symptoms currently experienced*")
    
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
        dyspnea_exertion = st.checkbox("Shortness of breath with exertion")
        dyspnea_rest = st.checkbox("Shortness of breath at rest")
        cough_dry = st.checkbox("Dry cough")
        cough_productive = st.checkbox("Cough with pink/frothy sputum")
        chest_tightness = st.checkbox("Chest tightness or gurgling")
    
    st.markdown("**🚨 Severe Warning Signs (Medical Emergency):**")
    col3, col4 = st.columns(2)
    
    with col3:
        ataxia = st.checkbox("Loss of coordination/balance")
        altered_mental = st.checkbox("Confusion or altered consciousness")
    with col4:
        severe_lassitude = st.checkbox("Severe weakness/inability to self-care")
        cyanosis = st.checkbox("Blue lips or fingertips")
    
    return Symptoms(
        headache=headache, nausea=nausea, fatigue=fatigue,
        dizziness=dizziness, anorexia=anorexia,
        dyspnea_exertion=dyspnea_exertion, dyspnea_rest=dyspnea_rest,
        cough_dry=cough_dry, cough_productive=cough_productive,
        chest_tightness=chest_tightness, ataxia=ataxia,
        altered_mental=altered_mental, severe_lassitude=severe_lassitude,
        cyanosis=cyanosis
    )

def render_diagnosis(symptoms: Symptoms):
    """Render diagnosis and treatment recommendations"""
    st.markdown("---")
    
    # Emergency conditions
    if symptoms.cerebral_count() > 0:
        st.markdown('<div class="emergency-box">', unsafe_allow_html=True)
        st.error("🚨 **EMERGENCY: High Altitude Cerebral Edema (HACE) SUSPECTED**")
        st.error("""
        **Immediate Actions Required:**
        - **DESCEND IMMEDIATELY** 300-1,000m (do not descend alone)
        - Administer **Dexamethasone 8mg** immediately, then 4mg every 6 hours
        - **Supplemental oxygen** 2-4 L/min if available (target SpO₂ >90%)
        - Consider portable hyperbaric chamber if descent delayed
        - **EVACUATE TO MEDICAL FACILITY**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if symptoms.pulmonary_count() >= 2 or symptoms.dyspnea_rest or symptoms.cough_productive:
        st.markdown('<div class="emergency-box">', unsafe_allow_html=True)
        st.erro
