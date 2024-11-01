from database import Base
from sqlalchemy import Column, Float, ForeignKey, Integer, String, Boolean, TIMESTAMP, text,Numeric,Date


class StockData(Base):
    __tablename__="stock_data"
    id=Column(Integer,primary_key=True,nullable=False)
    symbol=Column(String,index=True)
    date = Column(Date, index=True)
    open_price = Column(Numeric(10, 2))
    close_price = Column(Numeric(10, 2))
    high_price = Column(Numeric(10, 2))
    low_price = Column(Numeric(10, 2))
    volume = Column(Integer)
    
    
class PredictedStockData(Base):
    __tablename__ = 'predicted_stock_data'
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    predicted_price = Column(Float, nullable=False)
    actual_price=Column(Float,nullable=False)