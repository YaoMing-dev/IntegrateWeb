# Calorie Prediction — Integrate ML model to Web app

Web app dự đoán lượng calo tiêu thụ dựa trên thời gian tập luyện và số bước chân, sử dụng thuật toán **Linear Regression** theo kiến trúc 3 tầng:

```
frontend/index.html (HTML/CSS)  →  flask_backend (Flask, :5000)  →  models/model_calo.pkl (Linear Regression)
```

Frontend là một file HTML tĩnh tích hợp CSS; không cần thêm server riêng cho frontend. Backend sử dụng Flask để nạp mô hình đã được huấn luyện sẵn (pickle file) và trả kết quả dự đoán dưới dạng JSON.

## Yêu cầu hệ thống

- Python 3.10+
- Thư viện: `flask`, `flask-cors`, `scikit-learn`, `pandas`, `numpy`

## Cài đặt

### 1. Clone repo

```bash
git clone https://github.com/YaoMing-dev/IntegrateWeb.git
cd IntegrateWeb
```

### 2. Cài Python dependencies (Flask + ML)

```bash
pip install -r flask_backend/requirements.txt
```

## Quy trình chạy ứng dụng

Quy trình gồm 2 giai đoạn: Huấn luyện mô hình để tạo file đóng băng, sau đó khởi động server.

### Bước 1: Huấn luyện mô hình (Training)
Trước khi chạy website, bạn cần tạo ra file mô hình `.pkl`:

```bash
cd models
python train_model.py
```
> **Kết quả:** File `model_calo.pkl` sẽ xuất hiện trong thư mục `models`.

### Bước 2: Chạy Backend Server (Flask)
Mở terminal và khởi động dịch vụ máy học:

```bash
cd ../flask_backend
python server.py
```

Đợi tới khi thấy log `Server Flask đang chạy tại port 5000`. 

### Bước 3: Sử dụng giao diện
Mở trực tiếp URL backend (hoặc chạy local rồi vào `http://127.0.0.1:5000/`). Frontend và backend chạy chung một app Flask.

## Kiểm tra nhanh (Health Check)

Bạn có thể kiểm tra trạng thái server bằng lệnh curl:

```bash
# Kiểm tra server có sống không
curl http://127.0.0.1:5000/health

# Thử dự đoán thủ công (VD: 60 phút, 5000 bước)
curl -X POST -H "Content-Type: application/json" -d "{\"time\":60, \"steps\":5000}" http://127.0.0.1:5000/predict
```

## Cấu trúc thư mục

| Thư mục / Tập tin | Vai trò |
|---|---|
| `frontend/index.html` | Giao diện người dùng (HTML/CSS/JS) |
| `flask_backend/server.py` | Flask API — nhận dữ liệu, gọi model, trả kết quả dự đoán |
| `flask_backend/requirements.txt` | Danh sách các thư viện cần cài đặt |
| `render.yaml` | Cấu hình deploy Render 1 service |
| `models/train_model.py` | Script huấn luyện mô hình Linear Regression từ dữ liệu giả định |
| `models/model_calo.pkl` | File mô hình đã được đóng băng (máy học xong sẽ lưu vào đây) |

## Deploy Render

Repo đã sẵn cấu hình để deploy thành **1 Web Service** trên Render:

- **Build Command:** `pip install -r flask_backend/requirements.txt`
- **Start Command:** `gunicorn --chdir flask_backend server:app`

Khi chạy trên Render, mở URL gốc của service là dùng được ngay.

## Cấu hình (Config)

| Tham số | Giá trị mặc định | Tệp cấu hình |
|---|---|---|
| `Port` | `5000` | `flask_backend/server.py` |
| `Model Path` | `../models/model_calo.pkl` | `flask_backend/server.py` |
