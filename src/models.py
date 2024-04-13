from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class StoreActivity(Base):
    __tablename__ = "store_activity"
    id = Column(Integer, primary_key=True)  # Add if you want auto-incrementing IDs
    store_id = Column(BigInteger)
    timestamp_utc = Column(DateTime)
    status = Column(String)

class BusinessHours(Base):
    __tablename__ = "business_hours"
    id = Column(Integer, primary_key=True)
    store_id = Column(BigInteger)
    day = Column(Integer)
    start_time_local = Column(String) 
    end_time_local = Column(String) 

class Timezone(Base):
    __tablename__ = "timezones"
    id = Column(Integer, primary_key=True)
    store_id = Column(BigInteger)
    timezone_str = Column(String)
    
class StoreReport(Base):
    __tablename__ = 'store_reports'

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer)
    store_id = Column(Integer)
    uptime_last_hour = Column(Float)
    uptime_last_day = Column(Float)
    uptime_last_week = Column(Float)
    downtime_last_hour = Column(Float)
    downtime_last_day = Column(Float)
    downtime_last_week = Column(Float)
