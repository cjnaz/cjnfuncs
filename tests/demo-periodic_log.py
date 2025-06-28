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

__version__ = "1.0"


import time

from cjnfuncs.core import set_toolname, setuplogging, logging, periodic_log

set_toolname('demo_periodic_log')
setuplogging()
logging.getLogger().setLevel(10)


def dotest (testnum, message, category, log_interval='1s', log_level=30):
    print ("\n=============================================")
    print (f"Test {testnum} - category <{category:4}> - {message}")
    periodic_log (message, category, log_interval, log_level)

dotest(1, "Message_1 - WARNING Logged message",     'Cat1')
dotest(2, "Message_1 - INFO    Logged message",     2,      log_level=20)
dotest(3, "Message_2 - Not logged",                 'Cat1')
dotest(4, "Message_2 - Not logged",                 2)
time.sleep(1)
dotest(5, "Message_3 - INFO    Logged message",     'Cat1', log_level=20, log_interval=300)    # 2nd log_interval ignored
dotest(6, "Message_3 - DEBUG   Logged message",     2,      log_level=10)
time.sleep(1)
dotest(7, "Message_4 - WARNING Logged message",     'Cat1')
dotest(8, "Message_4 - INFO    Logged message",     2,      log_level=None)
