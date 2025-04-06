const express = require("express");
const http = require("http");
const cors = require("cors");
require("dotenv").config();
const { Server } = require("socket.io");
const fs = require("fs");
const path = require("path");
const twilio = require("twilio");
const multer = require("multer");
const { exec } = require("child_process");

// Twilio setup
const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;
const twilioPhone = process.env.TWILIO_PHONE_NUMBER;
const receiverPhone = process.env.ALERT_RECEIVER_NUMBER;

const twilioClient = twilio(accountSid, authToken);

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

// Send SMS with alert info
const sendSMSAlert = (alertData) => {
  const message = `🚨 Alert received!\nMessage: ${alertData.message || "No details"}\nTime: ${new Date(alertData.timestamp).toLocaleString()}`;

  twilioClient.messages
    .create({
      body: message,
      from: twilioPhone,
      to: receiverPhone,
    })
    .then((msg) => {
      console.log("📲 SMS alert sent:", msg.sid);
    })
    .catch((err) => {
      console.error("❌ Failed to send SMS alert:", err);
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
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
app.use('/processed', express.static(path.join(__dirname, 'processed')));

const uploadDir = path.join(__dirname, "uploads");
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir);
  console.log("📁 'uploads' folder created");
}

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    const ext = path.extname(file.originalname);
    const uniqueName = `${Date.now()}_${Math.round(Math.random() * 1e9)}${ext}`;
    cb(null, uniqueName);
  },
});

const upload = multer({ storage });



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
    alerts.push(alertWithTimestamp);

    // Broadcast to all clients
    io.emit("new_alert", alertWithTimestamp);
    saveAlertsToFile();
    sendSMSAlert(alertWithTimestamp); // 🔔 Send SMS here
  });

  socket.on("disconnect", (reason) => {
    console.log(`🔴 Client disconnected: ${socket.id} (${reason})`);
  });
});

// API to get logs
app.get("/api/logs", (req, res) => {
  res.json(alerts.slice().reverse()); // newest first
});


app.post("/api/process-video", upload.single("video"), (req, res) => {
  const inputPath = req.file.path;
  const outputFilename = `processed_${Date.now()}.mp4`;
  const outputPath = path.join(__dirname, "processed", outputFilename);
  console.log("Uploaded video saved at:", inputPath);
  // Ensure "processed" folder exists
  if (!fs.existsSync("processed")) fs.mkdirSync("processed");

  // Run the Python script
  const command = `python process_video.py ${inputPath} ${outputPath}`;

  exec(command, (err, stdout, stderr) => {
    if (err) {
      console.error("❌ Processing failed:", err);
      return res.status(500).json({ error: "Video processing failed." });
    }

    console.log("✅ Video processed:", outputFilename);
    res.json({ filename: outputFilename });

    // Optional: Delete the uploaded input file after processing
    fs.unlinkSync(inputPath);
  });
});


// Start server
server.listen(PORT, HOST, () => {
  console.log(`🚀 Server running on http://${LOCAL_IP}:${PORT}`);
});
