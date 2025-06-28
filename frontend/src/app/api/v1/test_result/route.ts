import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const text = searchParams.get('text');
  const lat = searchParams.get('lat');
  const lng = searchParams.get('lng');
  const types = searchParams.get('types');

  if (!lat || !lng || !types) {
    return NextResponse.json({ error: '필요한 정보가 누락되었습니다.' }, { status: 400 });
  }

  try {
    // Django 백엔드 API 호출
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/test_result/?text=${text}&lat=${lat}&lng=${lng}&types=${types}`
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (!data || !data.result) {
      throw new Error('Invalid response format');
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('테스트 결과 조회 실패:', error);
    return NextResponse.json({ 
      error: '테스트 결과를 가져오는데 실패했습니다.',
      detail: error instanceof Error ? error.message : '알 수 없는 오류'
    }, { status: 500 });
  }
} 