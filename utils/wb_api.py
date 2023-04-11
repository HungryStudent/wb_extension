import aiohttp


async def get_card(card_id):
    try:
        vol = int(str(card_id)[0:-5])
        part = int(str(card_id)[0:-3])
    except ValueError:
        return
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

    async with aiohttp.ClientSession() as session:
        async with session.get(f'https:{host}/vol{vol}/part{part}/{card_id}/info/ru/card.json') as resp:
            if resp.status == 404:
                return
            response = await resp.json()
            return response


async def get_card_details(article_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f'https://card.wb.ru/cards/detail?curr=rub&dest=-1257786&regions=80,64,38,4,115,83,33,68,70,69,30,86,75,40,1,66,48,110,22,31,71,114,111&spp=0&nm={article_id}') as resp:
            if resp.status == 404:
                return
            response = await resp.json(content_type="text/plain")
            if response["data"]["products"] is None:
                return
            return response["data"]["products"][0]
