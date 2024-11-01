from pydantic import BaseModel
from datetime import date

class StockDataBase(BaseModel):
    symbol: str
    date: date
    open_price: float
    close_price: float
    high_price: float
    low_price: float
    volume: int

    class Config:
        orm_mode = True

class CreateStockData(StockDataBase):
    pass  # You can extend this class if you need to add more fields or methods

class StockDataResponse(StockDataBase):
    id: int  # Include the ID field for responses
    class Config:
        orm_mode = True
        

class PredictedStockData(BaseModel):
    date: date  # Assuming you will return a date
    symbol:str
    predicted_price: float
    actual_price:float
    class Config:
        orm_mode = True  # Enable ORM mode to work with SQLAlchemy models
        from_attributes = True


# Schema for responses to clients
class PredictedStockDataResponse(PredictedStockData):
    id: int
