# app.py
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
from fastapi.responses import StreamingResponse
from fastapi import HTTPException
from urllib.parse import unquote

MAX_IMAGE_BYTES = 6 * 1024 * 1024 
# ---------- Config ----------
from typing import Optional, List, Dict, Any
import sqlite3
import os

DATABASE_URL = os.getenv("DATABASE_URL", "croma_products_normalized.db")
DEFAULT_PAGE_SIZE = 24
MAX_PAGE_SIZE = 200

# ---------- App ----------
app = FastAPI(title="Croma LED TV Products API",
              description="API to serve normalized Croma LED TV product data for demo UI and filters.",
              version="1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Models ----------
class Product(BaseModel):
    product_url: Optional[str] = None
    name: Optional[str] = None
    price: Optional[float] = None
    catalog_rank: Optional[int] = None
    is_smart_tv: Optional[bool] = None
    is_4k: Optional[bool] = None
    panel_led: Optional[bool] = None
    panel_qled: Optional[bool] = None
    panel_oled: Optional[bool] = None

    rating: Optional[float] = None
    rating_text_raw: Optional[str] = Field(None, alias="rating_text_raw")

    plp_product_tile_src: Optional[str] = Field(None, alias="plp_product_tile_src")
    brand: Optional[str] = None
    discount: Optional[str] = None
    delivery_pincode_text: Optional[str] = None


class PagedResult(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[Product]

def get_db_connection():
    if not os.path.exists(DATABASE_URL):
        raise FileNotFoundError(f"Database not found: {DATABASE_URL}")
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

def get_table_columns(conn, table_name="products"):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table_name})")
    rows = cur.fetchall()
    return set([r[1] for r in rows])  # column name at index 1

def build_where_clauses(params: Dict[str, Any], available_cols: set):
    """
    Build SQL WHERE clause and parameters, only using columns that exist in the DB.
    params keys (possible): q, min_price, max_price, panel, is_smart_tv, is_4k, brand,
    min_rating, max_rating, min_screen, max_screen, hdmi_min, usb_min, warranty_min, in_stock
    """
    clauses = []
    args = []

    q = params.get("q")
    if q:
        # Use name and product_url if present
        sub = []
        q_like = f"%{q}%"
        if "name" in available_cols:
            sub.append("name LIKE ?")
            args.append(q_like)
        if "product_url" in available_cols:
            sub.append("product_url LIKE ?")
            args.append(q_like)
        if sub:
            clauses.append("(" + " OR ".join(sub) + ")")

    # Price range
    if "price" in available_cols:
        if params.get("min_price") is not None:
            clauses.append("price >= ?"); args.append(params["min_price"])
        if params.get("max_price") is not None:
            clauses.append("price <= ?"); args.append(params["max_price"])

    # Panel type
    panel = params.get("panel")
    if panel and panel.lower() in ("led","qled","oled"):
        if panel.lower() == "led" and "panel_led" in available_cols:
            clauses.append("panel_led = 1")
        elif panel.lower() == "qled" and "panel_qled" in available_cols:
            clauses.append("panel_qled = 1")
        elif panel.lower() == "oled" and "panel_oled" in available_cols:
            clauses.append("panel_oled = 1")

    # Boolean flags
    if "is_smart_tv" in available_cols and params.get("is_smart_tv") is not None:
        clauses.append("is_smart_tv = ?"); args.append(1 if params["is_smart_tv"] else 0)
    if "is_4k" in available_cols and params.get("is_4k") is not None:
        clauses.append("is_4k = ?"); args.append(1 if params["is_4k"] else 0)

    
    # Brand
    if "brand" in available_cols and params.get("brand"):
        clauses.append("brand = ?"); args.append(params["brand"])

    # Rating range
    if "rating" in available_cols:
        if params.get("min_rating") is not None:
            clauses.append("rating >= ?"); args.append(params["min_rating"])
        if params.get("max_rating") is not None:
            clauses.append("rating <= ?"); args.append(params["max_rating"])

    # Screen size
    if "screen_size_inch" in available_cols:
        if params.get("min_screen") is not None:
            clauses.append("screen_size_inch >= ?"); args.append(params["min_screen"])
        if params.get("max_screen") is not None:
            clauses.append("screen_size_inch <= ?"); args.append(params["max_screen"])

    # HDMI / USB ports (minimum)
    if "hdmi_ports" in available_cols and params.get("hdmi_min") is not None:
        clauses.append("hdmi_ports >= ?"); args.append(params["hdmi_min"])
    if "usb_ports" in available_cols and params.get("usb_min") is not None:
        clauses.append("usb_ports >= ?"); args.append(params["usb_min"])

    # Warranty months minimum
    if "warranty_months" in available_cols and params.get("warranty_min") is not None:
        clauses.append("warranty_months >= ?"); args.append(params["warranty_min"])

    # In stock / availability (if column exists)
    if "in_stock" in available_cols and params.get("in_stock") is not None:
        clauses.append("in_stock = ?"); args.append(1 if params["in_stock"] else 0)

    where_sql = " AND ".join(clauses) if clauses else ""
    if where_sql:
        where_sql = "WHERE " + where_sql
    return where_sql, args

