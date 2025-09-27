import React, { useEffect, useState } from "react";

export default function Categories({ onSelect }) {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [active, setActive] = useState(null);

  useEffect(() => {
    fetch("/api/categories", {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      },
    })
      .then((res) => {
        if (!res.ok) throw new Error("Ошибка загрузки категорий");
        return res.json();
      })
      .then((data) => {
        setCategories(data);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  function handleSelect(id) {
    setActive(id);
    onSelect(id);
  }

  if (loading) return <div>Загрузка категорий...</div>;
  if (error) return <div style={{ color: "#e53935", marginBottom: 12 }}>{error}</div>;

  return (
    <div style={{ marginBottom: 20 }}>
      <b style={{ color: "#1976d2", fontWeight: 600, fontSize: "1.08em" }}>Категории:</b>
      <div className="categories-bar">
        <button className={`category-btn${active === null ? " active" : ""}`} onClick={() => handleSelect(null)}>
          Все
        </button>
        {categories.map((cat) => (
          <button
            key={cat.id}
            className={`category-btn${active === cat.id ? " active" : ""}`}
            onClick={() => handleSelect(cat.id)}
          >
            {cat.name}
          </button>
        ))}
      </div>
    </div>
  );
}
