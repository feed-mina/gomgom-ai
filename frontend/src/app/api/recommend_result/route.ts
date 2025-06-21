import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const text = searchParams.get('text');
  const lat = searchParams.get('lat');
  const lng = searchParams.get('lng');

  if (!lat || !lng) {
    return NextResponse.json({ error: '위치 정보가 필요합니다.' }, { status: 400 });
  }

  try {
    // Django 백엔드 API 호출
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/recommend_result/?text=${text}&lat=${lat}&lng=${lng}&mode=recommend`
    );
    const data = await response.json();

    return NextResponse.json(data);
  } catch (error) {
    console.error('추천 결과 조회 실패:', error);
    return NextResponse.json({ error: '추천 결과를 가져오는데 실패했습니다.' }, { status: 500 });
  }
} 