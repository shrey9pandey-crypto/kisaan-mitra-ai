





import os
import random
import requests
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB file limit

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Free Hugging Face API URL for Crop Disease Classification
API_URL = "https://api-inference.huggingface.co/models/nusret/plant-disease-recognition-resnet50"
# 🔒 SECURE WAY: Grab the API token safely from Render's environment
HF_TOKEN = os.environ.get("HF_API_TOKEN") 
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

# Comprehensive Knowledge Base mapped to real model outputs
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

def query_ai_model(filepath):
    """Sends the uploaded photo to the cloud AI model for actual classification."""
    try:
        with open(filepath, "rb") as f:
            data = f.read()
        response = requests.post(API_URL, headers=HEADERS, data=data, timeout=10)
        return response.json()
    except Exception:
        return None

def get_weather_advisory(city):
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

    # 1. Ask the AI Model to inspect the image
    ai_predictions = query_ai_model(filepath)
    
    detected_class = "Healthy"
    
    # 2. Check the results from the AI
    if ai_predictions and isinstance(ai_predictions, list) and len(ai_predictions) > 0:
        top_prediction = ai_predictions[0]
        label = top_prediction.get('label', '')
        score = top_prediction.get('score', 0.0)
        
        # Validation: If the AI is highly uncertain, it's a random object/non-crop photo
        if score < 0.30:
            return jsonify({
                "disease": "Invalid Image / Not a Crop Leaf",
                "treatment": "Please upload a clear, close-up picture of a plant or crop leaf.",
                "prevention": "Ensure lighting is clear and the leaf fills the frame.",
                "weather": get_weather_advisory(city)
            })
        
        # Map the model's output name to our database keys
        for key in DISEASE_DB.keys():
            if key.lower() in label.lower():
                detected_class = key
                break
            elif "healthy" in label.lower():
                detected_class = "Healthy"

    # 3. Pull the treatment data out
    data = DISEASE_DB.get(detected_class, DISEASE_DB["Healthy"])
    
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
        
    result_payload["weather"] = get_weather_advisory(city)
    return jsonify(result_payload)

if __name__ == '__main__':
    app.run(debug=True)
