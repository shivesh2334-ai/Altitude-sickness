from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Altitude sickness information database
ALTITUDE_INFO = {
    'acute_mountain_sickness': {
        'name': 'Acute Mountain Sickness (AMS)',
        'description': 'Acute Mountain Sickness is a pathological effect of high altitude on humans.',
        'symptoms': [
            'Headache',
            'Fatigue and weakness',
            'Dizziness',
            'Nausea and vomiting',
            'Shortness of breath',
            'Difficulty sleeping',
            'Loss of appetite'
        ],
        'affected_altitude': '2,500 meters (8,200 feet) and above',
        'onset': 'Usually 6-10 hours after reaching high altitude',
        'risk_factors': [
            'Rapid ascent',
            'Individual susceptibility',
            'Previous history of AMS',
            'Strenuous physical activity',
            'Dehydration',
            'Alcohol consumption'
        ],
        'prevention_guidelines': [
            'Ascend gradually - allow 2-3 days for acclimatization at intermediate altitudes',
            'Stay hydrated - drink 3-4 liters of water daily',
            'Avoid alcohol and smoking for at least 48 hours',
            'Eat light, carbohydrate-rich foods',
            'Get adequate rest and sleep',
            'Consider prophylactic medication (Acetazolamide) if rapidly ascending',
            'Avoid overexertion on the first day at altitude',
            'Monitor yourself for symptoms regularly'
        ],
        'treatment_guidelines': [
            'Descend to lower altitude immediately if symptoms worsen',
            'Rest at current altitude for acclimatization (usually 24-48 hours)',
            'Take over-the-counter pain relievers for headache (ibuprofen or acetaminophen)',
            'Stay hydrated with electrolyte solutions',
            'Use prescribed medications (Acetazolamide, Dexamethasone) as directed',
            'Increase oxygen intake or use supplemental oxygen if available',
            'Seek medical attention if symptoms persist beyond 48 hours',
            'Do not continue ascending until symptoms resolve'
        ],
        'additional_info': 'AMS typically resolves within 1-3 days with proper acclimatization. Most people experience only mild symptoms that do not require medical intervention.'
    },
    'high_altitude_cerebral_edema': {
        'name': 'High Altitude Cerebral Edema (HACE)',
        'description': 'A severe form of altitude sickness characterized by brain swelling and fluid accumulation.',
        'symptoms': [
            'Severe headache',
            'Ataxia (loss of coordination)',
            'Confusion and disorientation',
            'Difficulty walking',
            'Altered consciousness',
            'Hallucinations',
            'Coma (in severe cases)'
        ],
        'affected_altitude': '3,500 meters (11,500 feet) and above',
        'onset': 'Can develop within 1-3 days of rapid ascent',
        'risk_factors': [
            'Unacclimatized rapid ascent',
            'Untreated severe AMS',
            'High altitude exposure for extended periods',
            'Individual susceptibility',
            'Extreme physical exertion',
            'Dehydration'
        ],
        'prevention_guidelines': [
            'Follow strict acclimatization schedules',
            'Maintain excellent hydration (minimum 3-4 liters daily)',
            'Use prophylactic medications at high altitudes',
            'Avoid alcohol and sleeping medications',
            'Monitor for AMS symptoms constantly',
            'Consider avoiding extreme altitudes if not properly acclimatized',
            'Ensure proper nutrition and regular meals',
            'Sleep at lower altitudes when possible'
        ],
        'treatment_guidelines': [
            'IMMEDIATE DESCENT IS CRITICAL - descend at least 1,000 meters (3,300 feet)',
            'Administer supplemental oxygen immediately',
            'Use dexamethasone as a temporary measure (4mg every 6 hours)',
            'Seek emergency medical care urgently',
            'Maintain airway and monitor breathing',
            'Keep patient warm and monitor vital signs',
            'Avoid further exertion',
            'Transport to medical facility capable of ICU care'
        ],
        'additional_info': 'HACE is a medical emergency. Mortality rates increase significantly without prompt treatment. Immediate descent and medical intervention are life-saving measures.'
    },
    'high_altitude_pulmonary_edema': {
        'name': 'High Altitude Pulmonary Edema (HAPE)',
        'description': 'A potentially fatal condition where fluid accumulates in the lungs at high altitude.',
        'symptoms': [
            'Shortness of breath at rest',
            'Chest tightness',
            'Persistent cough (may produce frothy sputum)',
            'Wheezing or crackling sounds in lungs',
            'Blue lips or fingernails (cyanosis)',
            'Extreme fatigue',
            'Rapid heart rate',
            'Fever'
        ],
        'affected_altitude': '2,500 meters (8,200 feet) and above',
        'onset': '2-3 days after arriving at altitude (can be faster with rapid ascent)',
        'risk_factors': [
            'Individual susceptibility (highly variable)',
            'Rapid ascent without acclimatization',
            'Strenuous physical exertion',
            'Cold exposure',
            'Dehydration',
            'Previous HAPE episodes',
            'Male gender (slightly higher risk)',
            'Pre-existing lung or heart conditions'
        ],
        'prevention_guidelines': [
            'Gradual acclimatization over several days',
            'Avoid strenuous exercise for first 2-3 days',
            'Maintain strict hydration protocols',
            'Use nifedipine prophylactically if at high risk (history of HAPE)',
            'Stay warm - hypothermia increases risk',
            'Monitor respiratory rate and symptoms',
            'Sleep at lower altitudes initially',
            'Avoid alcohol and sedative medications'
        ],
        'treatment_guidelines': [
            'IMMEDIATE DESCENT IS CRITICAL - descend minimum 1,000 meters (3,300 feet)',
            'Administer high-flow supplemental oxygen (6-8 liters/minute)',
            'Maintain upright sitting position for easier breathing',
            'Use nifedipine to lower pulmonary artery pressure',
            'Give diuretics (furosemide) to reduce fluid overload',
            'Keep patient warm and minimize exertion',
            'Monitor oxygen saturation continuously',
            'Arrange immediate evacuation to medical facility',
            'Consider portable hyperbaric chamber (Gamow bag) as temporary measure'
        ],
        'additional_info': 'HAPE requires immediate medical attention. With proper treatment, prognosis is generally good. Prevention through gradual acclimatization is the most effective strategy.'
    }
}

