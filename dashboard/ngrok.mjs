// start-ngrok.js
import ngrok from "ngrok"
import fs from "fs"
import path from "path"
import { fileURLToPath } from 'url';

// ⛏️ Recreate __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
(async function () {
  const port = 6969; // Your backend port
  const url = await ngrok.connect(port);

  console.log(`🌐 Public URL: ${url}`);

  // Path to your frontend .env
  const envPath = path.join(__dirname, '.env');

  // Update the .env file with the new URL
  fs.writeFileSync(envPath, `REACT_APP_BACKEND_URL=${url}\n`);
  console.log(`✅ Updated .env file at ${envPath}`);

  console.log("🚀 You can now start your frontend.");
})();
