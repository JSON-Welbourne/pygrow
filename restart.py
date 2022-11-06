import os, time
import config

while 1:
    os.system(config.COMMAND_RESTART)
    print("Restarting...")
    time.sleep(config.TIME_SLEEP) # 200ms to CTR+C twice
