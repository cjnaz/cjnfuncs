#!/usr/bin/env python3
"""Demo/test for periodic_log

Produce / compare to golden results:
    ./demo-periodic_log.py | diff demo-periodic_log-golden.txt -
        No differences expected
"""

#==========================================================
#
#  Chris Nelson, 2025
#
#==========================================================

__version__ = "3.1"


import time
from cjnfuncs.core import set_toolname, setuplogging, logging, periodic_log, cats

set_toolname('demo_periodic_log')
setuplogging()
logging.getLogger().setLevel(10)


def dotest (testnum, message, category, log_level=None, logger_name='', log_interval='0.2', logger_level=logging.DEBUG):
    logging.getLogger(logger_name).setLevel(logger_level)
    print ("\n=============================================")
    print (f"Test {testnum} - category <{category:4}> logger <{logger_name}> - {message}")
    periodic_log (message, category, logger_name, log_interval, log_level)


# Root logger '' tests
dotest(1, "Expect logged message, WARNING [PLog-Cat1]",     'Cat1', log_level=30, log_interval=0.2)
dotest(2, "Expect logged message,    INFO [PLog-2]",        2,      log_level=20, log_interval=0.2)
dotest(3, "Expect NOT LOGGED",                              'Cat1', log_level=30)
dotest(4, "Expect NOT LOGGED",                              2,      log_level=30)

# Override default level, Ignore log_interval
time.sleep(0.2)
dotest(5, "Expect logged message,   DEBUG [PLog-Cat1]",     'Cat1', log_level=10, log_interval=300)
dotest(6, "Expect logged message, WARNING [PLog-2]",        2,      log_level=30, log_interval=300)

# Default logging level established on first calls
time.sleep(0.2)
dotest(7, "Expect logged message, WARNING [PLog-Cat1]",     'Cat1')
dotest(8, "Expect logged message,    INFO [PLog-2]",        2)

# Logger level set higher than message log level
time.sleep(0.2)
dotest(9, "Expect NOT LOGGED",                              'Cat1', log_level=20, logger_level=30)


# Child/named logging tests
dotest(20, "Expect logged message,    INFO [PLog-abc]",     category='abc',  logger_name='xyz', log_level=logging.INFO)
dotest(21, "Expect logged message, WARNING [PLog-def]",     category='def',  logger_name='ghi', log_level=logging.WARNING)

# logger_name changes ignored.  Use default log_levels
time.sleep(0.2)
dotest(22, "Expect logged message,    INFO [PLog-abc]",     category='abc',  logger_name='mmm')
dotest(23, "Expect logged message, WARNING [PLog-def]",     category='def',  logger_name='ppp')


print ("\n\n=====================\nKnown categories")
print ("Category name   logger_name    default log_level")
for cat in cats:
    print (f"{cat:4}             {cats[cat].logger_name:4}          {cats[cat].log_level:4}")


