import pandas as pd
from sqlalchemy import create_engine

# Free MySQL DB URL
DB_URL = "mysql+mysqlconnector://sql12788463:vwckZ4Bt7u@sql12.freesqldatabase.com:3306/sql12788463"

# Load CSV
df = pd.read_csv("data/WalmartSalesData.csv")

# Format date and time
df["Date"] = pd.to_datetime(df["Date"])
df["Time"] = pd.to_datetime(df["Time"]).dt.time

# Upload to MySQL
engine = create_engine(DB_URL)
df.to_sql("sales", con=engine, if_exists="replace", index=False)

print("✅ Data uploaded successfully.")