@app.route('/')
def index():
    """Render the home page with list of altitude sickness types."""
    return render_template('index.html', sickness_types=ALTITUDE_INFO.keys())

@app.route('/sickness/<sickness_id>')
def sickness_detail(sickness_id):
    """Render detailed information about a specific altitude sickness."""
    if sickness_id not in ALTITUDE_INFO:
        return render_template('error.html', message='Sickness type not found'), 404
    
    sickness_data = ALTITUDE_INFO[sickness_id]
    return render_template('detail.html', sickness_id=sickness_id, sickness=sickness_data)

@app.route('/api/sickness/<sickness_id>')
def api_sickness_detail(sickness_id):
    """API endpoint to get detailed information about a specific altitude sickness."""
    if sickness_id not in ALTITUDE_INFO:
        return jsonify({'error': 'Sickness type not found'}), 404
    
    return jsonify(ALTITUDE_INFO[sickness_id])

@app.route('/api/all')
def api_all_sickness():
    """API endpoint to get information about all altitude sickness types."""
    return jsonify(ALTITUDE_INFO)

@app.route('/api/search', methods=['POST'])
def api_search():
    """API endpoint to search for altitude sickness by symptoms or name."""
    query = request.json.get('query', '').lower()
    
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    results = []
    for sickness_id, sickness_data in ALTITUDE_INFO.items():
        # Search in name
        if query in sickness_data['name'].lower():
            results.append({'id': sickness_id, 'name': sickness_data['name']})
        # Search in symptoms
        elif any(query in symptom.lower() for symptom in sickness_data['symptoms']):
            results.append({'id': sickness_id, 'name': sickness_data['name']})
        # Search in description
        elif query in sickness_data['description'].lower():
            results.append({'id': sickness_id, 'name': sickness_data['name']})
    
    return jsonify({'results': results, 'count': len(results)})

@app.route('/prevention')
def prevention():
    """Render page with prevention guidelines for all altitude sickness types."""
    prevention_data = {}
    for sickness_id, sickness_data in ALTITUDE_INFO.items():
        prevention_data[sickness_id] = {
            'name': sickness_data['name'],
            'guidelines': sickness_data['prevention_guidelines']
        }
    return render_template('prevention.html', prevention_data=prevention_data)

@app.route('/treatment')
def treatment():
    """Render page with treatment guidelines for all altitude sickness types."""
    treatment_data = {}
    for sickness_id, sickness_data in ALTITUDE_INFO.items():
        treatment_data[sickness_id] = {
            'name': sickness_data['name'],
            'guidelines': sickness_data['treatment_guidelines']
        }
    return render_template('treatment.html', treatment_data=treatment_data)

@app.route('/emergency')
def emergency():
    """Render emergency response guidelines page."""
    return render_template('emergency.html', sickness_info=ALTITUDE_INFO)

@app.route('/about')
def about():
    """Render about page with additional information."""
    return render_template('about.html')

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('error.html', message='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return render_template('error.html', message='Internal server error'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
