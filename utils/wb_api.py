import aiohttp


def get_base_url(vol, part):
    if 0 <= vol <= 143:
        host = "//basket-01.wb.ru"
    elif 144 <= vol <= 287:
        host = "//basket-02.wb.ru"
    elif 288 <= vol <= 431:
        host = "//basket-03.wb.ru"
    elif 432 <= vol <= 719:
        host = "//basket-04.wb.ru"
    elif 720 <= vol <= 1007:
        host = "//basket-05.wb.ru"
    elif 1008 <= vol <= 1061:
        host = "//basket-06.wb.ru"
    elif 1062 <= vol <= 1115:
        host = "//basket-07.wb.ru"
    elif 1116 <= vol <= 1169:
        host = "//basket-08.wb.ru"
    elif 1170 <= vol <= 1313:
        host = "//basket-09.wb.ru"
    elif 1314 <= vol <= 1601:
        host = "//basket-10.wb.ru"
    elif 1602 <= vol <= 1655:
        host = "//basket-11.wb.ru"
    else:
        host = "//basket-12.wb.ru"
    return host


async def get_card(card_id):
    try:
        vol = int(str(card_id)[0:-5])
        part = int(str(card_id)[0:-3])
    except ValueError:
        return
    host = get_base_url(vol, part)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f'https:{host}/vol{vol}/part{part}/{card_id}/info/ru/card.json') as resp:
                if resp.status == 404:
                    return
                response = await resp.json()
                return response
        except aiohttp.client_exceptions.ClientConnectorError:
            return


async def get_certificate(card_id):
    try:
        vol = int(str(card_id)[0:-5])
        part = int(str(card_id)[0:-3])
    except ValueError:
        return
    host = get_base_url(vol, part)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f'https:{host}/vol{vol}/part{part}/{card_id}/info/certificate.json') as resp:
                if resp.status == 404:
                    return
                response = await resp.json()
                return response
        except aiohttp.client_exceptions.ClientConnectorError:
            return


async def get_card_details(article_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f'https://card.wb.ru/cards/detail?curr=rub&dest=-1257786&regions=80,64,38,4,115,83,33,68,70,69,30,86,75,40,1,66,48,110,22,31,71,114,111&spp=0&nm={article_id}') as resp:
            if resp.status == 404:
                return
            response = await resp.json(content_type="application/json")
            if response["data"]["products"] is None or not response["data"]["products"]:
                return
            return response["data"]["products"][0]


async def get_card_valuation(imt_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f'https://feedbacks1.wb.ru/feedbacks/v1/{imt_id}') as resp:
            response = await resp.json(content_type="application/json")
            if response["valuation"] != "":
                return {"valuation": response["valuation"], "valuationDistribution": response["valuationDistribution"],
                        "feedbackCount": response["feedbackCount"]}
        async with session.get(
                f'https://feedbacks2.wb.ru/feedbacks/v1/{imt_id}') as resp:
            response = await resp.json(content_type="application/json")
            if response["valuation"] != "":
                return {"valuation": response["valuation"], "valuationDistribution": response["valuationDistribution"],
                        "feedbackCount": response["feedbackCount"]}
            else:
                return None


async def get_feedbacks(imt_id, is_order_by_date=False):
    url = f'https://feedbacks1.wb.ru/feedbacks/v1/{imt_id}?'
    if is_order_by_date:
        url += "order=dateAsc"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            response = await resp.json(content_type="application/json")
            if response["valuation"] != "":
                return response["feedbacks"]
        async with session.get(
                f'https://feedbacks2.wb.ru/feedbacks/v1/{imt_id}') as resp:
            response = await resp.json(content_type="application/json")
            if response["valuation"] != "":
                return response["feedbacks"]
            else:
                return None
