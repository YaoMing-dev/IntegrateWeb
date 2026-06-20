// backend/server.js
import cors from "cors";
import express from "express";
import multer from "multer";
import { pathToFileURL } from "node:url";

const FLASK_URL = process.env.FLASK_URL || "http://127.0.0.1:5000";
const PORT = process.env.PORT || 4000;
const UPSTREAM_TIMEOUT_MS = 30_000; // generous given warm/cached models — not minutes
const ALLOWED_OCR_MODELS = new Set(["easyocr", "vietocr"]);

const upload = multer({ limits: { fileSize: 20 * 1024 * 1024 } });

async function readUpstreamBody(response) {
  const contentType = response.headers.get("content-type") || "";
  const text = await response.text();
  const trimmed = text.trim();
  if (contentType.includes("application/json") || trimmed.startsWith("{") || trimmed.startsWith("[")) {
    try {
      return { kind: "json", value: JSON.parse(text) };
    } catch {
      // Fall through to text when the body is not valid JSON despite the hint.
    }
  }

  return { kind: "text", value: text };
}

function toUpstreamError(body, fallbackMessage) {
  if (body.kind === "json" && body.value && typeof body.value === "object") {
    const error = body.value.error || body.value.message || fallbackMessage;
    return {
      error,
      detail: body.value.detail || body.value,
    };
  }

  const text = String(body.value || "").trim();
  return {
    error: text || fallbackMessage,
    detail: text || undefined,
  };
}

export function createApp({ fetchImpl = fetch } = {}) {
  const app = express();
  app.use(cors());

  app.get("/api/health", async (_req, res) => {
    try {
      const upstream = await fetchImpl(`${FLASK_URL}/health`, {
        signal: AbortSignal.timeout(UPSTREAM_TIMEOUT_MS),
      });
      const body = await readUpstreamBody(upstream);
      if (upstream.ok) {
        res.status(upstream.status).json(body.kind === "json" ? body.value : { status: body.value });
        return;
      }
      res.status(upstream.status).json(toUpstreamError(body, "ML service trả về lỗi"));
    } catch (err) {
      res.status(502).json({ error: "Không kết nối được ML service", detail: String(err) });
    }
  });

  app.post("/api/upload", upload.single("image"), async (req, res) => {
    if (!req.file) {
      res.status(400).json({ error: "Thiếu field 'image'" });
      return;
    }

    const form = new FormData();
    form.append("image", new Blob([req.file.buffer]), req.file.originalname);
    const ocrModel = String(req.body?.ocr_model || "easyocr").trim().toLowerCase();
    form.append("ocr_model", ALLOWED_OCR_MODELS.has(ocrModel) ? ocrModel : "easyocr");

    try {
      const upstream = await fetchImpl(`${FLASK_URL}/upload`, {
        method: "POST",
        body: form,
        signal: AbortSignal.timeout(UPSTREAM_TIMEOUT_MS),
      });
      const body = await readUpstreamBody(upstream);
      if (upstream.ok) {
        res.status(upstream.status).json(body.kind === "json" ? body.value : { result: body.value });
        return;
      }
      res.status(upstream.status).json(toUpstreamError(body, "ML service trả về lỗi"));
    } catch (err) {
      res.status(502).json({ error: "Không kết nối được ML service", detail: String(err) });
    }
  });

  return app;
}

const isMain = process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;
if (isMain) {
  createApp().listen(PORT, () => {
    console.log(`Express backend listening on http://127.0.0.1:${PORT}`);
  });
}
