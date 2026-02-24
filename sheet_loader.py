import pandas as pd

SHEET_URL = "https://docs.google.com/spreadsheets/d/1c1RlG6tPxUyw0xLsx67Pq6bT0ctLhniKBTuUyw6OkwU/export?format=csv"

def load_sheet():
    df = pd.read_csv(SHEET_URL)
    df = df[['Date', 'Deal Price', 'LINK']]
    df = df.dropna(subset=['LINK'])
    return df