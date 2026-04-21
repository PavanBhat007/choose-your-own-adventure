import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

import ThemeInput from "./ThemeInput";
import LoadingStatus from "./LoadingStatus";
import { API_BASE_URL } from "../util";

function StoryGenerator() {
  const navigate = useNavigate();

  const [theme, setTheme] = useState("");
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let pollInterval;

    if (jobId && jobStatus === "processing") {
      pollInterval = setInterval(() => {
        pollJobStatus(jobId);
      }, 5000);
    }

    return () => {
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [jobId, jobStatus]);

  const generateStory = async (theme) => {
    setLoading(true);
    setError(null);
    setTheme(theme);

    try {
      const response = await axios.post(API_BASE_URL + "/stories/create", {
        theme,
      });
      const { job_id, status } = response.data;
      setJobId(job_id);
      setJobStatus(status);

      pollJobStatus(job_id);
    } catch (e) {
      setLoading(false);
      setError("Story generation failed: " + e.message);
    }
  };

  const pollJobStatus = async (jobId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/jobs/${jobId}`);
      const { status, story_id, error: jobError } = response.data;
      setJobStatus(status);

      if (status === "completed" && story_id) {
        fetchStory(story_id);
      } else if (status === "failed" || jobError) {
        setError(jobError || "Failed to generate story");
        setLoading(false);
      }
    } catch (e) {
      if (e.response?.status !== 404) {
        setError("Failed to check story status: " + e.message);
        setLoading(false);
      }
    }
  };

  const reset = () => {
    setJobId(null);
    setJobStatus(null);
    setError(null);
    setTheme("");
    setLoading(false);
  };

  const fetchStory = async (storyId) => {
    try {
      setLoading(false);
      setJobStatus("completed");
      navigate(`/story/${storyId}`);
    } catch (e) {
      setError(`Failed to load story: ${e.message}`);
      setLoading(false);
    }
  };

  return (
    <div className="story-generator">
      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={reset}>Try Again</button>
        </div>
      )}

      {!jobId && !error && !loading && <ThemeInput onSubmit={generateStory} />}

      {loading && <LoadingStatus theme={theme} />}
    </div>
  );
}

export default StoryGenerator;
