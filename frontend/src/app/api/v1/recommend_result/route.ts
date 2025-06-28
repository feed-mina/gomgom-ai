import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const text = searchParams.get('text');
  const lat = searchParams.get('lat');
  const lng = searchParams.get('lng');
  const mode = searchParams.get('mode');
  const rand = searchParams.get('rand');

  const params = new URLSearchParams();
  if (text) params.append('text', text);
  if (lat) params.append('lat', lat);
  if (lng) params.append('lng', lng);
  if (mode) params.append('mode', mode);
  if (rand) params.append('rand', rand);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const response = await fetch(`${apiUrl}/api/v1/recommend_result?${params.toString()}`);
  const data = await response.json();

  return NextResponse.json(data);
} 