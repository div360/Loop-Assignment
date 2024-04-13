from datetime import datetime, timedelta
from typing import Dict, Tuple
from sqlalchemy.orm import Session
import pytz
from src.database import get_timezone, get_store_activities, generate_activity_query, generate_just_before_start_time_query, get_business_hours_for_date, is_within_business_hours, store_report_data
from src.utils import convert_to_local_time, convert_to_utc
from sqlalchemy.orm import Session

def calculate_uptime_downtime(store_id: int, current_time: datetime, db: Session) -> Dict[str, Tuple[float, float]]:
    timezone_str = get_timezone(store_id, db)
    current_time_local = convert_to_local_time(current_time, timezone_str)
    print(current_time_local)
    current_day = current_time_local.date()
    activities = get_store_activities(store_id, current_time_local, db)
    last_week_start = current_time_local - timedelta(days=7)
    last_day_start = current_time_local - timedelta(days=1)
    last_hour_start = current_time_local - timedelta(hours=1)
    
    
    if not activities:
        return {  
            'last_hour': (0, 0),  
            'last_day': (0, 0),
            'last_week': (0, 0)
        }
        
    results = {
        'last_hour': [0, 0], 
        'last_day': [0, 0],
        'last_week': [0, 0]
    }
    
    for interval, start_time in [('last_hour', last_hour_start), 
                                 ('last_day', last_day_start), 
                                 ('last_week', last_week_start)]:
        print(interval, start_time)
        start_time_utc = convert_to_utc(start_time, timezone_str)
        query = generate_activity_query(store_id, start_time_utc) 
        subquery = generate_just_before_start_time_query(store_id, start_time_utc)

        result_set = db.execute(query).fetchall()
        last_timestamp = db.execute(subquery).fetchone()
        if last_timestamp is not None:
            timestamp_utc_last = last_timestamp[0]
            status_last = last_timestamp[1]
        
        print(result_set)
        # result_set=activities.filter(StoreActivity.timestamp_utc >= start_time)
        
        current_status = None
        prev_timestamp = None
        last_weekday_observation=  None
        prev_date = None
        for row in result_set:
            timestamp_utc , status = row
            # print(timestamp_utc, status)
            timestamp_utc_datetime = datetime.strptime(timestamp_utc, "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=pytz.utc)
            timestamp_utc_datetime_local = convert_to_local_time(timestamp_utc_datetime, timezone_str)
            timestamp_utc_datetime_last_local = datetime.strptime(timestamp_utc_last, "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=pytz.utc)
            timestamp_utc_last_local = convert_to_local_time(timestamp_utc_datetime_last_local, timezone_str)
            if is_within_business_hours(store_id, timestamp_utc_datetime, db):
                current_date= timestamp_utc_datetime_local.date()
                if(current_date != prev_date and prev_timestamp is not None):  # Day has changed!
                    
                    business_start, business_end = get_business_hours_for_date(store_id, prev_date, db)
                    duration = business_end - prev_timestamp
                    if current_status == 'active':
                        results[interval][0] += duration.total_seconds() / 60
                    else:
                        results[interval][1] += duration.total_seconds() / 60
                        print("day change wala")
                        print(results[interval])
                    
                    prev_timestamp = None
                    
                business_start, business_end = get_business_hours_for_date(store_id, current_date, db)
                
                if prev_timestamp is None:
                    if(business_start > start_time):
                        prev_timestamp = business_start
                        current_status = status
                    else:
                        prev_timestamp = start_time
                        if(last_timestamp is not None and timestamp_utc_last_local.date() == current_date):
                            current_status = status_last
                        else:
                            current_status = status
                    # prev_timestamp = business_start
                    duration = timestamp_utc_datetime_local - prev_timestamp
                    print(results[interval])
                    print(timestamp_utc_datetime_local)
                    print(prev_timestamp)
                    
                    if current_status == 'active':
                        results[interval][0] +=  duration.total_seconds() / 60  
                    else:
                        results[interval][1] += duration.total_seconds() / 60  
                        print("none wala")
                        
                        print(results[interval])
                        
                elif prev_timestamp is not None and current_date == prev_date:
                    duration = timestamp_utc_datetime_local - prev_timestamp
                    if current_status == 'active':
                        results[interval][0] +=  duration.total_seconds() / 60 
                    else:
                        results[interval][1] +=  duration.total_seconds() / 60 
                        print("not none wala")
                        
                        print(results[interval])
                        
                if(row==result_set[-1]):
                    if(current_time_local < business_end):
                        duration = current_time_local - timestamp_utc_datetime_local
                    else:
                        duration = business_end - timestamp_utc_datetime_local
                    # print(current_time_utc,timestamp_utc_datetime,duration)
                    if status=='active':
                        results[interval][0] += duration.total_seconds() / 60
                    else:
                        print("last wala")
                        results[interval][1] += duration.total_seconds() / 60
                        print(results[interval])
                    
                prev_timestamp = timestamp_utc_datetime_local
                current_status = status
                prev_date = current_date
                            
        if interval != 'last_hour':
            results[interval] = (results[interval][0] / 60, results[interval][1] / 60)
            print(results[interval])
            
    for interval in results:
        results[interval] = (round(results[interval][0], 2), round(results[interval][1], 2))
    print(results)
    return results

def formatted_results(store_id, report_id, current_time, db):
    results = calculate_uptime_downtime(store_id, current_time, db)
    results_final = {
        'store_id': store_id,
        'current_time': current_time,
        'uptime_last_hour': results['last_hour'][0],
        'downtime_last_hour': results['last_hour'][1],
        'uptime_last_day': results['last_day'][0],
        'downtime_last_day': results['last_day'][1],
        'uptime_last_week': results['last_week'][0],
        'downtime_last_week': results['last_week'][1]
    }
    store_report_data(db, results_final, report_id)
    return results_final