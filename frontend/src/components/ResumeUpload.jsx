import { useState } from "react";
import axios from "axios";

export default function ResumeUpload() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  const handleUpload = async (e) => {
    e.preventDefault();
    const candidateId = localStorage.getItem("user_id");
    const formData = new FormData();
    formData.append("candidate_id", candidateId);
    formData.append("file", file);

    try {
      await axios.post("http://127.0.0.1:8000/upload-resume", formData);
      setStatus("Resume uploaded successfully.");
    } catch (err) {
      setStatus(err.response?.data?.detail || "Upload failed.");
    }
  };

  return (
    <form onSubmit={handleUpload} style={{ marginTop: "20px" }}>
      <h3>Upload Resume</h3>
      <input
        type="file"
        accept=".pdf"
        onChange={(e) => setFile(e.target.files[0])}
        required
      />
      <button type="submit" style={{ marginLeft: "10px" }}>
        Upload
      </button>
      {status && <p>{status}</p>}
    </form>
  );
}
