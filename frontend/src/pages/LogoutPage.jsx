import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function LogoutPage() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const run = async () => {
      await logout();
      navigate("/login", { replace: true });
    };

    run();
  }, [logout, navigate]);

  return (
    <div className="auth-page">
      <div className="card auth-card">
        <h1>Logging out...</h1>
      </div>
    </div>
  );
}
