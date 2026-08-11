import { useState } from "react";
import axios from "axios";

export default function PostJobForm({ onJobPosted }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const recruiterId = localStorage.getItem("user_id");
      await axios.post("http://localhost:8000/jobs", {
        recruiter_id: recruiterId,
        title,
        description,
      });
      setTitle("");
      setDescription("");
      onJobPosted && onJobPosted();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to post job.");
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginTop: "20px" }}>
      <h3>Post a Job</h3>
      <input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Job title"
        required
        style={{ display: "block", marginBottom: "8px" }}
      />
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Job description"
        required
        style={{ display: "block", marginBottom: "8px", width: "300px" }}
      />
      <button type="submit">Post Job</button>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </form>
  );
}
