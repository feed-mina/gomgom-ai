'use client';

import { useState } from 'react';

export default function TestTranslatePage() {
  const [inputTexts, setInputTexts] = useState<string>('');
  const [translatedTexts, setTranslatedTexts] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const handleTranslate = async () => {
    if (!inputTexts.trim()) {
      setError('번역할 텍스트를 입력해주세요.');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      // 텍스트를 줄바꿈으로 분할
      const texts = inputTexts.split('\n').filter(text => text.trim());
      
      console.log('번역 요청 텍스트:', texts);
      
      // 백엔드로 직접 호출
      const response = await fetch('http://localhost:8000/api/v1/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(texts),
      });

      console.log('응답 상태:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`번역 API 오류: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log('번역 결과:', data);
      
      setTranslatedTexts(data.translatedTexts || []);
      
    } catch (err) {
      console.error('번역 오류:', err);
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-8">번역 API 테스트</h1>
        
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">입력 텍스트</h2>
          <textarea
            value={inputTexts}
            onChange={(e) => setInputTexts(e.target.value)}
            placeholder="번역할 텍스트를 입력하세요. 여러 줄로 입력하면 각 줄이 별도로 번역됩니다."
            className="w-full h-40 p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          
          <button
            onClick={handleTranslate}
            disabled={loading}
            className="mt-4 px-6 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-400"
          >
            {loading ? '번역 중...' : '번역하기'}
          </button>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            <strong>오류:</strong> {error}
          </div>
        )}

        {translatedTexts.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">번역 결과</h2>
            <div className="space-y-2">
              {translatedTexts.map((text, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded border">
                  <span className="font-medium text-gray-600">텍스트 {index + 1}:</span>
                  <p className="mt-1">{text}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-800 mb-2">사용법:</h3>
          <ul className="text-blue-700 space-y-1 text-sm">
            <li>• 여러 줄로 텍스트를 입력하면 각 줄이 별도로 번역됩니다.</li>
            <li>• 긴 텍스트도 자동으로 청크로 나누어 번역됩니다.</li>
            <li>• 영어 → 한국어 번역이 지원됩니다.</li>
          </ul>
        </div>
      </div>
    </div>
  );
} 