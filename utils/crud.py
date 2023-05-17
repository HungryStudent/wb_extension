from typing import List

from utils import schemas

from contextlib import closing
import sqlite3

database = "database.db"


def start():
    with closing(sqlite3.connect(database)) as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS commissions(category_id INT PRIMARY KEY, fbo INT, fbs INT)")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS warehouses(warehouse_id INT, warehouse_name TEXT, warehouse_name_lower TEXT, logistic_base FLOAT, logistic FLOAT, from_client FLOAT, storage_base FLOAT, storage FLOAT, reception FLOAT)")
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
        return schemas.Warehouse(id=data[0], name=data[1], logistic_base=data[3], logistic=data[4], from_client=data[8],
                                 storage_base=data[5], storage=data[6], reception=data[7])


def add_warehouse(warehouse_name, warehouse_name_lower, logistic_base, logistic, storage_base, storage):
    with closing(sqlite3.connect(database)) as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO warehouses(warehouse_name, warehouse_name_lower, logistic_base, logistic, storage_base, storage) "
            "VALUES(?, ?, ?, ?, ?, ?)",
            (warehouse_name, warehouse_name_lower, logistic_base, logistic, storage_base, storage,))
        connection.commit()


def update_reception(name, reception):
    with closing(sqlite3.connect(database)) as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            "UPDATE warehouses SET reception = ? WHERE warehouse_name_lower = ?",
            (reception, name))
        connection.commit()


def update_logistic_and_storage(name, logistic_base, logistic, from_client, storage_base, storage):
    with closing(sqlite3.connect(database)) as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            "UPDATE warehouses SET logistic_base = ?, logistic = ?, from_client = ?, storage_base = ?, storage = ? WHERE warehouse_name_lower = ?",
            (logistic_base, logistic, from_client, storage_base, storage, name))
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

start()
