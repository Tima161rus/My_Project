import React from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function CartChart({ items }) {
  const data = {
    labels: items.map((item) => item.name),
    datasets: [
      {
        label: "Количество",
        data: items.map((item) => item.quantity),
        backgroundColor: "#42a5f5",
      },
      {
        label: "Сумма, ₽",
        data: items.map((item) => item.price * item.quantity),
        backgroundColor: "#66bb6a",
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: "top" },
      title: { display: true, text: "Статистика корзины" },
    },
  };

  return (
    <div style={{ background: "#f5faff", borderRadius: 12, padding: 16, marginBottom: 24 }}>
      <Bar data={data} options={options} />
    </div>
  );
}
