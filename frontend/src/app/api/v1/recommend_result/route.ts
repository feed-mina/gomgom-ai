import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const text = searchParams.get('text');
  const lat = searchParams.get('lat');
  const lng = searchParams.get('lng');
  const mode = searchParams.get('mode');
  const rand = searchParams.get('rand');
  const types = searchParams.get('types');

  const params = new URLSearchParams();
  if (text) params.append('text', text);
  if (lat) params.append('lat', lat);
  if (lng) params.append('lng', lng);
  if (mode) params.append('mode', mode);
  if (rand) params.append('rand', rand);
  if (types) {
    types.split(',').forEach((type, idx) => {
      params.append(`type${idx + 1}`, type);
    });
  }

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  try {
    const response = await fetch(`${apiUrl}/api/v1/recommend_result?${params.toString()}`);
    if (!response.ok) {
      const errorText = await response.text();
      return NextResponse.json({ error: `API 요청 실패: ${response.status} - ${errorText}` }, { status: response.status });
    }
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    return NextResponse.json({ error: `네트워크 오류 또는 서버 연결 실패: ${error.message}` }, { status: 500 });
  }
} 