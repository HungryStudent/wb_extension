from fastapi import APIRouter, HTTPException
from utils import schemas, crud, parse_card, wb_api
from typing import List

router = APIRouter(tags=["Unit"])


def calculate_logistic(size_data: schemas.Size, warehouse: schemas.Warehouse):
    volume = size_data.width * size_data.length * size_data.height * 0.001
    if volume <= 5:
        logistic_amount = 50
        storage_amount = 0.12
        reception_amount = 15.32
    else:
        logistic_amount = 50 + (volume - 5) * 5
        storage_amount = 0.12 + (volume - 5) * 0.012
        reception_amount = 15 + (volume - 5) * 1.5

    logistic_amount *= warehouse.ratio, 2
    storage_amount *= warehouse.ratio, 2
    from_client = 50
    if warehouse.reception_ratio is None:
        reception_amount = -1
    else:
        reception_amount *= warehouse.reception_ratio

    logistic_amount = round(logistic_amount, 2)
    storage_amount = round(storage_amount, 2)
    reception_amount = round(reception_amount, 2)

    return schemas.Logistic(warehouse_id=warehouse.id, logistic_amount=logistic_amount,
                            from_client=from_client,
                            storage_amount=storage_amount, reception_amount=reception_amount)


@router.get('/size/{article_id}', response_model=schemas.Size)
async def get_size_by_article_id_request(article_id: int):
    card = await wb_api.get_card(article_id)
    if card is None:
        raise HTTPException(404)

    return parse_card.get_size(card)


@router.get('/certificate/{article_id}')
async def get_certificate_request(article_id: int):
    certificate = await wb_api.get_certificate(article_id)
    if certificate is None:
        raise HTTPException(404)
    else:
        return certificate['url']


@router.get('/commission/{article_id}', response_model=schemas.CommissionResponse)
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


@router.get("/warehouse", response_model=List[schemas.WarehouseResponse])
async def get_warehouses():
    return crud.get_warehouses()


@router.get("/logistic/{article_id}/{warehouse_id}", response_model=schemas.Logistic)
async def get_logistic_request(article_id: int, warehouse_id: int):
    warehouse = crud.get_warehouse(warehouse_id)
    if warehouse is None:
        raise HTTPException(404)

    card = await wb_api.get_card(article_id)
    if card is None:
        raise HTTPException(404)

    size_data = parse_card.get_size(card)

    return calculate_logistic(size_data, warehouse)


@router.post("/calculation/{article_id}")
async def unit_calculation_request(article_id: int, data: schemas.UnitCalculation):
    warehouse = crud.get_warehouse(data.warehouse_id)
    if warehouse is None:
        raise HTTPException(404)

    card = await wb_api.get_card(article_id)
    if card is None:
        raise HTTPException(404)

    card_details = await wb_api.get_card_details(article_id)
    if card_details is None:
        raise HTTPException(404)

    size_data = parse_card.get_size(card)
    logistic_data = calculate_logistic(size_data=size_data, warehouse=warehouse)

    price_without_spp = card_details["salePriceU"] // 100
    margin = price_without_spp

    # вычитаем комиссию WB
    category = crud.get_deliveries_by_category_id(card_details["subjectId"])

    wb_commission_part = 1
    if data.delivery_type == schemas.DeliveryTypeEnum.fbo:
        wb_commission_part = category.fbo_part
    elif data.delivery_type == schemas.DeliveryTypeEnum.fbs:
        wb_commission_part = category.fbs_part
    wb_commission = card_details["salePriceU"] // 100 * wb_commission_part // 100
    margin -= wb_commission

    # вычитаем логистику
    margin -= logistic_data.logistic_amount

    # вычитаем приёмку
    pass

    # вычитаем цену закупки
    margin -= data.purchase_price

    # создаем вычитаемое для рентабельности
    profitability_subtract = data.purchase_price

    # вычитаем доп расходы
    if data.additional is not None:
        margin -= data.additional
        profitability_subtract += data.additional

    # вычитаем логистику до мп:
    if data.logistic_to_mp is not None:
        margin -= data.logistic_to_mp
        profitability_subtract += data.logistic_to_mp

    # вычитаем оборачиваемость
    if data.wrap_days is not None:
        margin -= logistic_data.storage_amount * data.wrap_days

    # вычитаем процент выкупа:
    if data.redemption_percent is not None:
        margin -= (logistic_data.logistic_amount * (1 + (100 - data.redemption_percent) / data.redemption_percent)) + (
                (100 - data.redemption_percent) / data.redemption_percent * data.logistic_to_mp)

    # вычитаем процент брака
    if data.marriage_percent is not None:
        margin -= data.purchase_price * (data.marriage_percent / 100)

    # вычитаем налоговую ставку
    if data.tax_rate is not None:
        margin -= price_without_spp * (data.tax_rate / 100)

    # считаем процент маржи и рентабельность
    margin_percent = round(margin / price_without_spp * 100, 2)
    profitability = margin / profitability_subtract

    # если запросили цель по прибыли - считаем, иначе выводим 0 0
    profit_target = schemas.ProfitTarget()
    if data.profit_target is not None:
        quantity = data.profit_target / margin
        profit_target.quantity = int(quantity)
        profit_target.day_quantity = int(quantity / 30)

    margin = round(margin, 2)
    return schemas.UnitCalculationResponse(margin=margin, margin_percent=margin_percent, profitability=profitability,
                                           profit_target=profit_target)
