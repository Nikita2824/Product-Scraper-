import React from "react";
import Navbar from "./components/Navbar";
import ProductCard from "./components/ProductCard";
import "./App.css";

// Example product data
const products = [
  { id: 1, name: "Product 1", price: "$19", description: "Awesome product", link: "#" },
  { id: 2, name: "Product 2", price: "$29", description: "Another product", link: "#" },
  { id: 3, name: "Product 3", price: "$39", description: "Great item", link: "#" },
];

function App() {
  return (
    <div>
      <Navbar />
      <div className="container">
        <h1>Our Products</h1>
        <div className="products-grid">
          {products.map((product, index) => (
            <ProductCard key={product.id} product={product} index={index} />
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
