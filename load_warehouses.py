import sqlite3
import json

with open('warehouses.json', 'r', encoding='utf-8') as f:  # открыли файл с данными
    print("Loading...")
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    warehouses = json.load(f)  # загнали все, что получилось в переменную
    for warehouse in warehouses:
        cursor.execute("INSERT INTO wb_warehouses VALUES (?, ?)", (warehouse["origid"], warehouse["warehouse"]))
        connection.commit()