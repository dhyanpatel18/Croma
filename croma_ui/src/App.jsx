import React, { useEffect, useState } from "react";
import Header from "./components/Header";
import HomeCarousel from "./components/HomeCarousel";
import ProductGrid from "./components/ProductGrid";

const API_BASE = "http://127.0.0.1:8000";

function qsFrom(obj) {
  return Object.entries(obj)
    .filter(([, v]) => v !== undefined && v !== null && v !== "")
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
    .join("&");
}

export default function App() {
  // UI state
  const [page, setPage] = useState(1);
  const [pageSize] = useState(24);
  const [query, setQuery] = useState("");
  const [panel, setPanel] = useState("");
  const [is4k, setIs4k] = useState("");
  const [isSmart, setIsSmart] = useState("");
  const [brand, setBrand] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [sortBy, setSortBy] = useState("rank");
  const [sortDir, setSortDir] = useState("asc");

  const [productsData, setProductsData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchProducts = async (overrides = {}) => {
    const params = {
      q: query || undefined,
      panel: panel || undefined,
      is_4k: is4k === "" ? undefined : is4k === "true",
      is_smart_tv: isSmart === "" ? undefined : isSmart === "true",
      brand: brand || undefined,
      min_price: minPrice || undefined,
      max_price: maxPrice || undefined,
      sort_by: sortBy || undefined,
      sort_dir: sortDir || undefined,
      page,
      page_size: pageSize,
      ...overrides
    };
    const qs = qsFrom(params);
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/products?${qs}`);
      const json = await res.json();
      setProductsData(json);
    } catch (e) {
      setProductsData({ total: 0, page, page_size: pageSize, items: [] });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
    // eslint-disable-next-line
  }, [page, panel, is4k, isSmart, brand, minPrice, maxPrice, sortBy, sortDir, query]);

  // load brands for dropdown
  const [brands, setBrands] = useState([]);
  useEffect(() => {
    fetch(`${API_BASE}/meta/brands`)
      .then((r) => r.json())
      .then((j) => {
        if (j && j.brands) setBrands(j.brands.map((b) => b.brand));
      })
      .catch(() => {});
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      <Header
        value={query}
        onChange={(v) => setQuery(v)}
        onSearch={() => { setPage(1); fetchProducts({ page: 1 }); }}
      />

      {/* Home carousel */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <HomeCarousel
          title="Featured TVs"
          apiFetch={(limit = 12) => fetch(`${API_BASE}/products?page=1&page_size=${limit}&sort_by=rank`).then(r => r.json())}
          onItemClick={(p) => {
            // set search to product name and load
            setQuery(p.name || "");
            setPage(1);
          }}
        />

        {/* Filters */}
        <section className="mt-8 bg-gray-800 p-4 rounded-lg">
          <div className="flex flex-wrap gap-3 items-center">
            <select className="bg-gray-700 p-2 rounded" value={panel} onChange={(e) => setPanel(e.target.value)}>
              <option value="">All Panels</option>
              <option value="led">LED</option>
              <option value="qled">QLED</option>
              <option value="oled">OLED</option>
            </select>

            <select className="bg-gray-700 p-2 rounded" value={is4k} onChange={(e) => setIs4k(e.target.value)}>
              <option value="">Any 4K</option>
              <option value="true">4K</option>
              <option value="false">Non-4K</option>
            </select>

            <select className="bg-gray-700 p-2 rounded" value={brand} onChange={(e) => setBrand(e.target.value)}>
              <option value="">All Brands</option>
              {brands.map((b) => <option value={b} key={b}>{b}</option>)}
            </select>

            <input className="bg-gray-700 p-2 rounded w-28" placeholder="min ₹" value={minPrice} onChange={(e) => setMinPrice(e.target.value)} />
            <input className="bg-gray-700 p-2 rounded w-28" placeholder="max ₹" value={maxPrice} onChange={(e) => setMaxPrice(e.target.value)} />

            <select className="bg-gray-700 p-2 rounded ml-auto" value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="rank">Relevance</option>
              <option value="price">Price</option>
              <option value="rating">Rating</option>
              <option value="name">Name</option>
            </select>
            <select className="bg-gray-700 p-2 rounded" value={sortDir} onChange={(e) => setSortDir(e.target.value)}>
              <option value="asc">Asc</option>
              <option value="desc">Desc</option>
            </select>

            <button className="bg-emerald-500 text-black px-3 py-2 rounded" onClick={() => { setPage(1); fetchProducts({ page: 1 }); }}>
              Apply
            </button>
          </div>
        </section>

        <section className="mt-6">
          <ProductGrid loading={loading} data={productsData} page={page} onPageChange={setPage} />
        </section>
      </main>
    </div>
  );
}
