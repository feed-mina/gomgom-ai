
// 카테고리 종류
fetch("https://www.yogiyo.co.kr/api/v1/restaurants?lat=37.475&lng=126.981&page=0&serving_type=delivery")
    .then(response => response.json())
    .then(data => {
        // 모든 카테고리를 하나의 배열로 모으기
        const allCategories = data.flatMap(item => item.categories);

        // 중복 제거 (Set 사용)
        const uniqueCategories = [...new Set(allCategories)];

        console.log("유일한 카테고리 목록:", uniqueCategories);
    })
    .catch(error => console.error("에러 발생:", error));


// 가게이름, 카테고리, 리뷰점수만 뽑기 
fetch("https://www.yogiyo.co.kr/api/v1/restaurants?lat=37.475&lng=126.981&page=0&serving_type=delivery")
    .then(response => response.json()) // JSON 형태로 변환
    .then(data => {
        // 여기서 원하는 값만 뽑을 거야
        const simplified = data.map(item => ({
            name: item.name,
            categories: item.categories,
            review_avg: item.review_avg
        }));

        console.log(simplified); // 확인용 출력
    })
    .catch(error => console.error("에러 발생:", error));