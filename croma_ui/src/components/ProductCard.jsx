import React from "react";

function formatRating(product) {
  if (!product) return { text: "No rating", value: null };

  if (product.rating !== undefined && product.rating !== null && String(product.rating).trim() !== "") {
    const v = Number(product.rating);
    if (!Number.isNaN(v)) {
      const cnt = product["rating-text-icon"] || product["rating-text-icon 2"] || product["rating_count"] || null;
      const text = v.toFixed(1) + (cnt ? " (" + cnt + ")" : "");
      return { text: text, value: v };
    }
  }
  const candidates = [
    product["rating-text"],
    product["rating_text"],
    product["rating-text-icon"],
    product["cp-rating href"],
    product["rating-text-icon 2"],
  ];
  for (const raw of candidates) {
    if (!raw) continue;
    const s = String(raw).trim();
    if (!s) continue;
    const mVal = s.match(/(\d+(?:\.\d+)?)/);
    const mCnt = s.match(/\((\d{1,6})\)/);
    if (mVal) {
      const v = parseFloat(mVal[1]);
      const text = v.toFixed(1) + (mCnt ? " (" + mCnt[1] + ")" : "");
      return { text: text, value: v };
    }
  }

  return { text: "No rating", value: null };
}

export default function ProductCard({ product }) {

  const rawImg = product.plp_product_tile_src || product["plp_product_tile src"] || product["plp_product_tile_src"] || "";
  const hasImg = typeof rawImg === "string" && rawImg.trim().length > 5 && !rawImg.toLowerCase().includes("plp_product_tile");

  const priceLabel = product.price ? `₹${product.price}` : "Price n/a";

  const { text: ratingText } = formatRating(product);

  return (
    <article className="bg-gradient-to-b from-gray-800 via-gray-800 to-gray-900 border border-gray-700 rounded-lg p-4 shadow-sm hover:shadow-lg transition-shadow duration-200">
      <div className="flex gap-3">
        <div className="w-28 h-20 flex-shrink-0 rounded-md overflow-hidden bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center">
          {hasImg ? (
            <div className="text-xs text-gray-300 px-2 text-center">Image</div>
          ) : (
            <div className="flex flex-col items-center justify-center px-2">
              <div className="w-10 h-6 rounded-sm bg-gray-700 mb-2 grid place-items-center text-xs text-gray-400">TV</div>
              <div className="text-xs text-gray-400">No image</div>
            </div>
          )}
        </div>

        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-semibold leading-tight text-white truncate" title={product.name}>
            {product.name || "Untitled product"}
          </h4>

          <div className="mt-1 text-xs text-gray-400 truncate">{product.catalog_rank ? `Rank: ${product.catalog_rank}` : ""}</div>

          <div className="mt-3 flex items-center justify-between gap-3">
            <div>
              <div className="text-sm font-bold text-emerald-300">{priceLabel}</div>

              <div className="mt-1">
                <div className="text-xs text-gray-300">
                  {ratingText}
                </div>
              </div>
            </div>

            <div className="flex flex-col items-end gap-2">
              <div className="flex gap-1 items-center">
                {product.is_4k ? <span className="text-[10px] font-medium bg-gray-700 text-emerald-300 px-2 py-1 rounded">4K</span> : null}
                {product.is_smart_tv ? <span className="text-[10px] font-medium bg-gray-700 text-emerald-300 px-2 py-1 rounded">Smart</span> : null}
                {product.panel_qled ? <span className="text-[10px] font-medium bg-gray-700 text-emerald-300 px-2 py-1 rounded">QLED</span> : (product.panel_oled ? <span className="text-[10px] font-medium bg-gray-700 text-emerald-300 px-2 py-1 rounded">OLED</span> : (product.panel_led ? <span className="text-[10px] font-medium bg-gray-700 text-emerald-300 px-2 py-1 rounded">LED</span> : null))}
              </div>

              <a
                href={product.product_url || "#"}
                target="_blank"
                rel="noreferrer"
                className="inline-block bg-emerald-400 text-black text-xs font-medium px-3 py-1 rounded-md hover:bg-emerald-300 transition-colors"
              >
                View
              </a>
            </div>
          </div>

          {product.discount ? (
            <div className="mt-3 text-xs text-pink-400">Save {product.discount}</div>
          ) : null}

          {product.delivery_pincode_text ? (
            <div className="mt-2 text-xs text-gray-500">{product.delivery_pincode_text}</div>
          ) : null}
        </div>
      </div>
    </article>
  );
}
