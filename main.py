import sqlite3

from starlette.middleware.cors import CORSMiddleware
from typing import List

import requests
from fastapi import FastAPI, HTTPException

from utils import wb_api, parse_card, schemas, crud

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=['POST', 'GET'],
    allow_credentials=True,
)





@app.get('/api/size/{article_id}', response_model=schemas.Size)
async def get_size_by_article_id_request(article_id: int):
    card = await wb_api.get_card(article_id)
    if card is None:
        raise HTTPException(404)

    return parse_card.get_size(card)


@app.get('/api/commission/{article_id}', response_model=schemas.CommissionResponse)
async def get_commission_by_article_id_request(article_id: int):
    card_details = await wb_api.get_card_details(article_id)
    if card_details is None:
        raise HTTPException(404)

    category = crud.get_deliveries_by_category_id(card_details["subjectId"])
    fbo = schemas.Commission(part=category.fbo_part,
                             amount="{:.2f}".format(card_details["salePriceU"] // 100 * category.fbo_part // 100))
    fbs = schemas.Commission(part=category.fbs_part,
                             amount="{:.2f}".format((card_details["salePriceU"] // 100 * category.fbs_part // 100)))
    return schemas.CommissionResponse(fbo=fbo, fbs=fbs)


@app.get("/api/warehouse", response_model=List[schemas.WarehouseResponse])
async def get_warehouses():
    return crud.get_warehouses()


@app.get("/api/logistic/{article_id}/{warehouse_id}", response_model=schemas.Logistic)
async def get_logistic_request(article_id: int, warehouse_id: int):
    warehouse = crud.get_warehouse(warehouse_id)
    if warehouse is None:
        raise HTTPException(404)

    card = await wb_api.get_card(article_id)
    if card is None:
        raise HTTPException(404)

    size_data = parse_card.get_size(card)
    volume = size_data.width * size_data.length * size_data.height * 0.001
    if volume <= 5:
        logistic_amount = warehouse.logistic_base
        storage_amount = warehouse.storage_base
    else:
        logistic_amount = warehouse.logistic_base + (volume - 5) * warehouse.logistic
        storage_amount = warehouse.storage_base + (volume - 5) * warehouse.storage

    return schemas.Logistic(warehouse_id=warehouse_id, logistic_amount=logistic_amount,
                            from_client=warehouse.from_client,
                            storage_amount=storage_amount, reception=warehouse.reception)


@app.get("/api/get_data", response_model=schemas.MainData)
async def get_priority_subjects_request(keyword: str):
    ads_data = requests.get(f"https://catalog-ads.wildberries.ru/api/v5/search?keyword={keyword}").json()
    categories = crud.get_categories_name(ads_data["prioritySubjects"])
    cards_ids = []
    for advert in ads_data["adverts"]:
        cards_ids.append(str(advert["id"]))
    nms = ";".join(cards_ids)

    cards = requests.get(
        f"https://card.wb.ru/cards/detail?curr=rub&dest=-1257786&regions=80,64,38,4,115,83,33,68,70,69,30,86,75,40,1,66,48,110,22,31,71,114,111&spp=0&nm={nms}").json()
    res_cards = []

    max_time = -1
    min_time = 1000
    for index, card in enumerate(cards["data"]["products"]):
        category_id = card["subjectId"]
        categories[category_id]["count"] += 1
        quantity = 0
        for size in card["sizes"]:
            for stock in size["stocks"]:
                quantity += stock["qty"]

        try:
            max_time = max(max_time, card["time1"] + card["time2"])
            min_time = min(min_time, card["time1"] + card["time2"])
        except KeyError:
            pass

        try:
            new_card = schemas.AdsCard(id=card['id'], page=1, pos=1, category=categories[category_id]["name"],
                                       brand=card['brand'], rating=card['rating'], quantity=quantity,
                                       time=card['time1'] + card["time2"], cpm=ads_data['adverts'][index]['cpm'])
        except KeyError:
            new_card = schemas.AdsCard(id=card['id'], page=1, pos=1, category=categories[category_id]["name"],
                                       brand=card['brand'], rating=card['rating'], quantity=quantity,
                                       time=0, cpm=ads_data['adverts'][index]['cpm'])
        res_cards.append(new_card)

    time_info = schemas.TimeInfo(max=max_time, min=min_time)

    summa = len(cards["data"]["products"])
    for category in categories.keys():
        categories[category]["percent_part"] = int((categories[category]["count"] / summa) * 100)
    res_categories = []
    for category in categories.keys():
        print(categories[category])
        res_categories.append(
            schemas.PriorityCategory(name=categories[category]['name'], count=categories[category]['count'],
                                     percent_part=categories[category]['percent_part']))

    return schemas.MainData(priority_categories=res_categories, time_info=time_info, cards=res_cards)
