// /app/api/v1/restaurants/route.ts
import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const lat = searchParams.get('lat');
  const lng = searchParams.get('lng');
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  if (!lat || !lng) {
    return NextResponse.json({ error: '위치 정보가 필요합니다.' }, { status: 400 });
  }

  try {
    const res = await fetch(`/api/v1/restaurants?lat=${lat}&lng=${lng}`);

    const contentType = res.headers.get('content-type') || '';

    if (!res.ok || !contentType.includes('application/json')) {
      console.error('[중계 오류]', await res.text());
      return NextResponse.json({ error: 'FastAPI 응답이 올바르지 않음' }, { status: 500 });
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (err) {
    console.error('[FastAPI fetch 실패]', err);
    return NextResponse.json({ error: 'FastAPI 요청 실패' }, { status: 500 });
  }
}
