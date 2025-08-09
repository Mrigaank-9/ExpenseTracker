from fastapi import FastAPI
import pandas as pd

from .Expenses.expenses import router as router_expense

app = FastAPI()

'''
{
  "expense_date": "2025-08-09",
  "category": "Food",
  "amount": 250.75,
  "description": "Dinner at Italian restaurant",
  "payment_method": "Credit Card",
  "currency": "INR",
  "created_at": "2025-08-09"
}

'''

app.include_router(router_expense)