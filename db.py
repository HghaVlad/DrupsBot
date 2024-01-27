import sqlite3
db = "db.sqlite3"


def add_purchase(telegram_id, first_name, data, ship_price):
    with sqlite3.connect(database=db) as con:
        curs = con.cursor()
        curs.execute("INSERT INTO purchases (telegram_id, telegram_first_name, telegram_link, good_link, good_quantity,"
                     "good_size, good_colour, is_photo, photo_path, good_category, good_ship, good_price, ship_price) "
                     "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (telegram_id, first_name,data['telegram'], data['link'], data['quantity'], data['size'], data['colour'], data['is_photo'], data['photo_path'], data['category'], data['ship'],data['price'], ship_price))

        con.commit()


def db_request(column):
    with sqlite3.connect(database=db) as con:
        curs = con.cursor()
        curs.execute(f"SELECT {column} FROM data", )
        res = curs.fetchone()
        print(res)
        return res[0]


def get_admins():
    with sqlite3.connect(database=db) as con:
        curs = con.cursor()
        curs.execute(f"SELECT telegram_id FROM admins" )
        admins = [x[0] for x in curs.fetchall()]
        return admins


def new_value(column, value):
    with sqlite3.connect(database=db) as con:
        curs = con.cursor()
        curs.execute(f"UPDATE data SET {column} = ?", (value,) )
        con.commit()
