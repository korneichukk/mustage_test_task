from fastapi import FastAPI

from src.expenses.router import router as expenses_router

app = FastAPI()

app.include_router(expenses_router)
