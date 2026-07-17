import os
import random
import requests
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Advanced Multi-Crop Vision Model (PlantVillage ResNet Model)
API_URL = "https://api-inference.huggingface.co/models/nusret/plant-disease-recognition-resnet50"
HF_TOKEN = os.environ.get("HF_API_TOKEN") 
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

# Massive Agronomy Knowledge Base (Multi-Crop, Deep Insights, 6 Languages)
DISEASE_DB = {
    "Potato___Early_blight": {
        "crop": "Potato",
        "disease": "Early Blight (Alternaria solani)",
        "treatment": "Apply Chlorothalonil or Mancozeb fungicides. Avoid overhead irrigation.",
        "prevention": "Rotate crops annually. Clear last season's crop debris entirely.",
        "growth_stage": "Vegetative to Tuber bulking phase tracking recommended.",
        "translation": {
            "hi": {"disease": "अगेती झुलसा रोग", "treatment": "मैनकोजेब कवकनाशी का छिड़काव करें। फव्वारा सिंचाई से बचें।", "prevention": "फसल चक्र अपनाएं।"},
            "te": {"disease": "ఆకు మచ్చ తెగులు", "treatment": "మాంకోజెబ్ పిచికారీ చేయండి. ఓవర్ హెడ్ నీటి పారుదల వద్దు.", "prevention": "పంట మార్పిడి చేయండి."},
            "ta": {"disease": "ஆரம்பகால கருகல் நோய்", "treatment": "மன்கோசெப் பூஞ்சணக்கொல்லியைப் பயன்படுத்தவும்.", "prevention": "பயிர் சுழற்சி முறை."},
            "mr": {"disease": "लवकर येणारा करपा", "treatment": "मॅन्कोझेब बुरशीनाशकाची फवारणी करा.", "prevention": "पीक फेरपालट करा."},
            "pa": {"disease": "ਅਗੇਤਾ ਝੁਲਸ ਰੋਗ", "treatment": "ਮੈਨਕੋਜ਼ੇਬ ਉੱਲੀਨਾਸ਼ਕ ਦਾ ਛਿੜਕਾਅ ਕਰੋ।", "prevention": "ਫ਼ਸਲ ਚੱਕਰ ਅਪਣਾਓ।"}
        }
    },
    "Tomato___Bacterial_spot": {
        "crop": "Tomato",
        "disease": "Bacterial Spot (Xanthomonas)",
        "treatment": "Spray copper-based bactericides combined with Mancozeb.",
        "prevention": "Use disease-free certified seeds. Do not harvest or trim when plants are wet.",
        "growth_stage": "Flowering and Fruit setting stage monitoring.",
        "translation": {
            "hi": {"disease": "जीवाणु जनित धब्बा रोग", "treatment": "तांबा-आधारित जीवाणुनाशक दवाओं का उपयोग करें।", "prevention": "प्रमाणित रोग-मुक्त बीजों का चयन करें।"},
            "te": {"disease": "బాక్టీరియల్ స్పాట్", "treatment": "కాपर ఆధారిత మందులు వాడండి.", "prevention": "ధృవీకరించబడిన విత్తనాలు వాడండి."},
            "ta": {"disease": "பாக்டீரியா புள்ளி நோய்", "treatment": "தாமிரம் சார்ந்த பாக்டீரியா கொல்லியை தெளிக்கவும்.", "prevention": "ஆரோக்கியமான விதைகளைப் பயன்படுத்துங்கள்."},
            "mr": {"disease": "जिवाणूजन्य ठिपके", "treatment": "तांबे-आधारित जिवाणूनाशक फवारा.", "prevention": "रोगमुक्त बियाणे वापरा."},
            "pa": {"disease": "ਬੈਕਟੀਰੀਅਲ ਸਪਾਟ", "treatment": "ਤਾਂਬੇ ਵਾਲੀ ਦਵਾਈ ਦਾ ਛਿੜਕਾਅ ਕਰੋ।", "prevention": "ਸਹੀ ਬੀਜਾਂ ਦੀ ਵਰਤੋਂ ਕਰੋ।"}
        }
    },
    "Tomato___Late_blight": {
        "crop": "Tomato",
        "disease": "Late Blight (Phytophthora infestans)",
        "treatment": "Apply systemic fungicides like Ridomil Gold. Destroy infected plants immediately.",
        "prevention": "Ensure wide spacing between plants for wind aeration. Avoid high moisture build-up.",
        "growth_stage": "Mid to Late vegetative development phase.",
        "translation": {
            "hi": {"disease": "पछेती झुलसा रोग", "treatment": "रिडोमिल गोल्ड का उपयोग करें। संक्रमित पौधों को नष्ट करें।", "prevention": "पौधों के बीच उचित दूरी रखें।"},
            "te": {"disease": "లేట్ బ్లైట్ తెగులు", "treatment": "రిడోమిల్ గోల్డ్ పిచికారీ చేయండి.", "prevention": "మొక్కల మధ్య సరైన దూరం ఉంచండి."},
            "ta": {"disease": "பின்கால கருகல் நோய்", "treatment": "பூஞ்சணக்கொல்லி தெளிக்கவும்.", "prevention": "பயிர்களுக்கு இடையே இடைவெளி விடுக."},
            "mr": {"disease": "उशिरा येणारा करपा", "treatment": "बुरशीनाशक फवारणी करा.", "prevention": "झाडांमध्ये योग्य अंतर ठेवा."},
            "pa": {"disease": "ਪਿਛੇਤਾ ਝੁਲਸ ਰੋਗ", "treatment": "ਉੱਲੀਨਾਸ਼ਕ ਦਵਾਈ ਪਾਓ।", "prevention": "ਬੂਟਿਆਂ ਵਿੱਚ ਸਹੀ ਦੂਰੀ ਰੱਖੋ।"}
        }
    },
    "Corn___Common_rust": {
        "crop": "Corn / Maize",
        "disease": "Common Rust (Puccinia sorghi)",
        "treatment": "Apply strobilurin or triazole fungicides if pustules appear on lower leaves.",
        "prevention": "Plant rust-resistant hybrid varieties suited for your agroclimatic zone.",
        "growth_stage": "Knee-high growth to Tasseling stage analysis.",
        "translation": {
            "hi": {"disease": "मक्के का गेरूआ रोग (रस्ट)", "treatment": "ट्रायज़ोल कवकनाशी का छिड़काव करें।", "prevention": "रोग-प्रतिरोधी संकर किस्मों को बोएं।"},
            "te": {"disease": "మొక్కజొన్న తుప్పు తెగులు", "treatment": "శిలీంద్ర సంహారిణి పిచికారీ చేయండి.", "prevention": "తట్టుకునే రకాలను ఎంచుకోండి."},
            "ta": {"disease": "சோள துரு நோய்", "treatment": "பூஞ்சணக்கொல்லி மருந்துகளைப் பயன்படுத்தவும்.", "prevention": "நோய் எதிர்ப்புத் திறன் கொண்ட பயிர்கள்."},
            "mr": {"disease": "मक्यावरील तांबेरा", "treatment": "बुरशीनाशक औषध फवारा.", "prevention": "तांबेरा-प्रतिकारक वाण वापरा."},
            "pa": {"disease": "ਮੱਕੀ ਦਾ ਕੁੰਗੀ ਰੋਗ", "treatment": "ਉੱਲੀਨਾਸ਼ਕ ਦਾ ਛਿੜਕਾਅ ਕਰੋ।", "prevention": "ਬੀਮਾਰੀ ਰਹਿਤ ਕਿਸਮਾਂ ਬੀਜੋ।"}
        }
    },
    "Healthy": {
        "crop": "Detected Crop",
        "disease": "Healthy Plant Leaf",
        "treatment": "No active disease found. Beautiful work keeping it nourished!",
        "prevention": "Maintain optimal N-P-K nutrient schedules and standard soil testing cycles.",
        "growth_stage": "Growth structure looks robust. Standard upkeep recommended.",
        "translation": {
            "hi": {"disease": "स्वस्थ पत्ता", "treatment": "कोई उपचार आवश्यक नहीं है। आपकी फसल बहुत अच्छी स्थिति में है!", "prevention": "नियमित रूप से संतुलित जैविक खाद दें।"},
            "te": {"disease": "ఆరోగ్యకరమైన ఆకు", "treatment": "చికిత్స అవసరం లేదు. మీ పంట సంపూర్ణ ఆరోగ్యంగా ఉంది!", "prevention": "సమతుల్య ఎరువులు వేయండి."},
            "ta": {"disease": "ஆரோக்கியமான இலை", "treatment": "சிகிச்சை தேவையில்லை. உங்கள் பயிர் நலம்!", "prevention": "முறையான உரம் மற்றும் நீர் மேலாண்மை."},
            "mr": {"disease": "निरोगी पान", "treatment": "कोणत्याही उपचाराची गरज नाही. पीक उत्तम आहे!", "prevention": "वेळेवर खते आणि पाणी व्यवस्थापन करा."},
            "pa": {"disease": "ਤੰਦਰੁਸਤ ਪੱਤਾ", "treatment": "ਕਿਸੇ ਇਲਾਜ ਦੀ ਲੋੜ ਨਹੀਂ। ਤੁਹਾਡੀ ਫ਼ਸਲ ਬਿਲਕੁਲ ਠੀਕ ਹੈ!", "prevention": "ਸਮੇਂ ਸਿਰ ਦੇਸੀ ਖਾਦਾਂ ਅਤੇ ਪਾਣੀ ਦਿਓ।"}
        }
    }
}

