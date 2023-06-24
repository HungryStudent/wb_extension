from pydantic import BaseModel
from typing import List
from enum import Enum



class DeliveryTypeEnum(Enum):
    fbo = "fbo"
    fbs = "fbs"


class UnitCalculation(BaseModel):
    delivery_type: DeliveryTypeEnum
    warehouse_id: int
    purchase_price: float
    additional: float = None
    logistic_to_mp: float = None
    wrap_days: int = None
    redemption_percent: int = None
    marriage_percent: int = None
    tax_rate: int = None
    profit_target: int = None


class ProfitTarget(BaseModel):
    quantity: int = 0
    day_quantity: int = 0


class UnitCalculationResponse(BaseModel):
    margin: float
    margin_percent: float
    profitability: int
    profit_target: ProfitTarget


class Rating(BaseModel):
    rate: float
    reviews_count: int


class RatingStar(BaseModel):
    rate: int
    reviews_count: int
    ratings: List[Rating]


class TimeInfo(BaseModel):
    max: int
    min: int


class PriorityCategory(BaseModel):
    name: str
    count: int
    percent_part: int


class AdsCard(BaseModel):
    id: int
    page: int
    pos: int
    category: str
    brand: str
    rating: float
    quantity: int
    time: int
    cpm: int


class MainData(BaseModel):
    priority_categories: List[PriorityCategory]
    time_info: TimeInfo
    cards: List[AdsCard]


class Size(BaseModel):
    length: int
    height: int
    width: int
    weight: int
    is_kgt: bool


class Commission(BaseModel):
    part: int
    amount: str


class CommissionResponse(BaseModel):
    fbo: Commission
    fbs: Commission


class Category(BaseModel):
    category_id: int
    fbo_part: int
    fbs_part: int


class WarehouseResponse(BaseModel):
    id: int
    name: str


class Warehouse(BaseModel):
    id: int
    name: str
    ratio: float
    reception_ratio: int = None


class Logistic(BaseModel):
    warehouse_id: int
    logistic_amount: float
    from_client: int
    storage_amount: float
    reception_amount: float


class StocksByWarehouses(BaseModel):
    warehouse_name: str
    percent: int
    qty: int


class StocksBySizes(BaseModel):
    size: str
    warehouse_name: str
    qty: int
