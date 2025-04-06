// src/App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Dashboard from "./Dashboard";
import Logs from "./Logs";
import VideoAnalysis from "./VideoAnalysis";

function App() {
  return (
    <Router>
      <nav className="bg-white shadow p-4 flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">
          🛡️ AI Border Surveillance System
        </h1>
        <div className="space-x-4">
          <Link
            to="/"
            className="bg-green-500 hover:bg-green-600 text-white text-xl font-semibold px-4 py-2 rounded transition duration-200"
          >
            Dashboard
          </Link>
          <Link
            to="/logs"
            className="bg-green-500 hover:bg-green-600 text-white text-xl font-semibold px-4 py-2 rounded transition duration-200"
          >
            Logs
          </Link>
          <Link
            to="/video-analysis"
            className="bg-green-500 hover:bg-green-600 text-white text-xl font-semibold px-4 py-2 rounded transition duration-200"
          >
            Video Analysis
          </Link>
        </div>
      </nav>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/logs" element={<Logs />} />
        <Route path="/video-analysis" element={<VideoAnalysis />} />
      </Routes>
    </Router>
  );
}

export default App;