def build_order_clause(sort_by: Optional[str], sort_dir: str, available_cols: set):
    allowed_map = {
        "price": "price",
        "rank": "catalog_rank",
        "rating": "rating",
        "name": "name"
    }
    if not sort_by or sort_by not in allowed_map:
        # default fallback if catalog_rank exists else price
        if "catalog_rank" in available_cols:
            return "ORDER BY catalog_rank ASC"
        elif "price" in available_cols:
            return "ORDER BY price ASC"
        else:
            return ""
    col = allowed_map[sort_by]
    if col not in available_cols:
        # fallback to price or rank if requested col missing
        if "catalog_rank" in available_cols:
            col = "catalog_rank"
        elif "price" in available_cols:
            col = "price"
        else:
            return ""
    dir_sql = "ASC" if sort_dir.lower() == "asc" else "DESC"
    return f"ORDER BY {col} {dir_sql}"

import re

def row_to_product(row):
    # row: sqlite3.Row (can use row['colname'])
    def getc(k):
        try:
            return row[k]
        except Exception:
            return None

    def as_bool(v):
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return bool(v)
        s = str(v).strip().lower()
        if s in ("1", "true", "yes", "y", "t"):
            return True
        if s in ("0", "false", "no", "n", "f"):
            return False
        return None

    def parse_price():
        val = getc("price") or getc("amount") or getc("amount 2")
        if val is None or str(val).strip() == "":
            return None
        ps = str(val).replace(",", "").strip()
        ps = re.sub(r"[^\d\.]", "", ps)
        if ps == "":
            return None
        try:
            return float(ps)
        except Exception:
            return None

    def parse_rating():
        rnum = getc("rating")
        if rnum is not None and str(rnum).strip() != "":
            try:
                return float(rnum)
            except Exception:
                return None
        raw = getc("rating-text") or getc("rating_text") or getc("rating-text-icon") or getc("cp-rating href")
        if not raw:
            return None
        m = re.search(r"(\d+(?:\.\d+)?)", str(raw))
        if not m:
            return None
        try:
            return float(m.group(1))
        except Exception:
            return None

    p = {}
    p["rowid"] = getc("rowid") or getc("id")
    p["product_url"] = getc("product_url")
    p["name"] = getc("name") or getc("product-title")
    p["price"] = parse_price()
    p["catalog_rank"] = getc("catalog_rank")

    # boolean flags
    p["is_smart_tv"] = as_bool(getc("is_smart_tv"))
    p["is_4k"] = as_bool(getc("is_4k"))
    p["panel_led"] = as_bool(getc("panel_led"))
    p["panel_qled"] = as_bool(getc("panel_qled"))
    p["panel_oled"] = as_bool(getc("panel_oled"))

    # image alias (normalize spaced column)
    p["plp_product_tile_src"] = (
        getc("plp_product_tile src") or getc("plp_product_tile_src") or getc("plp_product_tile")
    )

    # rating and raw rating text
    p["rating"] = parse_rating()
    p["rating_text_raw"] = getc("rating-text") or getc("rating_text") or None

    # other fields
    p["discount"] = getc("discount")
    p["delivery_pincode_text"] = getc("delivery-pincode-text") or getc("delivery_pincode_text")
    p["brand"] = getc("brand")

    return p


# ---------- Routes ----------
@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok", "db": DATABASE_URL}

# in app.py - replace the function signature and params mapping for get_products

