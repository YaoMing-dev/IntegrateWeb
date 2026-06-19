import os
import uuid
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

from pipeline import run_pipeline, PipelineError, warmup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "heic"}
MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/health", methods=["GET"])
def health():
    """Kiểm tra server còn sống không — FE hoặc devops dùng."""
    return jsonify({"status": "ok"}), 200


@app.route("/upload", methods=["POST"])
def upload():
    """
    Upload ảnh phiếu gửi hàng → chạy OCR pipeline → trả JSON.

    Request  : multipart/form-data, field "image"
    Response : JSON kết quả (xem README để biết các field)
    """

    if "image" not in request.files:
        return jsonify({"error": "Thiếu field 'image' trong form-data"}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "Chưa chọn file"}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "error": f"Định dạng không hỗ trợ. Chỉ nhận: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 415

    ext = file.filename.rsplit(".", 1)[1].lower()
    temp_filename = f"{uuid.uuid4().hex}.{ext}"
    temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)

    try:
        file.save(temp_path)
        logger.info(f"Saved upload: {temp_filename}")

        result = run_pipeline(temp_path)
        logger.info(f"Pipeline OK: ma_van_don={result.get('ma_van_don')}")
        return jsonify(result), 200

    except PipelineError as e:
        logger.error(f"Pipeline error: {e}")
        return jsonify({"error": str(e)}), 422

    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({"error": "Lỗi server nội bộ", "detail": str(e)}), 500

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            logger.debug(f"Removed temp file: {temp_filename}")


@app.errorhandler(413)
def request_too_large(_):
    return jsonify({"error": "File quá lớn. Giới hạn 20 MB"}), 413

@app.errorhandler(405)
def method_not_allowed(_):
    return jsonify({"error": "Method không được phép"}), 405

@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Endpoint không tồn tại"}), 404


if __name__ == "__main__":
    logger.info("Đang nạp model (YOLO + EasyOCR)...")
    warmup()
    logger.info("Model đã sẵn sàng. Đang khởi động Flask trên :5000")
    app.run(debug=False, port=5000, host="0.0.0.0")