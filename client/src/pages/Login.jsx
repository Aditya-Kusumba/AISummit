import { useState } from "react";
import { useNavigate } from "react-router-dom";

function Login() {
  const [role, setRole] = useState("");
  const [id, setId] = useState("");
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();

    // Simple verification rule
    if (
      (role === "admin" && id.startsWith("ADM-")) ||
      (role === "driver" && id.startsWith("DRV-")) ||
      (role === "officer" && id.startsWith("MED-"))
    ) {
      localStorage.setItem("role", role);
      localStorage.setItem("userId", id);

      navigate(`/${role}`);
    } else {
      alert("Invalid ID format for selected role");
    }
  };

  return (
    <div className="login-container">
      <form className="form-card" onSubmit={handleLogin}>
        <h2>Login</h2>

        <select onChange={(e) => setRole(e.target.value)} required>
          <option value="">Select Role</option>
          <option value="admin">Admin</option>
          <option value="driver">Driver</option>
          <option value="officer">Medical Officer</option>
        </select>

        <input
          type="text"
          placeholder="Enter ID (ADM-/DRV-/MED-)"
          value={id}
          onChange={(e) => setId(e.target.value)}
          required
        />

        <button type="submit">Login</button>
      </form>
    </div>
  );
}

export default Login;