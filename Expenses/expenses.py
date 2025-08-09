from fastapi import APIRouter, Query
import pandas as pd
from pydantic import BaseModel, Field
from datetime import date, datetime
from ..connect_csv import get_connection
router = APIRouter(prefix="/expenses", tags=["expenses"])

df = get_connection()

class Expense(BaseModel):
    expense_date: date
    category : str 
    amount : float
    description: str 
    payment_method: str 
    currency : str   
    created_at : datetime = Field(default_factory=datetime.utcnow)  
    
@router.get("/")
def all_expenses():
    expenses = {}
    for idx, row in df.iterrows():
        expenses[idx] = {col: str(row[col]) for col in df.columns}
    return expenses

@router.post("/")
def add_expense(new_expense: Expense):
    global df  
    for field, value in new_expense.dict().items():
        if isinstance(value, str):
            setattr(new_expense, field, value.lower())

    new_expense.created_at = datetime.now()
    expense_dict = new_expense.dict()
    df = pd.concat([df, pd.DataFrame([expense_dict])], ignore_index=True)
    df.to_csv("expenses.csv", index=False)
    return {"message": "Expense added successfully"}
    

@router.get("/{id}")
def get_by_id(id : int):
    if id >= len(df):
        return {"message" : "Not found"}
    row = df.loc[id]
    return row


@router.put("/{id}")
def get_by_id(id : int, new_expenses : Expense):
    global df
    if id >= len(df):
        return {"message" : "Not found"}
    df = df.drop(id)
    add_expense(new_expenses)
    return new_expenses

@router.delete("/{id}")
def get_by_id(id : int, new_expenses : Expense):
    global df
    if id >= len(df):
        return {"message" : "Not found"}
    df = df.drop(id)
    df.to_csv("expenses.csv", index=False)
    return {"message" : "Deleted"}

@router.get("/categories/")
def show_all_categories():
    global df
    categories = df["category"].unique().tolist()
    print(type(categories))
    categories_dict = {}
    for ind, val in enumerate(categories):
        categories_dict[ind] = val
    return {"category": categories_dict}

@router.delete("/categories/{categories}")
def delete(categories : str):
    df.drop(df[df["category"] == categories].index, inplace=True)
    df.to_csv("expenses.csv", index=False)
    
@router.get("/categories/{categories}")
def delete(categories : str):
    categories = categories.lower()
    new_df = df[df["category"] == categories] 
    if len(new_df) == 0:
        return {"message" : "not found"}
    expenses = {}
    for idx, row in new_df.iterrows():
        expenses[idx] = {col: str(row[col]) for col in df.columns}
    return expenses


@router.get("/summary/daily")
def daily_summary():
    """Get total expenses for today."""
    today = date.today()
    today_df = df[df["expense_date"] == str(today)]
    total = today_df["amount"].sum()
    return {"date": str(today), "total": total}


@router.get("/summary/monthly")
def monthly_summary(year: int = Query(...), month: int = Query(...)):
    """Get total expenses for a given month and year."""
    monthly_df = df[
        (pd.to_datetime(df["expense_date"]).dt.year == year) &
        (pd.to_datetime(df["expense_date"]).dt.month == month)
    ]
    total = monthly_df["amount"].sum()
    return {"year": year, "month": month, "total": total}


@router.get("/summary/by-category")
def summary_by_category():
    """Get total spent grouped by category."""
    category_totals = df.groupby("category")["amount"].sum().to_dict()
    return {"by_category": category_totals}


@router.get("/summary/date-range")
def summary_date_range(start_date: date, end_date: date):
    """Get total expenses between two dates."""
    range_df = df[
        (pd.to_datetime(df["expense_date"]) >= pd.to_datetime(start_date)) &
        (pd.to_datetime(df["expense_date"]) <= pd.to_datetime(end_date))
    ]
    total = range_df["amount"].sum()
    return {
        "start_date": str(start_date),
        "end_date": str(end_date),
        "total": total
    }
