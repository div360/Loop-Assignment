# Loop Assignment : Store Monitoring

## Problem Statement
Restaurant owners lack an efficient way to monitor store online/offline status and track the frequency of outages within business hours. This makes it difficult to identify operational issues, address problems promptly, and ensure a positive customer experience.

## Solution

#### Data handling
 - Ingestion: The system reads store status, business hours, and timezone information from provided CSV files.

 - Storage: A suitable database (e.g., SQLite or PostgreSQL) stores this data for efficient querying and updates.

#### Uptime/ Downtime Logic
- Described in detail below

#### API Design

- `/trigger_report`: Initiates on-demand report generation. It:
Processes the latest data from the database
Applies the uptime/downtime logic
Stores the generated report (or a task ID)
Returns a report_id to the user
- `/get_report`: Provides report status. It:
Accepts a report_id
Indicates "Running" if the report is in progress
Returns "Complete" with a downloadable CSV report upon completion

#### Technology

- Fast API
- Postgres Database

### File Structure

- Project Structure

- config.py: Contains configuration settings. This likely includes database connection details, API-specific settings, and potentially the path to your CSV data sources.
- database.py: Handles database interactions. Here you'd find functions for connecting to the database, executing queries (like retrieving activities, business hours, and timezones), and potentially storing the generated reports.
- main.py: The core of your FastAPI application. It sets up the API, defines endpoints (like /trigger_report and /get_report), and likely imports and uses functionality from other modules.
- models.py: Likely defines data models using a framework like SQLAlchemy or Pydantic. These models represent entities like Store, Activity, BusinessHours, and Report.
- script.py: A potential script for data loading or preprocessing. This might handle the initial loading of the CSV data into your database.
- service.py: Contains the core business logic for report generation. This is where you would find the functions that calculate uptime/downtime, handle time intervals, and implement your extrapolation logic.
- utils.py: Houses various helper functions for tasks like timezone conversions, date/time manipulation, and potentially CSV file handling.
test/test.py: Your unit tests! It's essential to have tests to verify your code's behavior, especially for a task with complex calculations like this.

### How to run the application
- After the assumptions point

### Logic and edge cases handled

#### 1. Initialization

 - Retrieve the store's timezone.
 - Get the current time and convert it to the store's local time.
 - Retrieve store activities (online/offline status changes) from the past 7 days.
 - Set up an empty results dictionary to store calculated uptime/downtime.

#### 2. Iterate Through Time Intervals

 - Consider three intervals: 'last_hour', 'last_day', 'last_week'.
 - For each interval:
   - Get all store activities since the start of that interval.
   - Initialize 'current_status', 'prev_timestamp', and 'prev_date' for tracking.

#### 3. Iterate Through Activities

- For each activity:
  - Get the timestamp and status.
  - Convert the timestamp to local time.
  - **Check Business Hours:** If the activity timestamp falls within the store's business hours for that day"
    - **Edge Case:** First Activity of the Day
      - Assume the store had the same status from the business start time until this first activity's timestamp.
    - **Regular Calculation**
      - Compare the current activity's status with the 'current_status' (status maintained from the previous activity).
      - Calculate the duration between 'prev_timestamp' and the current activity's timestamp.
      - Add the duration to the appropriate interval's uptime or downtime in the results dictionary.
    - **Edge Case:** Day Change
      - Calculate the duration between the previous activity's timestamp and the end of business hours on the previous day.
      - Add this duration to the appropriate interval's uptime or downtime in the results dictionary.
      - Reset 'prev_timestamp' to the start of business hours of the new day.
#### 4. Final Calculations

  - Last Activity: Calculate the duration from the last activity's timestamp to the current time or the end of business hours (whichever is earlier) and add it to the appropriate interval.
  - Convert Durations: Convert all the durations from minutes to hours (for 'last_day' and 'last_week' intervals).

#### 5. Format and Store Results

 - Create a final results dictionary with store ID, timestamps, and calculated uptime/downtime values.
 - Store this data in a report.

### Assumptions

Apart from the given assumptions i have assumed these things :

  - **Report generation:** After the `/trigger_report` api is called i create a report_id for each store_id and return a list of report_ids for which the report generation keeps happening at the backend. (Not a single report id generated that contained info of all the stores , i have modified the requirement here )

  - #### **Store Report Table:** 
     - I have created a store report table which contains the report id , store id and the details of the asked report generated.
     - Here is the schema of the table
        - id = Column(Integer, primary_key=True, index=True)
        - report_id = Column(Integer)
        - store_id = Column(Integer)
        - uptime_last_hour = Column(Float)
        - uptime_last_day = Column(Float)
        - uptime_last_week = Column(Float)
        - downtime_last_hour = Column(Float)
        - downtime_last_day = Column(Float)
        - downtime_last_week = Column(Float)

- **Data Quality:** The provided data is accurate and consistent. There are no errors in timestamps, statuses, or business hours.

- **Business Hours:** Business hours are well-defined. Edge cases like a store being open past midnight (e.g., 10 PM - 3 AM) are either not present or accommodated.
If business hours data is missing, the store is assumed to be open 24/7 for the purpose of uptime/downtime calculation.

- **Timezones:** All provided timestamps in the activity CSV are in UTC to ensure a consistent reference point.Local timezones are used solely for determining business hours and making calculations relative to those hours.

- #### **Extrapolation Logic:** 
  - A specific method of extrapolation is needed to fill in gaps between activity observations. For instance:
    - Simple: Assume the store maintains the last known status until a new activity changes things.

- #### **Report Intervals:** 
  - "Last hour", "last day", and "last week" refer to rolling intervals based on the current time, not fixed calendar periods.

- #### **Current Timestamp:** 
   - I have taken the current time as 2023-01-25 18:13:22.47922 because it was the latest value of time in the data

### How to run the application

- Prerequisites

   - Python (appropriate version)
FastAPI and its dependencies (like Uvicorn)
   - A database system PostgreSQL and its corresponding Python driver.
    - Optional: A virtual environment to isolate project dependencies.

- Setup

   - Clone the GitHub repository
   - If using a virtual environment, activate it.
   - Install dependencies: pip install -r requirements.txt
   - Configure your database connection details in config.py.
   - Potential initial setup: If data is not preloaded, you might need to run script.py or a similar mechanism to load the CSVs into your database.
   - Start the Application

   - From the project's src directory, run the command to start a Uvicorn development server: uvicorn main:app --reload
 
