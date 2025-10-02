import React, { useEffect, useState, useRef } from "react";
import ProductCard from "./ProductCard";
import "./App.css";

function App() {
  const [url, setUrl] = useState("");
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");
  const searchTimeout = useRef(null);

  const API_BASE = "http://127.0.0.1:5000/api";

  useEffect(() => {
    fetchProducts();
    // eslint-disable-next-line
  }, []);

  function fetchProducts(q = "") {
    const qs = q ? `?q=${encodeURIComponent(q)}` : "";
    fetch(`${API_BASE}/products${qs}`)
      .then((r) => r.json())
      .then((data) => setProducts(data))
      .catch((e) => console.error(e));
  }

  function handleScrape(e) {
    e.preventDefault();
    if (!url) return;
    setLoading(true);
    fetch(`${API_BASE}/scrape`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    })
      .then((r) => r.json())
      .then((data) => {
        setLoading(false);
        setUrl("");
        fetchProducts();
        if (data.error) {
          alert("Error: " + data.error);
        } else {
          alert("Scrape success!");
        }
      })
      .catch((e) => {
        setLoading(false);
        alert("Error: " + e);
      });
  }

  function handleSearchChange(e) {
    const val = e.target.value;
    setSearch(val);
    if (searchTimeout.current) clearTimeout(searchTimeout.current);
    searchTimeout.current = setTimeout(() => {
      fetchProducts(val);
    }, 500); // debounce 500ms
  }

  return (
    <div className="container">
      <h1>Product Scraper </h1>

      <form onSubmit={handleScrape} className="scrape-form">
        <input
          placeholder="Paste product URL here (example: flipkart product URL)"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Scraping..." : "Scrape & Save"}
        </button>
      </form>

      <div className="search-row">
        <input
          placeholder="Search products (title, description, category)"
          value={search}
          onChange={handleSearchChange}
        />
        <button onClick={() => fetchProducts(search)}>Search</button>
      </div>

      <div className="products-grid">
        {products.length === 0 ? (
          <p>No products yet. Scrape a URL to add one.</p>
        ) : (
          products.map((p) => <ProductCard key={p.id} product={p} />)
        )}
      </div>
    </div>
  );
}

export default App;
