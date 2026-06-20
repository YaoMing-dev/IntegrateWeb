# Mail OCR NER — Integrate ML model to Web app

Web app trích xuất thông tin phiếu gửi hàng (vận đơn) từ ảnh, theo kiến trúc 4 tầng:

```
frontend/frontend/index.html (HTML)  →  flask_backend (Flask, :5000)  →  src/ + models/ (YOLO + OCR)
```

Frontend chỉ là một file HTML tĩnh; không cần thêm server riêng cho frontend.

Model YOLO và 2 OCR backend được load một lần lúc Flask khởi động (warmup), không load lại mỗi request — nên mỗi lần upload chỉ mất khoảng 1-2 giây.

## Yêu cầu hệ thống

- Python 3.10+ (cài global, không cần venv)
- Git LFS (để clone được file model `.pt`/`.pth`)
- `vietocr` để chạy model `transformerocr.pth`

## Cài đặt

### 1. Clone repo (kèm Git LFS)

```bash
git lfs install
git clone https://github.com/YaoMing-dev/IntegrateWeb.git
cd IntegrateWeb
```

### 2. Cài Python dependencies (Flask + ML)

```bash
pip install -r flask_backend/requirements.txt
```

> Lưu ý: nếu máy đã cài `paddleocr`/`paddlex` cho project khác, các package này yêu cầu `numpy<2`. Sau khi cài xong, kiểm tra lại bằng `pip show numpy` — nếu bị nâng lên numpy 2.x, chạy `pip install "numpy<2"`.

## Chạy ứng dụng

Mở 1 terminal cho Flask, rồi mở file HTML trong trình duyệt:

**Terminal 1 — Flask (ML service, :5000)**

```bash
cd flask_backend
python server.py
```

Đợi tới khi thấy log `Model đã sẵn sàng. Đang khởi động Flask trên :5000`.

Mở trực tiếp `frontend/frontend/index.html` trong trình duyệt, miễn là Flask đang chạy.

## Kiểm tra nhanh (không cần mở trình duyệt)

```bash
curl http://127.0.0.1:5000/health
curl -F "image=@duong/dan/anh.jpg" -F "ocr_model=easyocr" http://127.0.0.1:5000/upload
```

## Cấu trúc thư mục

| Thư mục | Vai trò |
|---|---|
| `frontend/frontend/index.html` | Giao diện HTML/CSS/JS tĩnh |
| `flask_backend/` | Flask — nhận ảnh, gọi pipeline, trả JSON kết quả |
| `src/` | Pipeline xử lý: detect vùng bằng YOLO, OCR bằng EasyOCR hoặc VietOCR (VietOCR dùng EasyOCR để cắt line rồi nhận dạng) |
| `models/` | `yolo_regions/mail_3field/weights/best.pt` và `vietocr/transformerocr.pth` |

## Cấu hình

| Biến môi trường | Default | Dùng ở |
|---|---|---|
| `FLASK_HOST` | `0.0.0.0` | `flask_backend/server.py` |
| `FLASK_PORT` | `5000` | `flask_backend/server.py` |

## Test

```bash
python -m py_compile flask_backend/server.py flask_backend/pipeline.py src/local_3field_pipeline.py
```
