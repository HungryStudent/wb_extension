from utils import schemas
from typing import List
import configparser

from contextlib import closing
import sqlite3

from asyncpg import Connection
import asyncpg

database = "database.db"

config = configparser.ConfigParser()
config.read("settings.ini")
DB_USER = config["db"]["user"]
DB_PASSWORD = config["db"]["password"]
DB_DATABASE = config["db"]["database"]
DB_HOST = config["db"]["host"]
DB_PORT = config["db"]["port"]


async def get_conn() -> Connection:
    return await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE, host=DB_HOST, port=DB_PORT)


# async def start():
#     conn: Connection = await get_conn()
#     await conn.execute("CREATE TABLE IF NOT EXISTS commissions(id SMALLSERIAL PRIMARY KEY, fbo SMALLINT, fbs SMALLINT)")
#     await conn.execute("CREATE TABLE IF NOT EXISTS warehouses(warehouse_id SMALLSERIAL PRIMARY KEY,"
#             "warehouse_name VARCHAR(100) UNIQUE, warehouse_name_lower VARCHAR(100),"
#             "ratio FLOAT, reception_ratio INTEGER)")
#     await conn.execute("CREATE TABLE IF NOT EXISTS wb_warehouses(warehouse_id INTEGER, warehouse_name VARCHAR(100))")
#     await conn.execute("CREATE TABLE IF NOT EXISTS categories(id INTEGER, name VARCHAR(100))")
#     await conn.close()


def start():
    with closing(sqlite3.connect(database)) as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS warehouses(warehouse_id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "warehouse_name TEXT UNIQUE, warehouse_name_lower TEXT, "
            "ratio FLOAT, reception_ratio INTEGER)")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS wb_warehouses(warehouse_id INT, warehouse_name TEXT)")

        connection.commit()


def delete_categories():
    with closing(sqlite3.connect(database)) as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("DELETE FROM commissions")
        connection.commit()


def add_category(category_id, fbo, fbs):
    with closing(sqlite3.connect(database)) as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("INSERT INTO commissions VALUES(?, ?, ?)", (category_id, fbo, fbs))
        connection.commit()


def get_deliveries_by_category_id(category_id) -> schemas.Category:
    with closing(sqlite3.connect(database)) as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("SELECT * FROM commissions WHERE category_id = ?", (category_id,))
        data = cursor.fetchone()
        return schemas.Category(category_id=data[0], fbo_part=data[1], fbs_part=data[2])


def get_warehouses():
    with closing(sqlite3.connect(database)) as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("SELECT * FROM warehouses")
        data = cursor.fetchall()
        res = []
        for warehouse in data:
            res.append(schemas.WarehouseResponse(id=warehouse[0], name=warehouse[1]))
        return res


def get_warehouse(warehouse_id):
    with closing(sqlite3.connect(database)) as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("SELECT * FROM warehouses WHERE warehouse_id = ?", (warehouse_id,))
        data = cursor.fetchone()
        if data is None:
            return
        return schemas.Warehouse(id=data[0], name=data[1], ratio=data[3], reception_ratio=data[4])


def add_warehouse(warehouse_name, warehouse_name_lower, ratio):
    with closing(sqlite3.connect(database)) as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO warehouses(warehouse_name, warehouse_name_lower, ratio) VALUES(?, ?, ?)",
                (warehouse_name, warehouse_name_lower, ratio))
        except sqlite3.IntegrityError:
            return "unique error"
        connection.commit()


def update_warehouse_by_warehouse_name(warehouse_name, ratio):
    with closing(sqlite3.connect(database)) as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            "UPDATE warehouses set ratio = ? where warehouse_name = ?",
            (ratio, warehouse_name))
        connection.commit()


def update_reception(name, reception):
    with closing(sqlite3.connect(database)) as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            "UPDATE warehouses SET reception_ratio = ? WHERE warehouse_name_lower = ?",
            (reception, name))
        connection.commit()


def delete_warehouses():
    with closing(sqlite3.connect(database)) as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("DELETE FROM warehouses")
        connection.commit()


def get_categories_name(ids: List[int]):
    with closing(sqlite3.connect(database)) as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        res = {}
        for id in ids:
            cursor.execute("SELECT * FROM categories WHERE id = ?", (id,))
            category = cursor.fetchone()
            res[category[0]] = {"name": category[1], "count": 0}
        return res


def get_warehouse_name(warehouse_id):
    with closing(sqlite3.connect(database)) as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("SELECT * FROM wb_warehouses WHERE warehouse_id = ?", (warehouse_id,))
        return cursor.fetchone()
