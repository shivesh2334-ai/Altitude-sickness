import streamlit as st
import requests

# --- Helper function to get elevation from location using Open-Elevation API ---
def get_elevation_from_location(location: str):
    try:
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={location}"
        response = requests.get(url).json()
        if not response:
            return None
        lat, lon = response[0]["lat"], response[0]["lon"]
        elev_url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
        elev_response = requests.get(elev_url).json()
        elevation = elev_response["results"][0]["elevation"]
        return elevation
    except Exception:
        return None

# --- Risk assessment based on WMS 2024 guidelines ---
def assess_risk(elevation, ascent_rate=500, history="None"):
    if elevation < 2800 and history == "None":
        return "Low Risk"
    elif 2800 <= elevation <= 3500 or history == "Moderate AMS":
        return "Moderate Risk"
    else:
        return "High Risk"

# --- Recommendations based on guidelines ---
def get_recommendations(elevation, risk_level):
    recs = []
    if elevation >= 2500:
        recs.append("⚠️ Risk of Acute Altitude Illness begins above ~2500m.")
    if risk_level == "Low Risk":
        recs.append("✅ Gradual ascent is sufficient. No routine medication needed.")
    elif risk_level == "Moderate Risk":
        recs.append("💊 Consider acetazolamide prophylaxis (125 mg every 12h).")
        recs.append("🛌 Incorporate rest days every 3–4 days above 3000m.")
    else:
        recs.append("🚨 High risk: Strongly recommend acetazolamide prophylaxis.")
        recs.append("📉 Avoid rapid ascent >500m sleeping elevation per day.")
        recs.append("💊 Carry dexamethasone for emergency use.")
    return recs

# --- Streamlit UI ---
st.title("🏔️ Altitude Illness Risk & Management (WMS 2024)")
st.write("Enter a **location** or **height in meters** to assess altitude illness risk.")

option = st.radio("Choose input type:", ["Location", "Height (meters)"])

if option == "Location":
    location = st.text_input("Enter location (e.g., Leh, India)")
    if location:
        elevation = get_elevation_from_location(location)
        if elevation:
            st.success(f"Elevation of {location}: {elevation} meters")
            risk = assess_risk(elevation)
            st.subheader(f"Risk Level: {risk}")
            for r in get_recommendations(elevation, risk):
                st.write(r)
        else:
            st.error("Could not fetch elevation. Try another location.")
else:
    height = st.number_input("Enter height in meters", min_value=0, step=100)
    if height > 0:
        risk = assess_risk(height)
        st.success(f"Entered elevation: {height} meters")
        st.subheader(f"Risk Level: {risk}")
        for r in get_recommendations(height, risk):
            st.write(r)

st.markdown("---")
st.caption("Based on Wilderness Medical Society Clinical Practice Guidelines (2024 Update).")
