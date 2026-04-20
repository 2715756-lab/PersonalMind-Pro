'use client';

import { useState } from 'react';

interface Product {
  id: string;
  name: string;
  price: number;
  store: string;
  delivery_time?: string;
  description?: string;
}

interface CartItem {
  product: Product;
  quantity: number;
}

export function CommercePanel() {
  const [searchQuery, setSearchQuery] = useState('');
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedStore, setSelectedStore] = useState<string>('all');

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('/api/commerce/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: searchQuery,
          store: selectedStore === 'all' ? undefined : selectedStore,
        }),
      });

      const data = await response.json();
      setProducts(data.products || []);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const addToCart = (product: Product) => {
    setCart((prev) => {
      const existing = prev.find((item) => item.product.id === product.id);
      if (existing) {
        return prev.map((item) =>
          item.product.id === product.id ? { ...item, quantity: item.quantity + 1 } : item
        );
      }
      return [...prev, { product, quantity: 1 }];
    });
  };

  const removeFromCart = (productId: string) => {
    setCart((prev) => prev.filter((item) => item.product.id !== productId));
  };

  const totalPrice = cart.reduce((sum, item) => sum + item.product.price * item.quantity, 0);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Search & Products */}
      <div className="lg:col-span-2 space-y-4">
        {/* Search Bar */}
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 space-y-3">
          <div className="flex space-x-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Ищите товары, еду, пиццу..."
              className="flex-1 bg-gray-700 text-white p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleSearch}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 rounded transition"
            >
              {loading ? '⏳' : '🔍'}
            </button>
          </div>

          <div className="flex space-x-2">
            {['all', 'samokat', 'papajohns'].map((store) => (
              <button
                key={store}
                onClick={() => setSelectedStore(store)}
                className={`px-3 py-1 rounded text-sm transition ${
                  selectedStore === store
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-400 hover:text-gray-200'
                }`}
              >
                {store === 'all' ? '🌐 Все' : store === 'samokat' ? '🛒 Samokat' : '🍕 Papa Johns'}
              </button>
            ))}
          </div>
        </div>

        {/* Products Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {products.map((product) => (
            <div key={product.id} className="bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-blue-500 transition">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h4 className="font-semibold text-gray-100">{product.name}</h4>
                  <p className="text-xs text-gray-500">{product.store}</p>
                </div>
                <span className="text-sm text-yellow-400 font-bold">₽{product.price}</span>
              </div>
              {product.description && <p className="text-sm text-gray-400 mb-3">{product.description}</p>}
              {product.delivery_time && <p className="text-xs text-gray-500 mb-3">⏱️ {product.delivery_time}</p>}
              <button
                onClick={() => addToCart(product)}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded text-sm transition"
              >
                + В корзину
              </button>
            </div>
          ))}
        </div>
        
        {products.length === 0 && !loading && (
          <div className="text-center py-12 text-gray-500">
            <div className="text-4xl mb-2">🛍️</div>
            <p>Результаты поиска появятся здесь</p>
          </div>
        )}
      </div>

      {/* Shopping Cart */}
      <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 h-fit sticky top-6">
        <h3 className="text-lg font-semibold mb-4">🛒 Корзина</h3>
        
        {cart.length === 0 ? (
          <p className="text-gray-500 text-sm">Корзина пуста</p>
        ) : (
          <div className="space-y-3">
            {cart.map((item) => (
              <div key={item.product.id} className="flex justify-between items-start p-2 bg-gray-700/50 rounded">
                <div>
                  <p className="text-sm font-medium text-gray-200">{item.product.name}</p>
                  <p className="text-xs text-gray-500">{item.quantity} x ₽{item.product.price}</p>
                </div>
                <button
                  onClick={() => removeFromCart(item.product.id)}
                  className="text-red-500 hover:text-red-400 text-xs"
                >
                  ✕
                </button>
              </div>
            ))}

            <div className="border-t border-gray-600 pt-3 mt-3">
              <div className="flex justify-between font-bold text-gray-100 mb-3">
                <span>Итого:</span>
                <span>₽{totalPrice}</span>
              </div>
              <button className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded transition font-semibold">
                Оформить заказ
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
