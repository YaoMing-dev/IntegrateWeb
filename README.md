# Mail OCR NER — Integrate ML model to Web app

Web app trích xuất thông tin phiếu gửi hàng (vận đơn) từ ảnh, theo kiến trúc 4 tầng:

```
frontend/frontend/index.html (HTML)  →  backend (Node.js/Express, :4000)  →  flask_backend (Flask, :5000)  →  src/ + models/ (YOLO + OCR)
```

Frontend chỉ là một file HTML tĩnh; không cần thêm server riêng cho frontend.

Model YOLO và 2 OCR backend được load một lần lúc Flask khởi động (warmup), không load lại mỗi request — nên mỗi lần upload chỉ mất khoảng 1-2 giây.

## Yêu cầu hệ thống

- Python 3.10+ (cài global, không cần venv)
- Node.js 18+ (cần `fetch`/`FormData` built-in)
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

### 3. Cài Node.js dependencies (Express)

```bash
cd backend
npm install
cd ..
```

## Chạy ứng dụng

Mở 2 terminal, chạy theo thứ tự (Flask phải lên trước vì Express gọi vào nó):

**Terminal 1 — Flask (ML service, :5000)**

```bash
cd flask_backend
python server.py
```

Đợi tới khi thấy log `Model đã sẵn sàng. Đang khởi động Flask trên :5000`.

**Terminal 2 — Express (backend, :4000)**

```bash
cd backend
npm start
```

Mở trực tiếp `frontend/frontend/index.html` trong trình duyệt, miễn là backend đang chạy.

## Kiểm tra nhanh (không cần mở trình duyệt)

```bash
curl http://127.0.0.1:4000/api/health
curl -F "image=@duong/dan/anh.jpg" http://127.0.0.1:4000/api/upload
```

## Cấu trúc thư mục

| Thư mục | Vai trò |
|---|---|
| `frontend/frontend/index.html` | Giao diện HTML/CSS/JS tĩnh |
| `backend/` | Express — proxy request từ frontend sang Flask (`/api/health`, `/api/upload`) |
| `flask_backend/` | Flask — nhận ảnh, gọi pipeline, trả JSON kết quả |
| `src/` | Pipeline xử lý: detect vùng bằng YOLO, OCR bằng EasyOCR hoặc VietOCR (VietOCR dùng EasyOCR để cắt line rồi nhận dạng) |
| `models/` | `yolo_regions/mail_3field/weights/best.pt` và `vietocr/transformerocr.pth` |

## Cấu hình

| Biến môi trường | Default | Dùng ở |
|---|---|---|
| `FLASK_URL` | `http://127.0.0.1:5000` | `backend/server.js` |
| `PORT` | `4000` | `backend/server.js` |

## Test

```bash
cd backend
npm test
```
