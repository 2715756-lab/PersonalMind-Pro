'use client';

export function SubscriptionCard() {
  return (
    <div className="max-w-md mx-auto bg-gradient-to-br from-yellow-500 via-orange-500 to-red-500 p-6 rounded-lg shadow-lg">
      <div className="text-white">
        <h2 className="text-3xl font-bold mb-2">✨ PersonalMind Pro</h2>
        <p className="text-lg opacity-90 mb-4">Неограниченный доступ</p>
        
        <div className="space-y-3 mb-6 text-sm">
          <div className="flex items-center space-x-2">
            <span>✓</span>
            <span>Неограниченная память</span>
          </div>
          <div className="flex items-center space-x-2">
            <span>✓</span>
            <span>Все магазины и заказы</span>
          </div>
          <div className="flex items-center space-x-2">
            <span>✓</span>
            <span>Анализ документов</span>
          </div>
          <div className="flex items-center space-x-2">
            <span>✓</span>
            <span>Больше приоритета</span>
          </div>
        </div>

        <div className="bg-white/20 backdrop-blur p-3 rounded mb-4">
          <div className="text-2xl font-bold">₽199/месяц</div>
          <p className="text-sm opacity-90">Отмена в любой момент</p>
        </div>

        <button className="w-full bg-white text-orange-500 font-bold py-2 rounded hover:bg-gray-100 transition">
          Обновить до Pro
        </button>
      </div>
    </div>
  );
}
