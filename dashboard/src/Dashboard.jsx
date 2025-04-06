import React, { useEffect, useState } from "react";
import { io } from "socket.io-client";
import { motion, AnimatePresence } from "framer-motion";
import { BellAlertIcon, CameraIcon } from "@heroicons/react/24/outline";

const socket = io(import.meta.env.VITE_BACKEND_URL);

function Dashboard() {
  const [currentAlert, setCurrentAlert] = useState(null);
  const [alertsByCamera, setAlertsByCamera] = useState({});
  const [cameraCount, setCameraCount] = useState(1);
  const [selectedCamera, setSelectedCamera] = useState(1);

  useEffect(() => {
    socket.on("connect", () => {
      console.log("✅ Connected to backend");
    });

    socket.on("new_alert", (data) => {
      console.log("🚨 Alert received:", data);
      if (!data.message || !data.message.includes("Camera")) return;
      const cameraMatch = data.message.match(/Camera (\d+)/);
      if (!cameraMatch) return;

      const cameraId = parseInt(cameraMatch[1]);
      setAlertsByCamera((prev) => ({
        ...prev,
        [cameraId]: {
          ...data,
          timestamp: data.timestamp || new Date().toISOString(),
        },
      }));

      if (cameraId === selectedCamera) {
        setCurrentAlert({
          ...data,
          timestamp: data.timestamp || new Date().toISOString(),
        });
      }
    });
  }, [selectedCamera]);

  const handleCameraClick = (index) => {
    setSelectedCamera(index);
    setCurrentAlert(alertsByCamera[index] || null);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6 font-sans">
      <div className="max-w-7xl mx-auto space-y-10">
        {/* 🧠 Title */}
        <header className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">📹 Surveillance Dashboard</h1>
        </header>

        {/* 🚨 Alert Box */}
        <div className="min-h-[60px]">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentAlert?.id || `no-alert-${selectedCamera}`}
              initial={{ x: 300, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -300, opacity: 0 }}
              transition={{ duration: 0.4 }}
              className={`${
                currentAlert
                  ? "bg-red-100 border border-red-300 text-red-800"
                  : "bg-white border border-gray-300 text-gray-600"
              } px-5 py-4 rounded-xl shadow-md relative text-sm md:text-base`}
            >
              {currentAlert ? (
                <>
                  <div className="flex items-center gap-2">
                    <BellAlertIcon className="w-5 h-5 text-red-500" />
                    <span className="font-semibold">{currentAlert.message}</span>
                  </div>
                  <div className="absolute bottom-1 right-3 text-xs text-red-400">
                    {new Date(currentAlert.timestamp).toLocaleString()}
                  </div>
                </>
              ) : (
                <span>No alerts for Camera {selectedCamera}</span>
              )}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* 🎥 Camera Views */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-2xl shadow-md aspect-square overflow-hidden">
            <img
              src={`http://localhost:6924/video${selectedCamera}`}
              alt={`Camera ${selectedCamera} Live`}
              className="w-full h-full object-cover"
            />
          </div>
          <div className="bg-white rounded-2xl shadow-md aspect-square overflow-hidden">
            <video
              src="/output.mp4"
              autoPlay
              loop
              muted
              className="w-full h-full object-cover"
            />
          </div>
        </div>

        {/* 🔧 Controls */}
        <div className="flex items-center gap-4">
          <label htmlFor="camera-count" className="text-lg font-medium text-gray-700 flex items-center gap-2">
            <CameraIcon className="w-5 h-5" /> Number of Cameras:
          </label>
          <select
            id="camera-count"
            className="border border-gray-300 rounded px-3 py-1 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
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

        {/* 🗂 Camera Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {Array.from({ length: cameraCount }).map((_, index) => {
            const cameraId = index + 1;
            const alert = alertsByCamera[cameraId];
            return (
              <div
                key={cameraId}
                className={`cursor-pointer bg-white rounded-xl shadow hover:shadow-lg transition border-2 ${
                  selectedCamera === cameraId
                    ? "border-blue-500 ring-2 ring-blue-300"
                    : "border-transparent"
                }`}
                onClick={() => handleCameraClick(cameraId)}
              >
                <div className="aspect-square overflow-hidden rounded-t-xl">
                  <img
                    src={`http://localhost:6924/video${cameraId}`}
                    alt={`Camera ${cameraId}`}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="px-3 py-2 text-sm">
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={alert?.id || Date.now() + cameraId}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.3 }}
                      className={`${
                        alert
                          ? "bg-red-50 border border-red-300 text-red-700"
                          : "bg-gray-50 text-gray-500"
                      } px-2 py-1 rounded`}
                    >
                      {alert ? (
                        <>
                          <strong className="font-semibold">Alert:</strong>{" "}
                          {alert.message}
                          <div className="text-xs text-red-400 mt-1">
                            {new Date(alert.timestamp).toLocaleString()}
                          </div>
                        </>
                      ) : (
                        <span>No alert</span>
                      )}
                    </motion.div>
                  </AnimatePresence>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
