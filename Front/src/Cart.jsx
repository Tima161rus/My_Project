  // Оформление заказа
  const handleOrder = async () => {
    try {
      const res = await fetch("/api/orders", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({ items: items.map(i => ({ product_id: i.id, quantity: i.quantity })) }),
      });
      if (!res.ok) throw new Error("Ошибка оформления заказа");
      alert("Заказ успешно оформлен!");
      setItems([]);
    } catch (e) {
      alert(e.message);
    }
  };
import React, { useState, useEffect } from "react";
import CartChart from "./CartChart";

export default function Cart() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // URL API
  const API_URL = "/api/carts";

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setError("Для просмотра корзины выполните вход.");
      setLoading(false);
      return;
    }
    setLoading(true);
    fetch(API_URL, {
      credentials: "include",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then(async (res) => {
        if (!res.ok) {
          const text = await res.text();
          throw new Error(`Ошибка загрузки корзины (${res.status}): ${text}`);
        }
        return res.json();
      })
      .then((data) => {
        setItems((data.items || []).map((item) => ({
          id: item.id,
          product_name: item.product?.name || item.product_name || "Товар",
          price: item.product && typeof item.product.price === "number" ? item.product.price : (item.price || 0),
          quantity: item.quantity || 1,
          total_price_product: typeof item.total_price_product === "number" ? item.total_price_product : (item.price * item.quantity),
        })));
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  const handleDelete = async (itemId) => {
    try {
      const res = await fetch(`/api/carts/items/${itemId}`, {
        method: "DELETE",
        credentials: "include",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      if (!res.ok) throw new Error("Ошибка удаления товара");
      setItems((prev) => prev.filter((item) => item.id !== itemId));
    } catch (e) {
      alert(e.message);
    }
  };

  return (
    <div>
      <h2 style={{ color: "#1976d2", marginBottom: 16 }}>Корзина</h2>
      {items.length === 0 ? (
        <div style={{ color: "#aaa", fontSize: "1.1em", marginTop: 32 }}>Корзина пуста</div>
      ) : (
        <table className="cart-table">
          <thead>
            <tr>
              <th>Товар</th>
              <th>Цена</th>
              <th>Кол-во</th>
              <th>Сумма</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td>{item.product_name}</td>
                <td>{item.price} ₽</td>
                <td>{item.quantity}</td>
                <td>{item.total_price_product} ₽</td>
                <td>
                  <button className="cart-remove-btn" onClick={() => handleDelete(item.id)}>Удалить</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <div style={{ fontWeight: "bold", fontSize: 20, color: "#1976d2", marginTop: 18 }}>
        Итого: {items.reduce((sum, item) => sum + item.total_price_product, 0)} ₽
      </div>
      <button style={{ marginTop: 20, background: "#43a047", color: "#fff", border: "none", borderRadius: 6, padding: "10px 24px", fontSize: 16, cursor: "pointer" }} onClick={handleOrder} disabled={items.length === 0}>
        Оформить заказ
      </button>
    </div>
  );
}
