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
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')

router=APIRouter(
    prefix="/data",
     tags=['Data']
)



@router.get('/display/{symbol}', response_model=List[schemas.CreateStockData])
async def test_posts(symbol:str,db: AsyncSession = Depends(get_db)):
    try:
        # Execute the query to fetch stock data with the specified symbol
        result = await db.execute(
            select(models.StockData).where(models.StockData.symbol == symbol)
        )
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

@router.post('/populate/{symbol}', response_model=List[schemas.CreateStockData])
async def populate_stocks(symbol:str,db: AsyncSession = Depends(get_db)):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    symbol = symbol
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
        self.predicted_price = []  

    def next(self):
        # Add your logic for predicting prices
        if self.short_ma[0] > self.long_ma[0] or self.short_ma[0] < self.long_ma[0]:
            # Append current close price to predictions
            self.predicted_price.append(self.data.close[0])  # Now this works correctly



@router.post('/backtest', response_model=dict)
async def backtest_strategy(
    symbol: str = Body(..., description="Stock symbol to backtest"),
    short_period: int = Body(..., description="Short moving average period"),
    long_period: int = Body(..., description="Long moving average period"),
    initial_cash: float = Body(..., description="Initial investment amount"),
    db: AsyncSession = Depends(get_db)
):
    # Ensure the static directory exists
    if not os.path.exists("static"):
        os.makedirs("static")

    # Fetch stock data from the database
    stock_data = await db.execute(
        select(models.StockData).where(models.StockData.symbol == symbol)
    )
    sdata = stock_data.scalars().all()

    if not sdata:
        raise HTTPException(status_code=404, detail="No stock data found.")

    stock_data_dicts = [
        {
            "symbol": stock.symbol,
            "date": stock.date,
            "open_price": stock.open_price,
            "close_price": stock.close_price,
            "high_price": stock.high_price,
            "low_price": stock.low_price,
            "volume": stock.volume,
        }
        for stock in sdata
    ]

    df = pd.DataFrame(stock_data_dicts)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    cerebro = bt.Cerebro()
    data_feed = bt.feeds.PandasData(
        dataname=df,
        open='open_price',
        high='high_price',
        low='low_price',
        close='close_price',
        volume='volume',
    )
    cerebro.adddata(data_feed)
    cerebro.addstrategy(MovingAverageCrossStrategy, short_period=short_period, long_period=long_period)
    cerebro.broker.setcash(initial_cash)

    cerebro.run()
    plot_path = "../static/backtest_plot.png"

    strategy = cerebro.runstrats[0]
    predicted_price = strategy[0].predicted_price
    final_value = cerebro.broker.getvalue()
    total_return = final_value - initial_cash

    short_mavg = df['close_price'].rolling(window=short_period).mean()
    long_mavg = df['close_price'].rolling(window=long_period).mean()

    # Use the dates from your DataFrame for historical prices
    historical_close = df['close_price']  # Ensure you have the close prices

    # Define the date range for predictions
    predicted_dates = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), 
                                    periods=len(predicted_price), freq='B')  # Business days

    # Ensure historical close prices are plotted against their own dates
    plt.figure(figsize=(14, 7))

    # Plot historical close prices
    plt.plot(df.index, historical_close, label='Historical Close Prices', color='black', linewidth=1.5)

    # Plot short moving average, using the same index as historical data
    plt.plot(df.index, short_mavg, label='Short Moving Average', color='orange', linestyle='--')

    # Plot long moving average, using the same index as historical data
    plt.plot(df.index, long_mavg, label='Long Moving Average', color='green', linestyle='--')

    # Plot predicted prices against the new predicted_dates
    plt.plot(predicted_dates, predicted_price, label='Predicted Prices(Strategy usage)', color='blue', linestyle='dotted')

    # Indicate the final portfolio value
    final_value = cerebro.broker.getvalue()
    plt.axhline(y=final_value, color='red', linestyle='--', label='Final Portfolio Value')

    # Add titles and labels
    plt.title('Backtest Results with Strategy Performance')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()  

    # Save the plot
    try:
        plt.savefig(plot_path)
        print(f"Plot saved to {plot_path}")
    except Exception as e:
        print(f"Error saving plot: {e}")

    # Close the plot to free up memory
    plt.close()
    
    # try:
    #     cerebro.plot(show=False, savefig=plot_path)
    #     print(f"Plot saved to {plot_path}")
    # except Exception as e:
    #     print(f"Error saving plot: {e}")

    return {
        "final_value": final_value,
        "total_return": total_return,
        "predicted_prices": predicted_price,
        "plot_url": plot_path,
        "performance_summary": "Add more detailed metrics if needed."
    }



logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

@router.get("/backtest")
async def read_backtest():
    return FileResponse("Views/backtest.html")

@router.get("/populate")
async def read_backtest():
    return FileResponse("Views/populate.html")

@router.get("/predict")
async def read_backtest():
    return FileResponse("Views/prediction.html")


@router.get("/summary")
async def read_backtest():
    return FileResponse("Views/summary.html")

@router.post('/predict', response_model=dict)
async def predict_stock_prices(symbol: str = Body(...),db: AsyncSession = Depends(get_db)):
    try:
        # Check database session
        if db is None:
            raise HTTPException(status_code=500, detail="Database session is None.")

        # Fetch historical data for the stock symbol
        result = await db.execute(select(models.StockData).filter(models.StockData.symbol == symbol))
        historical_data = result.scalars().all()

        if not historical_data:
            raise HTTPException(status_code=404, detail="No historical data found for the specified symbol.")

        # Convert historical data to DataFrame
        data_dicts = [{"date": stock.date, "close_price": stock.close_price} for stock in historical_data]
        df = pd.DataFrame(data_dicts)

        # Filter the last 30 days of data
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').tail(30)

        # Prepare data for Linear Regression
        df['days'] = (df['date'] - df['date'].min()).dt.days
        X = df[['days']]
        y = df['close_price']

        # Fit a linear regression model
        model = LinearRegression()
        model.fit(X, y)

        # Predict the prices for the same 30 days
        predicted_prices = model.predict(X)

        # Prepare predictions for insertion
        prediction_entries = []
        for i, (actual_price, predicted_price, prediction_date) in enumerate(zip(y, predicted_prices, df['date'])):
            prediction_entry = models.PredictedStockData(
                symbol="IBM",
                date=prediction_date,
                actual_price=actual_price,
                predicted_price=predicted_price
            )
            prediction_entries.append(prediction_entry)

        # Add all prediction entries to the session
        db.add_all(prediction_entries)

        # Commit the transaction
        await db.commit()
        
        # Generate Plot
        plt.figure(figsize=(12, 6))
        plt.plot(df['date'], y, label='Actual Prices', marker='o', color='blue')
        plt.plot(df['date'], predicted_prices, label='Predicted Prices', marker='x', color='orange')
        plt.title('Actual vs Predicted Stock Prices')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid()

        plot_path = "static/prediction_plot.png"  # Save to static folder in the root of the project
        if not os.path.exists("static"):
            os.makedirs("static")

        # Save the plot
        plt.savefig(plot_path)
        plt.close()  # Close the plot to free up memory

        response_data = {
            "actual_prices": y.tolist(),  # Convert pandas Series to list
            "predicted_prices": predicted_prices.tolist(),
            "dates": df['date'].dt.strftime('%Y-%m-%d').tolist(),  # Format dates
            "plot_url": plot_path  # Include the plot URL in the response
        }

        return response_data

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred during prediction: {str(e)}")


@router.get("/report/{format}")
async def get_report(format: str):
    if format == "pdf":
        pdf_path = "path/to/report.pdf"
        return FileResponse(pdf_path, media_type="application/pdf", filename="report.pdf")
    elif format == "json":
        metrics = calculate_metrics(data)
        return JSONResponse(content=metrics)
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")