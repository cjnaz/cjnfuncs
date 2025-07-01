#!/usr/bin/env python3
import time
from cjnfuncs.core import set_toolname, setuplogging, periodic_log, set_logging_level, logging

set_toolname ('core_ex4')
setuplogging (ConsoleLogFormat='{asctime} {module:>6}.{funcName:6} {levelname:>8}:  {message}')
set_logging_level (logging.INFO)

periodic_log ("mycat1 messages are logged once every 1s at log_level WARNING", category='mycat1', log_interval='1s', log_level=30)
periodic_log ("mycat2 messages are logged once every 3s at log_level INFO", category='mycat2', log_interval='3s', log_level=logging.INFO)

for n in range(100):
    periodic_log (f"Loop iteration {n}", category='mycat1')
    periodic_log (f"Loop iteration {n}", category='mycat2')

    time.sleep (0.1)