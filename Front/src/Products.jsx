import React, { useEffect, useState } from "react";

export default function Products({ categoryId, onAddToCart }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let url = "/api/products";
    if (categoryId) {
      url = `/api/products/category/${categoryId}`;
    }
    fetch(url, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      },
    })
      .then((res) => {
        if (!res.ok) throw new Error("Ошибка загрузки товаров");
        return res.json();
      })
      .then((data) => {
        setProducts(data);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, [categoryId]);

  if (loading) return <div>Загрузка товаров...</div>;
  if (error) return <div style={{ color: "red" }}>{error}</div>;

  function handleAddToCart(productId) {
    const token = localStorage.getItem("access_token") || localStorage.getItem("token");
    fetch("/api/carts/items", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ product_id: productId, quantity: 1 }),
      credentials: "include",
    })
      .then((res) => res.json())
      .then(() => onAddToCart(productId));
  }

  return (
    <div>
      <h2 style={{ color: "#1976d2", marginBottom: 16 }}>Каталог товаров</h2>
      <div className="product-grid">
        {products.map((product) => (
          <div key={product.id} className="product-card">
            <div className="product-name">{product.name}</div>
            <div className="product-description">{product.description}</div>
            <div className="product-price">Цена: {product.price} ₽</div>
            <button onClick={() => handleAddToCart(product.id)}>В корзину</button>
          </div>
        ))}
      </div>
    </div>
  );
}
