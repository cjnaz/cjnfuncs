#!/usr/bin/env python3
"""Demo/test for periodic_log
"""
#==========================================================
#
#  Chris Nelson, 2025
#
#==========================================================

__version__ = "1.0"


import time

# cjnfuncs.core must be imported before mine, else circular import since mine imports mungePath
from cjnfuncs.core import set_toolname, setuplogging, logging, set_logging_level, restore_logging_level, get_logging_level_stack

set_toolname('demo_logging_level_set_restore')


def print_test_header(tnum, header):
    print ("\n======================================================================================================")
    print (f"***** Test number {tnum}: {header} *****")
    print ("======================================================================================================\n")

def test_logs ():
    logging.debug   ("")
    logging.info    ("")
    logging.warning ("")
    logging.error   ("")
    print (f"ll_history: {get_logging_level_stack()}")


print_test_header (1, "Initial level WARNING")
test_logs()

print_test_header (2, "set to DEBUG")
set_logging_level (logging.DEBUG)
test_logs()

print_test_header (3, "restored to WARNING")
restore_logging_level ()
test_logs()

print_test_header (4, "restored with no prior set")
restore_logging_level ()
test_logs()

print_test_header (5, "set to INFO")
set_logging_level (logging.INFO)
test_logs()

print_test_header (6, "set to ERROR")
set_logging_level (logging.ERROR)
test_logs()

print_test_header (7, "restored to INFO")
restore_logging_level ()
test_logs()

print_test_header (8, "restored to WARNING")
restore_logging_level ()
test_logs()

