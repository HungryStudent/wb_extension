from typing import List

from pydantic import BaseModel


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
    logistic_base: float
    logistic: float
    from_client: float
    storage_base: float
    storage: float
    reception: float


class Logistic(BaseModel):
    warehouse_id: int
    logistic_amount: float
    from_client: int
    storage_amount: float
    reception: int
