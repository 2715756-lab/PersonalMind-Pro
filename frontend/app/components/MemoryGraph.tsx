'use client';

import { useState, useEffect } from 'react';

interface MemoryNode {
  id: string;
  content: string;
  type: 'episodic' | 'semantic' | 'procedural' | 'document';
  importance: number;
  created_at: string;
}

export function MemoryGraph() {
  const [memories, setMemories] = useState<MemoryNode[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMemoryData();
  }, []);

  const fetchMemoryData = async () => {
    try {
      const response = await fetch('/api/memory/stats?user_id=default_user');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching memory:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      episodic: 'bg-blue-500',
      semantic: 'bg-purple-500',
      procedural: 'bg-green-500',
      document: 'bg-yellow-500',
    };
    return colors[type] || 'bg-gray-500';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin text-4xl">🔄</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="text-3xl font-bold text-blue-400">{stats?.total_memories || 0}</div>
          <div className="text-sm text-gray-400">Всего воспоминаний</div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="text-3xl font-bold text-purple-400">{stats?.by_type?.episodic || 0}</div>
          <div className="text-sm text-gray-400">Эпизодических</div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="text-3xl font-bold text-green-400">{stats?.by_type?.semantic || 0}</div>
          <div className="text-sm text-gray-400">Семантических</div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="text-3xl font-bold text-yellow-400">{stats?.by_type?.document || 0}</div>
          <div className="text-sm text-gray-400">Из документов</div>
        </div>
      </div>

      {/* Memory Timeline */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-xl font-semibold mb-4">Временная шкала</h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between text-gray-400">
            <span>Старейшее:</span>
            <span>{stats?.oldest_memory ? new Date(stats.oldest_memory).toLocaleDateString('ru-RU') : 'Нет'}</span>
          </div>
          <div className="flex justify-between text-gray-400">
            <span>Последнее:</span>
            <span>{stats?.newest_memory ? new Date(stats.newest_memory).toLocaleDateString('ru-RU') : 'Нет'}</span>
          </div>
          <div className="flex justify-between text-gray-400">
            <span>Средняя важность:</span>
            <span>{(stats?.total_importance || 0).toFixed(2)}</span>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-xl font-semibold mb-4">Типы памяти</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span className="text-gray-300">Эпизодическая (события)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
            <span className="text-gray-300">Семантическая (факты)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-gray-300">Процедурная (навыки)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <span className="text-gray-300">Документы</span>
          </div>
        </div>
      </div>
    </div>
  );
}
