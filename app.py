import os
import random
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB file limit

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Predefined Knowledge Base for Crop Diseases
DISEASE_DB = {
    "Potato___Early_blight": {
        "disease": "Early Blight (Alternaria solani)",
        "treatment": "Apply fungicides like Chlorothalonil or Mancozeb. Avoid overhead irrigation.",
        "prevention": "Rotate crops annually. Remove leftover plant debris from last season.",
        "translation": {
            "hi": {
                "disease": "अगेती झुलसा रोग (अल्टरनेरिया सोलानी)",
                "treatment": "क्लोरोथालोनिल या मैनकोजेब जैसे कवकनाशी का छिड़काव करें। फव्वारा सिंचाई से बचें।",
                "prevention": "हर साल फसल चक्र अपनाएं। पिछली फसल के बचे हुए अवशेषों को नष्ट कर दें।"
            },
            "te": {
                "disease": "ఆకు మచ్చ తెగులు (Early Blight)",
                "treatment": "క్లోరోథలోనిల్ లేదా మాంకోజెబ్ వంటి శిలీంద్ర సంహారిణులను పిచికారీ చేయండి.",
                "prevention": "పంట మార్పిడిని పాటించండి. పాత పంట వ్యర్థాలను తొలగించండి."
            }
        }
    },
    "Tomato___Bacterial_spot": {
        "disease": "Bacterial Spot (Xanthomonas)",
        "treatment": "Spray copper-based bactericides combined with Mancozeb.",
        "prevention": "Use disease-free certified seeds and avoid working among wet plants.",
        "translation": {
            "hi": {
                "disease": "जीवाणु जनित धब्बा रोग (बैक्टीरियल स्पॉट)",
                "treatment": "मैनकोजेब के साथ मिलाकर तांबा-आधारित जीवाणुनाशक दवाओं का छिड़काव करें।",
                "prevention": "रोग-मुक्त प्रमाणित बीजों का उपयोग करें और गीले पौधों के बीच काम करने से बचें।"
            },
            "te": {
                "disease": "బాక్టీరియల్ స్పాట్",
                "treatment": "కాపర్ ఆధారిత బాక్టీరియా సంహారిణులను మాంకోజెబ్‌తో కలిపి పిచికారీ చేయండి.",
                "prevention": "ధృవీకరించబడిన నాణ్యమైన విత్తనాలను వాడండి."
            }
        }
    },
    "Healthy": {
        "disease": "Healthy Leaf",
        "treatment": "No treatment required. Your crop looks in excellent shape!",
        "prevention": "Maintain scheduled watering cycles and balanced N-P-K fertilizer distribution.",
        "translation": {
            "hi": {
                "disease": "स्वस्थ पत्ता",
                "treatment": "किसी उपचार की आवश्यकता नहीं है। आपकी फसल बिल्कुल स्वस्थ दिख रही है!",
                "prevention": "नियमित रूप से पानी देने का चक्र बनाए रखें और संतुलित खाद का उपयोग करें।"
            },
            "te": {
                "disease": "ఆరోగ్యకరమైన ఆకు",
                "treatment": "ఎటువంటి చికిత్స అవసరం లేదు. మీ పంట చాలా ఆరోగ్యంగా ఉంది!",
                "prevention": "క్రమం తప్పకుండా నీటి పారుదల మరియు సమతుల్య ఎరువులు వాడండి."
            }
        }
    }
}

def get_weather_advisory(city):
    # Simulated weather variation based on location
    mock_weather_conditions = [
        {"temp": 34, "condition": "Sunny", "advisory": "High evaporation rates predicted. Water fields in early morning hours to save water."},
        {"temp": 22, "condition": "Heavy Rain", "advisory": "Risk of waterlogging. Clear drainage channels to prevent root rot."},
        {"temp": 28, "condition": "Humid", "advisory": "High humidity increases fungal risks. Inspect leaf undersides closely."}
    ]
    return random.choice(mock_weather_conditions)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/diagnose', methods=['POST'])
def diagnose():
    lang = request.form.get('language', 'en')
    city = request.form.get('city', 'New Delhi')
    
    file = request.files.get('image')
    if not file or file.filename == '':
        return jsonify({"error": "No image uploaded"}), 400
        
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Randomly select a disease for demonstration purposes
    detected_class = random.choice(list(DISEASE_DB.keys()))
    data = DISEASE_DB[detected_class]
    
    # Apply translation selection
    if lang in ['hi', 'te'] and lang in data['translation']:
        result_payload = {
            "disease": data['translation'][lang]['disease'],
            "treatment": data['translation'][lang]['treatment'],
            "prevention": data['translation'][lang]['prevention']
        }
    else:
        result_payload = {
            "disease": data["disease"],
            "treatment": data["treatment"],
            "prevention": data["prevention"]
        }
        
    # Attach simulated weather insights
    result_payload["weather"] = get_weather_advisory(city)

    return jsonify(result_payload)

if __name__ == '__main__':
    app.run(debug=True)