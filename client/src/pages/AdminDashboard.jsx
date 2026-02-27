import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import axios from "axios";
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
} from "react-leaflet";

function AdminDashboard() {
  const [heatData, setHeatData] = useState([]);
  const [ranking, setRanking] = useState([]);
  const [dashboardStats, setDashboardStats] = useState({});
  const [inventory, setInventory] = useState({});
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  // Fetch backend data
  useEffect(() => {
    axios.get("http://127.0.0.1:8000/admin/heatmap")
      .then(res => setHeatData(res.data));

    axios.get("http://127.0.0.1:8000/admin/priority-ranking")
      .then(res => setRanking(res.data));

    axios.get("http://127.0.0.1:8000/admin/dashboard")
      .then(res => setDashboardStats(res.data));

    axios.get("http://127.0.0.1:8000/debug/inventory")
      .then(res => setInventory(res.data))
      .catch(() => {});
  }, []);

  // Online/offline listener
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

  return (
    
    <div className={`admin-container ${isOnline ? "online" : "offline"}`}>
      <Navbar />
      
      <div className="top-bar">
        <h2>Admin Control Panel</h2>
        <span className="status-badge">
          {isOnline ? "🟢 Online Mode" : "🔴 Offline Mode"}
        </span>
      </div>

      {/* KPI CARDS */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <h4>Total Villages</h4>
          <p>{dashboardStats.total_villages || 0}</p>
        </div>

        <div className="kpi-card">
          <h4>Total Reports</h4>
          <p>{dashboardStats.total_reports || 0}</p>
        </div>

        <div className="kpi-card">
          <h4>Doctors Available</h4>
          <p>{inventory.doctors_available || 0}</p>
        </div>

        <div className="kpi-card">
          <h4>Malaria Kits</h4>
          <p>{inventory.malaria_kits || 0}</p>
        </div>
      </div>

      {/* MAP SECTION */}
      <div className="section">
        <h3>Outbreak Heatmap</h3>
        <MapContainer
          center={[17.125, 78.46]}
          zoom={13}
          className="map-container"
        >
          <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {heatData.map((v) => (
            <CircleMarker
              key={v.village_id}
              center={[v.latitude, v.longitude]}
              radius={Math.max(v.risk_score * 25, 8)}
              pathOptions={{
                color: v.risk_score > 0.6 ? "red" : "orange",
              }}
            >
              <Popup>
                <strong>Village:</strong> {v.village_id} <br />
                <strong>Risk:</strong> {v.risk_score.toFixed(2)} <br />
                <strong>Disease:</strong> {v.disease_id}
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      {/* PRIORITY TABLE */}
      <div className="section">
        <h3>Priority Ranking</h3>
        <table className="ranking-table">
          <thead>
            <tr>
              <th>Village</th>
              <th>Risk Score</th>
              <th>Positivity</th>
              <th>Spread</th>
            </tr>
          </thead>
          <tbody>
            {ranking.map((r, index) => (
              <tr key={index}>
                <td>{r.village_id}</td>
                <td>{r.risk_score.toFixed(3)}</td>
                <td>{(r.positivity_rate * 100).toFixed(1)}%</td>
                <td>{(r.spread_velocity * 100).toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
}

export default AdminDashboard;