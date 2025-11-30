
---

# **Croma LED TV Product Scraper, API & Frontend UI**

A complete end-to-end project that **collects LED TV listings from Croma**, normalizes the scraped data into a structured database, exposes a fully searchable **FastAPI backend**, and visualizes products using a modern **React + Tailwind CSS** frontend.

This project demonstrates:

* Real-world **web scraping** & data normalization
* Designing a clean **REST API** with filters & pagination
* Serving structured data from **SQLite**
* Building a responsive, modern **product listing UI**
* Handling missing images gracefully
* Clean architecture separation: backend ↔ frontend

---

## ⭐ **Features**

### **Backend (FastAPI)**

* Product listing with:

  * pagination
  * sorting (`price`, `rank`, `rating`, `name`)
  * filters (4K, LED/QLED/OLED panel, price range, rating range, brand, etc.)
* Clean JSON responses with normalized fields
* SQLite database support
* Automatic API documentation at `/docs`
* Optional image-proxy endpoint (when real images are required)

### **Frontend (React + Tailwind CSS)**

* Responsive product grid
* Homepage carousel
* Product cards with:

  * price
  * rating (numeric)
  * panel badges
  * "View" button (opens product on Croma)
* Elegant dark UI inspired by modern e-commerce layouts

### **Data Processing**

* Rating extraction from messy text → numeric rating
* Panel-type inference (LED/QLED/OLED)
* Brand parsing from inconsistent titles
* Price cleaning & conversion

---

## 🗂️ **Project Structure**

```
/
├── app.py                         # FastAPI backend
├── croma_ui/                      # React frontend
│   ├── src/components/            # ProductCard, Grid, Carousel, Header
│   ├── src/styles/
│   └── package.json
├── fix_ratings.py                 # Script to normalize rating column
├── create_indexes.py              # (Optional) DB performance tuning
├── sample_products.csv            # (Recommended) small demo dataset
└── README.md
```

*Note: Full scraping DBs are intentionally excluded from the repository.*

---

## 🚀 **Getting Started**

### **1. Backend Setup (FastAPI)**

**Create & activate virtual environment**

Windows:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python -m venv venv
source venv/bin/activate
```

**Install dependencies**

```bash
pip install -r requirements.txt
```

**Run the backend**

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at:
**[http://127.0.0.1:8000](http://127.0.0.1:8000)**

Interactive Swagger docs:
**[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

### **2. Frontend Setup (React + Vite)**

```bash
cd croma_ui
npm install
npm run dev
```

Frontend runs at:
**[http://localhost:5173](http://localhost:5173)**

---

## 🔍 **API Overview**

### **GET /products**

Returns paginated products with filtering options.

**Supported Query Parameters**

| Parameter                  | Description                  |
| -------------------------- | ---------------------------- |
| `q`                        | Full-text search             |
| `min_price`, `max_price`   | Price range                  |
| `is_4k`                    | true / false                 |
| `panel`                    | led / qled / oled            |
| `brand`                    | Filter by brand              |
| `min_rating`, `max_rating` | Rating range                 |
| `sort_by`                  | price / rank / rating / name |
| `page`, `page_size`        | Pagination                   |

**Example:**

```
/products?is_4k-true&panel=qled&min_rating=4
```

---

## 🎨 **Frontend UI Highlights**

* Fully responsive layout
* Carousel for featured items
* Clean, card-based product display
* Dynamic badges (4K, Smart, LED/QLED/OLED)
* Graceful fallback for missing images
* Quick link to product page on Croma

---

## 📊 **Data Processing Tools**

### `fix_ratings.py`

Converts textual rating formats like `"4.2 (11)"` into numeric `4.2`.


### `create_indexes.py`

Adds helpful indexes to the database for faster queries.

---

## 🧪 **Demo Workflow**

1. Launch Backend
2. Launch Frontend
3. Open UI → Browse list & carousel
4. Apply filters (4K, rating, panel type)
5. Click **View** to open product on Croma
6. Show API output in Swagger docs

---




