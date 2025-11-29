# create_indexes_existing.py
import sqlite3, os
DB = os.getenv("DATABASE_URL", "croma_products_normalized.db")
if not os.path.exists(DB):
    raise SystemExit(f"DB not found: {DB}")

conn = sqlite3.connect(DB)
cur = conn.cursor()

# get existing columns
cols = [r[1] for r in cur.execute("PRAGMA table_info(products)").fetchall()]
cols_set = set(cols)
print("Existing columns:", cols)

index_map = {
    "idx_price": "price",
    "idx_rank": "catalog_rank",
    "idx_name": "name",
    "idx_is_smart": "is_smart_tv",
    "idx_is_4k": "is_4k",
    "idx_panel_led": "panel_led",
    "idx_panel_qled": "panel_qled",
    "idx_panel_oled": "panel_oled"
}

for idx_name, col in index_map.items():
    if col in cols_set:
        sql = f"CREATE INDEX IF NOT EXISTS {idx_name} ON products({col})"
        try:
            cur.execute(sql)
            print(f"Created index: {idx_name} on {col}")
        except Exception as e:
            print(f"Failed to create {idx_name} on {col}: {e}")
    else:
        print(f"Skipping index {idx_name}: column '{col}' not present")

conn.commit()
conn.close()
print("Index script finished.")
