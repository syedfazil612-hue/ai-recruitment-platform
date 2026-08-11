import { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import PostJobForm from "../components/PostJobForm";
import ResumeUpload from "../components/ResumeUpload";
import { API_URL } from "../config";

function Dashboard() {
  const [jobs, setJobs] = useState([]);
  const role = localStorage.getItem("role");
  const navigate = useNavigate();

  useEffect(() => {
    if (!localStorage.getItem("token")) {
      navigate("/login");
      return;
    }
    axios.get(`${API_URL}/jobs`).then((res) => {
      setJobs(res.data);
    });
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    navigate("/login");
  };

  return (
    <div
      style={{
        maxWidth: "700px",
        margin: "50px auto",
        fontFamily: "sans-serif",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h2>Dashboard ({role})</h2>
        <button onClick={handleLogout}>Logout</button>
      </div>

      <h3>Available Jobs</h3>
      {role === "recruiter" && (
        <PostJobForm onJobPosted={() => window.location.reload()} />
      )}
      {role === "candidate" && <ResumeUpload />}
      {jobs.length === 0 && <p>No jobs posted yet.</p>}
      {jobs.map((job) => (
        <div
          key={job.id}
          style={{
            border: "1px solid #ccc",
            borderRadius: "8px",
            padding: "15px",
            marginBottom: "10px",
          }}
        >
          <h4>{job.title}</h4>
          <p>{job.description}</p>

          {role === "recruiter" && (
            <button
              onClick={async () => {
                const res = await axios.get(
                  `${API_URL}/jobs/${job.id}/applicants`,
                );
                if (res.data.length === 0) {
                  alert("No applicants yet.");
                } else {
                  alert(
                    res.data
                      .map(
                        (a) =>
                          `${a.candidate_name}: ${a.score.toFixed(1)}% match`,
                      )
                      .join("\n"),
                  );
                }
              }}
            >
              View Applicants
            </button>
          )}

          {role === "candidate" && (
            <button
              onClick={async () => {
                try {
                  await axios.post(`${API_URL}/apply`, {
                    job_id: job.id,
                    candidate_id: parseInt(localStorage.getItem("user_id")),
                  });
                  alert("Applied successfully!");
                } catch (err) {
                  alert(err.response?.data?.detail || "Failed to apply.");
                }
              }}
            >
              Apply
            </button>
          )}
        </div>
      ))}
    </div>
  );
}

export default Dashboard;
