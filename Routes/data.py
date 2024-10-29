from sqlite3 import IntegrityError
from typing import List
from fastapi.responses import FileResponse
from database import get_db
from fastapi import APIRouter, Body, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from starlette import status
import schemas
import models
from fastapi import APIRouter
import requests
from datetime import datetime, timedelta
import backtrader as bt
import pandas as pd

router=APIRouter(
    prefix="/data",
     tags=['Data']
)


@router.get('/', response_model=List[schemas.CreateStockData])
async def test_posts(db: AsyncSession = Depends(get_db)):
    try:
        # Execute the query to fetch all stock data
        result = await db.execute(select(models.StockData))
        sdata = result.scalars().all()

        if not sdata:
            # If no data is found, return an empty list with a 200 status code
            return []

        print(sdata)  # Debug print, remove in production if not needed
        return sdata

    except SQLAlchemyError as e:
        # Log the specific error and raise a 500 Internal Server Error with a message
        print(f"Database error occurred: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch data from the database due to an internal error.")

    except Exception as e:
        # Catch any unexpected errors
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request.")

@router.post('/populate', response_model=List[schemas.CreateStockData])
async def populate_stocks(db: AsyncSession = Depends(get_db)):
    api_key = "70K7U0ICKG3Q15KB"
    symbol = "IBM"
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}&outputsize=full'

    try:
        # Fetch the data    
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        # Extract the daily time series data
        daily_data = data.get("Time Series (Daily)", {})

        # Calculate the date two years ago from today
        two_years_ago = datetime.now() - timedelta(days=2 * 365)

        # Filter data to get only the entries from the past two years
        filtered_data = {
            date: values
            for date, values in daily_data.items()
            if datetime.strptime(date, "%Y-%m-%d") >= two_years_ago
        }

        # Prepare data for insertion
        stock_entries = []
        for date, values in filtered_data.items():
            stock_entry = models.StockData(
                date=datetime.strptime(date, "%Y-%m-%d").date(),
                symbol=symbol,
                open_price=float(values["1. open"]),
                high_price=float(values["2. high"]),
                low_price=float(values["3. low"]),
                close_price=float(values["4. close"]),
                volume=float(values["5. volume"]),
            )
            stock_entries.append(stock_entry)

        # Insert data into the database
        async with db.begin():
            db.add_all(stock_entries)

        return stock_entries  # You can modify this return as needed

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from Alpha Vantage: {e}")
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Data integrity error: possible duplicate entries.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    
    
    
class MovingAverageCrossStrategy(bt.Strategy):
    params = (('short_period', 50), ('long_period', 200))

    def __init__(self):
        self.short_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.short_period)
        self.long_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.long_period)
        self.order = None

    def next(self):
        if self.order:
            return

        print(f"Close: {self.data.close[0]}, Short MA: {self.short_ma[0]}, Long MA: {self.long_ma[0]}")  # Debugging line

        if self.short_ma[0] > self.long_ma[0]:
            if not self.position:
                self.order = self.buy()
        elif self.short_ma[0] < self.long_ma[0]:
            if self.position:
                self.order = self.sell()


@router.post('/backtest', response_model=dict)
async def backtest_strategy(
    short_period: int = Body(..., description="Short moving average period"),
    long_period: int = Body(..., description="Long moving average period"),
    initial_cash: float = Body(..., description="Initial investment amount"),
    db: AsyncSession = Depends(get_db)
):
    # Fetch stock data from the database
    result = await db.execute(select(models.StockData))
    sdata = result.scalars().all()
    
    # Convert the stock data to a DataFrame for Backtrader
    if not sdata:
        raise HTTPException(status_code=404, detail="No stock data found.")

    stock_data_dicts = [
        {
            "symbol": stock.symbol,
            "date": stock.date,  # Ensure date is a datetime object
            "open_price": stock.open_price,
            "close_price": stock.close_price,
            "high_price": stock.high_price,
            "low_price": stock.low_price,
            "volume": stock.volume,
        }
        for stock in sdata
    ]

    # Create a DataFrame from the list of dictionaries
    df = pd.DataFrame(stock_data_dicts)

    # Check for the 'date' column
    if 'date' not in df.columns:
        raise KeyError("'date' column not found in DataFrame")

    # Convert 'date' to datetime if it's not already
    df['date'] = pd.to_datetime(df['date'])
    df['open_price'] = df['open_price'].astype(float)
    df['high_price'] = df['high_price'].astype(float)
    df['low_price'] = df['low_price'].astype(float)
    df['close_price'] = df['close_price'].astype(float)
    df['volume'] = df['volume'].astype(float)
    # Set 'date' as the index
    df.set_index('date', inplace=True)

    # Check DataFrame structure after modifications
    print(df.head())  # Print first few rows
    # print(df.columns)  # Print column names
    print(df.isnull().sum())  # Check for NaN values in the DataFrame
    print("=========================")

    # Set up Backtrader
    cerebro = bt.Cerebro()
    data_feed = bt.feeds.PandasData(
    dataname=df,
    open='open_price',  # Name of the column for open prices
    high='high_price',  # Name of the column for high prices
    low='low_price',    # Name of the column for low prices
    close='close_price', # Name of the column for close prices
    volume='volume',     # Name of the column for volume
)
    cerebro.adddata(data_feed)

    # Add the strategy with the specified parameters
    cerebro.addstrategy(MovingAverageCrossStrategy, short_period=short_period, long_period=long_period)
    cerebro.broker.setcash(initial_cash)  # Set initial cash

    # Run the backtest
    cerebro.run()

    # Get final portfolio value and calculate returns
    final_value = cerebro.broker.getvalue()
    total_return = final_value - initial_cash  # Assuming initial investment is provided
    
    plot_path = "static/backtest_plot.png"  # Ensure this directory exists
    cerebro.plot(savefig=plot_path)  # Save the plot to a file

    return {
        "final_value": final_value,
        "total_return": total_return,
        "performance_summary": "Add more detailed metrics if needed."
    }

def plot_results(cerebro):
    # Plot the results
    cerebro.plot(style='candlestick')
    
    
@router.get("/backtest")
async def read_backtest():
    return FileResponse("static/backtest.html")