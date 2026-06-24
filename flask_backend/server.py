from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pickle
import numpy as np
import os

app = Flask(__name__)
CORS(app)

base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, '..', 'models', 'model_calo.pkl')
frontend_path = os.path.join(base_dir, '..', 'frontend')

if not os.path.exists(model_path):
    raise FileNotFoundError(f"Không tìm thấy model tại: {model_path}")

with open(model_path, 'rb') as f:
    model = pickle.load(f)


@app.route('/')
def index():
    return send_from_directory(frontend_path, 'index.html')


@app.route('/<path:path>')
def static_proxy(path):
    file_path = os.path.join(frontend_path, path)
    if os.path.isfile(file_path):
        return send_from_directory(frontend_path, path)
    return send_from_directory(frontend_path, 'index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json(silent=True) or {}
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
    port = int(os.environ.get('PORT', 5000))
    print(f"Server Flask đang chạy tại port {port}...")
    app.run(debug=False, host='0.0.0.0', port=port)