import os
from sqlite3 import IntegrityError
from typing import List
from fastapi.responses import FileResponse
from database import get_db
from fastapi import APIRouter, Body, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
import logging
import schemas
from sklearn.linear_model import LinearRegression
import models
from fastapi import APIRouter
import requests
from datetime import datetime, timedelta
import backtrader as bt
import pandas as pd
import numpy as np

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
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
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
        self.predicted_price = []  # Initialize predicted_prices as an instance variable

    def next(self):
        # Add your logic for predicting prices
        if self.short_ma[0] > self.long_ma[0] or self.short_ma[0] < self.long_ma[0]:
            # Append current close price to predictions
            self.predicted_prices.append(self.data.close[0])  # Now this works correctly



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

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


@router.post('/predict', response_model=List[schemas.PredictedStockData])
async def predict_stock_prices(
    db: AsyncSession = Depends(get_db)
):
    try:
        # Log the session to ensure it's not None
        if db is None:
            raise HTTPException(status_code=500, detail="Database session is None.")

        # Fetch historical data for the stock symbol
        result = await db.execute(select(models.StockData).filter(models.StockData.symbol == "IBM"))
        historical_data = result.scalars().all()

        print("==========DATA FOUND============")
        if not historical_data:
            raise HTTPException(status_code=404, detail="No historical data found for the specified symbol.")

        # Convert historical data to DataFrame
        data_dicts = [
            {
                "date": stock.date,
                "close_price": stock.close_price,
            }
            for stock in historical_data
        ]
        df = pd.DataFrame(data_dicts)

        # Prepare data for Linear Regression
        df['date'] = pd.to_datetime(df['date'])
        df['days'] = (df['date'] - df['date'].min()).dt.days  # Convert dates to numerical values

        # Fit a linear regression model
        X = df[['days']]  # Features (days)
        y = df['close_price']  # Target variable (close price)
        
        model = LinearRegression()
        model.fit(X, y)

        print("=========Model Fitted===========")
        # Predict the next 30 days
        last_day = df['days'].max()
        future_days = np.array(range(last_day + 1, last_day + 31)).reshape(-1, 1)
        predicted_prices = model.predict(future_days)
        
        print("=========Predictio Start===========")
        # Prepare predictions for insertion
        prediction_entries = []
        last_date = df['date'].max()
        for i, predicted_price in enumerate(predicted_prices):
            prediction_date = last_date + timedelta(days=i + 1)
            prediction_entry = models.PredictedStockData(
                symbol="IBM",
                date=prediction_date,
                predicted_price=predicted_price
            )
            prediction_entries.append(prediction_entry)
            print("Prediction ", prediction_entry.predicted_price,prediction_entry.date)  # Print entries for debugging

        
        print("=========Starting Push to db===========")
        await db.add_all(prediction_entries)  # Add entries to the session

        print("=========Commiting to DB===========")
        await db.commit()  # Commit the transaction

        # Return predictions
        return [{"date": entry.date, "predicted_price": entry.predicted_price} for entry in prediction_entries]

    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred during prediction: {str(e)}")

