import React, { useEffect, useState } from "react";
import axios from "axios";

function Logs() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await axios.get(`${import.meta.env.VITE_BACKEND_URL}/api/logs`);
        console.log("Fetched logs:", response.data);
        setLogs(response.data);
      } catch (error) {
        console.error("Failed to fetch logs", error);
      }
    };

    fetchLogs();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800">📜 Alert Logs</h1>
        </div>

        <div className="space-y-4">
          {logs.length === 0 ? (
            <p className="text-center text-gray-500 italic">No logs yet. You're all clear 🚀</p>
          ) : (
            logs.map((log, index) => (
              <div
                key={index}
                className="bg-white p-4 rounded shadow border-l-4 border-red-400"
              >
                <p className="font-semibold text-gray-700">
                  {log.message || JSON.stringify(log)}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  {new Date(log.timestamp).toLocaleString()}
                </p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default Logs;
