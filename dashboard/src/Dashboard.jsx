import React, { useEffect, useState } from "react";
import { io } from "socket.io-client";
import { motion, AnimatePresence } from "framer-motion";

const socket = io(`http://10.1.7.104:6969`);

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
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* 🔺 Alert Box */}
        <div className="min-h-[60px]">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentAlert?.id || `no-alert-${selectedCamera}`}
              initial={{ x: 300, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -300, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className={`${
                currentAlert
                  ? "bg-red-100 border border-red-400 text-red-700"
                  : "bg-gray-100 border border-gray-300 text-gray-600"
              } px-4 py-3 rounded shadow-md relative`}
            >
              {currentAlert ? (
                <>
                  <strong className="font-bold">🚨 Alert:</strong>{" "}
                  {currentAlert.message}
                  <div className="absolute bottom-1 right-2 text-xs text-red-500">
                    {new Date(currentAlert.timestamp).toLocaleString()}
                  </div>
                </>
              ) : (
                <span className="text-sm">
                  No alerts for Camera {selectedCamera}
                </span>
              )}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* ⬜ Big Camera View & Heatmap */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-md flex items-center justify-center aspect-square w-full text-gray-700 text-xl font-semibold">
            <video
              src="/camera.mp4"
              autoPlay
              loop
              muted
              className="w-full h-full object-cover rounded-xl"
            />
          </div>
          <div className="bg-white rounded-xl shadow-md flex items-center justify-center aspect-square w-full text-gray-700 text-xl font-semibold">
            <video
              src="/output.mp4"
              autoPlay
              loop
              muted
              className="w-full h-full object-cover rounded-xl"
            />
          </div>
        </div>

        {/* 🔻 Camera Count Selector */}
        <div className="flex items-center gap-4 mt-4">
          <label htmlFor="camera-count" className="text-lg font-medium">
            🎥 Number of Cameras:
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

        {/* 🔻 Camera Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {Array.from({ length: cameraCount }).map((_, index) => {
            const cameraId = index + 1;
            const alert = alertsByCamera[cameraId];
            return (
              <div
                key={cameraId}
                className={`cursor-pointer bg-white rounded-xl shadow-md border-2 transition-all hover:shadow-lg ${
                  selectedCamera === cameraId
                    ? "border-blue-500 ring-2 ring-blue-300"
                    : "border-transparent"
                }`}
                onClick={() => handleCameraClick(cameraId)}
              >
                <div className="aspect-square bg-gray-100 flex items-center justify-center rounded-t-xl text-gray-600 text-lg font-medium">
                  📷 Camera {cameraId}
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
