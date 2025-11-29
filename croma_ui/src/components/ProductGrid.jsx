import React from "react";
import ProductCard from "./ProductCard";

export default function ProductGrid({ loading, data, page, onPageChange }) {
  if (loading) return <div className="py-12 text-center">Loading…</div>;
  if (!data) return <div className="py-12 text-center">No data</div>;

  const total = data.total || 0;
  const items = data.items || [];

  return (
    <div>
      <div className="mt-4 text-sm text-gray-400">Showing {items.length} of {total} results</div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-4">
        {items.map((p, i) => <ProductCard key={p.product_url || i} product={p} />)}
      </div>

      <div className="flex items-center justify-between mt-6">
        <div className="text-sm text-gray-400">Page {data.page}</div>
        <div className="flex gap-2">
          <button disabled={page <= 1} onClick={() => onPageChange(page - 1)} className="bg-gray-700 px-3 py-2 rounded disabled:opacity-50">Prev</button>
          <button disabled={items.length === 0} onClick={() => onPageChange(page + 1)} className="bg-gray-700 px-3 py-2 rounded disabled:opacity-50">Next</button>
        </div>
      </div>
    </div>
  );
}