@app.get("/products", response_model=PagedResult, tags=["products"])
def get_products(
    q: Optional[str] = Query(None, description="Full-text search on name or url"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    panel: Optional[str] = Query(None, description="led|qled|oled"),
    is_smart_tv: Optional[bool] = Query(None, description="Filter smart TVs (boolean)"),
    is_4k: Optional[bool] = Query(None),
    brand: Optional[str] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0),
    max_rating: Optional[float] = Query(None, ge=0),
    min_screen: Optional[float] = Query(None, ge=0),
    max_screen: Optional[float] = Query(None, ge=0),
    hdmi_min: Optional[int] = Query(None, ge=0),
    usb_min: Optional[int] = Query(None, ge=0),
    warranty_min: Optional[int] = Query(None, ge=0),
    in_stock: Optional[bool] = Query(None),
    sort_by: Optional[str] = Query(None, description="price|rank|rating|name"),
    sort_dir: Optional[str] = Query("asc", description="asc or desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE)
):
    params = {
        "q": q,
        "min_price": min_price,
        "max_price": max_price,
        "panel": panel,
        "is_smart_tv": is_smart_tv,
        "is_4k": is_4k,
        "brand": brand,
        "min_rating": min_rating,
        "max_rating": max_rating,
        "min_screen": min_screen,
        "max_screen": max_screen,
        "hdmi_min": hdmi_min,
        "usb_min": usb_min,
        "warranty_min": warranty_min,
        "in_stock": in_stock
    }
    

    conn = get_db_connection()
    try:
        cols = get_table_columns(conn, "products")
        where_sql, args = build_where_clauses(params, cols)
        order_sql = build_order_clause(sort_by, sort_dir, cols)

        offset = (page - 1) * page_size
        limit = page_size

        count_sql = f"SELECT COUNT(*) as cnt FROM products {where_sql}"
        select_sql = f"SELECT * FROM products {where_sql} {order_sql} LIMIT ? OFFSET ?"

        cur = conn.cursor()
        cur.execute(count_sql, args)
        total = cur.fetchone()["cnt"]
        cur.execute(select_sql, args + [limit, offset])
        rows = cur.fetchall()
        items = [row_to_product(r) for r in rows]
        return {"total": total, "page": page, "page_size": page_size, "items": items}
    finally:
        conn.close()

@app.get("/products/{encoded_path}", response_model=Product, tags=["products"])
def get_product_by_encoded(encoded_path: str):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM products WHERE product_url = ?", (encoded_path,))
        row = cur.fetchone()
        if not row:
            cur.execute("SELECT * FROM products WHERE product_url LIKE ?", (f"%{encoded_path}%",))
            row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Product not found")
        return row_to_product(row)
    finally:
        conn.close()

# Metadata endpoints
@app.get("/meta/brands", tags=["meta"])
def list_brands(limit: int = Query(200)):
    conn = get_db_connection()
    try:
        cols = get_table_columns(conn, "products")
        if "brand" not in cols:
            return {"brands": []}
        cur = conn.cursor()
        cur.execute("SELECT brand, COUNT(*) as cnt FROM products GROUP BY brand ORDER BY cnt DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        return {"brands": [{"brand": r[0], "count": r[1]} for r in rows]}
    finally:
        conn.close()

@app.get("/meta/panels", tags=["meta"])
def list_panels():
    conn = get_db_connection()
    try:
        cols = get_table_columns(conn, "products")
        panels = []
        if "panel_led" in cols:
            panels.append({"type":"LED","count": conn.execute("SELECT COUNT(*) FROM products WHERE panel_led=1").fetchone()[0]})
        if "panel_qled" in cols:
            panels.append({"type":"QLED","count": conn.execute("SELECT COUNT(*) FROM products WHERE panel_qled=1").fetchone()[0]})
        if "panel_oled" in cols:
            panels.append({"type":"OLED","count": conn.execute("SELECT COUNT(*) FROM products WHERE panel_oled=1").fetchone()[0]})
        return {"panel_types": panels}
    finally:
        conn.close()

@app.get("/meta/stats", tags=["meta"])
def stats(brand: Optional[str] = Query(None)):
    conn = get_db_connection()
    try:
        cols = get_table_columns(conn, "products")
        cur = conn.cursor()
        where = ""
        args = []
        if brand and "brand" in cols:
            where = "WHERE brand = ?"; args = [brand]

        # average price
        avg_price = None
        if "price" in cols:
            cur.execute(f"SELECT AVG(price) FROM products {where}", args)
            avg_price = cur.fetchone()[0]

        # count
        cur.execute(f"SELECT COUNT(*) FROM products {where}", args)
        count = cur.fetchone()[0]

        # top 5 by rating if rating column exists
        top_by_rating = []
        if "rating" in cols:
            cur.execute(f"SELECT name, price, rating FROM products {where} ORDER BY rating DESC LIMIT 5", args)
            top_by_rating = [{"name": r[0], "price": r[1], "rating": r[2]} for r in cur.fetchall()]

        return {"count": count, "avg_price": avg_price, "top_by_rating": top_by_rating}
    finally:
        conn.close()
@app.get("/image-proxy")
async def image_proxy(url: str):
    if not url:
        raise HTTPException(status_code=400, detail="Missing url")
    u = unquote(url).strip()

    # sanitize / fix scheme-less or relative URLs
    if u.startswith("//"):
        u = "https:" + u
    if u.startswith("/"):
        u = "https://www.croma.com" + u
    if not u.startswith("http://") and not u.startswith("https://"):
        u = "https://" + u

    # quick sanitization for broken '?tr=' double question marks
    if '?' in u:
        parts = u.split('?', 1)
        tail = parts[1].replace('?tr=', '&tr=')
        u = parts[0] + '?' + tail

    headers = {"User-Agent": "Mozilla/5.0 (compatible)", "Referer": "https://www.croma.com"}
    timeout = httpx.Timeout(10.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout, headers=headers, follow_redirects=True) as client:
        try:
            resp = await client.get(u)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Upstream fetch failed: {e}")

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Upstream returned non-200")
    ctype = resp.headers.get("content-type", "application/octet-stream")
    content = resp.content
    if len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image too large")
    return StreamingResponse(iter([content]), media_type=ctype)