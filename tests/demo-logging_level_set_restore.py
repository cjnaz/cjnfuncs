#!/usr/bin/env python3
"""Demo/test for set / restore_logging_level

Produce / compare to golden results:
    ./demo-logging_level_set_restore.py | diff demo-logging_level_set_restore-golden.txt -
        No differences expected

"""
#==========================================================
#
#  Chris Nelson, 2025
#
#==========================================================

__version__ = "1.0"


from cjnfuncs.core import set_toolname, logging, set_logging_level, restore_logging_level, get_logging_level_stack, pop_logging_level_stack

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
    print (f"logging level {logging.getLogger().level}, ll_history stack: {get_logging_level_stack()}")


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


print_test_header (9, "Load the stack, set with save=False")
set_logging_level (logging.ERROR)               # default WARNING pushed    [30]
set_logging_level (logging.INFO)                # ERROR pushed              [30, 40]
test_logs()             # logging level 20, ll_history stack: [30, 40]

print ()
set_logging_level (logging.DEBUG, save=False)   # No push
test_logs()             # logging level 10, ll_history stack: [30, 40]

print ()
pop_logging_level_stack()                       #                           [30]
set_logging_level (logging.CRITICAL, save=False)   # No push
test_logs()             # logging level 50, ll_history stack: [30]

print ()
restore_logging_level ()
test_logs()             # logging level 30, ll_history stack: []


print_test_header (10, "Load the stack, set_logging_level with clear=True")
set_logging_level (logging.ERROR)               # default WARNING pushed    [30]
set_logging_level (logging.INFO)                # ERROR pushed              [30, 40]
set_logging_level (logging.DEBUG, clear=True)
test_logs()             # logging level 10, ll_history stack: [20]

print()
set_logging_level (logging.ERROR)               # default WARNING pushed    [20, 10]
set_logging_level (logging.INFO)                # ERROR pushed              [20, 10, 40]
test_logs()             # logging level 20, ll_history stack: [20, 10, 40]

print()
set_logging_level (logging.ERROR, save=False, clear=True)
test_logs()             # logging level 40, ll_history stack: []

print()
restore_logging_level ()                        # Restore from empty stack sets to WARNING
test_logs()             # logging level 30, ll_history stack: []


print_test_header (11, "Load the stack, pop_logging_level with clear=True")
set_logging_level (logging.ERROR)               # default WARNING pushed    [30]
set_logging_level (logging.INFO)                # ERROR pushed              [30, 40]
set_logging_level (logging.ERROR)               # INFO pushed               [30, 40, 20]
set_logging_level (logging.INFO)                # ERROR pushed              [30, 40, 20, 40]
pop_logging_level_stack ()
test_logs()             # logging level 20, ll_history stack: [30, 40, 20]

print()
pop_logging_level_stack ()
test_logs()             # logging level 20, ll_history stack: [30, 40]

print()
pop_logging_level_stack (clear=True)
test_logs()             # logging level 20, ll_history stack: []
