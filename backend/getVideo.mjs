import express from 'express';
import fetch from 'node-fetch';
import cors from "cors";
import { spawn } from 'child_process';

const app = express();
const PORT = 6924;

app.use(cors());

const MOBILE_STREAM_URL = 'http://192.168.68.38:8080/video'; // your phone's stream

// ✅ Route for phone camera stream
app.get('/video2', async (req, res) => {
  try {
    const streamRes = await fetch(MOBILE_STREAM_URL);
    if (!streamRes.ok || !streamRes.body) {
      return res.status(500).send('Failed to fetch mobile stream');
    }

    res.setHeader('Content-Type', streamRes.headers.get('content-type') || 'multipart/x-mixed-replace');
    streamRes.body.pipe(res);
  } catch (err) {
    console.error('Error streaming from phone:', err.message);
    res.status(500).send('Stream error');
  }
});

// ✅ Route for laptop webcam stream
app.get('/video1', (req, res) => {
  // Set MJPEG stream headers
  res.setHeader('Content-Type', 'multipart/x-mixed-replace; boundary=frame');

  // Start FFmpeg process to capture webcam and output MJPEG
  const ffmpeg = spawn('ffmpeg', [
    '-f', 'dshow',
    '-i', 'video=HP Wide Vision HD Camera',
    '-f', 'mjpeg',
    '-q:v', '5',           // Image quality (lower is better quality)
    '-r', '15',            // Frame rate
    '-boundary_tag', 'frame',
    '-loglevel', 'error',  // Optional: hide warnings
    '-'
  ]);

  ffmpeg.stdout.pipe(res);

  // Handle errors
  ffmpeg.stderr.on('data', (data) => {
    console.error(`FFmpeg stderr: ${data}`);
  });

  // Clean up on client disconnect
  req.on('close', () => {
    ffmpeg.kill('SIGINT');
  });
});


app.listen(PORT, () => {
  console.log(`🚀 Server running at http://localhost:${PORT}/video1 and /video2`);
});
