import pandas as pd 

def add_datetime_column(df):
    """
    Thêm cột DATETIME vào dataframe dựa trên PRD_ID và CYCLE.
    """
    df = df.copy()
    def parse_datetime(row):
        val = str(row["PRD_ID"])
        if len(val) == 8:
            try:
                return pd.to_datetime(val, format="%Y%m%d")
            except Exception:
                return pd.NaT
        return pd.NaT
    df["DATETIME"] = df.apply(parse_datetime, axis=1)
    return df

def add_time_features(df):
    """
    Thêm các cột YEAR, MONTH, QUARTER, DAY dựa trên cột DATETIME.
    """
    df = df.copy()
    df["YEAR"] = df["DATETIME"].dt.year
    df["MONTH"] = df["DATETIME"].dt.month
    df["QUARTER"] = df["DATETIME"].dt.quarter
    df["DAY"] = df["DATETIME"].dt.day
    return df