fetch("https://mindevprofile.kr/api/recommend/", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
    },
    body: JSON.stringify({
        text: "매운 음식 먹고 싶어",
        price: "10000",
        selected_tests: ["혼밥", "한식"]
    })
})
    .then(res => res.json())
    .then(data => {
        console.log("추천 결과:", data.recommendation);
    });
