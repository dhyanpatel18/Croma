# fix_ratings.py
import sqlite3, os, shutil, re, sys

# set DB name if different
DB = os.getenv("DATABASE_URL", "croma_products_normalized.db")
if not os.path.exists(DB):
    print("DB not found:", DB)
    sys.exit(1)

# backup
bak = DB + ".bak"
if not os.path.exists(bak):
    shutil.copyfile(DB, bak)
    print("Backup created:", bak)
else:
    print("Backup exists:", bak)

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# ensure column rating exists
cols = [r["name"] for r in cur.execute("PRAGMA table_info(products)").fetchall()]
if "rating" not in cols:
    cur.execute('ALTER TABLE products ADD COLUMN rating REAL')
    conn.commit()
    print("Added rating column")

# regex to extract numeric token
num_re = re.compile(r"(\d+(?:\.\d+)?)")

updated = 0
# iterate rows and populate rating from rating-text (if present)
for row in cur.execute('SELECT rowid, "rating-text", "rating-text-icon", rating FROM products'):
    rowid = row["rowid"]
    # skip if rating already present
    if row["rating"] is not None and str(row["rating"]).strip() != "":
        continue
    raw = row["rating-text"]
    if not raw:
        # sometimes review count is in different col; skip if no rating-text
        continue
    s = str(raw).strip()
    if not s or s.lower() in ("nan", "none", "null"):
        continue
    m = num_re.search(s)
    if m:
        try:
            val = float(m.group(1))
        except:
            continue
        # clamp to expected range 0..5
        if val < 0 or val > 10:  # ignore clearly invalid >10
            continue
        # if >5 but <=10 it might be 10-scale; we still write it — you can rescale later if needed
        cur.execute("UPDATE products SET rating = ? WHERE rowid = ?", (val, rowid))
        updated += 1

conn.commit()
print("Updated numeric rating for", updated, "rows")

# add index for efficient filtering if missing
try:
    cur.execute("CREATE INDEX IF NOT EXISTS idx_rating ON products(rating)")
    conn.commit()
    print("Ensured idx_rating exists")
except Exception as e:
    print("Index creation error:", e)

conn.close()
print("Done. If you need to undo, restore DB from:", bak)
