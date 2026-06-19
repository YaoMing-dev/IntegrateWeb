// backend/server.test.js
import assert from "node:assert/strict";
import test from "node:test";
import { createApp } from "./server.js";

test("GET /api/health proxies Flask's health response", async () => {
  const fetchImpl = async (url) => {
    assert.equal(url, "http://127.0.0.1:5000/health");
    return new Response(JSON.stringify({ status: "ok" }), { status: 200 });
  };
  const app = createApp({ fetchImpl });
  const server = app.listen(0);
  const { port } = server.address();

  const res = await fetch(`http://127.0.0.1:${port}/api/health`);
  const body = await res.json();
  server.close();

  assert.equal(res.status, 200);
  assert.deepEqual(body, { status: "ok" });
});

test("POST /api/upload forwards field name 'image' and the original filename to Flask", async () => {
  let captured = null;
  const fetchImpl = async (url, init) => {
    captured = { url, init };
    return new Response(JSON.stringify({ fields: { ma_van_don: "123" } }), { status: 200 });
  };
  const app = createApp({ fetchImpl });
  const server = app.listen(0);
  const { port } = server.address();

  const form = new FormData();
  form.append("image", new Blob([Buffer.from("fake-bytes")]), "label.jpg");

  const res = await fetch(`http://127.0.0.1:${port}/api/upload`, {
    method: "POST",
    body: form,
  });
  const body = await res.json();
  server.close();

  assert.equal(res.status, 200);
  assert.deepEqual(body, { fields: { ma_van_don: "123" } });
  assert.equal(captured.url, "http://127.0.0.1:5000/upload");
  const forwardedFile = captured.init.body.get("image");
  assert.equal(forwardedFile.name, "label.jpg");
});

test("POST /api/upload without a file returns 400", async () => {
  const app = createApp({ fetchImpl: async () => new Response("{}") });
  const server = app.listen(0);
  const { port } = server.address();

  const res = await fetch(`http://127.0.0.1:${port}/api/upload`, { method: "POST" });
  const body = await res.json();
  server.close();

  assert.equal(res.status, 400);
  assert.ok(body.error);
});

test("POST /api/upload returns 502 when Flask is unreachable", async () => {
  const fetchImpl = async () => {
    throw new Error("connection refused");
  };
  const app = createApp({ fetchImpl });
  const server = app.listen(0);
  const { port } = server.address();

  const form = new FormData();
  form.append("image", new Blob([Buffer.from("x")]), "a.jpg");

  const res = await fetch(`http://127.0.0.1:${port}/api/upload`, {
    method: "POST",
    body: form,
  });
  const body = await res.json();
  server.close();

  assert.equal(res.status, 502);
  assert.ok(body.error);
});
