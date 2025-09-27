// Toast уведомление
function Toast({ message, type, onClose }) {
  if (!message) return null;
  return (
    <div style={{
      position: "fixed",
      top: 24,
      right: 24,
      zIndex: 1000,
      background: type === "error" ? "#e53935" : "#43a047",
      color: "#fff",
      padding: "16px 28px",
      borderRadius: 10,
      boxShadow: "0 2px 12px #0002",
      fontWeight: 500,
      fontSize: "1.1em",
      minWidth: 180,
      transition: "opacity 0.2s"
    }}>
      {message}
      <button style={{ marginLeft: 16, background: "#fff2", color: "#fff", border: "none", borderRadius: 6, padding: "4px 10px", cursor: "pointer" }} onClick={onClose}>×</button>
    </div>
  );
}
import React, { useState } from "react";
import Cart from "./Cart";
import Orders from "./Orders";
import Login from "./Login";
import Categories from "./Categories";
import Products from "./Products";
import CartChart from "./CartChart";

export default function App() {
  const [page, setPage] = useState("catalog");
  const [isAuth, setIsAuth] = useState(!!localStorage.getItem("access_token"));
  const [categoryId, setCategoryId] = useState(null);
  const [cartItems, setCartItems] = useState([]);
  const [toast, setToast] = useState({ message: "", type: "success" });

  const handleLogin = () => {
    setIsAuth(true);
    setToast({ message: "Успешный вход!", type: "success" });
    setTimeout(() => setToast({ message: "", type: "success" }), 2500);
  };

  const handleAddToCart = async (productId) => {
    try {
      const res = await fetch("/api/carts/items", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({ product_id: productId, quantity: 1 }),
      });
      if (!res.ok) throw new Error("Ошибка добавления в корзину");
      setToast({ message: "Товар добавлен в корзину!", type: "success" });
      setTimeout(() => setToast({ message: "", type: "success" }), 2500);
      // Обновить корзину
      fetch("/api/carts", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      })
        .then((res) => res.json())
        .then((data) => {
          setCartItems((data.items || []).map((item) => ({
            name: item.product?.name || "Товар",
            price: item.product?.price || 0,
            quantity: item.quantity,
          })));
        });
    } catch (e) {
      setToast({ message: e.message, type: "error" });
      setTimeout(() => setToast({ message: "", type: "error" }), 3000);
    }
  };

  // Загружаем корзину при старте
  React.useEffect(() => {
    fetch("/api/carts", {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      },
    })
      .then((res) => res.json())
      .then((data) => {
        setCartItems((data.items || []).map((item) => ({
          name: item.product?.name || "Товар",
          price: item.product?.price || 0,
          quantity: item.quantity,
        })));
      });
  }, []);

  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  function handleRegister(e) {
    e.preventDefault();
    const form = e.target;
    const username = form.username.value;
    const password = form.password.value;
    fetch("/api/users/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.id || data.username) {
          setShowRegister(false);
          setShowLogin(true);
          setToast({ message: "Регистрация успешна! Теперь войдите.", type: "success" });
          setTimeout(() => setToast({ message: "", type: "success" }), 2500);
        } else {
          setToast({ message: "Ошибка регистрации: " + (data.detail || ""), type: "error" });
          setTimeout(() => setToast({ message: "", type: "error" }), 3000);
        }
      })
      .catch(() => {
        setToast({ message: "Ошибка регистрации", type: "error" });
        setTimeout(() => setToast({ message: "", type: "error" }), 3000);
      });
  }

  if (!isAuth || showLogin || showRegister) {
    return (
      <>
        {showLogin && (
          <Login onLogin={() => { setShowLogin(false); handleLogin(); }} />
        )}
        {showRegister && (
          <div className="login-modal" style={{ background: "#fff", borderRadius: 12, boxShadow: "0 2px 12px #1976d233", padding: 24, maxWidth: 320, margin: "32px auto", position: "relative", zIndex: 10 }}>
            <form onSubmit={handleRegister}>
              <h3 style={{ marginBottom: 16 }}>Регистрация</h3>
              <input name="username" type="text" placeholder="Логин" style={{ width: "100%", marginBottom: 12, padding: 8, borderRadius: 6, border: "1px solid #ccc" }} required />
              <input name="password" type="password" placeholder="Пароль" style={{ width: "100%", marginBottom: 12, padding: 8, borderRadius: 6, border: "1px solid #ccc" }} required />
              <button type="submit" style={{ width: "100%", background: "#43a047", color: "#fff", borderRadius: 6, padding: 10, fontWeight: 500 }}>Зарегистрироваться</button>
              <button type="button" style={{ width: "100%", marginTop: 8, background: "#eee", color: "#1976d2", borderRadius: 6, padding: 10 }} onClick={() => setShowRegister(false)}>Отмена</button>
            </form>
          </div>
        )}
        {!isAuth && !showLogin && !showRegister && (
          <div style={{ textAlign: "center", marginTop: 48 }}>
            <button style={{ background: "#1976d2", color: "#fff", marginRight: 12, borderRadius: 6, padding: "10px 24px", fontWeight: 500 }} onClick={() => setShowLogin(true)}>Авторизация</button>
            <button style={{ background: "#43a047", color: "#fff", borderRadius: 6, padding: "10px 24px", fontWeight: 500 }} onClick={() => setShowRegister(true)}>Регистрация</button>
          </div>
        )}
      </>
    );
  }

  return (
    <div className="app-container">
      <Toast message={toast.message} type={toast.type} onClose={() => setToast({ message: "", type: toast.type })} />
      <h1>Магазин</h1>
      <nav style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 24 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <button style={{ background: "#1976d2", color: "#fff", borderRadius: 6, padding: "10px 18px", fontWeight: 500 }} onClick={() => setShowLogin(true)}>
            Войти
          </button>
          <button style={{ background: "#43a047", color: "#fff", borderRadius: 6, padding: "10px 18px", fontWeight: 500 }} onClick={() => setShowRegister(true)}>
            Регистрация
          </button>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={() => setPage("catalog")}>Каталог</button>
          <button onClick={() => setPage("cart")}>Корзина</button>
          <button onClick={() => setPage("orders")}>Заказы</button>
        </div>
      </nav>
      {page === "catalog" && (
        <>
          <Categories onSelect={setCategoryId} />
          <Products categoryId={categoryId} onAddToCart={handleAddToCart} />
        </>
      )}
      {page === "cart" && <Cart />}
      {page === "orders" && <Orders />}
    </div>
  );
}
