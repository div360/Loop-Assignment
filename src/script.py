import pandas as pd
import logging
from database import SessionLocal, init_db
from models import StoreActivity, BusinessHours, Timezone


def load_data():
    init_db() 
    db = SessionLocal()

    def load_csv(path, model, chunk_size=1000):
        try:
            df = pd.read_csv(path, dtype={'store_id': 'Int64'})  # Enforce Int64 for store_id
            data = df.to_dict(orient='records')

            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]
                db.execute(model.__table__.insert(), chunk)
                db.commit()

            print(f"Data from {path} loaded successfully.")
        except Exception as e:
            db.rollback()
            logging.error(f"Failed to load data from {path}: {e}") 


    load_csv("D:\\Loop Assignment\\store_status.csv", StoreActivity)
    load_csv("D:\\Loop Assignment\\menu_hours.csv", BusinessHours)
    load_csv("D:\\Loop Assignment\\business_timezones.csv", Timezone)

    db.close()
    
load_data()
