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
    .guideline-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🏔️ Altitude Sickness Risk Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666;">Based on 2024 Wilderness Medical Society Clinical Practice Guidelines</p>', unsafe_allow_html=True)

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
            'category': 'Intermediate Altitude (1,500-2,500m)',
            'risk': 'Low',
            'description': 'Physiological changes detectable. Arterial oxygen saturation >90%. Altitude illness rare but possible with rapid ascent, exercise, and susceptible individuals.',
            'oxygen_sat': '>90%',
            'color': 'low'
        }
    elif 2500 <= elevation < 3500:
        return {
            'category': 'High Altitude (2,500-3,500m)',
            'risk': 'Moderate',
            'description': 'Altitude illness common when individuals ascend rapidly. Gradual ascent and prophylaxis recommended.',
            'oxygen_sat': '85-90%',
            'color': 'medium'
        }
    elif 3500 <= elevation < 5800:
        return {
            'category': 'Very High Altitude (3,500-5,800m)',
            'risk': 'High',
            'description': 'Altitude illness common. Marked hypoxemia during exercise. Maximum altitude of permanent habitation.',
            'oxygen_sat': '<90%',
            'color': 'high'
        }
    elif 5800 <= elevation < 8000:
        return {
            'category': 'Extreme Altitude (5,800-8,000m)',
            'risk': 'Very High',
            'description': 'Marked hypoxemia at rest. Progressive deterioration despite maximal acclimatization. Permanent survival not possible.',
            'oxygen_sat': '<80%',
            'color': 'high'
        }
    else:
        return {
            'category': 'Death Zone (>8,000m)',
            'risk': 'Extreme',
            'description': 'Prolonged acclimatization (>6 weeks) essential. Most mountaineers require supplementary oxygen. Arterial oxygen saturations ~55%. Rapid deterioration inevitable.',
            'oxygen_sat': '~55%',
            'color': 'high'
        }

