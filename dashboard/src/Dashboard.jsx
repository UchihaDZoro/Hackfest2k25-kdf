import React, { useEffect, useState } from "react";
import { io } from "socket.io-client";
import { motion, AnimatePresence } from "framer-motion";

const socket = io(`http://10.1.7.104:6969`);

function Dashboard() {
  const [currentAlert, setCurrentAlert] = useState(null);
  const [show, setShow] = useState(false);
  const [cameraCount, setCameraCount] = useState(1);

  useEffect(() => {
    socket.on("connect", () => {
      console.log("✅ Connected to backend");
    });

    socket.on("new_alert", (data) => {
      console.log("🚨 Alert received:", data);
      setShow(false);
      setTimeout(() => {
        setCurrentAlert(data);
        setShow(true);
      }, 300);
    });
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-4xl mx-auto space-y-8">

        {/* Alert Banner */}
        <div className="relative h-20">
          <AnimatePresence mode="wait">
            {show && currentAlert && (
              <motion.div
                key={currentAlert?.id || Date.now()}
                initial={{ x: 300, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ x: -300, opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded shadow-md absolute w-full"
              >
                <strong className="font-bold">🚨 Alert: </strong>
                <span className="block sm:inline">
                  {currentAlert.message || JSON.stringify(currentAlert)}
                </span>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Camera Selector */}
        <div className="flex items-center gap-4">
          <label htmlFor="camera-count" className="text-lg font-medium">
            🎥 Number of Cameras:
          </label>
          <select
            id="camera-count"
            className="border border-gray-300 rounded px-3 py-1"
            value={cameraCount}
            onChange={(e) => setCameraCount(parseInt(e.target.value))}
          >
            {[...Array(10).keys()].map((i) => (
              <option key={i + 1} value={i + 1}>
                {i + 1}
              </option>
            ))}
          </select>
        </div>

        {/* Heatmaps Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {Array.from({ length: cameraCount }).map((_, index) => (
            <div
              key={index}
              className="bg-white rounded shadow p-4 flex items-center justify-center text-gray-600 h-48"
            >
              <span>📡 Heatmap Feed {index + 1}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
