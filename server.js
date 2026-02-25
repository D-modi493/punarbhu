require("dotenv").config();

const { spawn } = require("child_process");
const path = require("path");
const readline = require("readline");

const { app, initBridge } = require("./chatbot/chatbot_bridge");

const PORT = process.env.PORT || 3001;
const PROJECT_ROOT = __dirname;
// const PYTHON_PATH = path.join(PROJECT_ROOT,"chatbot" ,"chat-venv", "Scripts", "python.exe");
const PYTHON_PATH = "python"
const CHATBOT_WORKER = path.join(PROJECT_ROOT, "chatbot/chatbot_worker.py");

let chatbotWorker = null;
let workerReady = false;
let responseHandlers = new Map();
let requestId = 0;

/* ======================================================
   START PYTHON WORKER
====================================================== */

function startChatbotWorker() {
  return new Promise((resolve, reject) => {
    console.log("🚀 Starting chatbot worker...");

    chatbotWorker = spawn(PYTHON_PATH, [CHATBOT_WORKER], {
      cwd: PROJECT_ROOT,
      env: { ...process.env, PYTHONIOENCODING: "utf-8" }
    });

    const rl = readline.createInterface({
      input: chatbotWorker.stdout,
      crlfDelay: Infinity
    });

    rl.on("line", (line) => {
      try {
        const response = JSON.parse(line);

        if (response.status === "ready") {
          workerReady = true;
          // console.log("✅ Chatbot worker ready");
          resolve();
          return;
        }

        if (response._requestId !== undefined) {
          const handler = responseHandlers.get(response._requestId);
          if (handler) {
            handler(response);
            responseHandlers.delete(response._requestId);
          }
        }
      } catch (_) {}
    });

    chatbotWorker.stderr.on("data", (d) =>
      console.log("[Worker]", d.toString())
    );

    chatbotWorker.on("error", reject);
  });
}

/* ======================================================
   START SERVER (YOUR REQUIRED FORMAT)
====================================================== */

async function startServer() {
  try {
    // Start worker process
    await startChatbotWorker();

    // Init bridge AFTER worker is ready
    initBridge({
      chatbotWorker,
      responseHandlers,
      workerReady: () => workerReady,
      nextRequestId: () => requestId++
    });

    // Start Express server
    app.listen(PORT,'0.0.0.0', () => {
      console.log(`
╔════════════════════════════════════════════════════╗
║                                                    ║
║   🚀 Bhusampadan Backend Server                    ║
║                                                    ║
║   ✅ Running on: http://localhost:${PORT}              ║
║   ✅ Single URL - No background ports!             ║
║                                                    ║
║   📡 Endpoints:                                    ║
║      POST /api/chat                                ║
║      POST /api/get_response_by_key                 ║
║      POST /api/tts                                 ║
║      GET  /health                                  ║
║                                                    ║
║   ℹ️  Python worker: Process (no HTTP server)      ║
║                                                    ║
╚════════════════════════════════════════════════════╝
      `);
    });

  } catch (err) {
    console.error("❌ Failed to start server:", err.message);
    process.exit(1);
  }
}

startServer();
