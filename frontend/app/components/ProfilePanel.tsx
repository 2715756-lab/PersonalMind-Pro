'use client';

import { useState, useEffect } from 'react';

interface UserProfile {
  user_id: string;
  demographics: Record<string, any>;
  interests: Array<{ name: string; weight: number }>;
  goals: Array<{ description: string; category: string }>;
  preferences: Record<string, any>;
}

export function ProfilePanel() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState<any>({});

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await fetch('/api/profile?user_id=default_user');
      const data = await response.json();
      setProfile(data);
      setFormData(data.demographics || {});
    } catch (error) {
      console.error('Error loading profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      await fetch('/api/profile/update', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'default_user',
          updates: formData,
        }),
      });
      setEditMode(false);
      loadProfile();
    } catch (error) {
      console.error('Error saving profile:', error);
    }
  };

  if (loading) {
    return <div className="text-center text-gray-400">⏳ Загрузка...</div>;
  }

  if (!profile) {
    return <div className="text-center text-red-400">Ошибка загрузки профиля</div>;
  }

  return (
    <div className="space-y-6">
      {/* Personal Info */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold">👤 Персональная информация</h3>
          <button
            onClick={() => setEditMode(!editMode)}
            className="text-sm bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded transition"
          >
            {editMode ? 'Отменить' : '✏️ Редактировать'}
          </button>
        </div>

        {editMode ? (
          <form onSubmit={(e) => { e.preventDefault(); handleSave(); }} className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Возраст</label>
              <input
                type="number"
                value={formData.age || ''}
                onChange={(e) => setFormData({ ...formData, age: parseInt(e.target.value) })}
                className="w-full bg-gray-700 text-white p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Город</label>
              <input
                type="text"
                value={formData.location || ''}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                className="w-full bg-gray-700 text-white p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Род деятельности</label>
              <input
                type="text"
                value={formData.occupation || ''}
                onChange={(e) => setFormData({ ...formData, occupation: e.target.value })}
                className="w-full bg-gray-700 text-white p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <button
              type="submit"
              className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded transition"
            >
              Сохранить изменения
            </button>
          </form>
        ) : (
          <div className="space-y-2">
            {profile.demographics.age && <div className="text-gray-300">🎂 Возраст: {profile.demographics.age}</div>}
            {profile.demographics.location && <div className="text-gray-300">📍 Город: {profile.demographics.location}</div>}
            {profile.demographics.occupation && <div className="text-gray-300">💼 Род деятельности: {profile.demographics.occupation}</div>}
            {!profile.demographics.age && !profile.demographics.location && !profile.demographics.occupation && (
              <p className="text-gray-500 italic">Информация не заполнена</p>
            )}
          </div>
        )}
      </div>

      {/* Interests */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-xl font-semibold mb-4">💡 Интересы</h3>
        {profile.interests.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {profile.interests.map((interest, idx) => (
              <span
                key={idx}
                className="bg-blue-600/30 text-blue-300 px-3 py-1 rounded-full text-sm border border-blue-500/50"
              >
                {interest.name}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 italic">Интересы будут добавлены при общении</p>
        )}
      </div>

      {/* Goals */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-xl font-semibold mb-4">🎯 Цели</h3>
        {profile.goals.length > 0 ? (
          <div className="space-y-2">
            {profile.goals.map((goal, idx) => (
              <div key={idx} className="flex items-start space-x-2">
                <span className="text-yellow-500">•</span>
                <div>
                  <p className="text-gray-300">{goal.description}</p>
                  <p className="text-xs text-gray-500">{goal.category}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 italic">Цели будут добавлены при общении</p>
        )}
      </div>
    </div>
  );
}
