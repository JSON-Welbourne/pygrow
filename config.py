import datetime

# Restart
COMMAND_RESTART = "python monitor.py"
TIME_SLEEP = 1

# Aranet
ARANET_DEVICES = {
    'EB623E67-579F-6BE9-A517-65151E38585A': 'Office',
    '2D33E01C-8C4D-6DFE-150B-41FB9133E77F': 'Grow Tent',
}
ARANET_TZ_OFFSET = datetime.timedelta(hours=4)
ARANET_POLLING_EXTRA_SECONDS = 2
ARANET_ENTRY_FILTER = {}

# SQL Commands
SQL_PATH = 'grow.sqlite3'
SQL_COMMAND_CREATE = """
CREATE TABLE IF NOT EXISTS readings (
    sensor TEXT,
    name TEXT,
    version TEXT,
    battery NUMBER,
    status NUMBER,
    interval NUMBER,
    ago NUMBER,
    stored NUMBER,
    time_recorded DATETIME, 
    time_collected DATETIME, 
    co2 NUMBER, 
    temperature NUMBER, 
    humidity NUMBER, 
    pressure NUMBER, 
    UNIQUE(
        sensor,
        time_recorded,
        co2,
        temperature,
        humidity,
        pressure
    )
);"""
SQL_COMMAND_INSERT_MANY = """
INSERT OR IGNORE INTO readings (
    sensor, 
    time_recorded, 
    time_collected, 
    co2, 
    temperature, 
    humidity, 
    pressure
) VALUES (
    ?,?,?,?,?,?,?
);"""
SQL_COMMAND_INSERT_ONE = """
INSERT OR IGNORE INTO readings (
    name,
    version,
    battery,
    status,
    interval,
    ago,
    stored,
    sensor, 
    time_recorded, 
    time_collected, 
    co2, 
    temperature, 
    humidity, 
    pressure
) VALUES (
    ?,?,?,?,?,?,?,?,?,?,?,?,?,?
);"""
