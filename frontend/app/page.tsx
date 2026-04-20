// frontend/app/page.tsx — Главная страница
'use client';

import { useState } from 'react';
import { MemoryGraph } from '@/components/MemoryGraph';
import { FileManager } from '@/components/FileManager';
import { ChatInterface } from '@/components/ChatInterface';
import { CommercePanel } from '@/components/CommercePanel';
import { SubscriptionCard } from '@/components/SubscriptionCard';
import { ProfilePanel } from '@/components/ProfilePanel';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('chat');
  const [isPro, setIsPro] = useState(false);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 p-4 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
              <span className="text-xl">🧠</span>
            </div>
            <div>
              <h1 className="text-xl font-bold">PersonalMind Pro</h1>
              <p className="text-xs text-gray-400">Твоя вторая память</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {!isPro && (
              <button 
                onClick={() => setActiveTab('upgrade')}
                className="bg-gradient-to-r from-yellow-500 to-orange-500 px-4 py-2 rounded-lg font-semibold text-sm hover:shadow-lg transition"
              >
                ⭐ Обновить до Pro
              </button>
            )}
            <div className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center cursor-pointer hover:bg-gray-600">
              👤
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-gray-800 border-b border-gray-700 sticky top-16 z-10">
        <div className="max-w-7xl mx-auto flex space-x-1 p-2 overflow-x-auto">
          {[
            { id: 'chat', label: '💬 Чат' },
            { id: 'memory', label: '🧠 Память' },
            { id: 'files', label: '📁 Файлы' },
            { id: 'commerce', label: '🛒 Заказы', pro: true },
            { id: 'profile', label: '👤 Профиль' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => !tab.pro || isPro ? setActiveTab(tab.id) : setActiveTab('upgrade')}
              className={`px-4 py-2 rounded-lg transition whitespace-nowrap ${
                activeTab === tab.id 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-400 hover:bg-gray-700'
              } ${tab.pro && !isPro ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {tab.label}
              {tab.pro && !isPro && <span className="text-xs ml-1 bg-yellow-500 text-black px-1 rounded">PRO</span>}
            </button>
          ))}
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto p-6">
        {activeTab === 'chat' && <ChatInterface />}
        {activeTab === 'memory' && <MemoryGraph />}
        {activeTab === 'files' && <FileManager />}
        {activeTab === 'commerce' && isPro && <CommercePanel />}
        {activeTab === 'commerce' && !isPro && <div className="text-center py-12"><SubscriptionCard /></div>}
        {activeTab === 'profile' && <ProfilePanel />}
        {activeTab === 'upgrade' && <div className="text-center py-12"><SubscriptionCard /></div>}
      </main>
    </div>
  );
}

// components/MemoryGraph.tsx — Визуализация памяти
'use client';

import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

export function MemoryGraph() {
  const svgRef = useRef<SVGSVGElement>(null);
  const [memories, setMemories] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    // Загрузка данных памяти
    fetch('/api/memory/graph')
      .then(r => r.json())
      .then(data => {
        setMemories(data.nodes);
        renderGraph(data);
      });
  }, []);

  const renderGraph = (data) => {
    if (!svgRef.current) return;
    
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const width = 800;
    const height = 600;

    // Simulation
    const simulation = d3.forceSimulation(data.nodes)
      .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2));

    // Links
    const link = svg.append("g")
      .selectAll("line")
      .data(data.links)
      .enter().append("line")
      .attr("stroke", "#4b5563")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", 2);

    // Nodes
    const node = svg.append("g")
      .selectAll("g")
      .data(data.nodes)
      .enter().append("g")
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    // Node circles
    node.append("circle")
      .attr("r", d => d.importance * 20 + 10)
      .attr("fill", d => {
        const colors = {
          episodic: "#3b82f6",  // blue
          semantic: "#10b981",  // green
          procedural: "#f59e0b", // yellow
          document: "#8b5cf6"    // purple
        };
        return colors[d.type] || "#6b7280";
      })
      .attr("stroke", "#fff")
      .attr("stroke-width", 2)
      .on("click", (event, d) => setSelectedNode(d));

    // Node labels
    node.append("text")
      .text(d => d.content.substring(0, 20) + "...")
      .attr("x", 12)
      .attr("y", 4)
      .attr("fill", "#fff")
      .attr("font-size", "12px");

    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node.attr("transform", d => `translate(${d.x},${d.y})`);
    });

    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  };

  return (
    <div className="grid grid-cols-3 gap-6">
      <div className="col-span-2 bg-gray-800 rounded-xl p-4">
        <h2 className="text-lg font-semibold mb-4">🕸️ Граф памяти</h2>
        <svg ref={svgRef} width="100%" height="600" className="bg-gray-900 rounded-lg" />
      </div>
      
      <div className="bg-gray-800 rounded-xl p-4">
        <h2 className="text-lg font-semibold mb-4">📊 Статистика</h2>
        <div className="space-y-4">
          <div className="bg-gray-700 p-3 rounded-lg">
            <p className="text-gray-400 text-sm">Всего воспоминаний</p>
            <p className="text-2xl font-bold text-blue-400">{memories.length}</p>
          </div>
          
          <div className="bg-gray-700 p-3 rounded-lg">
            <p className="text-gray-400 text-sm">Типы</p>
            <div className="flex flex-wrap gap-2 mt-2">
              <span className="px-2 py-1 bg-blue-600 rounded text-xs">Эпизодические</span>
              <span className="px-2 py-1 bg-green-600 rounded text-xs">Семантические</span>
              <span className="px-2 py-1 bg-purple-600 rounded text-xs">Документы</span>
            </div>
          </div>

          {selectedNode && (
            <div className="bg-gray-700 p-3 rounded-lg">
              <p className="text-gray-400 text-sm mb-2">Выбрано:</p>
              <p className="text-sm">{selectedNode.content}</p>
              <p className="text-xs text-gray-500 mt-2">
                Важность: {(selectedNode.importance * 100).toFixed(0)}%
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// components/CommercePanel.tsx — Панель заказов (Pro only)
'use client';

import { useState } from 'react';

export function CommercePanel() {
  const [activeOrder, setActiveOrder] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const stores = [
    { id: 'samokat', name: 'Samokat', category: 'продукты', color: 'bg-yellow-500' },
    { id: 'yandex_lavka', name: 'Yandex Lavka', category: 'продукты', color: 'bg-red-500' },
    { id: 'papa_johns', name: 'Papa Johns', category: 'пицца', color: 'bg-green-600' },
    { id: 'dodo', name: 'Dodo Pizza', category: 'пицца', color: 'bg-orange-500' },
    { id: 'ozon', name: 'Ozon', category: 'товары', color: 'bg-blue-500' },
  ];

  const handleQuickOrder = (type: string) => {
    // Отправка команды боту
    const commands = {
      pizza: 'Закажи пиццу пепперони большую',
      groceries: 'Купи продуктов на ужин',
      repeat: 'Закажи как в прошлый раз'
    };
    
    // Открытие чата с командой
    window.open(`https://t.me/${process.env.NEXT_PUBLIC_BOT_USERNAME}?start=order_${type}`, '_blank');
  };

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl p-6">
        <h2 className="text-2xl font-bold mb-2">🛒 Быстрые заказы</h2>
        <p className="text-gray-200 mb-4">Выбери категорию или напиши боту конкретный запрос</p>
        
        <div className="grid grid-cols-3 gap-4">
          <button 
            onClick={() => handleQuickOrder('pizza')}
            className="bg-white/20 hover:bg-white/30 backdrop-blur p-4 rounded-xl transition"
          >
            <span className="text-3xl">🍕</span>
            <p className="font-semibold mt-2">Пицца</p>
            <p className="text-sm text-gray-300">15-30 мин</p>
          </button>
          
          <button 
            onClick={() => handleQuickOrder('groceries')}
            className="bg-white/20 hover:bg-white/30 backdrop-blur p-4 rounded-xl transition"
          >
            <span className="text-3xl">🥑</span>
            <p className="font-semibold mt-2">Продукты</span>
            <p className="text-sm text-gray-300">15-60 мин</p>
          </button>
          
          <button 
            onClick={() => handleQuickOrder('repeat')}
            className="bg-white/20 hover:bg-white/30 backdrop-blur p-4 rounded-xl transition"
          >
            <span className="text-3xl">🔄</span>
            <p className="font-semibold mt-2">Повторить</p>
            <p className="text-sm text-gray-300">Прошлый заказ</p>
          </button>
        </div>
      </div>

      <div className="bg-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4">🏪 Доступные магазины</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {stores.map(store => (
            <div key={store.id} className="bg-gray-700 p-4 rounded-lg flex items-center space-x-3">
              <div className={`w-12 h-12 ${store.color} rounded-lg flex items-center justify-center text-xl`}>
                🏪
              </div>
              <div>
                <p className="font-semibold">{store.name}</p>
                <p className="text-sm text-gray-400">{store.category}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4">📦 История заказов</h3>
        <div className="space-y-3">
          <div className="bg-gray-700 p-4 rounded-lg flex justify-between items-center">
            <div>
              <p className="font-semibold">Papa Johns — Пепперони 35см</p>
              <p className="text-sm text-gray-400">2 дня назад • 899₽</p>
            </div>
            <button 
              onClick={() => handleQuickOrder('repeat')}
              className="bg-blue-600 px-4 py-2 rounded-lg text-sm hover:bg-blue-500"
            >
              Повторить
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// components/SubscriptionCard.tsx — Монетизация
'use client';

import { useState } from 'react';

export function SubscriptionCard({ onUpgrade }) {
  const [selectedPlan, setSelectedPlan] = useState('monthly');

  const plans = {
    free: {
      name: 'Free',
      price: 0,
      features: [
        '100 воспоминаний',
        '5 документов',
        'Базовый чат',
        '1 магазин (демо)',
        'Поддержка сообщества'
      ],
      cta: 'Текущий план',
      disabled: true
    },
    pro: {
      name: 'Pro',
      price: selectedPlan === 'monthly' ? 9.99 : 8.25,
      period: selectedPlan === 'monthly' ? '/мес' : '/мес (год)',
      features: [
        '✅ Безлимитная память',
        '✅ Безлимит документов',
        '✅ Все магазины (10+)',
        '✅ Приоритетная обработка',
        '✅ API доступ',
        '✅ Расширенный профиль',
        '✅ Поддержка 24/7',
        '✅ Ранний доступ к новым фичам'
      ],
      cta: 'Обновить сейчас',
      popular: true
    },
    business: {
      name: 'Business',
      price: 29.99,
      period: '/мес',
      features: [
        '✅ Всё из Pro',
        '✅ 5 пользователей',
        '️ Командная память',
        '✅ Аналитика и отчёты',
        '✅ Интеграции (Slack, Notion)',
        '✅ White-label опция',
        '✅ Персональный менеджер'
      ],
      cta: 'Связаться с sales',
      disabled: false
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold mb-2">⭐ Выбери свой тариф</h2>
        <p className="text-gray-400">Начни бесплатно, обновись когда понадобится больше</p>
        
        <div className="flex justify-center mt-6 bg-gray-800 inline-flex rounded-lg p-1">
          <button
            onClick={() => setSelectedPlan('monthly')}
            className={`px-4 py-2 rounded-md transition ${
              selectedPlan === 'monthly' ? 'bg-blue-600 text-white' : 'text-gray-400'
            }`}
          >
            Месячно
          </button>
          <button
            onClick={() => setSelectedPlan('yearly')}
            className={`px-4 py-2 rounded-md transition ${
              selectedPlan === 'yearly' ? 'bg-blue-600 text-white' : 'text-gray-400'
            }`}
          >
            Годовой (-17%)
          </button>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {Object.entries(plans).map(([key, plan]) => (
          <div 
            key={key}
            className={`bg-gray-800 rounded-2xl p-6 border-2 ${
              plan.popular ? 'border-blue-500 relative' : 'border-gray-700'
            }`}
          >
            {plan.popular && (
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-semibold">
                Популярный выбор
              </div>
            )}
            
            <div className="mb-4">
              <h3 className="text-xl font-bold">{plan.name}</h3>
              <div className="mt-2">
                <span className="text-3xl font-bold">${plan.price}</span>
                <span className="text-gray-400">{plan.period}</span>
              </div>
            </div>

            <ul className="space-y-3 mb-6">
              {plan.features.map((feature, i) => (
                <li key={i} className="flex items-start space-x-2">
                  <span className={feature.startsWith('✅') ? 'text-green-400' : 'text-gray-500'}>
                    {feature.startsWith('✅') ? '✓' : '•'}
                  </span>
                  <span className={feature.startsWith('✅') ? '' : 'text-gray-400'}>
                    {feature.replace('✅ ', '').replace('• ', '')}
                  </span>
                </li>
              ))}
            </ul>

            <button
              onClick={() => !plan.disabled && onUpgrade()}
              disabled={plan.disabled}
              className={`w-full py-3 rounded-xl font-semibold transition ${
                plan.disabled
                  ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                  : plan.popular
                  ? 'bg-blue-600 hover:bg-blue-500 text-white'
                  : 'bg-gray-700 hover:bg-gray-600 text-white'
              }`}
            >
              {plan.cta}
            </button>
          </div>
        ))}
      </div>

      <div className="mt-8 text-center text-gray-400 text-sm">
        <p>💡 30 дней гарантии возврата денег. Отмена в любой момент.</p>
        <p className="mt-2">Оплата через Stripe / ЮKassa • Безопасно и надёжно</p>
      </div>
    </div>
  );
}