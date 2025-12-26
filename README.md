# 🏔️ Altitude Sickness Risk Analyzer

A comprehensive web application to help travelers assess their risk of altitude sickness, identify symptoms, and learn about prevention and treatment options.

## Features

### 📍 Location-Based Analysis
- Search any location worldwide to get elevation data
- Automatic retrieval of elevation using OpenStreetMap and Open-Elevation APIs
- Manual elevation input option

### 🎯 Risk Assessment
- Altitude categorization (Sea Level to Death Zone)
- Expected oxygen saturation levels
- Personal risk factor evaluation
- Customized recommendations based on your profile

### 🩺 Symptoms Checker
- Interactive checklist for altitude sickness symptoms
- Automatic detection of:
  - High Altitude Headache
  - Acute Mountain Sickness (AMS)
  - High Altitude Cerebral Edema (HACE)
  - High Altitude Pulmonary Edema (HAPE)
- Severity assessment using Lake Louise Score

### 🛡️ Prevention Strategies
- Evidence-based ascent guidelines
- Pharmacological prevention options (Acetazolamide, Dexamethasone)
- Hydration and acclimatization recommendations

### 💊 Treatment Options
- Symptom-specific treatment protocols
- Emergency response guidelines
- Medication dosing information

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/altitude-sickness-analyzer.git
cd altitude-sickness-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

4. Open your browser and navigate to:
```
http://localhost:8501
```

## Usage

### Getting Started
1. **Enter a location** in the sidebar (e.g., "Mount Kilimanjaro", "Machu Picchu")
2. Click **"Analyze Location"** to fetch elevation data
3. Review the altitude category and risk assessment

### Personal Risk Assessment
- Check boxes for relevant risk factors:
  - Rapid ascent planning
  - Previous altitude sickness history
  - Strenuous exercise plans
  - Known susceptibility

### Symptoms Checker
- Select any symptoms you're experiencing
- Get immediate feedback on potential conditions
- Receive appropriate treatment recommendations

### Example Locations
- Mount Everest Base Camp, Nepal (5,364m)
- Mount Kilimanjaro, Tanzania (5,895m)
- Machu Picchu, Peru (2,430m)
- La Paz, Bolivia (3,650m)
- Lhasa, Tibet (3,656m)

## Altitude Categories

| Category | Elevation | Risk Level | Description |
|----------|-----------|------------|-------------|
| Sea Level - Low | <1,500m | Minimal | No altitude effects |
| Intermediate | 1,500-2,500m | Low | Detectable changes, rare illness |
| High | 2,500-3,500m | Moderate | Common illness with rapid ascent |
| Very High | 3,500-5,800m | High | Common illness, O₂ sat <90% |
| Extreme | 5,800-8,000m | Very High | Marked hypoxemia, no permanent survival |
| Death Zone | >8,000m | Extreme | Supplementary oxygen required |

## Medical Information

### Conditions Covered
- **High Altitude Headache (HAH)**: Headache developing within 24 hours of ascent
- **Acute Mountain Sickness (AMS)**: Headache plus nausea, fatigue, dizziness, or sleep difficulty
- **High Altitude Cerebral Edema (HACE)**: Life-threatening brain swelling
- **High Altitude Pulmonary Edema (HAPE)**: Life-threatening fluid in lungs

### Key Statistics
- 80% of people experience high altitude headache above 2,500m
- 50% of trekkers develop AMS when ascending >4,000m over 5+ days
- HAPE occurs in 0.2-7% depending on ascent rate

## APIs Used

- **OpenStreetMap Nominatim**: Geocoding and location search
- **Open-Elevation API**: Elevation data retrieval

## Medical Disclaimer

⚠️ **Important:** This application is for informational and educational purposes only. It does not replace professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider before traveling to high altitudes, especially if you have pre-existing medical conditions.

## Emergency Guidelines

**Seek immediate medical attention if experiencing:**
- Mental confusion or altered consciousness
- Loss of coordination (ataxia)
- Severe breathlessness at rest
- Crackling sounds in chest
- Blood-tinged sputum

**When in doubt, descend immediately.** Descent is the most effective treatment for all altitude illnesses.

## Data Sources

This application is based on clinical guidelines and research from:
- International Headache Society definitions
- Wilderness Medical Society recommendations
- High Altitude Medicine Handbook
- Peer-reviewed altitude medicine research

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Elevation data from [Open-Elevation](https://open-elevation.com/)
- Geocoding from [OpenStreetMap Nominatim](https://nominatim.openstreetmap.org/)
- Based on altitude medicine clinical research and guidelines

## Support

If you encounter any issues or have questions:
1. Check the GitHub Issues page
2. Consult the documentation
3. Contact your healthcare provider for medical questions

## Version History

- **v1.0.0** (2024): Initial release
  - Location-based elevation lookup
  - Risk assessment tools
  - Symptoms checker
  - Prevention and treatment guidelines

---

**Remember:** When experiencing altitude sickness symptoms, the most effective treatment is always descent. Stay safe and enjoy your high-altitude adventures! 🏔️
