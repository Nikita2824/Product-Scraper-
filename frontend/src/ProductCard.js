import React, { useState } from "react";

const API_BASE = "http://127.0.0.1:5000/api";

export default function ProductCard({ product }) {
  const [loading, setLoading] = useState(false);

  function handleRefetch() {
    setLoading(true);
    fetch(`${API_BASE}/refetch/${product.id}`, { method: "POST" })
      .then((r) => r.json())
      .then((data) => {
        setLoading(false);
        if (data && data.product) {
          window.location.reload(); // quick and simple: reload to show updated data
        } else {
          alert("Refetch failed");
        }
      })
      .catch((e) => {
        setLoading(false);
        alert("Error: " + e);
      });
  }

  return (
    <div className="card">
      <h3>{product.title || "No title"}</h3>
      <p className="meta">
        <strong>Price:</strong> {product.price || "—"}{" "}
        <strong>Category:</strong> {product.category || "—"}
      </p>
      <p className="desc">{product.description || "No description"}</p>
      <p className="meta">
        <small>Last updated: {new Date(product.updated_at).toLocaleString()}</small>
      </p>
      <div className="card-actions">
        <a href={product.url} target="_blank" rel="noreferrer">
          Open Source URL
        </a>
        <button onClick={handleRefetch} disabled={loading}>
          {loading ? "Refetching..." : "Refetch"}
        </button>
      </div>
    </div>
  );
}
