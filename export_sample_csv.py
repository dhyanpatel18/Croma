# export_sample_csv.py
import sqlite3, csv
DB = "croma_products_normalized.db"
out = "sample_products.csv"
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT rowid, name, product_url, price, catalog_rank, is_smart_tv, is_4k, panel_led, panel_qled, panel_oled, rating FROM products LIMIT 100")
rows = cur.fetchall()
cols = [d[0] for d in cur.description]
with open(out, "w", newline="", encoding="utf8") as f:
    w = csv.writer(f)
    w.writerow(cols)
    w.writerows(rows)
conn.close()
print("Wrote", out)