# Function to assess risk based on WMS 2024 guidelines
def assess_risk_profile(elevation, previous_ams, previous_hace, previous_hape, rapid_ascent, 
                       physical_activity, no_acclimatization):
    """Assess risk based on WMS 2024 Figure 1 criteria"""
    risk_level = "Low"
    risk_factors = []
    
    # History-based risk
    if previous_hace or previous_hape:
        risk_level = "High"
        if previous_hace:
            risk_factors.append("Previous HACE episode - high risk for recurrence")
        if previous_hape:
            risk_factors.append("Previous HAPE episode - high risk for recurrence")
    elif previous_ams:
        if elevation >= 3500:
            risk_level = "High"
            risk_factors.append("Previous AMS with rapid ascent to very high altitude")
        else:
            risk_level = "Moderate"
            risk_factors.append("Previous AMS history increases risk")
    
    # Ascent profile risk
    if elevation >= 3500:
        if rapid_ascent or no_acclimatization:
            risk_level = "High"
            risk_factors.append("Rapid ascent to very high altitude (>3,500m)")
    elif elevation >= 2800:
        if rapid_ascent:
            if risk_level != "High":
                risk_level = "Moderate"
            risk_factors.append("Rapid ascent to high altitude without acclimatization")
    
    # Physical activity risk
    if physical_activity and elevation >= 2500:
        risk_factors.append("Strenuous physical activity increases risk")
        
    return risk_level, risk_factors

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
    if elevation >= 2500:
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
        
        risk_level, risk_factors = assess_risk_profile(
            elevation, previous_ams, previous_hace, previous_hape,
            rapid_ascent, physical_activity, no_acclimatization
        )
        
        # Display risk assessment
        if risk_level == "High":
            st.error(f"🚨 **HIGH RISK** - Prophylactic medication strongly recommended")
        elif risk_level == "Moderate":
            st.warning(f"⚠️ **MODERATE RISK** - Prophylactic medication should be considered")
        else:
            st.success(f"✅ **LOW RISK** - Gradual ascent alone may be sufficient")
        
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
    
    # Calculate Lake Louise Score for AMS
    lake_louise_score = 0
    if headache:
        lake_louise_score += 1
    if nausea or anorexia:
        lake_louise_score += 1
    if fatigue:
        lake_louise_score += 1
    if dizziness:
        lake_louise_score += 1
    
    # Symptom analysis
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
        if lake_louise_score >= 6:
            st.warning("⚠️ **SEVERE Acute Mountain Sickness (AMS)** - Lake Louise Score: 6-12")
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
            st.info("ℹ️ **MILD-MODERATE Acute Mountain Sickness (AMS)** - Lake Louise Score: 3-5")
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
    
    # Prevention Guidelines
    st.markdown("---")
    st.header("🛡️ Prevention Recommendations")
    st.markdown("*Based on WMS 2024 Clinical Practice Guidelines*")
    
    if elevation >= 2500:
        st.markdown("""
        <div class="guideline-box">
            <h3>📋 Gradual Ascent Protocol (STRONG RECOMMENDATION)</h3>
            <ul>
                <li><strong>Above 3,000m:</strong> Limit sleeping elevation increase to <500m per day</li>
                <li><strong>Rest days:</strong> Include a rest day every 3-4 days (no increase in sleeping elevation)</li>
                <li><strong>"Climb high, sleep low":</strong> Day altitude can exceed sleeping altitude</li>
                <li><strong>Staged ascent:</strong> Consider spending 2+ days at 2,500-3,000m before higher ascent</li>
                <li><strong>Note:</strong> Sleeping elevation is more important than daytime elevation reached</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("💊 Pharmacological Prophylaxis")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "Acetazolamide (Primary)", 
            "Dexamethasone (Alternative)", 
            "Ibuprofen", 
            "HAPE Prevention"
        ])
        
        with tab1:
            st.markdown("""
            **Acetazolamide (Diamox) - STRONG RECOMMENDATION**
            
            **Indications:**
            - Moderate to high-risk ascent profiles
            - History of AMS
            - Rapid ascent above 2,500m
            
            **Dosing:**
            - **Adults:** 125mg every 12 hours (standard dose)
            - **High-risk situations:** 250mg every 12 hours up to 5,000m
            - **Children:** 1.25 mg/kg every 12 hours (max 125mg/dose)
            - **Start:** Night before ascent (or day of ascent if necessary)
            - **Duration:** Continue for 2 days at target elevation (or 2-4 days if rapid ascent)
            
            **Evidence:** HIGH-QUALITY EVIDENCE
            
            **Contraindications:**
            - Prior anaphylaxis to sulfonamides
            - Stevens-Johnson syndrome history
            - Note: Low risk of allergic reaction in sulfa allergy patients
            
            **Side Effects:**
            - Tingling in fingers/toes (common, harmless)
            - Increased urination
            - Altered taste (carbonated beverages taste flat)
            - Minimal effect on exercise performance at recommended doses
            """)
        
        with tab2:
            st.markdown("""
            **Dexamethasone - STRONG RECOMMENDATION (Alternative)**
            
            **Indications:**
            - Alternative to acetazolamide in adults
            - Acetazolamide contraindicated or not tolerated
            - Very high-risk situations (military/rescue personnel airlifted >3,500m)
            
            **Dosing:**
            - **Standard:** 2mg every 6 hours OR 4mg every 12 hours
            - **High-risk:** 4mg every 6 hours (limited circumstances only)
            - **Duration:** Up to 5-7 days (tapering not required for short duration)
            - **Pediatrics:** NOT recommended for prophylaxis in children
            
            **Evidence:** HIGH-QUALITY EVIDENCE
            
            **Important Notes:**
            - Does NOT facilitate acclimatization (only masks symptoms)
            - Risk of adrenal suppression with prolonged use
            - Not for routine use in children
            
            **Concurrent Use:**
            - Acetazolamide + Dexamethasone: Only in very high-risk situations
            - Limited evidence, not recommended for routine use
            """)
        
        with tab3:
            st.markdown("""
            **Ibuprofen - WEAK RECOMMENDATION (Second-line)**
            
            **Indications:**
            - Cannot or unwilling to take acetazolamide or dexamethasone
            - Allergies or intolerance to primary medications
            
            **Dosing:**
            - **Adults:** 600mg every 8 hours
            - Start before ascent
            - Short-term use only (24-48 hours studied)
            
            **Evidence:** MODERATE-QUALITY EVIDENCE
            - Less effective than acetazolamide
            - Equal efficacy to acetazolamide for high altitude headache prevention
            - Safety concerns with prolonged use (GI bleeding, renal dysfunction)
            
            **Note:** Acetaminophen NOT recommended for AMS prevention
            """)
        
        with tab4:
            st.markdown("""
            **HAPE Prevention - For HAPE-Susceptible Individuals Only**
            
            **Nifedipine (STRONG RECOMMENDATION - First Choice):**
            - **Dose:** 30mg extended release every 12 hours
            - **Start:** Day before ascent
            - **Duration:** 4 days at highest elevation (up to 7 days if rapid ascent)
            - **Evidence:** MODERATE-QUALITY
            - **Risk:** May cause hypotension (uncommon with ER version)
            
            **Tadalafil (STRONG RECOMMENDATION - Alternative):**
            - **Dose:** 10mg every 12 hours
            - **Use:** When nifedipine contraindicated
            - **Evidence:** LOW-QUALITY
            - **Note:** Limited clinical experience
            
            **Dexamethasone (STRONG RECOMMENDATION - Second Alternative):**
            - **Dose:** 8mg every 12 hours
            - **Use:** When nifedipine and tadalafil contraindicated
            - **Evidence:** LOW-QUALITY
            - **Note:** Mechanism unclear, limited experience
            
            **Salmeterol (NOT RECOMMENDED):**
            - High doses (125μg twice daily) showed benefit
            - Significant side effects (tremor, tachycardia)
            - Limited clinical experience
            
            **Acetazolamide:**
            - NOT recommended for HAPE prevention
            - May be considered for re-entry HAPE
            """)
    
    # Treatment Guidelines
    st.markdown("---")
    st.header("💊 Treatment Guidelines (WMS 2024)")
    
    treatment_tab1, treatment_tab2, treatment_tab3 = st.tabs(["AMS Treatment", "HACE Treatment", "HAPE Treatment"])
    
    with treatment_tab1:
        st.markdown("""
        ### Acute Mountain Sickness (AMS) Treatment
        
        **Mild-Moderate AMS (Lake Louise Score 3-5):**
        - **STOP ASCENT** - remain at current altitude
        - Monitor closely for progression
        - **Symptom relief:**
          - Ibuprofen 600mg every 8 hours (STRONG RECOMMENDATION)
          - Acetaminophen 1000mg every 8 hours (alternative)
        - **Adequate hydration** (not overhydration)
        - **Rest** for 1-3 days until symptoms resolve
        - **Acetazolamide** 250mg every 12 hours may be considered (STRONG RECOMMENDATION)
        - **Descend** if symptoms worsen or fail to improve
        
        **Severe AMS (Lake Louise Score 6-12):**
        - **CEASE ASCENDING** immediately
        - **DESCEND** to lower elevation
        - **Dexamethasone** 4mg every 6 hours (STRONG RECOMMENDATION)
        - **Acetazolamide** 250mg every 12 hours (can be used as adjunct)
        - **Supplemental oxygen** if available (target SpO₂ >90%)
        - **Portable hyperbaric chamber** if descent not feasible
        
        **Return to Ascent:**
        - Only after complete symptom resolution
        - Use acetazolamide prophylaxis for reascent
        - Slower ascent rate than previous attempt
        """)
    
    with treatment_tab2:
        st.markdown("""
        ### High Altitude Cerebral Edema (HACE) Treatment
        
        **HACE is a MEDICAL EMERGENCY**
        
        **Immediate Treatment (STRONG RECOMMENDATIONS):**
        1. **DESCEND IMMEDIATELY** 300-1,000m
           - Do NOT descend alone
           - Mechanical transport preferred (minimize exertion)
           - Continue descent until symptoms resolve
        
        2. **Dexamethasone** (PRIMARY TREATMENT)
           - **Adults:** 8mg immediately, then 4mg every 6 hours
           - **Children:** 0.15 mg/kg/dose every 6 hours (max 4mg/dose)
           - Continue during and after descent until symptoms resolve
        
        3. **Supplemental Oxygen**
           - 2-4 L/min or higher to achieve SpO₂ >90%
           - Continue during descent
        
        4. **Portable Hyperbaric Chamber**
           - Use if descent impossible or delayed
           - Does not replace descent when feasible
        
        5. **Acetazolamide**
           - Can be used as adjunct to dexamethasone
           - 250mg every 12 hours
        
        **Clinical Signs:**
        - Ataxia (heel-to-toe walking test failure)
        - Altered mental status, confusion
        - Severe lassitude, inability to self-care
        - Progression to coma if untreated
        
        **NO REASCENT** during same trip after HACE
        """)
    
    with treatment_tab3:
        st.markdown("""
        ### High Altitude Pulmonary Edema (HAPE) Treatment
        
        **HAPE is a MEDICAL EMERGENCY**
        
        **Immediate Treatment (STRONG RECOMMENDATIONS):**
        
        1. **DESCEND IMMEDIATELY**
           - Descend at least 1,000m or until symptoms resolve
           - **MINIMIZE EXERTION** (use mechanical transport if possible)
           - Exertion worsens pulmonary edema
        
        2. **Supplemental Oxygen** (First-line)
           - Target SpO₂ >90%
           - Suitable alternative to immediate descent in monitored settings
           - Continue until stable off oxygen
        
        3. **Nifedipine** (Use ONLY if oxygen unavailable)
           - **Dose:** 30mg extended release every 12 hours
           - Do NOT use short-acting version (hypotension risk)
           - May not provide additional benefit if oxygen available
           - Use only when descent/oxygen impossible or delayed
        
        4. **Portable Hyperbaric Chamber**
           - Use if descent delayed and oxygen unavailable
           - Does not replace descent when feasible
        
        5. **Alternative Medications (if nifedipine unavailable):**
           - **Tadalafil** 10mg every 12 hours OR
           - **Sildenafil** 50mg every 8 hours
           - **WEAK RECOMMENDATION** - limited evidence
           - Do NOT combine multiple vasodilators (hypotension risk)
        
        6. **CPAP/EPAP** (Adjunctive therapy)
           - May improve oxygenation
           - Use as adjunct to oxygen in monitored settings
           - Requires patient cooperation and normal mental status
        
        **DO NOT USE:**
        - ❌ Diuretics (may worsen intravascular depletion)
        - ❌ Acetazolamide (no benefit, may cause hypotension)
        - ❌ Beta-agonists (insufficient evidence)
        
        **Concurrent HAPE and HACE:**
        - Add **Dexamethasone** to HAPE treatment
        - Prefer phosphodiesterase inhibitors over nifedipine (less hypotension)
        
        **Reascent:**
        - Only after complete resolution off oxygen
        - Use nifedipine prophylaxis for reascent
        - Very gradual ascent rate
        """)
    
    # Additional Information
    st.markdown("---")
    st.header("📚 Additional Clinical Information")
    
    with st.expander("🔬 What NOT to Use (WMS 2024)"):
        st.markdown("""
        **NOT RECOMMENDED for AMS/HACE Prevention:**
        - ❌ **Inhaled Budesonide** - Multiple high-quality studies show no benefit
        - ❌ **Ginkgo biloba** - Inconsistent evidence, not standardized
        - ❌ **Acetaminophen** - Not effective for prevention
        - ❌ **Hypoxic tents** - Insufficient evidence for benefit
        - ❌ **Coca leaves/tea** - Not properly studied
        - ❌ **Forced hydration** - No benefit, may cause hyponatremia
        - ❌ **Oxygen bars** - Too brief to provide benefit
        - ❌ **Over-the-counter supplements/patches** - No evidence
        
        **NOT RECOMMENDED for HAPE Prevention:**
        - ❌ **Acetazolamide** - No benefit for HAPE (use for AMS only)
        - ❌ **Salmeterol** - High-dose side effects, limited experience
        
        **NOT RECOMMENDED for Treatment:**
        - ❌ **Diuretics for HAPE** - May worsen condition
        - ❌ **Acetazolamide for HAPE** - No benefit
        """)
    
    with st.expander("⚕️ When to Seek Medical Care"):
        st.markdown("""
        **Immediate Medical Evacuation Required:**
        - Loss of coordination (ataxia)
        - Altered mental status or confusion
        - Severe shortness of breath at rest
        - Cough with pink or frothy sputum
        - Inability to walk or care for oneself
        - Blue discoloration of lips/fingertips
        - Symptoms worsening despite treatment
        
        **Seek Medical Evaluation:**
        - AMS symptoms not improving after 1-3 days of rest
        - Unable to tolerate oral medications due to vomiting
        - Uncertainty about diagnosis
        - Need for oxygen or medications not available
        - Any concerning symptoms
        
        **Differential Diagnosis to Consider:**
        - Carbon monoxide poisoning (similar symptoms to AMS)
        - Dehydration (mimics AMS)
        - Hypothermia (can present with ataxia)
        - Hypoglycemia (altered mental status)
        - Hyponatremia (from overhydration)
        - Pneumonia (respiratory symptoms)
        - Viral upper respiratory infection
        - Pulmonary embolism
        - Myocardial infarction
        - Exhaustion (severe fatigue)
        """)
    
    with st.expander("🏥 Post-COVID-19 High Altitude Travel"):
        st.markdown("""
        **WMS 2024 Recommendations for COVID-19 Survivors:**
        
        **Most people recover fully** with no lasting effects on exercise capacity or gas exchange.
        
        **Pre-Travel Evaluation Recommended for:**
        - Persistent symptoms >2 weeks after positive test or hospital discharge
        - Required intensive care unit admission
        - History of COVID-related myocarditis
        - History of COVID-related thromboembolic disease
        
        **Recommended Testing:**
        - Pulse oximetry (rest and with activity)
        - Pulmonary function testing
        - Chest X-ray
        - Electrocardiography (ECG)
        - B-type natriuretic peptide (BNP)
        - High-sensitivity troponin
        - Echocardiography
        
        **Additional Testing if Indicated:**
        - Chest CT scan (if hypoxemia and abnormal CXR)
        - Cardiac MRI (if elevated troponin or abnormal echo)
        - Cardiopulmonary exercise testing (marked exercise limitation or heavy exertion planned)
        
        **Action:** Modify or defer travel plans based on results
        """)
    
    with st.expander("👶 Pediatric Considerations"):
        st.markdown("""
        **Medication Dosing for Children:**
        
        **Acetazolamide (Prevention):**
        - 1.25 mg/kg every 12 hours
        - Maximum: 125mg per dose
        - STRONG RECOMMENDATION for AMS prevention
        
        **Acetazolamide (Treatment):**
        - 2.5 mg/kg every 12 hours
        - Maximum: 250mg per dose
        
        **Dexamethasone (Treatment only):**
        - 0.15 mg/kg every 6 hours
        - Maximum: 4mg per dose
        - NOT recommended for prophylaxis in children
        
        **Special Considerations:**
        - Children can develop altitude illness at same elevations as adults
        - May have difficulty communicating symptoms
        - Symptoms may be misattributed to other causes
        - Same ascent guidelines apply
        - Acetazolamide is safe and effective for prevention
        - Gradual ascent preferred over medication when possible
        """)
    
    with st.expander("📊 Lake Louise Scoring System (Updated 2018)"):
        st.markdown("""
        **Self-Report AMS Score:**
        
        Rate each symptom from 0-3:
        - **0** = Not present
        - **1** = Mild
        - **2** = Moderate  
        - **3** = Severe
        
        **Symptoms:**
        1. Headache
        2. Gastrointestinal (nausea, vomiting, anorexia)
        3. Fatigue/weakness
        4. Dizziness/lightheadedness
        
        **Total Score Interpretation:**
        - **0-2:** No AMS
        - **3-5:** Mild-Moderate AMS
        - **6-12:** Severe AMS
        
        **Note:** 
        - Headache is emphasized as cardinal feature
        - Sleep disturbance de-emphasized in diagnosis
        - Functional status important: if you feel ill and must reduce activities = likely AMS
        """)
    
    with st.expander("💡 Practical Tips & Best Practices"):
        st.markdown("""
        **Ascent Planning:**
        - Plan itinerary with gradual ascent in mind
        - Build in flexibility for extra rest days if needed
        - "Climb high, sleep low" strategy when possible
        - Avoid alcohol first 48 hours at new altitude
        - Avoid sleeping pills (suppress breathing)
        
        **Hydration:**
        - Maintain normal hydration (not overhydration)
        - Aim for clear to pale yellow urine
        - Don't force excessive fluids (hyponatremia risk)
        
        **Physical Activity:**
        - Reduce exercise intensity first 1-2 days
        - Listen to your body
        - Don't "push through" worsening symptoms
        
        **Medication Timing:**
        - Start acetazolamide night before ascent
        - Continue 2 days at highest elevation
        - Can stop when descent initiated (if no symptoms)
        
        **Recognition:**
        - Most symptoms appear 6-12 hours after ascent
        - Peak symptoms typically 1-2 days after arrival
        - Improvement expected by day 3 with acclimatization
        - Worsening symptoms = descend
        
        **Group Travel:**
        - Communicate symptoms openly
        - Don't pressure others to continue if symptomatic
        - Buddy system for monitoring
        - Leadership should prioritize safety over summit goals
        """)
    
    with st.expander("🔍 Evidence Quality & Recommendation Strength"):
        st.markdown("""
        **WMS 2024 uses CHEST grading system:**
        
        **Recommendation Strength:**
        - **Strong:** "We recommend..." - Benefits clearly outweigh risks
        - **Weak:** "We suggest..." - Benefits likely outweigh risks but less certain
        
        **Evidence Quality:**
        - **High:** Further research unlikely to change confidence in estimate
        - **Moderate:** Further research may impact confidence
        - **Low:** Further research very likely to impact confidence
        
        **Key Strong Recommendations (High-Quality Evidence):**
        - Gradual ascent for prevention
        - Acetazolamide for AMS prevention (moderate-high risk)
        - Dexamethasone for AMS prevention (alternative)
        - Descent for any altitude illness
        - Supplemental oxygen for AMS/HACE/HAPE
        - Dexamethasone for AMS/HACE treatment
        - Nifedipine for HAPE prevention (susceptible individuals)
        
        **Areas with Limited Evidence:**
        - Optimal preacclimatization protocols
        - Pediatric medication dosing
        - Reascent after HACE/HAPE
        - Many alternative treatments
        """)

else:
    # Welcome screen
    st.info("""
    👋 **Welcome to the Altitude Sickness Risk Analyzer!**
    
    This tool is based on the **2024 Wilderness Medical Society Clinical Practice Guidelines** 
    for the Prevention, Diagnosis, and Treatment of Acute Altitude Illness.
    
    **Features:**
    - ✅ Evidence-based risk assessment
    - ✅ Location elevation lookup worldwide
    - ✅ Symptom checker with Lake Louise scoring
    - ✅ Prevention strategies (Strong recommendations)
    - ✅ Treatment protocols for AMS, HACE, and HAPE
    - ✅ Medication dosing (adults and children)
    - ✅ Updated 2024 guidelines
    
    **Get started by entering a location in the sidebar** or manually entering an elevation.
    
    **Popular destinations to try:**
    - Mount Everest Base Camp, Nepal (5,364m)
    - Machu Picchu, Peru (2,430m)  
    - Mount Kilimanjaro, Tanzania (5,895m)
    - La Paz, Bolivia (3,650m)
    - Lhasa, Tibet (3,656m)
    - Cusco, Peru (3,400m)
    - Quito, Ecuador (2,850m)
    """)
    
    st.markdown("""
    <div class="guideline-box">
        <h3>📋 Key Altitude Thresholds</h3>
        <ul>
            <li><strong>2,500m:</strong> Threshold for altitude illness risk</li>
            <li><strong>3,000m:</strong> Begin strict ascent rate limits (≤500m/day)</li>
            <li><strong>3,500m:</strong> Very high altitude - increased risk</li>
            <li><strong>5,800m:</strong> Extreme altitude - permanent habitation limit</li>
            <li><strong>8,000m:</strong> "Death zone" - supplemental oxygen required</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.warning("""
    ⚠️ **Medical Disclaimer:** This tool provides information based on current medical guidelines 
    but does not replace professional medical advice, diagnosis, or treatment. Always consult with 
    a qualified healthcare provider before traveling to high altitudes, especially if you have 
    pre-existing medical conditions, are pregnant, or have had previous altitude illness.
    
    **In case of emergency altitude illness:** Descend immediately and seek medical attention.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p><strong>⚠️ EMERGENCY:</strong> If experiencing severe symptoms (confusion, ataxia, severe breathlessness), 
    <strong>DESCEND IMMEDIATELY</strong> and seek medical help.</p>
    <p><strong>Guidelines Source:</strong> Wilderness Medical Society Clinical Practice Guidelines 2024</p>
    <p><strong>Authors:</strong> Luks AM, Beidleman BA, Freer L, Grissom CK, Keyes LE, McIntosh SE, et al.</p>
    <p><strong>Published:</strong> Wilderness & Environmental Medicine 2024, Vol. 35(1S)</p>
    <p style='margin-top: 1rem; font-size: 0.9em;'>
        <strong>Data Sources:</strong> OpenStreetMap Nominatim (geocoding) • Open-Elevation API (elevation data)
    </p>
</div>
""", unsafe_allow_html=True)