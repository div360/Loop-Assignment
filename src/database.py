from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import DATABASE_URI
from src.models import Base 
from src.models import Timezone, StoreActivity, BusinessHours, StoreReport
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy.sql import select, column
from typing import List
import pytz
from src.utils import convert_to_local_time
from datetime import date
from typing import Optional, Tuple, Dict

engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    
def get_timezone(store_id: int, db: Session) -> pytz.timezone:
    timezone_str = db.query(Timezone.timezone_str).filter(Timezone.store_id == store_id).scalar()
    
    if timezone_str:
        return timezone_str
    else:
        return 'America/Chicago'

def get_store_activities(store_id: int, current_time: datetime, db: Session) -> List[StoreActivity]:
    last_week_start = current_time - timedelta(days=7)
    return db.query(StoreActivity) \
                   .filter(StoreActivity.store_id == store_id) \
                   .filter(StoreActivity.timestamp_utc >= last_week_start) \
                   .order_by(StoreActivity.timestamp_utc) \
                   .all()
                   

def generate_activity_query(store_id, start_time):
    query = select(column('timestamp_utc'), column('status')) \
              .filter(StoreActivity.store_id == store_id) \
              .filter(StoreActivity.timestamp_utc >= start_time) \
              .order_by(StoreActivity.timestamp_utc)
    return query

def generate_just_before_start_time_query(store_id, start_time):
    subquery = select(column('timestamp_utc'),  column('status')) \
                 .filter(StoreActivity.store_id == store_id) \
                 .filter(StoreActivity.timestamp_utc < start_time) \
                 .order_by(StoreActivity.timestamp_utc.desc()) \
                 .limit(1)
    return subquery

def get_business_hours_for_date(store_id: int, date: date, db:Session) -> Optional[Tuple[datetime, datetime]]:

    day_of_week = date.weekday()  # Get the day of the week (Monday = 0, Sunday = 6)
    timezone_str = get_timezone(store_id, db)  # You'll need this function as well
    timezone = pytz.timezone(timezone_str)

    business_hours = db.query(BusinessHours) \
                       .filter(BusinessHours.store_id == store_id) \
                       .filter(BusinessHours.day == day_of_week) \
                       .first()

    if business_hours:
        start_time_local_str = business_hours.start_time_local
        end_time_local_str = business_hours.end_time_local
        
        start_time_local = datetime.strptime(start_time_local_str, "%H:%M:%S").time()
        end_time_local = datetime.strptime(end_time_local_str, "%H:%M:%S").time()
        

        start_datetime_local = timezone.localize(datetime.combine(date, start_time_local))
        end_datetime_local = timezone.localize(datetime.combine(date, end_time_local))

        return start_datetime_local, end_datetime_local
    else:
        start_datetime = timezone.localize(datetime.combine(date, datetime.min.time())).astimezone(timezone)
        end_datetime= timezone.localize(datetime.combine(date, datetime.max.time())).astimezone(timezone)
        return start_datetime, end_datetime 

def is_within_business_hours(store_id: int, utc_dt: datetime, db: Session) -> bool:
    timezone_str = get_timezone(store_id, db)

    local_dt = convert_to_local_time(utc_dt, timezone_str)
    if local_dt is None:
        # Handle invalid timezone
        return False

    day_of_week = local_dt.weekday()
    business_hours = db.query(BusinessHours).filter(BusinessHours.store_id == store_id, BusinessHours.day == day_of_week).first()
    
    if not business_hours:
        # Assume 24/7 open
        return True

    start_time_str = business_hours.start_time_local
    end_time_str = business_hours.end_time_local
    
    start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
    end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()
    
    # Handle end time being after midnight
    if end_time < start_time:
        end_time += timedelta(days=1)

    return start_time <= local_dt.timetz() < end_time

def store_report_data(db: Session, results: Dict[str, Tuple[float, float]], report_id):
    for store_id, values in results.items():
        uptime_last_hour, uptime_last_day, uptime_last_week, downtime_last_hour, downtime_last_day, downtime_last_week = values

        # Create a new StoreReport object with the calculated values
        report = StoreReport(
            report_id=report_id,
            store_id=store_id,
            uptime_last_hour=uptime_last_hour,
            uptime_last_day=uptime_last_day,
            uptime_last_week=uptime_last_week,
            downtime_last_hour=downtime_last_hour,
            downtime_last_day=downtime_last_day,
            downtime_last_week=downtime_last_week
        )
        
        db.add(report)
    
    db.commit()

def get_store_ids(db):
    results = db.query(StoreActivity.store_id).distinct()  
    return [row.store_id for row in results]