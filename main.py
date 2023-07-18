from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from utils import wb_api, schemas, crud
from endpoints import *
from typing import List
import requests
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=['POST', 'GET'],
    allow_credentials=True,
)

app.include_router(unit.router, prefix="/api/unit")


@app.on_event("startup")
async def startup_event():
    crud.start()
    pass


@app.get("/api/get_data", response_model=schemas.MainData)
async def get_priority_subjects_request(keyword: str):
    ads_data = requests.get(f"https://catalog-ads.wildberries.ru/api/v5/search?keyword={keyword}").json()
    if ads_data['adverts'] is None:
        raise HTTPException(404)

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
        res_categories.append(
            schemas.PriorityCategory(name=categories[category]['name'], count=categories[category]['count'],
                                     percent_part=categories[category]['percent_part']))

    return schemas.MainData(priority_categories=res_categories, time_info=time_info, cards=res_cards)


@app.get('/api/create_product_date/{article_id}')
async def create_product_date_request(article_id: int):
    card = await wb_api.get_card(article_id)
    if card is None:
        raise HTTPException(404)
    # получаем информацию об отзывах на эту карточку
    feedbacks = await wb_api.get_feedbacks(card["imt_id"], is_order_by_date=True)
    min_date = "2024-01-01"
    for record in feedbacks:
        min_date = min(min_date, record["createdDate"])
    return min_date[:10]


@app.get('/api/rating_calculator/{article_id}', response_model=List[schemas.RatingStar])
async def get_rating_data_request(article_id: int):
    card = await wb_api.get_card(article_id)
    if card is None:
        raise HTTPException(404)

    # получаем информацию об отзывах на эту карточку
    card_valuation_data = await wb_api.get_card_valuation(card["imt_id"])
    if card_valuation_data is None:
        return []

    valuation = float(card_valuation_data["valuation"])
    if valuation > 4.6:
        return []
    valuationDistributionSum = 0
    feedbackCount = card_valuation_data["feedbackCount"]
    for key, value in card_valuation_data["valuationDistribution"].items():
        valuationDistributionSum += int(key) * value

    # создаем массив с основными int рейтингами, где index|rate = [0|2, 1|3, 2|4, 3|5]
    rating_stars = [schemas.RatingStar(rate=i, reviews_count=0, ratings=[]) for i in range(2, 6)]

    for i in range(int(valuation * 10) + 1, 47):
        rating = i / 10

        reviews_count = math.ceil((rating * feedbackCount - valuationDistributionSum) / (5 - rating))
        rating_star_index = 0
        if 0 <= rating <= 1.6:
            rating_star_index = 0
        elif 1.7 <= rating <= 2.6:
            rating_star_index = 1
        elif 2.7 <= rating <= 3.6:
            rating_star_index = 2
        elif 3.7 <= rating <= 4.6:
            rating_star_index = 3

        rating_stars[rating_star_index].ratings.append(schemas.Rating(rate=rating, reviews_count=reviews_count))
        rating_stars[rating_star_index].reviews_count += 1

    return rating_stars


@app.get("/api/stocks/{article_id}")
async def get_stock_request(article_id: int, get_by: str):
    card = await wb_api.get_card_details(article_id)
    if card is None:
        raise HTTPException(404)
    if get_by == "warehouses":
        temp_stocks = {}
        all_stocks_count = 0
        for size in card["sizes"]:
            for warehouse in size["stocks"]:
                all_stocks_count += warehouse["qty"]
                try:
                    temp_stocks[warehouse["wh"]] += warehouse["qty"]
                except KeyError:
                    temp_stocks[warehouse["wh"]] = warehouse["qty"]

        res = []
        seller_warehouse = schemas.StocksByWarehouses(warehouse_name="Склад поставщика", percent=0, qty=0)
        for warehouse_id, qty in temp_stocks.items():
            warehouse_data = crud.get_warehouse_name(warehouse_id)
            if warehouse_data is None:
                seller_warehouse.qty += qty
                continue
            warehouse_name = warehouse_data[1]

            percent = qty * 100 / all_stocks_count
            percent = 1 if percent < 1 else int(percent)
            res.append(
                schemas.StocksByWarehouses(warehouse_name=warehouse_name, percent=percent,
                                           qty=qty))

        percent = seller_warehouse.qty * 100 / all_stocks_count
        percent = 1 if percent < 1 else int(percent)
        seller_warehouse.percent = percent
        res.append(seller_warehouse)

        res = sorted(res, key=lambda x: x.percent, reverse=True)
        return res
    elif get_by == "sizes":
        res = []

        for size in card["sizes"]:
            seller_sizes = schemas.StocksBySizes(size=size["name"], warehouse_name="Склад поставщика", qty=0)
            for warehouse in size["stocks"]:
                warehouse_data = crud.get_warehouse_name(warehouse["wh"])
                if warehouse_data is None:
                    seller_sizes.qty += warehouse["qty"]
                    continue
                warehouse_name = warehouse_data[1]
                if warehouse["qty"] != 0:
                    res.append(
                        schemas.StocksBySizes(size=size["name"], warehouse_name=warehouse_name, qty=warehouse["qty"]))
            if seller_sizes.qty != 0:
                res.append(seller_sizes)
        return res
    else:
        raise HTTPException(400, "invalid get_by param")


@app.get("/api/seasonality")
async def get_seasonality_request(query: str):
    res = requests.get(f"http://127.0.0.1:8002/seasonality?query={query}")
    if res.status_code == 404:
        raise HTTPException(404, "not found")
    return res.json()


@app.get("/api/photos/{article_id}")
async def get_photos_by_article_id_request(article_id: int):
    try:
        vol = int(str(article_id)[0:-5])
        part = int(str(article_id)[0:-3])
    except ValueError:
        return
    host = wb_api.get_base_url(vol, part)
    card = await wb_api.get_card(article_id)
    photo_count = card["media"]["photo_count"]
    photo_urls = []
    for i in range(photo_count):
        url = f"https:{host}/vol{vol}/part{part}/{article_id}/images/big/{i + 1}.jpg"
        photo_urls.append(url)
    return photo_urls
