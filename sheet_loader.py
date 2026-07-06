from typing import cast

import pandas as pd
import streamlit as st

SHEET_URL = "https://docs.google.com/spreadsheets/d/1c1RlG6tPxUyw0xLsx67Pq6bT0ctLhniKBTuUyw6OkwU/export?format=csv"

@st.cache_data(ttl=60)
def load_sheet() -> pd.DataFrame:

    df = cast(pd.DataFrame, pd.read_csv(SHEET_URL))

    df = cast(pd.DataFrame, df[["Date", "Deal Price", "LINK"]])

    df = cast(pd.DataFrame, df[pd.notna(df["LINK"])])

    return df.reset_index(drop=True)