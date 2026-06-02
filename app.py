from transformers import pipeline
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

print("Loading models...")

# Emotions Model
emotion_pipeline = pipeline("text-classification", 
                           model="j-hartmann/emotion-english-distilroberta-base", 
                           top_k=None)

# Zero-Shot Tone Analysis
zero_shot_classifier = pipeline("zero-shot-classification", 
                               model="facebook/bart-large-mnli")

print("✅ Models loaded successfully!")

def get_emotions(text):
    results = emotion_pipeline(text)[0]
    sorted_emotions = sorted(results, key=lambda x: x['score'], reverse=True)
    return {"top_emotions": sorted_emotions[:8]}

def get_zero_shot_tone(text):
    candidate_labels = [
        "threatening", "angry", "rude", "sarcastic", "polite", 
        "professional", "casual", "sad", "disappointed", "excited",
        "formal", "informal", "encouraging", "neutral", "happy"
    ]
    
    result = zero_shot_classifier(text, candidate_labels, multi_label=False)
    
    return {
        "top_tones": [
            {"label": result['labels'][i], "score": float(result['scores'][i])} 
            for i in range(7)
        ]
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        input_text = request.form['input_text'].strip()
        analysis_type = request.form.get('analysis_type', 'full')

        if not input_text:
            return jsonify({"error": "Empty input"}), 400

        result = {"input": input_text}

        if analysis_type in ['emotions', 'full']:
            result["emotions"] = get_emotions(input_text)
        
        if analysis_type in ['tone', 'full']:
            result["tone_analysis"] = get_zero_shot_tone(input_text)

        return jsonify(result)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)