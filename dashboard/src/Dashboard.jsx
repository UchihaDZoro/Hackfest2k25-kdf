import React, { useEffect, useState } from "react";
import { io } from "socket.io-client";
import { motion, AnimatePresence } from "framer-motion";
import { BellAlertIcon } from "@heroicons/react/24/outline";

const socket = io(import.meta.env.VITE_BACKEND_URL);

function Dashboard() {
  const [currentAlert, setCurrentAlert] = useState(null);

  useEffect(() => {
    socket.on("connect", () => {
      console.log("✅ Connected to backend");
    });

    socket.on("new_alert", (data) => {
      console.log("🚨 Alert received:", data);
      setCurrentAlert({
        ...data,
        timestamp: data.timestamp || new Date().toISOString(),
      });
    });
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-6 font-sans">
      <div className="max-w-4xl mx-auto space-y-10">
        {/* Title */}
        <header className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">📹 Surveillance Dashboard</h1>
        </header>

        {/* Alert Box */}
        <div className="min-h-[60px]">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentAlert?.timestamp || "no-alert"}
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
                <span>No alerts</span>
              )}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Video Feeds */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-2xl shadow-md aspect-square overflow-hidden">
            <img
              src={`http://localhost:6924/video1`}
              alt="Camera Live"
              className="w-full h-full object-cover"
            />
          </div>
          <div className="bg-white rounded-2xl shadow-md aspect-square overflow-hidden">
            <video
              src={`http://localhost:6923/video2`}
              className="w-full h-full object-cover"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
