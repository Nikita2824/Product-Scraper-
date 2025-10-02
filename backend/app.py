from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re
import json

app = Flask(__name__)
CORS(app)

# SQLite DB file in backend folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(1000), unique=True, nullable=False)
    title = db.Column(db.String(500))
    description = db.Column(db.Text)
    price = db.Column(db.String(200))
    contact = db.Column(db.String(200))
    size = db.Column(db.String(200))
    category = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "contact": self.contact,
            "size": self.size,
            "category": self.category,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

# Basic scraping function (best-effort, works for many product pages)
def scrape_product(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        r = requests.get(url, headers=headers, timeout=12)
    except Exception as e:
        return {"error": f"Request failed: {e}"}
    if r.status_code != 200:
        return {"error": f"Status code: {r.status_code}"}

    soup = BeautifulSoup(r.text, "html.parser")

    # title
    title = ""
    t = soup.find("meta", property="og:title") or soup.find("title")
    if t:
        title = t.get("content") if t.has_attr("content") else t.text.strip()

    # description
    desc = ""
    d = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
    if d and d.has_attr("content"):
        desc = d["content"]

    # price: try common meta, json-ld and then text search for ₹ or Rs
    price = ""
    pmeta = soup.find("meta", property="product:price:amount") or soup.find("meta", attrs={"itemprop": "price"})
    if pmeta and pmeta.has_attr("content"):
        price = pmeta["content"]
    else:
        # check json-ld
        ld = soup.find("script", type="application/ld+json")
        if ld:
            try:
                data = json.loads(ld.string)
                if isinstance(data, dict):
                    offers = data.get("offers")
                    if isinstance(offers, dict):
                        price = offers.get("price", price)
            except Exception:
                pass
        # fallback: search rupee symbol
        if not price:
            m = re.search(r"₹\s?[\d,]+", r.text)
            if not m:
                m = re.search(r"Rs\.?\s?[\d,]+", r.text)
            if m:
                price = m.group(0)

    # contact phone (best-effort)
    contact = ""
    phone_match = re.search(r'(\+?\d{1,3}[\s-])?(\d{10})', r.text)
    if phone_match:
        contact = phone_match.group(0)

    # size/category attempt (from json-ld or page)
    size = ""
    category = ""
    if ld:
        try:
            data = json.loads(ld.string)
            if isinstance(data, dict):
                size = data.get("size", "")
                category = data.get("category", "") or data.get("itemCategory", "")
        except Exception:
            pass

    return {
        "title": title,
        "description": desc,
        "price": price,
        "contact": contact,
        "size": size,
        "category": category
    }

# --- API endpoints ---

# Submit URL to scrape
@app.route("/api/scrape", methods=["POST"])
def api_scrape():
    body = request.get_json() or {}
    url = body.get("url")
    force = body.get("force", False)
    if not url:
        return jsonify({"error": "url is required"}), 400

    existing = Product.query.filter_by(url=url).first()
    now = datetime.utcnow()
    if existing and not force:
        # if updated within 7 days, return stored
        if now - existing.updated_at < timedelta(days=7):
            return jsonify({"status": "cached", "product": existing.to_dict()})

    scraped = scrape_product(url)
    if "error" in scraped:
        return jsonify({"error": scraped["error"]}), 400

    if not existing:
        existing = Product(url=url)
        db.session.add(existing)

    existing.title = scraped.get("title")
    existing.description = scraped.get("description")
    existing.price = scraped.get("price")
    existing.contact = scraped.get("contact")
    existing.size = scraped.get("size")
    existing.category = scraped.get("category")
    existing.updated_at = now

    db.session.commit()
    return jsonify({"status": "ok", "product": existing.to_dict()})

# Get list of products, optional search q param
@app.route("/api/products", methods=["GET"])
def api_products():
    q = request.args.get("q", "").strip()
    query = Product.query
    if q:
        ilike = "%{}%".format(q)
        query = query.filter(
            (Product.title.ilike(ilike)) |
            (Product.description.ilike(ilike)) |
            (Product.category.ilike(ilike))
        )
    items = query.order_by(Product.updated_at.desc()).all()
    return jsonify([p.to_dict() for p in items])

# Get single product
@app.route("/api/products/<int:id>", methods=["GET"])
def api_product(id):
    p = Product.query.get_or_404(id)
    return jsonify(p.to_dict())

# Force refetch by id
@app.route("/api/refetch/<int:id>", methods=["POST"])
def api_refetch(id):
    p = Product.query.get_or_404(id)
    scraped = scrape_product(p.url)
    if "error" in scraped:
        return jsonify({"error": scraped["error"]}), 400
    p.title = scraped.get("title")
    p.description = scraped.get("description")
    p.price = scraped.get("price")
    p.contact = scraped.get("contact")
    p.size = scraped.get("size")
    p.category = scraped.get("category")
    p.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"status": "ok", "product": p.to_dict()})

# health
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})

if __name__ == "__main__":
    # ensure tables exist
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
