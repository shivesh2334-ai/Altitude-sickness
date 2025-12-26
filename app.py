import streamlit as st
import requests
from datetime import datetime

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
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🏔️ Altitude Sickness Risk Analyzer</h1>', unsafe_allow_html=True)

# Function to get elevation data
def get_elevation(location_name):
    """Get elevation for a location using OpenStreetMap Nominatim API"""
    try:
        # Geocode the location with English language preference
        geocode_url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json&limit=1&accept-language=en"
        headers = {'User-Agent': 'AltitudeSicknessAnalyzer/1.0'}
        response = requests.get(geocode_url, headers=headers, timeout=10)
        
        if response.status_code == 200 and response.json():
            data = response.json()[0]
            lat = data['lat']
            lon = data['lon']
            display_name = data['display_name']
            
            # Get elevation using Open-Elevation API
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

# Function to analyze altitude category
def analyze_altitude(elevation):
    """Categorize altitude and provide physiological information"""
    if elevation < 1500:
        return {
            'category': 'Sea Level to Low Altitude',
            'risk': 'Minimal',
            'description': 'No altitude-related physiological changes expected.',
            'oxygen_sat': '>95%',
            'color': 'low'
        }
    elif 1500 <= elevation < 2500:
        return {
            'category': 'Intermediate Altitude',
            'risk': 'Low',
            'description': 'Physiological changes detectable. Arterial oxygen saturation >90%. Altitude illness rare but possible with rapid ascent, exercise, and susceptible individuals.',
            'oxygen_sat': '>90%',
            'color': 'low'
        }
    elif 2500 <= elevation < 3500:
        return {
            'category': 'High Altitude',
            'risk': 'Moderate',
            'description': 'Altitude illness common when individuals ascend rapidly.',
            'oxygen_sat': '85-90%',
            'color': 'medium'
        }
    elif 3500 <= elevation < 5800:
        return {
            'category': 'Very High Altitude',
            'risk': 'High',
            'description': 'Altitude illness common. Arterial oxygen saturation <90%. Marked hypoxaemia during exercise.',
            'oxygen_sat': '<90%',
            'color': 'medium'
        }
    elif 5800 <= elevation < 8000:
        return {
            'category': 'Extreme Altitude',
            'risk': 'Very High',
            'description': 'Marked hypoxaemia at rest. Progressive deterioration despite maximal acclimatisation. Permanent survival not possible.',
            'oxygen_sat': '<80%',
            'color': 'high'
        }
    else:
        return {
            'category': 'Death Zone',
            'risk': 'Extreme',
            'description': 'Prolonged acclimatisation (>6 weeks) essential. Most mountaineers require supplementary oxygen. Arterial oxygen saturations about 55%. Rapid deterioration inevitable.',
            'oxygen_sat': '~55%',
            'color': 'high'
        }

# Function to assess risk factors
def assess_personal_risk(rapid_ascent, previous_ams, exercise_planned, susceptible):
    """Calculate personal risk score"""
    risk_score = 0
    risk_factors = []
    
    if rapid_ascent:
        risk_score += 3
        risk_factors.append("Rapid ascent increases risk significantly")
    
    if previous_ams:
        risk_score += 2
        risk_factors.append("Previous acute mountain sickness indicates susceptibility")
    
    if exercise_planned:
        risk_score += 1
        risk_factors.append("Strenuous exercise at altitude increases risk")
    
    if susceptible:
        risk_score += 2
        risk_factors.append("Individual susceptibility is a major factor")
    
    return risk_score, risk_factors

# Sidebar - Location Input
st.sidebar.header("📍 Location Information")
location_name = st.sidebar.text_input("Enter Location Name", placeholder="e.g., Mount Kilimanjaro, Machu Picchu")

if st.sidebar.button("🔍 Analyze Location"):
    if location_name:
        with st.spinner("Fetching elevation data..."):
            result = get_elevation(location_name)
            
            if result['success']:
                st.session_state['elevation_data'] = result
            else:
                st.error(f"❌ Error: {result['error']}")
    else:
        st.warning("Please enter a location name")

