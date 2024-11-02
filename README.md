# FastAPI Stock Prediction API

This project is a stock prediction API built with FastAPI. It integrates financial data from Alpha Vantage, uses a pre-trained Hugging Face model for stock price predictions, and includes backtesting and performance reporting features.

## Features
- Fetches and stores historical stock data.
- Predicts future stock prices using a regression model.
- Backtesting with customizable strategies.
- Generates performance reports as PDFs and JSON responses.
- Dockerized deployment with AWS RDS for PostgreSQL.
- CI/CD pipeline for automated deployment.

## Table of Contents
- [Requirements](#requirements)
- [Setup](#setup)
  - [Environment Variables](#environment-variables)
  - [Database Setup](#database-setup)
  - [Docker Setup](#docker-setup)
- [Running Locally](#running-locally)
- [Database Migrations](#database-migrations)
- [Testing](#testing)
- [Deployment](#deployment)

---

## Requirements
- Python 3.10+
- Docker
- PostgreSQL (local or AWS RDS)
- Alpha Vantage API Key

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/yourproject.git
cd yourproject

```
### 2. Environment Variables
Create a .env file in the project root with the following values:

env

```
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
DATABASE_URL=postgresql://username:password@localhost:5432/your_db_name
SECRET_KEY=your_secret_key
```

### 3. Setup Database
If using Docker, PostgreSQL will be set up automatically.
If using AWS RDS, replace DATABASE_URL with your RDS endpoint in .env.


### 4. Docker Setup
Make sure you have Docker installed. Run the following command to build and start the containers:

```bash
docker-compose up --build
```

### 5. Running Locally
Activate your virtual environment (if not using Docker):

```bash
source venv/bin/activate
```
Install dependencies:

```bash
pip install -r requirements.txt
```
Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

### 6. Database Migrations
Initialize Alembic (if not already done):

```bash
alembic init alembic
```
Generate a New Migration:

```bash
alembic revision --autogenerate -m "your message here"
```
Apply Migrations:

```bash
alembic upgrade head
```
Downgrade (optional):
```bash
alembic downgrade -1
```

### 6. Deployment
## 1. CI/CD with GitHub Actions
Set up a GitHub Actions workflow for CI/CD.
Use GitHub Secrets to securely store environment variables like ALPHA_VANTAGE_API_KEY, SECRET_KEY, and DATABASE_URL.
## 2. Deploying on AWS
Dockerize your Application: Ensure your application is fully Dockerized.

Push to AWS ECR (Elastic Container Registry):

Build and tag the Docker image.
Push the image to ECR.
Use Elastic Beanstalk or ECS to deploy your containerized application:

Elastic Beanstalk: Create a new environment with Docker support.
ECS: Use a Fargate task to run the container.
Database: Connect to AWS RDS for PostgreSQL as specified in .env.

Automate Deployments: Configure GitHub Actions to automatically deploy changes.
