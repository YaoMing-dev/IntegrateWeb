from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import os

app = Flask(__name__)
CORS(app) 

base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, '..', 'models', 'model_calo.pkl')

with open(model_path, 'rb') as f:
    model = pickle.load(f)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        time = float(data['time'])
        steps = float(data['steps'])
        
        input_data = np.array([[time, steps]])
        prediction = model.predict(input_data)
        
        return jsonify({
            'success': True,
            'calories': round(prediction[0], 2)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "Server Flask đang chạy tốt"})

if __name__ == '__main__':
    print("Server Flask đang chạy tại port 5000...")
    app.run(debug=True, port=5000)