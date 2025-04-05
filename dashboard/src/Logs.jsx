// src/Logs.jsx
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

function Logs() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetch(`http://${window.location.hostname}:6969/api/logs`)
      .then((res) => res.json())
      .then((data) => setLogs(data))
      .catch((err) => console.error("Failed to fetch logs", err));
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800">📜 Alert Logs</h1>
        </div>

        <div className="space-y-4">
          {logs.length === 0 ? (
            <p className="text-gray-600">No logs yet.</p>
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
                  {new Date(log.time).toLocaleString()}
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
