import pytest
from src.service import calculate_uptime_downtime
from src.models import StoreActivity, BusinessHours, Timezone, Base
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pytest_mock import mocker 
from unittest.mock import patch,MagicMock  
import pandas
import pytz

# @pytest.mark.parametrize("utc_time, timezone_str, expected_local_time", [
#     ("2023-01-22 12:09:39.388884", "America/New_York", "2023-01-22 07:09:39.388884"),
#     ("2023-01-24 09:06:42.605777", "Europe/London", "2023-01-24 09:06:42.605777"),
#     ("2023-01-24 09:07:26.441407", "Asia/Tokyo", "2023-01-24 18:07:26.441407")
# ])
 

# def test_convert_to_local_time(utc_time, timezone_str, expected_local_time):
#     # Convert string to datetime object
#     utc_time = datetime.strptime(utc_time, "%Y-%m-%d %H:%M:%S.%f")
#     expected_local_time = datetime.strptime(expected_local_time, "%Y-%m-%d %H:%M:%S.%f")

#     local_time = convert_to_local_time(utc_time, timezone_str)

#     # Assert the result
#     assert local_time.replace(tzinfo=None) == expected_local_time.replace(tzinfo=None)
@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    session.add_all([
        StoreActivity(store_id=1, timestamp_utc=datetime(2024, 4, 8, 14, 0, tzinfo=pytz.utc).astimezone(pytz.utc), status='active'),
        StoreActivity(store_id=1, timestamp_utc=datetime(2024, 4, 8, 20, 0, tzinfo=pytz.utc).astimezone(pytz.utc), status='inactive'),
        StoreActivity(store_id=1, timestamp_utc=datetime(2024, 4, 9, 15, 0, tzinfo=pytz.utc).astimezone(pytz.utc), status='inactive'),
        
        BusinessHours(store_id=1, day=0, start_time_local='09:00:00', end_time_local='17:00:00'),
        BusinessHours(store_id=1, day=1, start_time_local='09:00:00', end_time_local='12:00:00'),
        Timezone(store_id=1, timezone_str='America/New_York')
    ])
    
    session.commit()

    yield session

    session.close()

def test_calculate_uptime_downtime_on_day_change(db_session):
    current_time=datetime(2024, 4, 9, 13, 0, tzinfo=pytz.timezone('America/New_York')).astimezone(pytz.timezone('America/New_York'))# 12 PM
    print(current_time)
    results = calculate_uptime_downtime(1, current_time, db_session)
    
    assert results['last_hour'] == (0.0, 0.0)
    assert results['last_day'] == (2.07,4.0)
    assert results['last_week'] == (7.0,4.0)