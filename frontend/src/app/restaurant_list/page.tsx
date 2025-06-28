'use client';

import { useEffect, useState, useCallback, useRef, Suspense } from 'react';
import styled from '@emotion/styled';
import Image from 'next/image';
import { useSearchParams } from 'next/navigation';

import Loading from '@/components/Loading';
import { Restaurant } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

const Container = styled.div`
  background-color: honeydew;
  min-height: 100vh;
  padding: 1rem;
`;

const Title = styled.h1`
  margin: 1rem;
  font-weight: bold;
  color: #222;
  font-size: 1.5rem;
  
  @media (max-width: 768px) {
    font-size: 1.2rem;
    margin: 0.75rem;
  }
`;

const Address = styled.h2`
  margin: 1rem;
  font-weight: bold;
  color: #222;
  font-size: 1.2rem;
  
  @media (max-width: 768px) {
    font-size: 1rem;
    margin: 0.75rem;
  }
`;

const StoreCard = styled.div`
  border: 1px solid #ccc;
  border-radius: 0.75rem;
  padding: 1.25rem;
  margin: 1.25rem;
  box-shadow: 0.125rem 0.125rem 0.625rem rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 1.25rem;
  background-color: #fff;
  
  @media (max-width: 768px) {
    padding: 1rem;
    margin: 1rem;
    gap: 1rem;
    flex-direction: column;
    text-align: center;
  }
`;

const StoreInfo = styled.div`
  flex: 1;
`;

const StoreName = styled.div`
  font-size: 1.375rem;
  font-weight: bold;
  
  @media (max-width: 768px) {
    font-size: 1.1rem;
  }
`;

const StoreImage = styled(Image)`
  border-radius: 0.5rem;
  width: 6.25rem;
  height: auto;
  
  @media (max-width: 768px) {
    width: 5rem;
  }
`;

const EmptyMessage = styled.p`
  text-align: center;
  margin: 2rem;
  font-size: 1.2rem;
  color: #666;
  
  @media (max-width: 768px) {
    font-size: 1rem;
    margin: 1.5rem;
  }
`;

function RestaurantListPage() {
  const searchParams = useSearchParams();
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [currentAddress, setCurrentAddress] = useState<string>('로딩 중...');
  const [isLoading, setIsLoading] = useState(true);
  const isFetchingRef = useRef(false);
  const locationFetchRef = useRef(false);

  const fetchLocationFromIP = useCallback(async () => {
    if (locationFetchRef.current) return;
    locationFetchRef.current = true;

    try {
      const response = await fetch(`${API_BASE_URL}/api/ip-location/`);
      const data = await response.json();
      if (data.loc) {
        const [latitude, longitude] = data.loc.split(',');
        loadRestaurants(parseFloat(latitude), parseFloat(longitude));
        console.log('loadRestaurants 호출됨:', latitude, longitude);
        console.log('data:', data);
        console.log('response:', response);
      }
    } catch (error) {
      console.error('IP 위치 요청 실패', error);
    } finally {
      locationFetchRef.current = false;
    }
  }, []);

  useEffect(() => {
    const lat = searchParams.get('lat');
    const lng = searchParams.get('lng');
    if (!lat || !lng) {
      fetchLocationFromIP();
    } else {
      loadRestaurants(parseFloat(lat), parseFloat(lng));
    }
  }, [searchParams, fetchLocationFromIP]);

  const loadRestaurants = async (lat: number, lng: number) => {
    if (isFetchingRef.current) return;
    isFetchingRef.current = true;

    console.log('[loadRestaurants] 호출됨:', lat, lng);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';
      const response = await fetch(`${apiUrl}/api/v1/restaurants?lat=${lat}&lng=${lng}`);
      const contentType = response.headers.get("content-type");
      console.log('[loadRestaurants] contentType:', contentType);
      console.log('[loadRestaurants] response:', response);
      if (!response.ok || !contentType?.includes("application/json")) {
        throw new Error("서버 응답이 JSON이 아닙니다.");
      }
      if (!response.ok) {
        throw new Error('Failed to fetch restaurants');
      }
      const data = await response.json();
      console.log('[loadRestaurants] data', data);
      setRestaurants(Array.isArray(data) ? data : data.restaurants.slice(0, 100) || []);
      setCurrentAddress(data.address || '위치 정보를 가져올 수 없습니다.');
    } catch (error) {
      console.error('[loadRestaurants] 레스토랑 정보 로딩 실패', error);
      setRestaurants([]);
      setCurrentAddress('위치 정보를 가져올 수 없습니다.');
    } finally {
      setIsLoading(false);
      isFetchingRef.current = false;
    }
  };

  if (isLoading) {
    return <Loading />;
  }

  return (
    <Container>
      <Title>🥄 근처 배달 가능한 가게 목록</Title>
      <Address>{currentAddress}</Address>

      {Array.isArray(restaurants) && restaurants.length > 0 ? (
        restaurants.map((restaurant, index) => (
          <StoreCard key={`${restaurant.id}-${index}`}>
            <StoreImage
              src={restaurant.logo_url || "/image/default_store.png"}
              alt={restaurant.name}
              width={100}
              height={100}
            />
            <StoreInfo>
              <StoreName>
                {restaurant.name} (⭐ {restaurant.review_avg})
              </StoreName>
              <div className="store-category">
                카테고리: {Array.isArray(restaurant.categories) ? restaurant.categories.join(', ') : '정보 없음'}
              </div>
              <div className="store-delivery">
                배달비: {restaurant.delivery_fee_to_display?.basic || '정보 없음'}
              </div>
              <div className="store-review">
                리뷰 수: {restaurant.review_count ?? '정보 없음'}
              </div>
            </StoreInfo>
          </StoreCard>
        ))
      ) : (
        <EmptyMessage>😢 근처 가게를 불러오지 못했어요.</EmptyMessage>
      )}

    </Container>
  );
}

export default function RestaurantList() {
  return (
    <Suspense fallback={<Loading />}>
      <RestaurantListPage />
    </Suspense>
  );
} 