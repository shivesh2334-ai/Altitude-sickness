import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Altitude Sickness Analyzer",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 0rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #ffe6e6;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #ff4444;
    }
    .success-box {
        background-color: #e6ffe6;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #44ff44;
    }
    .info-box {
        background-color: #e6f3ff;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #4444ff;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🏔️ Altitude Sickness Analyzer")
st.markdown("A comprehensive tool for understanding and managing altitude-related health issues")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a section:", [
    "Risk Assessment",
    "Prevention Guidelines",
    "Treatment Guidelines",
    "Additional Information"
])

# Risk Assessment Page
if page == "Risk Assessment":
    st.header("Altitude Sickness Risk Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Personal Information")
        age = st.number_input("Age (years)", min_value=1, max_value=120, value=30)
        weight = st.number_input("Weight (kg)", min_value=20, max_value=200, value=70)
        fitness_level = st.select_slider(
            "Fitness Level",
            options=["Very Poor", "Poor", "Average", "Good", "Excellent"],
            value="Average"
        )
    
    with col2:
        st.subheader("Altitude Information")
        current_altitude = st.number_input("Current Altitude (meters)", min_value=0, max_value=10000, value=0)
        destination_altitude = st.number_input("Destination Altitude (meters)", min_value=0, max_value=10000, value=3000)
        acclimatization_days = st.number_input("Days for Acclimatization", min_value=0, max_value=21, value=3)
    
    st.subheader("Health Conditions")
    col3, col4, col5 = st.columns(3)
    
    with col3:
        asthma = st.checkbox("Asthma or Respiratory Issues")
        hypertension = st.checkbox("Hypertension")
    
    with col4:
        heart_disease = st.checkbox("Heart Disease")
        diabetes = st.checkbox("Diabetes")
    
    with col5:
        pregnancy = st.checkbox("Pregnancy")
        sleep_apnea = st.checkbox("Sleep Apnea")
    
    # Calculate risk score
    if st.button("Calculate Risk Assessment", use_container_width=True):
        risk_score = 0
        risk_factors = []
        
        # Age factor
        if age < 18 or age > 65:
            risk_score += 15
            risk_factors.append("Age outside optimal range")
        
        # Fitness level factor
        fitness_scores = {
            "Very Poor": 30,
            "Poor": 20,
            "Average": 10,
            "Good": 5,
            "Excellent": 0
        }
        risk_score += fitness_scores[fitness_level]
        
        # Altitude gain factor
        altitude_gain = destination_altitude - current_altitude
        if altitude_gain > 3000:
            risk_score += 25
            risk_factors.append("Rapid altitude gain (>3000m)")
        elif altitude_gain > 1500:
            risk_score += 15
            risk_factors.append("Moderate altitude gain (1500-3000m)")
        
        # Acclimatization factor
        if acclimatization_days < 3:
            risk_score += 20
            risk_factors.append("Insufficient acclimatization time")
        
        # Health conditions
        if asthma or heart_disease or sleep_apnea:
            risk_score += 25
            risk_factors.append("Pre-existing respiratory or cardiac conditions")
        
        if hypertension or diabetes:
            risk_score += 15
            risk_factors.append("Metabolic or cardiovascular risk factors")
        
        if pregnancy:
            risk_score += 30
            risk_factors.append("Pregnancy - special considerations needed")
        
        # Cap risk score at 100
        risk_score = min(risk_score, 100)
        
        # Display results
        st.markdown("---")
        st.subheader("Assessment Results")
        
        col6, col7, col8 = st.columns(3)
        
        with col6:
            st.metric("Risk Score", f"{risk_score}/100")
        
        with col7:
            st.metric("Altitude Gain", f"{altitude_gain}m")
        
        with col8:
            st.metric("Acclimatization Days", acclimatization_days)
        
        # Risk level indicator
        if risk_score < 25:
            st.markdown('<div class="success-box"><h3>✅ Low Risk</h3><p>You have a low risk of altitude sickness. Standard precautions recommended.</p></div>', unsafe_allow_html=True)
        elif risk_score < 50:
            st.markdown('<div class="info-box"><h3>⚠️ Moderate Risk</h3><p>You have a moderate risk of altitude sickness. Follow prevention guidelines carefully.</p></div>', unsafe_allow_html=True)
        elif risk_score < 75:
            st.markdown('<div class="warning-box"><h3>⚠️ High Risk</h3><p>You have a high risk of altitude sickness. Consult with a healthcare provider before ascending.</p></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-box"><h3>🚨 Very High Risk</h3><p>You have a very high risk of altitude sickness. Medical consultation strongly recommended. Consider alternative plans.</p></div>', unsafe_allow_html=True)
        
        # Risk factors
        if risk_factors:
            st.subheader("Risk Factors Identified:")
            for i, factor in enumerate(risk_factors, 1):
                st.write(f"{i}. {factor}")
        
        # Oxygen saturation estimation
        st.subheader("Estimated Oxygen Saturation")
        sea_level_spo2 = 98
        estimated_spo2 = sea_level_spo2 - (destination_altitude / 1000) * 3
        estimated_spo2 = max(estimated_spo2, 70)
        
        fig = go.Figure(data=[go.Gauge(
            mode="gauge+number+delta",
            value=estimated_spo2,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "SpO2 (%)"},
            delta={'reference': sea_level_spo2},
            gauge={
                'axis': {'range': [70, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [70, 85], 'color': "red"},
                    {'range': [85, 92], 'color': "orange"},
                    {'range': [92, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        )])
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info(f"Estimated SpO2 at {destination_altitude}m: {estimated_spo2:.1f}% (sea level: {sea_level_spo2}%)")

# Prevention Guidelines Page
elif page == "Prevention Guidelines":
    st.header("Prevention Guidelines")
    
    st.subheader("Pre-Ascent Preparation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Medical Consultation
        - Schedule check-up with your doctor
        - Discuss medications and supplements
        - Get baseline health measurements
        - Consult specialist if you have pre-existing conditions
        
        ### Physical Training
        - Begin 4-6 weeks before trip
        - Focus on cardiovascular fitness
        - Include altitude training if possible
        - Build endurance gradually
        
        ### Medication Prophylaxis
        - **Acetazolamide (Diamox)**: Reduces symptoms by 50%
          - Dosage: 125-250mg twice daily
          - Start 24 hours before ascent
          - Continue during ascent period
        - **Dexamethasone**: For HACE prevention
        - **Nifedipine**: May help prevent HAPE
        """)
    
    with col2:
        st.markdown("""
        ### Equipment and Supplies
        - Portable oxygen concentrator
        - Pulse oximeter
        - First aid kit with altitude sickness medications
        - Insulated water bottles
        - Sun protection (SPF 50+)
        - Warm clothing layers
        
        ### Pre-Trip Health
        - Get sufficient sleep (7-9 hours)
        - Avoid alcohol 48 hours before
        - Stay well hydrated
        - Maintain healthy diet rich in iron
        - Consider iron supplements if anemic
        
        ### Mental Preparation
        - Learn about altitude sickness symptoms
        - Know when to descend
        - Understand rescue procedures
        - Practice meditation/relaxation
        """)
    
    st.subheader("During Ascent Strategy")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        ### Acclimatization Schedule
        - **Climb high, sleep low**: Ascend during day, descend for sleep
        - **Rule of 3000**: Don't go higher than 3000m first day
        - **Daily gain**: Limit to 300-500m above 2500m
        - **Rest days**: One rest day every 3-4 days
        
        ### Hydration
        - Drink 3-4 liters of water daily
        - Avoid caffeine and alcohol
        - Monitor urine color (pale = hydrated)
        - Drink electrolyte-balanced fluids
        """)
    
    with col4:
        st.markdown("""
        ### Nutrition
        - High carbohydrate diet (60% calories)
        - Adequate protein intake (1.2-1.6g/kg)
        - Iron-rich foods
        - Frequent small meals
        - Ginger for nausea relief
        - Garlic and citrus for circulation
        
        ### Activity Management
        - Rest at arrival for first 24 hours
        - Light activities day 2-3
        - Avoid strenuous exercise first week
        - Pace slowly and steadily
        - Use "pressure breathing" technique
        """)
    
    st.subheader("Daily Routine at Altitude")
    
    daily_routine = {
        "Morning": [
            "Check oxygen saturation with pulse oximeter",
            "Drink 500ml water with electrolytes",
            "Light breakfast with carbohydrates",
            "Take prophylactic medications if prescribed",
            "Do gentle stretching exercises"
        ],
        "Midday": [
            "Rest for 2-3 hours",
            "Stay in shade/indoors during peak sun",
            "Hydrate frequently",
            "Light snacks",
            "Assess symptoms"
        ],
        "Evening": [
            "Light physical activity if feeling well",
            "Gradual acclimatization hike",
            "Substantial meal (high carbs, iron)",
            "Evening medications",
            "Relaxation and early sleep"
        ],
        "Night": [
            "Sleep in elevated head position",
            "Keep water nearby",
            "Monitor breathing patterns",
            "Assess dreams and sleep quality"
        ]
    }
    
    for time, activities in daily_routine.items():
        with st.expander(f"⏰ {time} Routine"):
            for activity in activities:
                st.write(f"✓ {activity}")

# Treatment Guidelines Page
elif page == "Treatment Guidelines":
    st.header("Treatment Guidelines")
    
    st.subheader("Symptom Recognition and Management")
    
    symptoms_data = {
        "Symptom": [
            "Headache",
            "Nausea/Vomiting",
            "Fatigue",
            "Dizziness",
            "Sleep Disturbance",
            "Rapid Breathing",
            "Weakness"
        ],
        "Mild AMS": [
            "Mild to moderate",
            "Mild",
            "Noticeable",
            "Mild",
            "Common",
            "Slight",
            "Moderate"
        ],
        "Moderate AMS": [
            "Moderate to severe",
            "Moderate",
            "Severe",
            "Moderate",
            "Significant",
            "Noticeable",
            "Severe"
        ],
        "Severe (HACE)": [
            "Severe, unbearable",
            "Severe",
            "Incapacitating",
            "Severe/Ataxia",
            "Impossible",
            "Rapid",
            "Extreme"
        ]
    }
    
    symptoms_df = pd.DataFrame(symptoms_data)
    st.dataframe(symptoms_df, use_container_width=True)
    
    st.subheader("Treatment Protocol by Severity")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### Mild AMS Treatment
        **Symptoms**: Light headache, nausea
        
        ✓ **Immediate Actions**:
        - Rest and acclimatize
        - Increase hydration
        - Light meals
        - Avoid strenuous activity
        
        ✓ **Medications**:
        - Ibuprofen 400-600mg
        - Paracetamol 500mg
        - Ginger supplements
        
        ✓ **Monitoring**:
        - Check every 4 hours
        - Record symptoms
        - Continue activity carefully
        
        ⏱️ **Duration**: Usually 24-48 hours
        """)
    
    with col2:
        st.markdown("""
        ### Moderate AMS Treatment
        **Symptoms**: Severe headache, vomiting, fatigue
        
        ⚠️ **Immediate Actions**:
        - Stop ascending immediately
        - Rest completely
        - Increase oxygen intake
        - Hydrate aggressively
        
        ✓ **Medications**:
        - Acetazolamide 250mg twice daily
        - Dexamethasone if severe
        - Ibuprofen for pain
        - Anti-nausea medication
        
        ✓ **Monitoring**:
        - Check every 2 hours
        - Use pulse oximeter
        - Watch for progression
        
        ⚠️ **Decision**: Descend if no improvement in 24 hours
        """)
    
    with col3:
        st.markdown("""
        ### Severe AMS (HACE/HAPE)
        **Symptoms**: Ataxia, confusion, fluid in lungs
        
        🚨 **EMERGENCY ACTION**:
        - IMMEDIATE descent required
        - Call emergency services
        - Administer oxygen
        - Position semi-upright
        
        ✓ **Medications**:
        - Dexamethasone 8mg immediately
        - Then 4mg every 6 hours
        - Oxygen as available
        - Nifedipine for HAPE
        
        ✓ **Priority**:
        1. Begin descent NOW
        2. Administer medications
        3. Call for helicopter/rescue
        4. Continuous monitoring
        
        ⏱️ **Timeline**: Descend at least 1000m immediately
        """)
    
    st.subheader("Medication Reference")
    
    medications = {
        "Medication": ["Acetazolamide", "Dexamethasone", "Ibuprofen", "Nifedipine", "Sildenafil", "Ginger"],
        "Purpose": ["Acclimatization aid", "Severe AMS/HACE", "Pain relief", "HAPE prevention", "HAPE treatment", "Nausea relief"],
        "Dosage": ["125-250mg BID", "8mg, then 4mg Q6H", "400-600mg Q6H", "20mg BID", "50mg Q8H", "250-500mg Q6H"],
        "When to Use": ["Start 24hr before", "Severe symptoms only", "Mild symptoms", "High altitude + risk", "Severe HAPE", "Throughout stay"],
        "Side Effects": ["Tingling, altered taste", "Insomnia, agitation", "GI upset", "Headache, flushing", "Headache, flushing", "Mild GI upset"]
    }
    
    med_df = pd.DataFrame(medications)
    st.dataframe(med_df, use_container_width=True)
    
    st.warning("⚠️ Important: Always consult with a healthcare provider before using any medications. Dosages and usage may vary based on individual health conditions.")
    
    st.subheader("Red Flags - Immediate Descent Required")
    
    red_flags = [
        "Severe, persistent headache unresponsive to medication",
        "Vomiting or inability to eat/drink",
        "Difficulty walking in straight line (ataxia)",
        "Confusion or altered mental status",
        "Extreme fatigue or inability to care for self",
        "Rapid breathing at rest (>30 breaths/min)",
        "Persistent blue lips or fingernails",
        "Frothy/bubbly sputum (possible HAPE)",
        "Loss of consciousness",
        "Chest pain or severe breathing difficulty"
    ]
    
    for i, flag in enumerate(red_flags, 1):
        st.error(f"🚨 {i}. {flag}")

# Additional Information Page
else:  # Additional Information
    st.header("Additional Information")
    
    st.subheader("Understanding Altitude Sickness")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### What is Altitude Sickness?
        
        Altitude sickness occurs when your body cannot adapt quickly to lower oxygen levels at high elevations. It's a natural response and can affect anyone, regardless of fitness level.
        
        ### Types of Altitude Sickness
        
        **1. Acute Mountain Sickness (AMS)**
        - Most common form
        - Occurs within 6-12 hours of ascent
        - Usually mild and self-limiting
        - Symptoms: headache, nausea, fatigue
        
        **2. High Altitude Pulmonary Edema (HAPE)**
        - Fluid accumulates in lungs
        - Occurs at 2,500m+ altitude
        - Life-threatening if untreated
        - Symptoms: shortness of breath, cough
        
        **3. High Altitude Cerebral Edema (HACE)**
        - Brain swelling due to fluid
        - Occurs at 2,500m+ altitude
        - Medical emergency
        - Symptoms: confusion, ataxia, headache
        """)
    
    with col2:
        st.markdown("""
        ### Physiological Changes at Altitude
        
        **Oxygen Levels**: Decrease by ~3% per 1000m gain
        - Sea level: ~21% oxygen (100% in air)
        - 3000m: ~12% oxygen
        - 5000m: ~10% oxygen
        
        **Body's Response**:
        - Increased breathing rate
        - Faster heart rate
        - Blood vessel dilation
        - Red blood cell production
        - Fluid shifts and edema
        
        ### Risk Factors
        
        **Individual Factors**:
        - Age (extremes higher risk)
        - Physical fitness
        - Previous altitude sickness
        - Rate of ascent
        - Genetics
        
        **Environmental Factors**:
        - Altitude gain
        - Temperature
        - Humidity
        - Physical activity level
        """)
    
    st.subheader("Altitude Classification")
    
    altitude_classes = {
        "Elevation Range": [
            "0 - 1500m",
            "1500 - 2500m",
            "2500 - 3500m",
            "3500 - 5500m",
            "5500 - 8000m",
            "8000m+"
        ],
        "Classification": [
            "Low Altitude",
            "Moderate Altitude",
            "High Altitude",
            "Very High Altitude",
            "Extreme Altitude",
            "Death Zone"
        ],
        "Risk Level": [
            "Minimal",
            "Low to Moderate",
            "Moderate",
            "High",
            "Very High",
            "Extreme"
        ],
        "Special Considerations": [
            "Standard precautions",
            "Gradual ascent advised",
            "Acclimatization needed",
            "Prophylactic medications",
            "Expert guidance required",
            "Extremely dangerous"
        ]
    }
    
    altitude_df = pd.DataFrame(altitude_classes)
    st.dataframe(altitude_df, use_container_width=True)
    
    st.subheader("Popular High Altitude Destinations")
    
    destinations = {
        "Destination": [
            "Mount Kilimanjaro",
            "Mount Elbrus",
            "Aconcagua",
            "Mount Denali",
            "Mount Everest Base Camp",
            "Mount Everest Summit"
        ],
        "Country": [
            "Tanzania",
            "Russia",
            "Argentina",
            "USA (Alaska)",
            "Nepal",
            "Nepal/Tibet"
        ],
        "Altitude (m)": [
            5895,
            5642,
            6961,
            6190,
            5364,
            8849
        ],
        "Risk Level": [
            "Moderate",
            "Moderate",
            "High",
            "Moderate",
            "Moderate-High",
            "Extreme"
        ],
        "Typical Duration": [
            "5-7 days",
            "3-5 days",
            "14-16 days",
            "7-10 days",
            "12-14 days",
            "45-60 days"
        ]
    }
    
    dest_df = pd.DataFrame(destinations)
    st.dataframe(dest_df, use_container_width=True)
    
    st.subheader("Research and Statistics")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        ### AMS Incidence Rates
        
        - **At 2500m**: 20-50% of unacclimatized people
        - **At 3000m**: 30-60% incidence
        - **At 4000m**: 50-80% incidence
        
        ### Factors Affecting Incidence
        
        - **Rate of ascent**: Fastest factor
        - **Final altitude reached**
        - **Individual susceptibility**: Genetics play major role
        - **Age**: U-shaped curve (children and elderly at higher risk)
        - **Physical fitness**: Minimal protective effect
        - **Previous experience**: Some acclimatization memory
        """)
    
    with col4:
        st.markdown("""
        ### HAPE and HACE Statistics
        
        - **HAPE**: 0.5-3% at 3000m, up to 10% at extreme altitudes
        - **HACE**: 0.1-1% at high altitudes
        - **Mortality rate**: 50% if HACE untreated
        - **Mortality rate**: 50% if HAPE untreated
        
        ### Prevention Effectiveness
        
        - **Slow ascent**: 80% reduction in AMS
        - **Acetazolamide**: 50% reduction in AMS
        - **Combination**: Up to 90% effective
        - **Descent**: Nearly 100% effective if done promptly
        """)
    
    st.subheader("Quick Reference: Descent Decision Tree")
    
    st.info("""
    **If experiencing any of these conditions, DESCEND IMMEDIATELY:**
    
    ↓
    
    **SEVERE SYMPTOMS?** (inability to walk, confusion, severe breathlessness)
    → YES: DESCEND 1000m+ NOW, call rescue
    
    ↓
    
    **MODERATE SYMPTOMS?** (severe headache, vomiting, significant fatigue)
    → YES: Stop ascending, rest 24 hours
    → If no improvement: DESCEND to previous camp
    
    ↓
    
    **MILD SYMPTOMS?** (mild headache, slight nausea, normal function)
    → Continue rest and hydration
    → If improving: Continue cautious ascent
    → If worsening: Consider rest day or descent
    """)
    
    st.subheader("Resources and Further Reading")
    
    resources = """
    ### Medical Organizations
    - **IMAX** (International Society for Mountain Medicine)
    - **ISMM** (Indian Society of Mountain Medicine)
    - **WHO** (World Health Organization)
    
    ### Recommended Books
    - "Medicine for Mountaineering" - James Wilkerson
    - "Altitude Illness: Prevention & Treatment" - Stephen Bezruchka
    - "Going Higher" - Charles Houston
    
    ### Online Resources
    - Medscape Altitude Sickness
    - UpToDate: Mountain Medicine
    - Wilderness Medical Society Guidelines
    
    ### Emergency Contacts
    - Keep emergency numbers accessible
    - Inform someone of your itinerary
    - Register with embassy/consulate
    - Know location of nearest clinic
    """
    
    st.markdown(resources)
    
    st.subheader("Disclaimer")
    
    st.warning("""
    ⚠️ **Medical Disclaimer**
    
    This tool is for educational purposes only and should not replace professional medical advice. 
    Always consult with qualified healthcare providers before undertaking high altitude activities, 
    especially if you have pre-existing health conditions.
    
    The risk assessment provided is approximate and based on general guidelines. Individual risk 
    factors may vary significantly. Your medical history, current health status, and specific 
    environmental conditions should be evaluated by a healthcare professional.
    
    In case of medical emergency at altitude, seek professional medical help immediately.
    """)
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.metric("Tool Version", "1.0.0")
    
    with col6:
        st.metric("Last Updated", "December 2025")
