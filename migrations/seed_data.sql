INSERT INTO users (email, hashed_password, full_name, is_active, is_superuser)
VALUES 
    ('admin@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Admin User', true, true),
    ('user@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Test User', true, false);

INSERT INTO recipes (name, description, instructions, cooking_time, difficulty)
VALUES 
    ('김치찌개', '맛있는 김치찌개 레시피', '1. 돼지고기를 적당한 크기로 썰어주세요.\n2. 김치는 적당한 크기로 썰어주세요.\n3. 냄비에 물을 붓고 돼지고기를 넣어 끓여주세요.\n4. 고기가 익으면 김치를 넣고 끓여주세요.', 30, '쉬움'),
    ('된장찌개', '구수한 된장찌개 레시피', '1. 두부를 적당한 크기로 썰어주세요.\n2. 애호박과 양파를 썰어주세요.\n3. 냄비에 물을 붓고 된장을 풀어주세요.\n4. 재료를 넣고 끓여주세요.', 25, '쉬움'),
    ('불고기', '달콤한 불고기 레시피', '1. 쇠고기를 적당한 크기로 썰어주세요.\n2. 양파와 당근을 썰어주세요.\n3. 양념장을 만들어 고기를 재워주세요.\n4. 팬에 기름을 두르고 고기를 구워주세요.', 40, '보통');

INSERT INTO ingredients (name, price, unit)
VALUES 
    ('돼지고기', 15000, 'g'),
    ('김치', 8000, 'g'),
    ('두부', 2000, '개'),
    ('된장', 5000, 'g'),
    ('쇠고기', 25000, 'g'),
    ('양파', 2000, '개'),
    ('당근', 1500, '개');

INSERT INTO ingredients_ko (name, ingredient_id)
VALUES 
    ('돼지고기', 1),
    ('김치', 2),
    ('두부', 3),
    ('된장', 4),
    ('쇠고기', 5),
    ('양파', 6),
    ('당근', 7);

INSERT INTO locations (name, address, latitude, longitude)
VALUES 
    ('강남점', '서울특별시 강남구 테헤란로 123', 37.5665, 127.0280),
    ('홍대점', '서울특별시 마포구 홍대입구로 123', 37.5575, 126.9250),
    ('부산점', '부산광역시 해운대구 해운대해변로 123', 35.1796, 129.1686);

INSERT INTO recommendations (user_id, recipe_id, score)
VALUES 
    (1, 1, 4.5),
    (1, 2, 4.0),
    (1, 3, 4.8),
    (2, 1, 4.2),
    (2, 2, 4.7),
    (2, 3, 4.3);

SELECT 'Users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'Recipes', COUNT(*) FROM recipes
UNION ALL
SELECT 'Ingredients', COUNT(*) FROM ingredients
UNION ALL
SELECT 'Ingredients_KO', COUNT(*) FROM ingredients_ko
UNION ALL
SELECT 'Locations', COUNT(*) FROM locations
UNION ALL
SELECT 'Recommendations', COUNT(*) FROM recommendations; 