import requests
import sqlite3
req = requests.get("https://static-basket-01.wb.ru/vol0/data/subject-base.json")
data = req.json()
print("Loading...")
connection = sqlite3.connect("database.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS categories(id INTEGER PRIMARY KEY, name TEXT)")
for parent in data:
    for category in parent["childs"]:
        cursor.execute("INSERT INTO categories VALUES (?, ?)", (category["id"], category["name"]))
        connection.commit()

