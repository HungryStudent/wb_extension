from utils import crud
import configparser
import requests
import datetime
import logging

config = configparser.ConfigParser()
config.read("settings.ini")
WBToken = config["settings"]["WBToken"]
receptionWBToken = config["settings"]["receptionWBToken"]
x_supplier_id = config["settings"]["x-supplier-id"]
x_supplier_id_external = config["settings"]["x-supplier-id-external"]
logging.basicConfig(filename="load_logistic.txt",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)


# Получаем данные о коэффициенте логистики и хранения
def update_warehouse():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/39.0.2171.95 Safari/537.36',
        'Content-Type': 'application/json'
    }
    cookies = {"WBToken": WBToken}
    payload = {"warehouse": "asc"}

    now_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")

    res = requests.post(
        f"https://seller-weekly-report.wildberries.ru/ns/categories-info/suppliers-portal-analytics/api/v1/tariffs-period?date={now_date}",
        headers=headers, json=payload, cookies=cookies)

    warehouses = res.json()["data"]["warehouseList"]

    # проходим по складам, если его нет - добавляем, иначе обновляем
    for warehouse in warehouses:
        ratio = int(warehouse["boxDeliveryAndStorageExpr"]) / 100
        res = crud.add_warehouse(warehouse["warehouseName"], warehouse["warehouseName"].lower(), ratio)
        if res == "unique error":
            crud.update_warehouse_by_warehouse_name(warehouse["warehouseName"], ratio)
    logging.info(f"end update warehouses {len(warehouses)}")


# Получаем данные о коэффициенте приемки
def update_reception():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/39.0.2171.95 Safari/537.36',
        'Content-Type': 'application/json'
    }
    cookies = {"WBToken": receptionWBToken, "x-supplier-id-external": x_supplier_id_external}
    # Даты для приёмки
    now_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
    end_date = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=6), "%Y-%m-%d")
    payload = {
        "id": "json-rpc_9",
        "jsonrpc": "2.0",
        "params": {
            "dateTo": f"{end_date}T21:00:00.000Z",
            "dateFrom": f"{now_date}T01:37:15.584Z"
        },
    }

    res = requests.post(
        "https://seller-supply.wildberries.ru/ns/sm-supply/supply-manager/api/v1/supply/acceptanceCoefficientsReport",
        headers=headers, json=payload, cookies=cookies)

    warehouses = res.json()['result']['report']
    for warehouse in warehouses:
        if warehouse['date'][:10] == now_date and warehouse['acceptanceType'] == 6:

            warehouse_name = warehouse['warehouseName'].replace("СЦ ", "").lower()

            if warehouse_name == "санкт-петербург":
                crud.update_reception('санкт-петербург уткина заводь', warehouse['coefficient'])
                crud.update_reception('санкт-петербург шушары', warehouse['coefficient'])
                crud.update_reception('санкт-петербург кбт', warehouse['coefficient'])
            else:
                crud.update_reception(warehouse_name, warehouse['coefficient'])
    logging.info(f"end update receptions {len(warehouses)}")


update_warehouse()
update_reception()
