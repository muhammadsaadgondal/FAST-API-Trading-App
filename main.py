
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
import models
from database import engine, get_db
import Routes.data as sdata
import asyncpg
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
# Create the database tables

load_dotenv()

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(sdata.router)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your actual frontend origin if needed
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


async def create_database(db_name: str):
    # Connect to the 'postgres' database or another existing database
    conn = await asyncpg.connect('postgresql://app_user:saad123@localhost/postgres')
    try:
        await conn.execute(f"CREATE DATABASE {db_name};")
        print(f"Database {db_name} created successfully.")
    except asyncpg.exceptions.DuplicateDatabaseError:
        print(f"Database {db_name} already exists shit.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await conn.close()
        
# Initialize the database tables
@app.on_event("startup")
async def startup_event():
    # await create_database("stock_db")
    await init_models()

@app.get("/")
async def root():
   return {"Message":"Working ha vro"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello bhai {name}"}
