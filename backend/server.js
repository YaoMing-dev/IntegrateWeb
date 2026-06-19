// backend/server.js
import cors from "cors";
import express from "express";
import multer from "multer";
import { pathToFileURL } from "node:url";

const FLASK_URL = process.env.FLASK_URL || "http://127.0.0.1:5000";
const PORT = process.env.PORT || 4000;
const UPSTREAM_TIMEOUT_MS = 30_000; // generous given warm/cached models — not minutes

const upload = multer({ limits: { fileSize: 20 * 1024 * 1024 } });

export function createApp({ fetchImpl = fetch } = {}) {
  const app = express();
  app.use(cors());

  app.get("/api/health", async (_req, res) => {
    try {
      const upstream = await fetchImpl(`${FLASK_URL}/health`, {
        signal: AbortSignal.timeout(UPSTREAM_TIMEOUT_MS),
      });
      const data = await upstream.json();
      res.status(upstream.status).json(data);
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

    try {
      const upstream = await fetchImpl(`${FLASK_URL}/upload`, {
        method: "POST",
        body: form,
        signal: AbortSignal.timeout(UPSTREAM_TIMEOUT_MS),
      });
      const data = await upstream.json();
      res.status(upstream.status).json(data);
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
