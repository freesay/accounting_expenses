CREATE TABLE IF NOT EXISTS categories(
    category VARCHAR(255),
    aliases TEXT
);

CREATE TABLE IF NOT EXISTS expenses(
    id INTEGER PRIMARY KEY,
    message_id INTEGER,
    user_id INTEGER,
    amount INTEGER,
    created DATE,
    category INTEGER
);

INSERT INTO categories (category, aliases)
VALUES
    ('продукты', 'еда, завтрак, обед, ужин, хлеб, кофе, чай'),
    ('кафе', 'кафе, ресторан, мак, бургер, кфс'),
    ('сигареты', 'сиги, сижки'),
    ('транспорт', 'метро, автобус, маршрутка, троллейбус, тралик, трамвай'),
    ('такси', 'убер'),
    ('телефон', 'теле2, связь, ёта, yota, мегафон, мтс'),
    ('интернет', 'инет'),
    ('прочее', 'клей, саморезы');
