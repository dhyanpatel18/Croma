import React, { useEffect, useRef, useState } from "react";

export default function HomeCarousel({ title, apiFetch, onItemClick }) {
  const [items, setItems] = useState([]);
  const sc = useRef(null);

  useEffect(() => {
    let mounted = true;
    apiFetch(12)
      .then((j) => {
        if (!mounted) return;
        setItems((j && j.items) || []);
      })
      .catch(() => {
        if (!mounted) return;
        setItems([]);
      });
    return () => {
      mounted = false;
    };
  }, [apiFetch]);

  const scroll = (dir) => {
    if (!sc.current) return;
    sc.current.scrollBy({
      left: dir * (sc.current.offsetWidth * 0.8),
      behavior: "smooth",
    });
  };

  return (
    <section className="mt-6">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xl font-semibold text-white">{title}</h3>
        <div className="flex gap-2">
          <button
            aria-label="Scroll left"
            className="bg-gray-700 p-2 rounded"
            onClick={() => scroll(-1)}
          >
            ◀
          </button>
          <button
            aria-label="Scroll right"
            className="bg-gray-700 p-2 rounded"
            onClick={() => scroll(1)}
          >
            ▶
          </button>
        </div>
      </div>

      <div
        ref={sc}
        className="carousel-scroll overflow-x-auto flex gap-4 pb-4"
        role="list"
        aria-label={title}
      >
        {items.map((p) => {
          const key =
            p.product_url || p.name || Math.random().toString(36).slice(2, 9);
          const name = p.name || "Untitled";
          const price = p.price ? `₹${p.price}` : "Price n/a";
          const hasImg = !!(
            p.plp_product_tile_src || p["plp_product_tile src"]
          );
          return (
            <div
              role="listitem"
              key={key}
              className="min-w-[260px] max-w-[280px] bg-gradient-to-b from-gray-800 to-gray-900 border border-gray-700 rounded-lg p-3 shadow-sm hover:shadow-lg transition-shadow duration-200"
            >
              <div className="h-36 bg-gradient-to-br from-gray-700 to-gray-800 rounded-md mb-3 flex items-center justify-center">
                {hasImg ? (
                  <div className="text-sm text-gray-300">Image</div>
                ) : (
                  <div className="flex flex-col items-center justify-center text-center">
                    <div className="w-12 h-7 rounded-sm bg-gray-700 mb-2 grid place-items-center text-xs text-gray-400">
                      TV
                    </div>
                    <div className="text-xs text-gray-400">No image</div>
                  </div>
                )}
              </div>

              <div
                className="font-semibold text-sm leading-tight truncate"
                title={name}
              >
                {name}
              </div>
              <div className="mt-2 text-emerald-300 font-bold">{price}</div>

              <div className="mt-3 flex items-center justify-between">
                <div className="text-xs text-gray-400">
                  {p.is_4k ? (
                    <span className="mr-2 px-2 py-1 bg-gray-700 rounded-sm">
                      4K
                    </span>
                  ) : null}
                  {p.is_smart_tv ? (
                    <span className="mr-2 px-2 py-1 bg-gray-700 rounded-sm">
                      Smart
                    </span>
                  ) : null}
                </div>

                <a
                  href={p.product_url || "#"}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs bg-emerald-400 text-black px-3 py-1 rounded-md hover:bg-emerald-300 transition-colors"
                >
                  View
                </a>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
