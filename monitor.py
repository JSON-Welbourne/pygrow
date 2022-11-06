import aranet4 
import sqlite3
import datetime
import time
import config

def c2f(c):
   return round(9 * c / 5 + 32)

print(f"{' ' * 0}Connecting to DB `{config.SQL_PATH}`...")
try:
    db = sqlite3.connect(config.SQL_PATH)
except Exception as e:
    print(f"{' ' * 4}ERROR Connecting to DB: {e}")
else:
    print(f"{' ' * 4}Connected to DB!")
    db.execute(config.SQL_COMMAND_CREATE)
    print("Scanning Devices...")
    for device in config.ARANET_DEVICES.keys():
        try:
            print(f"{' ' * 4}Reading from {config.ARANET_DEVICES[device]}")
            history = aranet4.client.get_all_records(
                device, 
                entry_filter=config.ARANET_ENTRY_FILTER
            )
        except Exception as e:
            print(f"{' ' * 8}ERROR Reading multiple records from {device}: {e}")
        else:
            print(f"{' ' * 8}Processing Rows...")
            for row in history.value:
                db.execute(
                    config.SQL_COMMAND_INSERT_MANY,
                    [
                        device,
                        row.date - config.ARANET_TZ_OFFSET, 
                        datetime.datetime.now(),
                        row.co2, 
                        row.temperature, 
                        row.humidity, 
                        row.pressure
                    ]
                )
            print(f"{' ' * 8}Inserting {len(history.value)} Rows: {device}")
            db.commit()
    row = {}
    newRow = {}
    when = {}
    dTemperature = 0
    dPressure = 0
    dHumidity = 0
    dCO2 = 0
    while True:
        worked = False
        for device in [device for device in config.ARANET_DEVICES.keys() if device not in when.keys() or when[device] < datetime.datetime.now()]:
            try:
                worked = True
                print(f"{' ' * 4}Reading from {config.ARANET_DEVICES[device]}")
                newRow[device] = aranet4.client.get_current_readings(device)
                when[device] = (datetime.datetime.now() + datetime.timedelta(seconds=(newRow[device].interval - newRow[device].ago)))
            except Exception as e:
                print(f"{' ' * 8}ERROR Reading single record from {device}: {e}")
            else:
                maxLen = max([
                    len(str(newRow[device].pressure)),
                    len(str(c2f(newRow[device].temperature))),
                    len(str(newRow[device].humidity)),
                    len(str(newRow[device].co2)),
                ]) + 3
                dHumidityNew = newRow[device].humidity - row[device].humidity  if device in row.keys() else 0
                dTemperatureNew = c2f(newRow[device].temperature) - c2f(row[device].temperature) if device in row.keys() else 0
                dPressureNew = round(newRow[device].pressure - row[device].pressure if device in row.keys() else 0,1)
                dCO2New = newRow[device].co2 - row[device].co2 if device in row.keys() else 0
                maxLen2 = max([
                    len(str(dHumidityNew)),
                    len(str(dTemperatureNew)),
                    len(str(dPressureNew)),
                    len(str(dCO2New)),
                ]) + 3
                print(f"{' ' * 8}Inserting 1 Row: {config.ARANET_DEVICES[device]}")
                print(f"{' ' * 12}Name:         {newRow[device].name}")
                print(f"{' ' * 12}Version:      {newRow[device].version}")
                print(f"{' ' * 12}Temperature:  {c2f(newRow[device].temperature)}{' ' * (maxLen - len(str(c2f(newRow[device].temperature))))}{'+' if dTemperatureNew >= 0 else ''}{dTemperatureNew}/m{' ' * (maxLen2 - len(str(dTemperatureNew)))}{dTemperatureNew - dTemperature}/m2")
                print(f"{' ' * 12}Humidity:     {newRow[device].humidity}{' ' * (maxLen - len(str(newRow[device].humidity)))}{'+' if dHumidityNew >= 0 else ''}{dHumidityNew}/m{' ' * (maxLen2 - len(str(dHumidityNew)))}{dHumidityNew - dHumidity}/m2")
                print(f"{' ' * 12}Pressure:     {newRow[device].pressure}{' ' * (maxLen - len(str(newRow[device].pressure)))}{'+' if dPressureNew >= 0 else ''}{dPressureNew}/m{' ' * (maxLen2 - len(str(dPressureNew)))}{dPressureNew - dPressure}/m2")
                print(f"{' ' * 12}CO2:          {newRow[device].co2}{' ' * (maxLen - len(str(newRow[device].co2)))}{'+' if dCO2New >= 0 else ''}{dCO2New}/m {' ' * (maxLen2 - len(str(dCO2New)))}{dCO2New - dCO2}/m2")
                print(f"{' ' * 12}Battery:      {newRow[device].battery}")
                print(f"{' ' * 12}Status:       {newRow[device].status}")
                print(f"{' ' * 12}Interval:     {newRow[device].interval}")
                print(f"{' ' * 12}Ago:          {newRow[device].ago}")
                print(f"{' ' * 12}Stored:       {newRow[device].stored}")
                try:
                    row[device] = newRow[device]
                    dTemperature = dTemperatureNew
                    dHumidity = dHumidityNew
                    dPressure = dPressureNew
                    dCO2 = dCO2New
                    db.execute(
                        config.SQL_COMMAND_INSERT_ONE,
                        [
                            row[device].name,
                            row[device].version,
                            row[device].battery,
                            row[device].status,
                            row[device].interval,
                            row[device].ago,
                            row[device].stored,
                            device,
                            datetime.datetime.now(), 
                            datetime.datetime.now(),
                            row[device].co2, 
                            row[device].temperature, 
                            row[device].humidity, 
                            row[device].pressure
                        ]
                    )
                except Exception as e:
                    print(f"{' ' * 8}ERROR Inserting 1 Row: {device}")
                else:
                    print(f"{' ' * 8}Inserted 1 Row: {device}")
        if worked:
            print(f"{' ' * 4}Commiting to DB")
            db.commit()
        else:
            seconds = min([(when[device] - datetime.datetime.now()).seconds for device in config.ARANET_DEVICES]) + config.ARANET_POLLING_EXTRA_SECONDS
            print(f"{' ' * 4}Sleeping for {seconds} seconds")
            time.sleep(seconds)
finally:
    try:
        print("Closing DB")
        db.close()
    except Exception as e:
        print(f"{' ' * 4}ERROR Closing DB: {e}")
    else:
        print(f"{' ' * 4}Closed DB")
