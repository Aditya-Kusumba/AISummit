import { useNavigate } from "react-router-dom";

function Navbar() {
  const navigate = useNavigate();
  const role = localStorage.getItem("role");

  const handleLogout = () => {
    localStorage.clear();
    navigate("/");
  };

  return (
    <div className="navbar">
      <div className="nav-left">
        <h3>Rural Health Logistics</h3>
      </div>

      <div className="nav-right">
        <span className="role-badge">
          {role ? role.toUpperCase() : ""}
        </span>
        {role && (
          <button className="logout-btn" onClick={handleLogout}>
            Logout
          </button>
        )}
      </div>
    </div>
  );
}

export default Navbar;