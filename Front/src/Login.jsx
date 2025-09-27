import React, { useState } from "react";

export default function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const form = new FormData();
      form.append("username", username);
      form.append("password", password);
      form.append("grant_type", "password");
  const res = await fetch("/api/users/token", {
        method: "POST",
        body: form,
      });
      if (!res.ok) throw new Error("Неверный логин или пароль");
      const data = await res.json();
      localStorage.setItem("access_token", data.access_token);
      onLogin();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{
      maxWidth: 340,
      margin: "48px auto",
      background: "#fff",
      borderRadius: 16,
      boxShadow: "0 4px 24px #1976d233",
      padding: "32px 28px",
      display: "flex",
      flexDirection: "column",
      gap: 18,
      position: "relative"
    }}>
      <h2 style={{ textAlign: "center", color: "#1976d2", marginBottom: 24, fontWeight: 700 }}>Вход</h2>
      <input
        type="text"
        placeholder="Логин"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        required
        style={{
          padding: "12px 16px",
          borderRadius: 8,
          border: "1.5px solid #1976d2",
          fontSize: "1.08em",
          marginBottom: 12,
          outline: "none",
          boxShadow: "0 1.5px 8px #1976d222",
          transition: "border 0.2s, box-shadow 0.2s",
        }}
        onFocus={e => e.target.style.border = "2px solid #43a047"}
        onBlur={e => e.target.style.border = "1.5px solid #1976d2"}
      />
      <input
        type="password"
        placeholder="Пароль"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        style={{
          padding: "12px 16px",
          borderRadius: 8,
          border: "1.5px solid #1976d2",
          fontSize: "1.08em",
          marginBottom: 12,
          outline: "none",
          boxShadow: "0 1.5px 8px #1976d222",
          transition: "border 0.2s, box-shadow 0.2s",
        }}
        onFocus={e => e.target.style.border = "2px solid #43a047"}
        onBlur={e => e.target.style.border = "1.5px solid #1976d2"}
      />
      {error && <div style={{ color: "#e53935", textAlign: "center", marginBottom: 8, fontWeight: 500 }}>{error}</div>}
      <button type="submit" disabled={loading} style={{
        marginTop: 10,
        background: "linear-gradient(90deg, #1976d2 60%, #43a047 100%)",
        color: "#fff",
        border: "none",
        borderRadius: 8,
        padding: "12px 0",
        fontWeight: 600,
        fontSize: "1.08em",
        boxShadow: "0 2px 8px #1976d222",
        cursor: loading ? "not-allowed" : "pointer",
        transition: "background 0.2s, box-shadow 0.2s"
      }}>
        {loading ? "Вход..." : "Войти"}
      </button>
    </form>
  );
}
