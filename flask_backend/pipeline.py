import os
import sys

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_SRC_PATH = os.path.join(_PROJECT_ROOT, "src")

if _SRC_PATH not in sys.path:
    sys.path.insert(0, _SRC_PATH)

try:
    from local_3field_pipeline import (
        OCR_MODEL_EASYOCR,
        OCR_MODEL_VIETOCR,
        process_image,
        warmup as _warmup_models,
    )
except ImportError as e:
    raise RuntimeError(
        f"Không import được local_3field_pipeline từ {_SRC_PATH}.\n"
        f"Kiểm tra lại đường dẫn và .venv.\nLỗi gốc: {e}"
    )

_MODEL_PATH = os.path.join(
    _PROJECT_ROOT, "models", "yolo_regions", "mail_3field", "weights", "best.pt"
)
_OCR_MODEL_PATH = os.path.join(_PROJECT_ROOT, "models", "vietocr", "transformerocr.pth")


class PipelineError(Exception):
    """Lỗi có thể đoán trước trong pipeline (ảnh hỏng, không detect được...)."""
    pass


def warmup() -> None:
    """Preload YOLO and both OCR backends once at process startup."""
    if not os.path.exists(_MODEL_PATH):
        raise PipelineError(f"Không tìm thấy model YOLO tại: {_MODEL_PATH}")
    if not os.path.exists(_OCR_MODEL_PATH):
        raise PipelineError(f"Không tìm thấy model VietOCR tại: {_OCR_MODEL_PATH}")
    _warmup_models(_MODEL_PATH, ocr_models=(OCR_MODEL_EASYOCR, OCR_MODEL_VIETOCR))


def run_pipeline(image_path: str, ocr_model: str = OCR_MODEL_EASYOCR) -> dict:
    """
    Nhận đường dẫn ảnh tạm, chạy full pipeline, trả dict kết quả.

    Raises:
        PipelineError  — khi pipeline trả về lỗi có thể xử lý
        Exception      — lỗi không lường trước (để server.py bắt riêng)
    """
    if not os.path.exists(image_path):
        raise PipelineError(f"File không tồn tại: {image_path}")

    if not os.path.exists(_MODEL_PATH):
        raise PipelineError(f"Không tìm thấy model YOLO tại: {_MODEL_PATH}")
    if not os.path.exists(_OCR_MODEL_PATH):
        raise PipelineError(f"Không tìm thấy model VietOCR tại: {_OCR_MODEL_PATH}")

    if ocr_model not in {OCR_MODEL_EASYOCR, OCR_MODEL_VIETOCR}:
        raise PipelineError(f"Model OCR không hỗ trợ: {ocr_model}")

    try:
        result = process_image(
            image_path,
            model_path=_MODEL_PATH,
            ocr_model=ocr_model,
            save_debug=False,
        )
    except FileNotFoundError as e:
        raise PipelineError(f"Không tìm thấy model hoặc file: {e}")
    except ValueError as e:
        raise PipelineError(f"Ảnh không hợp lệ hoặc không detect được vùng: {e}")

    if not isinstance(result, dict):
        raise PipelineError("Pipeline trả về kiểu dữ liệu không hợp lệ (không phải dict)")

    return result
