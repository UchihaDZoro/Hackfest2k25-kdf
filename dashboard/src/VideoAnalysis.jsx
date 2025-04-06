// src/VideoAnalysis.jsx
import React, { useState } from "react";
import axios from "axios";
import { Loader2, UploadCloud } from "lucide-react";

const VideoAnalysis = () => {
  const [inputVideo, setInputVideo] = useState(null);
  const [processedVideoUrl, setProcessedVideoUrl] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setInputVideo(URL.createObjectURL(file));
    setProcessedVideoUrl(null); // Clear previous
    setLoading(true);

    const formData = new FormData();
    formData.append("video", file);

    try {
      const response = await axios.post("http://localhost:6969/api/process-video", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setProcessedVideoUrl(`http://localhost:6969/processed/${response.data.filename}`);
    } catch (error) {
      console.error("Error processing video:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 md:p-10 max-w-7xl mx-auto">
      <h2 className="text-3xl font-bold mb-6 text-center text-gray-800">🎥 Video Analysis</h2>

      <div className="flex flex-col items-center justify-center border-4 border-dashed border-gray-300 rounded-xl p-10 bg-gray-50 hover:shadow-lg transition duration-300 ease-in-out">
        <label htmlFor="videoUpload" className="cursor-pointer text-center">
          <UploadCloud className="mx-auto text-gray-500" size={48} />
          <p className="text-lg mt-2 text-gray-600 font-medium">
            Click or drag a video file to upload
          </p>
        </label>
        <input
          id="videoUpload"
          type="file"
          accept="video/*"
          onChange={handleUpload}
          className="hidden"
        />
      </div>

      {loading && (
        <div className="flex items-center justify-center mt-6">
          <Loader2 className="animate-spin mr-2 text-blue-500" />
          <span className="text-blue-600 font-medium">Processing video...</span>
        </div>
      )}

      {(inputVideo || processedVideoUrl) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-10">
          {inputVideo && (
            <div className="bg-white shadow rounded-xl p-4">
              <h3 className="text-xl font-semibold mb-2 text-gray-700">🎬 Original Video</h3>
              <video src={inputVideo} controls className="w-full rounded-lg shadow-md" />
            </div>
          )}

          {processedVideoUrl && (
            <div className="bg-white shadow rounded-xl p-4">
              <h3 className="text-xl font-semibold mb-2 text-gray-700">🧠 Processed Video</h3>
              <video src={processedVideoUrl} controls className="w-full rounded-lg shadow-md" />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default VideoAnalysis;
