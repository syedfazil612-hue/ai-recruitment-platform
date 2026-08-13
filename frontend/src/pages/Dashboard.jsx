import { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import PostJobForm from "../components/PostJobForm";
import ResumeUpload from "../components/ResumeUpload";
import { API_URL } from "../config";

function Dashboard() {
  const [jobs, setJobs] = useState([]);
  const [applicantsByJob, setApplicantsByJob] = useState({});
  const role = localStorage.getItem("role");
  const navigate = useNavigate();

  const isRecruiter = role === "recruiter";
  const themeColor = isRecruiter ? "#2c5f8a" : "#2c8a5f";

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

  const handleViewApplicants = async (jobId) => {
    const res = await axios.get(`${API_URL}/jobs/${jobId}/applicants`);
    setApplicantsByJob((prev) => ({ ...prev, [jobId]: res.data }));
  };

  const handleApply = async (jobId) => {
    try {
      await axios.post(`${API_URL}/apply`, {
        job_id: jobId,
        candidate_id: parseInt(localStorage.getItem("user_id")),
      });
      alert("Applied successfully!");
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to apply.");
    }
  };

  return (
    <div
      style={{
        maxWidth: "700px",
        margin: "50px auto",
        fontFamily: "sans-serif",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderBottom: `3px solid ${themeColor}`,
          paddingBottom: "10px",
        }}
      >
        <h2 style={{ color: themeColor, margin: 0 }}>
          {isRecruiter ? "Recruiter Dashboard" : "Candidate Dashboard"}
        </h2>
        <button onClick={handleLogout}>Logout</button>
      </div>

      {isRecruiter ? (
        <>
          <h3 style={{ marginTop: "25px" }}>Post a Job</h3>
          <PostJobForm onJobPosted={() => window.location.reload()} />
        </>
      ) : (
        <>
          <h3 style={{ marginTop: "25px" }}>Upload Resume</h3>
          <ResumeUpload />
        </>
      )}

      <h3 style={{ marginTop: "30px" }}>
        {isRecruiter ? "Your Posted Jobs" : "Available Jobs"}
      </h3>
      {jobs.length === 0 && <p>No jobs posted yet.</p>}
      {jobs.map((job) => (
        <div
          key={job.id}
          style={{
            border: `1px solid ${themeColor}`,
            borderRadius: "8px",
            padding: "15px",
            marginBottom: "15px",
          }}
        >
          <h4 style={{ marginTop: 0 }}>{job.title}</h4>
          <p>{job.description}</p>

          {isRecruiter ? (
            <>
              <button onClick={() => handleViewApplicants(job.id)}>
                View Applicants
              </button>
              {applicantsByJob[job.id] && (
                <div style={{ marginTop: "10px" }}>
                  {applicantsByJob[job.id].length === 0 ? (
                    <p style={{ color: "#777" }}>No applicants yet.</p>
                  ) : (
                    <table
                      style={{ width: "100%", borderCollapse: "collapse" }}
                    >
                      <thead>
                        <tr
                          style={{
                            textAlign: "left",
                            borderBottom: "1px solid #ccc",
                          }}
                        >
                          <th>Candidate</th>
                          <th>Match Score</th>
                        </tr>
                      </thead>
                      <tbody>
                        {applicantsByJob[job.id].map((a) => (
                          <tr key={a.application_id}>
                            <td>{a.candidate_name}</td>
                            <td>{a.score.toFixed(1)}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              )}
            </>
          ) : (
            <button onClick={() => handleApply(job.id)}>Apply</button>
          )}
        </div>
      ))}
    </div>
  );
}

export default Dashboard;
