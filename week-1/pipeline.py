import os
import sys
import time

import pandas as pd
import wget
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DATABASE: str = str(os.environ["DATABASE"])
DB_USER: str = str(os.environ["DB_USER"])
DB_PASSWORD: str = str(os.environ["DB_PASSWORD"])
DB_HOST: str = str(os.getenv("DB_HOST", "localhost"))
DB_PORT: int = int(os.getenv("DB_PORT", 5432))

CHUNK_SIZE: int = 100_000

while True:
    try:
        print("Connecting to database...")
        engine = create_engine(
            f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DATABASE}"
        )
        engine.connect()
    except Exception as e:
        print("Could not connect to database...Retrying:::\nError: {}".format(e))
        time.sleep(4)
    else:
        print("Database connected successfully!")
        break

# collect url to download .csv file from
# return file-error f file isn't csv
# load csv topostgres with pandas.io.sql

def fetch_data(file_url: str = sys.argv[1], dest: str = "./data"):
    """
    Fetch data from a given url if file doesn't on disk

    @arguments
    file_url: str
        URL to download the file from.

    @returns
    dest: str
        destination to save file to.
    """
    base_file = os.path.basename(file_url)
    ext = os.path.splitext(file_url)[-1]

    file_path = os.path.join(dest, base_file)
    print(f"filepath: {file_path}")
    if os.path.exists(file_path):
        print("File already exists as {}".format(file_path))
        return file_path
    else:
        assert len(ext) > 1, AttributeError("URL must be a file path to a downloadable file with an extension.")
        print(f"file url: {file_url}")
        # check is url is really a url, maybe with pydantic
        print(f"==>Downloading {ext} file<==")
        filename = wget.download(file_url)
        print(f"{filename} downloaded succesfully!")
        return filename

def check_unnamed(col_name: str) -> bool:
    """Check if a column is named `Unnamed`
    
    @argument
    col_name: str
        column name to check
        
    @returns
    is_unnamed: bool
    """
    if not ("unnamed" in col_name.strip().lower()):
        return True
    else:
        return False

filename = fetch_data()
running_dir = os.path.dirname(__file__)
table_name = sys.argv[2]

df = pd.read_csv(
    os.path.join(running_dir, filename),
    usecols=check_unnamed,
    nrows=CHUNK_SIZE
)

df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])
df.columns = [column.lower() for column in df.columns]
schema = pd.io.sql.get_schema(df, name=table_name, con=engine)
print(schema)

# df = pd.read_csv(
#     os.path.join(running_dir, filename),
#     usecols=check_unnamed,
#     iterator=True,
#     chunksize=CHUNK_SIZE
# )

# # create table with sql alchemy

# df.to_sql(
#     name=table_name, con=engine, if_exists="replace", index=False
# )
