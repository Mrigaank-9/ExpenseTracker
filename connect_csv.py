import pandas as pd

data_csv = pd.read_csv("expenses.csv")

def get_connection():
    return data_csv