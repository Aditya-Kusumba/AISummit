import { useEffect, useState } from "react";
import axios from "axios";
import Navbar from "../components/Navbar";

function OfficerDashboard() {
  const [villages, setVillages] = useState([]);
  const [diseases, setDiseases] = useState([]);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  const [form, setForm] = useState({
    village_id: "",
    disease_id: "",
    tests_done: "",
    positive_cases: "",
  });

  // Fetch villages and diseases
  useEffect(() => {
    axios.get("http://127.0.0.1:8000/villages")
      .then(res => setVillages(res.data));

    axios.get("http://127.0.0.1:8000/diseases")
      .then(res => setDiseases(res.data));
  }, []);

  // Online/offline
  useEffect(() => {
    const goOnline = () => setIsOnline(true);
    const goOffline = () => setIsOnline(false);

    window.addEventListener("online", goOnline);
    window.addEventListener("offline", goOffline);

    return () => {
      window.removeEventListener("online", goOnline);
      window.removeEventListener("offline", goOffline);
    };
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    axios.post("http://127.0.0.1:8000/ingest", [
      {
        village_id: Number(form.village_id),
        disease_id: Number(form.disease_id),
        tests_done: Number(form.tests_done),
        positive_cases: Number(form.positive_cases),
      },
    ])
    .then(() => {
      alert("Report submitted successfully!");
      setForm({
        village_id: "",
        disease_id: "",
        tests_done: "",
        positive_cases: "",
      });
    })
    .catch(() => alert("Submission failed"));
  };

  return (
    <>
      <Navbar />

      <div className={`dashboard-container ${isOnline ? "online" : "offline"}`}>
        <h2>Medical Officer Dashboard</h2>

        <div className="form-card">
          <h3>Submit Test Report</h3>

          <form onSubmit={handleSubmit}>

            <label>Village</label>
            <select
              name="village_id"
              value={form.village_id}
              onChange={handleChange}
              required
            >
              <option value="">Select Village</option>
              {villages.map(v => (
                <option key={v.id} value={v.id}>
                  {v.name}
                </option>
              ))}
            </select>

            <label>Disease</label>
            <select
              name="disease_id"
              value={form.disease_id}
              onChange={handleChange}
              required
            >
              <option value="">Select Disease</option>
              {diseases.map(d => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>

            <label>Tests Conducted</label>
            <input
              type="number"
              name="tests_done"
              value={form.tests_done}
              onChange={handleChange}
              required
            />

            <label>Positive Cases</label>
            <input
              type="number"
              name="positive_cases"
              value={form.positive_cases}
              onChange={handleChange}
              required
            />

            <button type="submit">Submit Report</button>
          </form>
        </div>
      </div>
    </>
  );
}

export default OfficerDashboard;