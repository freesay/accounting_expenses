import os
import sqlite3
from datetime import date

conn = sqlite3.connect(os.path.join('db', 'finance.db'))
cursor = conn.cursor()


def parse_message(message_id, user_id, message):
    print(message_id, user_id, ':', message)
    category = str(message.split()[0]).lower()
    amount = int(message.split()[1])
    parse_data = {'message_id': message_id, 'user_id': user_id, 'category': category, 'amount': amount}
    return parse_data


def check_aliases(data):
    parse_data = data
    get_aliases = cursor.execute("SELECT category, aliases FROM categories;")
    aliases = get_aliases.fetchall()
    dict_aliases = {}
    for row in aliases:
        dict_aliases[row[0]] = row[1]
    flag = False
    for key, values in dict_aliases.items():
        for value in values.split(', '):
            if parse_data['category'] == key or parse_data['category'] == value:
                parse_data['category'] = key
                flag = True
                break
    return flag, parse_data


def add_alias(category, alias):
    get_aliases = cursor.execute("SELECT aliases FROM categories "
                                 "WHERE category = ?;", (category,))
    aliases = get_aliases.fetchone()[0] + ', ' + alias
    cursor.execute("UPDATE categories "
                   "SET aliases = ? "
                   "WHERE category = ?;", (aliases, category))
    conn.commit()


def delete_alias(category, alias):
    get_aliases = cursor.execute("SELECT aliases FROM categories "
                                 "WHERE category = ?;", (category,))
    aliases = get_aliases.fetchone()[0]
    if aliases.endswith(f', {alias}'):
        aliases = aliases[:len(aliases) - len(f', {alias}')]
    cursor.execute("UPDATE categories "
                   "SET aliases = ? "
                   "WHERE category = ?;", (aliases, category))
    conn.commit()


def insert(data):
    db_values = (data['message_id'], data['user_id'], data['amount'], str(date.today()), data['category'])
    cursor.execute("INSERT INTO expenses (message_id, user_id, amount, created, category)"
                   "VALUES (?, ?, ?, ?, ?)", db_values)
    conn.commit()


def get_day_statistics(user_id):
    today = str(date.today())
    statistics = cursor.execute("SELECT created, "
                                "(SELECT category "
                                "FROM categories "
                                "WHERE expenses.category = categories.category) AS category, "
                                "SUM(amount) AS amount "
                                "FROM expenses "
                                "WHERE created = ? AND user_id = ? "
                                "GROUP BY category "
                                "ORDER BY amount DESC;", (today, user_id))
    rows = statistics.fetchall()
    dict_row = {}
    for row in rows:
        dict_row[row[1]] = row[2]
    amount = cursor.execute("SELECT SUM(amount) AS amount "
                            "FROM expenses "
                            "WHERE created = ? AND user_id = ? "
                            "GROUP BY created;", (today, user_id))
    fetch_amount = amount.fetchone()
    return dict_row, fetch_amount


def get_month_statistics(user_id):
    today = date.today()
    month = today.month
    statistics = cursor.execute("SELECT "
                                "(SELECT category "
                                "FROM categories "
                                "WHERE expenses.category = categories.category) AS category, "
                                "SUM(amount) "
                                "FROM expenses "
                                "WHERE strftime('%m', created) = ? AND user_id = ? "
                                "GROUP BY category "
                                "ORDER BY SUM(amount) DESC;", (f'{month:02d}', user_id))
    rows = statistics.fetchall()
    dict_row = {}
    for row in rows:
        dict_row[row[0]] = row[1]
    amount = cursor.execute("SELECT SUM(amount) AS amount "
                            "FROM expenses "
                            "WHERE strftime('%m', created) = ? AND user_id = ?;", (f'{month:02d}', user_id))
    fetch_amount = amount.fetchone()
    return dict_row, fetch_amount


def get_categories():
    categories = cursor.execute("SELECT category, aliases FROM categories;")
    rows = categories.fetchall()
    categories_dict = {}

    for row in rows:
        categories_dict[row[0]] = row[1].split()
    return categories_dict


def add_categories(category, alias):
    cursor.execute("INSERT INTO categories (category, aliases) "
                   "VALUES (?, ?);", (category.lower(), alias.lower()))
    conn.commit()


def delete_category(category):
    cursor.execute("DELETE FROM categories "
                   "WHERE category = ?;", (category,))
    conn.commit()


def check_entry(message):
    if message == '/day':
        today = str(date.today())
        entry = cursor.execute("SELECT created FROM expenses "
                               "WHERE created = ?;", (today,))
        entry_exists = entry.fetchall()
        if not entry_exists:
            return True
    elif message == '/month':
        today = date.today()
        month = today.month
        entry = cursor.execute("SELECT created FROM expenses "
                               "WHERE strftime('%m', created) = ?;", (f'{month:02d}',))
        entry_exists = entry.fetchall()
        if not entry_exists:
            return True


def delete_entry(message_id, user_id):
    cursor.execute("DELETE FROM expenses "
                   "WHERE message_id = ? AND user_id = ?;", (message_id, user_id))
    conn.commit()


def init_db():
    with open('db/create_db.sql', 'r') as file:
        sql = file.read()
    cursor.executescript(sql)
    conn.commit()


def check_init():
    info = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_exists = info.fetchall()
    if not table_exists:
        init_db()


check_init()
