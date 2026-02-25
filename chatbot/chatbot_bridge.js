// chatbot/chatbot_bridge.js

const express = require("express");
const cors = require("cors");

let chatbotWorker;
let responseHandlers;
let workerReady;
let nextRequestId;

/* ======================================================
   INIT FROM SERVER.JS
====================================================== */

function initBridge(deps) {
  chatbotWorker = deps.chatbotWorker;
  responseHandlers = deps.responseHandlers;
  workerReady = deps.workerReady;
  nextRequestId = deps.nextRequestId;
}

/* ======================================================
   EXPRESS APP
====================================================== */

const app = express();
app.use(cors());
app.use(express.json({ limit: "1mb" }));

/* ======================================================
   WORKER COMMUNICATION
====================================================== */

function sendToWorker(action, data) {
  return new Promise((resolve, reject) => {
    if (!workerReady()) {
      return reject(new Error("Worker not ready"));
    }

    const id = nextRequestId();
    const payload = { _requestId: id, action, ...data };

    responseHandlers.set(id, (response) => {
      if (response.success) resolve(response.data);
      else reject(new Error(response.error || "Worker error"));
    });

    chatbotWorker.stdin.write(JSON.stringify(payload) + "\n");

    setTimeout(() => {
      if (responseHandlers.has(id)) {
        responseHandlers.delete(id);
        reject(new Error("Request timeout"));
      }
    }, 30000);
  });
}

/* ======================================================
   ROUTES
====================================================== */

app.post("/api/chatbot/chat", async (req, res) => {
  try {
    const { messages = [], language = "en", role = null } = req.body;
    if (!messages.length) {
      return res.status(400).json({ error: "Messages required" });
    }
    res.json(await sendToWorker("chat", { messages, language, role }));
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post("/api/chatbot/get_response_by_key", async (req, res) => {
  try {
    res.json(await sendToWorker("get_response_by_key", req.body));
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post("/api/chatbot/tts", async (req, res) => {
  try {
    const result = await sendToWorker("tts", req.body);
    res.setHeader("Content-Type", "audio/mpeg");
    res.send(Buffer.from(result.audio, "base64"));
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get("api/chatbot/health", (req, res) => {
  res.json({
    status: "ok",
    worker: workerReady() ? "ok" : "starting"
  });
});

module.exports = { app, initBridge };