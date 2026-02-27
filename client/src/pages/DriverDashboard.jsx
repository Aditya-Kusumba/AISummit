import { useEffect, useState } from "react";
import axios from "axios";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
} from "react-leaflet";
import Navbar from "../components/Navbar";

function DriverDashboard() {
  const [routeData, setRouteData] = useState(null);
  const [heatData, setHeatData] = useState([]);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  const BATCH_ID = 1; // change if needed

  useEffect(() => {
    axios
      .post(`http://127.0.0.1:8000/admin/generate-route/${BATCH_ID}`)
      .then((res) => setRouteData(res.data));

    axios
      .get("http://127.0.0.1:8000/admin/heatmap")
      .then((res) => setHeatData(res.data));
  }, []);

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

  if (!routeData) return <div>Loading route...</div>;

  const routeVillages = routeData.route_sequence
    .map((id) => heatData.find((v) => v.village_id === id))
    .filter(Boolean);

  const polylinePositions = routeVillages.map((v) => [
    v.latitude,
    v.longitude,
  ]);

  return (
    <>
      <Navbar />

      <div className={`dashboard-container ${isOnline ? "online" : "offline"}`}>
        
        <h2>Driver Mission Dashboard</h2>

        {/* ROUTE STATS */}
        <div className="kpi-grid">
          <div className="kpi-card">
            <h4>Total Distance</h4>
            <p>{routeData.total_distance_km} km</p>
          </div>

          <div className="kpi-card">
            <h4>Travel Time</h4>
            <p>{routeData.travel_time_minutes} mins</p>
          </div>

          <div className="kpi-card">
            <h4>Treatment Time</h4>
            <p>{routeData.treatment_time_minutes} mins</p>
          </div>

          <div className="kpi-card">
            <h4>Total Mission Time</h4>
            <p>{routeData.total_mission_time_minutes} mins</p>
          </div>
        </div>

        {/* MAP */}
        <MapContainer
          center={[17.125, 78.46]}
          zoom={13}
          className="map-container"
        >
          <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {routeVillages.map((v, index) => (
            <Marker
              key={v.village_id}
              position={[v.latitude, v.longitude]}
            >
              <Popup>
                Stop {index + 1} <br />
                Village ID: {v.village_id}
              </Popup>
            </Marker>
          ))}

          <Polyline positions={polylinePositions} color="blue" />
        </MapContainer>

      </div>
    </>
  );
}

export default DriverDashboard;