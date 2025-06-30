import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL;
if (!BACKEND_URL) {
  throw new Error('NEXT_PUBLIC_API_URL is not defined');
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // 백엔드로 요청 전달
    const response = await fetch(`${BACKEND_URL}/api/v1/translate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      console.error('Backend translation API error:', response.status, response.statusText);
      return NextResponse.json(
        { error: 'Translation service error' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('Translation API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 