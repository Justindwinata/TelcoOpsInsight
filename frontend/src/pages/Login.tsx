import { FormEvent, useState } from "react";
import { useAuth } from "../auth/AuthContext";

export function Login() {
  const { login } = useAuth();
  const [username, setUsername] = useState("noc_manager");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(username, password);
    } catch {
      setError("Login failed. Use a valid demo username and password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-screen">
      <section className="login-panel">
        <span className="eyebrow">NusaTel Digital Network</span>
        <h1>TelcoOps Insight</h1>
        <p className="muted">Local authentication prototype for the service assurance dashboard.</p>
        <form className="login-form" onSubmit={submit}>
          <label>
            Username
            <select value={username} onChange={(event) => setUsername(event.target.value)}>
              <option value="noc_manager">NOC Manager</option>
              <option value="service_assurance">Service Assurance Lead</option>
              <option value="field_ops">Field Operations Lead</option>
              <option value="analyst">Analyst</option>
              <option value="viewer">Viewer</option>
            </select>
          </label>
          <label>
            Password
            <input value={password} type="password" onChange={(event) => setPassword(event.target.value)} />
          </label>
          <button className="primary-button" type="submit" disabled={loading}>
            {loading ? "Signing in..." : "Sign In"}
          </button>
          {error ? <p className="permission-message">{error}</p> : null}
        </form>
      </section>
    </main>
  );
}
