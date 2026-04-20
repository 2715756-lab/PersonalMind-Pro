'use client';

import { useState, useRef } from 'react';

interface FileInfo {
  filename: string;
  size_bytes: number;
  modified: string;
}

export function FileManager() {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('user_id', 'default_user');

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (data.status === 'success') {
        await loadFiles();
      }
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setLoading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const loadFiles = async () => {
    try {
      const response = await fetch('/api/documents?user_id=default_user');
      const data = await response.json();
      setFiles(data.documents || []);
    } catch (error) {
      console.error('Error loading files:', error);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div className="bg-gray-800 p-8 rounded-lg border-2 border-dashed border-gray-600 hover:border-blue-500 transition">
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileUpload}
          disabled={loading}
          className="hidden"
          accept=".pdf,.txt,.md,.csv,.json,.py,.js,.html,.docx"
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={loading}
          className="w-full text-center"
        >
          <div className="text-4xl mb-2">📄</div>
          <div className="text-gray-300 font-semibold">
            {loading ? 'Загружается...' : 'Нажмите или перетащите файлы сюда'}
          </div>
          <div className="text-gray-500 text-sm mt-2">PDF, TXT, Markdown, CSV, JSON и другие</div>
        </button>
      </div>

      {/* Files List */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="p-4 border-b border-gray-700">
          <h3 className="text-lg font-semibold">Загруженные документы ({files.length})</h3>
        </div>
        
        {files.length === 0 ? (
          <div className="p-8 text-center text-gray-400">
            <div className="text-3xl mb-2">📭</div>
            <p>Документов не найдено</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-700">
            {files.map((file) => (
              <div key={file.filename} className="p-4 hover:bg-gray-700/50 transition flex items-center justify-between">
                <div className="flex items-center space-x-3 flex-1">
                  <div className="text-2xl">
                    {file.filename.endsWith('.pdf') ? '📕' : file.filename.endsWith('.md') ? '📝' : '📄'}
                  </div>
                  <div>
                    <div className="font-medium text-gray-100 truncate">{file.filename}</div>
                    <div className="text-xs text-gray-500">
                      {formatFileSize(file.size_bytes)} • {new Date(file.modified).toLocaleDateString('ru-RU')}
                    </div>
                  </div>
                </div>
                <button className="text-red-500 hover:text-red-400 text-sm">Удалить</button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