def query_ai_model(filepath):
    try:
        with open(filepath, "rb") as f:
            data = f.read()
        response = requests.post(API_URL, headers=HEADERS, data=data, timeout=12)
        return response.json()
    except Exception:
        return None

def generate_smart_advisory(city):
    """Generates rich real-world simulation of dynamic weather alerts and farming notifications."""
    conditions = [
        {"temp": 33, "condition": "Sunny / Clear Sky", "alert": "High Evapotranspiration Alert!", "notification": "Schedule drip irrigation early at 5:00 AM or late evening to maximize moisture absorption."},
        {"temp": 21, "condition": "Heavy Monsoonal Rain", "alert": "Waterlogging Risk & Root Rot Alert!", "notification": "Immediately inspect drainage outtakes. Pause all granular chemical fertilizer applications."},
        {"temp": 27, "condition": "High Humidity / Overcast", "alert": "Fungal Infection Alert Spore Index High!", "notification": "High risk environment for Blight spreading. Inspect undersides of lower canopy foliage today."}
    ]
    return random.choice(conditions)

@app.route('/')@app.route('/diagnose', methods=['POST'])
def diagnose():
    lang = request.form.get('language', 'en')
    city = request.form.get('city', 'New Delhi')
    
    file = request.files.get('image')
    if not file or file.filename == '':
        # If no image, reload home with an error message
        return render_template('index.html', error="No image uploaded")
        
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Trigger Intelligence Inspection Engine
    ai_predictions = query_ai_model(filepath)
    
    detected_class = "Healthy"
    
    if ai_predictions and isinstance(ai_predictions, list) and len(ai_predictions) > 0:
        top_prediction = ai_predictions[0]
        label = top_prediction.get('label', '')
        score = top_prediction.get('score', 0.0)
        
        # Smart Validation Threshold
        if score < 0.28:
            result_payload = {
                "crop": "Unknown Object Detected",
                "disease": "Invalid / Non-Plant Image",
                "treatment": "We couldn't verify this image as a farm crop. Please take a clear, brightly lit close-up photo focusing only on a single crop leaf.",
                "prevention": "Avoid blurry pictures, background noise, or capturing human hands/tools in the frame.",
                "growth_stage": "N/A"
            }
            return render_template('index.html', result=result_payload, weather=generate_smart_advisory(city))
        
        matched = False
        for key in DISEASE_DB.keys():
            if key.lower() in label.lower():
                detected_class = key
                matched = True
                break
        
        if not matched and "healthy" in label.lower():
            detected_class = "Healthy"

    data = DISEASE_DB.get(detected_class, DISEASE_DB["Healthy"])
    
    # Build Multi-Language Translation Map
    if lang in ['hi', 'te', 'ta', 'mr', 'pa'] and lang in data['translation']:
        result_payload = {
            "crop": data["crop"],
            "disease": data['translation'][lang]['disease'],
            "treatment": data['translation'][lang]['treatment'],
            "prevention": data['translation'][lang]['prevention'],
            "growth_stage": data["growth_stage"]
        }
    else:
        result_payload = {
            "crop": data["crop"],
            "disease": data["disease"],
            "treatment": data["treatment"],
            "prevention": data["prevention"],
            "growth_stage": data["growth_stage"]
        }
        
    weather_data = generate_smart_advisory(city)

    # Render the template directly with the data injection
    return render_template('index.html', result=result_payload, weather=weather_data)

if __name__ == '__main__':
    app.run(debug=True)
def home():
    return render_template('index.html')

