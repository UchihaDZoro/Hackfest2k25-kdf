const express = require("express");
const http = require("http");
const cors = require("cors");
require("dotenv").config();
const { Server } = require("socket.io");
const fs = require("fs");
const path = require("path");

// File path for saving alerts
const ALERTS_FILE = path.join(__dirname, "alerts.json");

// Load existing alerts from file at startup
let alerts = [];
try {
  const data = fs.readFileSync(ALERTS_FILE, "utf-8");
  alerts = JSON.parse(data);
  console.log(`📁 Loaded ${alerts.length} alerts from alerts.json`);
} catch (err) {
  console.warn("⚠️ Couldn't read alerts.json, starting fresh.");
}

// Save alerts to file
const saveAlertsToFile = () => {
  fs.writeFile(ALERTS_FILE, JSON.stringify(alerts, null, 2), (err) => {
    if (err) {
      console.error("❌ Error saving alerts:", err);
    } else {
      console.log("💾 Alerts saved to alerts.json");
    }
  });
};

const PORT = process.env.PORT || 5000;
const HOST = "0.0.0.0"; // to allow local network access
const LOCAL_IP = "10.1.7.104"; // update with your actual IP if needed

const app = express();
const server = http.createServer(app);

// Initialize Socket.io
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"],
  },
});

// Middlewares
app.use(cors());
app.use(express.json());


// Handle socket events
io.on("connection", (socket) => {
  console.log(`🟢 Client connected: ${socket.id}`);

  // Listen for alert from ML
  socket.on("send_alert", (alertData) => {

    const alertWithTimestamp = {
      ...alertData,
      timestamp: new Date().toISOString(),
    };

    console.log("📨 Alert from ML:", alertWithTimestamp);
    alerts.push(alertWithTimestamp); // optional: for history/debug

    // Broadcast to all clients
    io.emit("new_alert", alertWithTimestamp);
    saveAlertsToFile();
  });

  // Debug when a socket disconnects
  socket.on("disconnect", (reason) => {
    console.log(`🔴 Client disconnected: ${socket.id} (${reason})`);
  });
});

app.get("/api/logs", (req, res) => {
  res.json(alerts.slice().reverse()); // newest first
});

// Start server
server.listen(PORT, HOST, () => {
  console.log(`🚀 Server running on http://${LOCAL_IP}:${PORT}`);
});
