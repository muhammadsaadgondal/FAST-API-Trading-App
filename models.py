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
    __tablename__ = "predicted_stock_data"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)  # Stock symbol
    predicted_price = Column(Float)  # Predicted stock price
    date = Column(Date)  # Date for which the prediction is made

    def __repr__(self):
        return f"<PredictedStockData(symbol={self.symbol}, predicted_price={self.predicted_price}, date={self.date})>"