import React, { useState, useEffect } from "react";

function Orders() {
  const [orders, setOrders] = useState([]);
  useEffect(() => {
    fetch("/api/orders", { credentials: "include" })
      .then((res) => res.json())
      .then((data) => setOrders(data))
      .catch(() => setOrders([]));
  }, []);

  return (
    <div>
      <h2 style={{ color: "#1976d2", marginBottom: 16 }}>Ваши заказы</h2>
      {orders.length === 0 ? (
        <div className="empty-orders">Нет заказов</div>
      ) : (
        <div className="orders-grid">
          {orders.map((order) => (
            <div key={order.id} className="order-card">
              <div className="order-title">Заказ №{order.id}</div>
              <div className="order-status">Статус: <span>{order.status}</span></div>
              <div className="order-price">Сумма: {order.total_price} ₽</div>
              <div className="order-items">
                <span>Товары:</span>
                <ul>
                  {order.items.map((item) => (
                    <li key={item.id} className="order-item">{item.product_name} <span>x{item.quantity}</span></li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Orders;
