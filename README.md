 Product Scraper 

A full-stack web application that scrapes product details from e-commerce websites and saves them into a database.
Users can add product URLs, search saved products, view details, refresh outdated data.

---

 Features

Scrape product details (title, description, price, category, contact if available)
Data stored in SQLite using Flask + SQLAlchemy
Search products by title, description, or category
Refetch (refresh) products if outdated
Responsive UI built with React 
Toast notifications for success & errors

---

Tech Stack

Frontend

React (Create React App)
React Icons
React Hot Toast

Backend

Flask (Python)
Flask-CORS
Flask-SQLAlchemy
BeautifulSoup4 + Requests

Database

SQLite (auto-created)

---

Project Structure

```
product-scraper/
│
├── backend/          # Flask backend
│   ├── venv/         # Virtual environment
│   ├── app.py        # Flask API
│   ├── requirements.txt
│   └── products.db   # SQLite database (auto-created)
│
├── frontend/         # React frontend
│   ├── src/          # React components
│   ├── package.json
│   
│
└── README.md
```

---

 Setup & Installation

  1)Clone the Repository

```bash
git clone  https://github.com/Nikita2824/Product-Scraper-.git
cd product-scraper
```

---

2)Backend Setup (Flask)

```bash
cd backend
# create virtual environment
python -m venv venv
# activate venv (Windows PowerShell)
.\venv\Scripts\Activate
# install dependencies
pip install -r requirements.txt
# run backend
python app.py
```

Backend runs at → `http://127.0.0.1:5000`

Test endpoint: [http://127.0.0.1:5000/api/health](http://127.0.0.1:5000/api/health)

---

3)Frontend Setup (React)

```bash
cd ../frontend
# install dependencies
npm install
# start frontend
npm start
```

Frontend runs at → `http://localhost:3000`

---

 API Endpoints

`POST /api/scrape` → Scrape a new product (requires JSON `{ "url": "..." }`)
`GET /api/products` → Get all products (supports `?q=searchTerm`)
`GET /api/products/<id>` → Get single product
`POST /api/refetch/<id>` → Refresh a product by ID
`GET /api/health` → Health check

---


 Notes

* This project is for learning/demo purposes.
* Many e-commerce sites block scraping — success depends on site structure.
* Use responsibly and respect websites’ Terms of Service.

---

 Author

Developed by Nikita Narole

GitHub: [@Nikita2824](https://github.com/Nikita2824)


---