# Manual elevation input option
st.sidebar.markdown("---")
st.sidebar.markdown("**Or enter elevation manually:**")
manual_elevation = st.sidebar.number_input("Elevation (meters)", min_value=0, max_value=9000, value=0, step=100)

if st.sidebar.button("Use Manual Elevation"):
    st.session_state['elevation_data'] = {
        'success': True,
        'elevation': manual_elevation,
        'location': 'Manual Entry',
        'lat': None,
        'lon': None
    }

# Main content
if 'elevation_data' in st.session_state and st.session_state['elevation_data']['success']:
    elevation_data = st.session_state['elevation_data']
    elevation = elevation_data['elevation']
    
    # Display location info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📍 Location", elevation_data['location'])
    with col2:
        st.metric("⛰️ Elevation", f"{elevation:,.0f} m")
    with col3:
        st.metric("🗻 Elevation (ft)", f"{elevation * 3.28084:,.0f} ft")
    
    # Altitude analysis
    altitude_info = analyze_altitude(elevation)
    
    st.markdown("---")
    st.header("🎯 Altitude Category & Risk Assessment")
    
    risk_class = f"risk-{altitude_info['color']}"
    st.markdown(f"""
    <div class="{risk_class}">
        <h3>{altitude_info['category']}</h3>
        <p><strong>Risk Level:</strong> {altitude_info['risk']}</p>
        <p><strong>Expected Oxygen Saturation:</strong> {altitude_info['oxygen_sat']}</p>
        <p>{altitude_info['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Personal Risk Assessment
    st.markdown("---")
    st.header("🧑‍⚕️ Personal Risk Assessment")
    
    col1, col2 = st.columns(2)
    with col1:
        rapid_ascent = st.checkbox("Planning rapid ascent (>300m/day above 3000m)")
        previous_ams = st.checkbox("Previous history of altitude sickness")
    with col2:
        exercise_planned = st.checkbox("Planning strenuous exercise")
        susceptible = st.checkbox("Known susceptibility to altitude illness")
    
    personal_risk_score, risk_factors = assess_personal_risk(rapid_ascent, previous_ams, exercise_planned, susceptible)
    
    if personal_risk_score > 0:
        st.subheader("Your Additional Risk Factors:")
        for factor in risk_factors:
            st.warning(f"⚠️ {factor}")
    
    # Symptoms Checker
    st.markdown("---")
    st.header("🩺 Symptoms Checker")
    
    st.subheader("Are you experiencing any of these symptoms?")
    
    col1, col2 = st.columns(2)
    with col1:
        headache = st.checkbox("Headache (especially worsening at night)")
        nausea = st.checkbox("Nausea or vomiting")
        fatigue = st.checkbox("Extreme fatigue or weakness")
        dizziness = st.checkbox("Dizziness or lightheadedness")
    
    with col2:
        sleep_difficulty = st.checkbox("Difficulty sleeping")
        decreased_urine = st.checkbox("Decreased urine output")
        shortness_breath = st.checkbox("Shortness of breath at rest")
        cough = st.checkbox("Dry cough or cough with blood-tinged sputum")
    
    # Advanced symptoms (danger signs)
    st.markdown("**⚠️ Serious Warning Signs:**")
    col3, col4 = st.columns(2)
    with col3:
        confusion = st.checkbox("Mental confusion or altered consciousness")
        ataxia = st.checkbox("Loss of coordination (ataxia)")
    with col4:
        severe_breathlessness = st.checkbox("Severe breathlessness even at rest")
        crackling_chest = st.checkbox("Crackling sounds in chest")
    
    # Symptom analysis
    basic_symptoms = sum([headache, nausea, fatigue, dizziness, sleep_difficulty, decreased_urine])
    pulmonary_symptoms = sum([shortness_breath, cough, severe_breathlessness, crackling_chest])
    cerebral_symptoms = sum([confusion, ataxia])
    
    if cerebral_symptoms > 0:
        st.error("🚨 **EMERGENCY: High Altitude Cerebral Edema (HACE) suspected!**")
        st.error("Immediate descent and medical attention required. Administer dexamethasone if available.")
    
    if pulmonary_symptoms >= 2:
        st.error("🚨 **EMERGENCY: High Altitude Pulmonary Edema (HAPE) suspected!**")
        st.error("Immediate descent required. Administer oxygen if available. Seek medical help immediately.")
    
    if headache and basic_symptoms >= 2 and cerebral_symptoms == 0:
        if basic_symptoms >= 3:
            st.warning("⚠️ **Moderate to Severe Acute Mountain Sickness (AMS)** - Lake Louise Score: 5+")
            st.warning("Stop ascent. Consider descent. Medication recommended.")
        else:
            st.info("ℹ️ **Mild Acute Mountain Sickness (AMS)** - Lake Louise Score: 3-4")
            st.info("Rest, hydrate, and monitor symptoms. Consider medication.")
    
    # Prevention Recommendations
    st.markdown("---")
    st.header("🛡️ Prevention Recommendations")
    
    if elevation >= 2500:
        st.subheader("Ascent Guidelines")
        st.write("""
        - **Ascend slowly:** Above 3000m, ascend no more than 300m per day
        - **Rest days:** Take a rest day for every 1000m climbed
        - **Sleep low:** "Climb high, sleep low" - sleep at lower altitudes when possible
        - **Stay hydrated:** Drink 3-4 liters of water daily
        - **Avoid alcohol:** Especially in first 48 hours at altitude
        """)
        
        st.subheader("💊 Pharmacological Prevention")
        
        tab1, tab2 = st.tabs(["Acetazolamide (Diamox)", "Dexamethasone"])
        
        with tab1:
            st.write("""
            **Acetazolamide (Primary preventive medication)**
            - **Dose:** 125-250mg twice daily
            - **Start:** 1-2 days before ascent
            - **Duration:** Continue for 2 days at maximum altitude or until descent
            - **Effectiveness:** Proven to reduce symptoms of AMS
            - **Side effects:** Tingling in fingers/toes, increased urination, altered taste
            - **Note:** Does not prevent symptoms if ascent is too rapid
            """)
        
        with tab2:
            st.write("""
            **Dexamethasone (For prevention in high-risk situations)**
            - **Dose:** 2-4mg every 6 hours or 4mg every 12 hours
            - **Use:** When acetazolamide contraindicated or for rapid ascent
            - **Note:** Potential side effects generally outweigh benefits for routine prophylaxis
            - **Warning:** Does not aid acclimatization, only masks symptoms
            """)
    
    # Treatment Recommendations
    st.markdown("---")
    st.header("💊 Treatment Options")
    
    if basic_symptoms > 0 or pulmonary_symptoms > 0 or cerebral_symptoms > 0:
        st.subheader("Based on Your Symptoms")
        
        if cerebral_symptoms > 0 or pulmonary_symptoms >= 2:
            st.error("""
            **EMERGENCY TREATMENT REQUIRED:**
            1. **Immediate descent 300-1000m** (mechanized transport preferred)
            2. **Oxygen:** 2-4 L/min for HACE, higher for HAPE
            3. **Dexamethasone:** 8mg immediately, then 4mg every 6 hours
            4. **For HAPE:** Nifedipine 30mg sustained release twice daily
            5. **Portable hyperbaric chamber** if descent impossible
            6. **Seek immediate medical evacuation**
            """)
        
        elif basic_symptoms >= 3:
            st.warning("""
            **MODERATE TO SEVERE AMS TREATMENT:**
            - **Stop ascent immediately**
            - **Consider descent** if symptoms don't improve
            - **Acetazolamide:** 250mg every 12 hours
            - **Dexamethasone:** 4-8mg initially, then 4mg every 6 hours
            - **Rest and hydration**
            - **Supplemental oxygen:** 2L/min if available
            """)
        
        elif basic_symptoms >= 1:
            st.info("""
            **MILD AMS TREATMENT:**
            - **Stop ascent** until symptoms resolve
            - **Rest** for 24-48 hours at current altitude
            - **Hydration:** Ensure adequate fluid intake
            - **Pain relief:** Ibuprofen 600mg or Paracetamol 1000mg
            - **Acetazolamide:** 250mg twice daily (if symptoms persist)
            - **Monitor symptoms** - descend if worsening
            """)
    
    else:
        st.success("""
        **General Treatment Guidelines:**
        
        **Mild AMS (Lake Louise Score 3-4):**
        - Rest and maintain hydration
        - Ibuprofen or paracetamol for headache
        - Acetazolamide 250mg every 12 hours if needed
        
        **Moderate-Severe AMS (Lake Louise Score 5+):**
        - Acetazolamide 250mg every 12 hours
        - Dexamethasone 8mg initially, then 4mg every 6 hours
        - Stop ascent or descend
        
        **HACE:**
        - Immediate descent 300-1000m
        - Dexamethasone 8mg immediately, then 4mg every 6 hours
        - Oxygen 2-4 L/min
        
        **HAPE:**
        - Immediate descent 300-1000m
        - Nifedipine 30mg sustained release twice daily
        - Oxygen if available
        - Minimize exertion
        """)
    
    # Additional Information
    st.markdown("---")
    st.header("📚 Important Information")
    
    with st.expander("📊 Altitude Illness Statistics"):
        st.write(f"""
        **At {elevation}m elevation:**
        
        - **High Altitude Headache:** Up to 80% of people may experience this
        - **Acute Mountain Sickness:** 
          - 84% of people flying directly to ~3740m develop AMS
          - 50% of trekkers walking to >4000m over 5+ days develop AMS
        - **HACE:** Rare but life-threatening progression of AMS
        - **HAPE:** 
          - 0.2% in general population
          - 4% among those ascending >600m/day
          - 7% of climbers arriving rapidly at ~4500m
        """)
    
    with st.expander("⚠️ When to Descend Immediately"):
        st.write("""
        **Descend immediately if:**
        - Symptoms of HACE (confusion, ataxia, altered consciousness)
        - Symptoms of HAPE (severe breathlessness at rest, crackling in chest)
        - AMS symptoms worsen despite rest and medication
        - You develop symptoms you cannot explain
        - Ataxia test failure (inability to walk heel-to-toe in straight line)
        
        **Remember:** Descent is the most effective treatment for all altitude illnesses
        """)
    
    with st.expander("🏥 Medical Contraindications"):
        st.write("""
        **Consult a doctor before ascending if you have:**
        - Previous history of HACE or HAPE
        - Pulmonary hypertension
        - Heart conditions
        - Sickle cell disease
        - Pregnancy (especially >3000m)
        - Recent surgery
        
        **Acetazolamide contraindications:**
        - Sulfa drug allergy
        - Severe liver or kidney disease
        """)

else:
    # Welcome screen
    st.info("""
    👋 **Welcome to the Altitude Sickness Risk Analyzer!**
    
    This tool helps you:
    - ✅ Check the elevation of your destination
    - ✅ Assess your risk of altitude sickness
    - ✅ Identify symptoms of altitude-related illnesses
    - ✅ Learn prevention strategies
    - ✅ Understand treatment options
    
    **Get started by entering a location in the sidebar** or manually entering an elevation.
    
    **Example locations to try:**
    - Mount Everest Base Camp, Nepal (5,364m)
    - Machu Picchu, Peru (2,430m)
    - Mount Kilimanjaro, Tanzania (5,895m)
    - La Paz, Bolivia (3,650m)
    - Lhasa, Tibet (3,656m)
    """)
    
    st.warning("""
    ⚠️ **Medical Disclaimer:** This tool is for informational purposes only and does not replace 
    professional medical advice. Always consult with a healthcare provider before traveling to 
    high altitudes, especially if you have pre-existing medical conditions.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>Emergency:</strong> If experiencing severe symptoms, descend immediately and seek medical help.</p>
    <p>Data based on clinical guidelines and altitude medicine research.</p>
</div>
""", unsafe_allow_html=True)
