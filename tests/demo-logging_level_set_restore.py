#!/usr/bin/env python3
"""Demo/test for set / restore_logging_level

Produce / compare to golden results:
    ./demo-logging_level_set_restore.py | diff demo-logging_level_set_restore-golden.txt -
        No differences expected

Diffing output between Linux and Windows may fail due to locale differences.  Check in Beyond Compare.

"""
#==========================================================
#
#  Chris Nelson, 2025
#
#==========================================================

__version__ = "3.1"


from cjnfuncs.core import set_toolname, logging, set_logging_level, restore_logging_level, get_logging_level_stack, pop_logging_level_stack

set_toolname('demo_logging_level_set_restore')


def print_test_header(tnum, desc, expect):
    print ("\n======================================================================================================")
    print (f"Test number {tnum}:  {desc}")
    print (f"Expect:\n{expect}")
    print ("======================================================================================================\n")


def test_logs (logger=''):
    test_logger = logging.getLogger(logger)
    test_logger.debug   (f"logger <{logger}>")
    test_logger.info    (f"logger <{logger}>")
    test_logger.warning (f"logger <{logger}>")
    test_logger.error   (f"logger <{logger}>")
    print (f"logger <{logger}> logging level {logging.getLogger(logger).level}, history stack: {get_logging_level_stack(logger)}")


print_test_header (1, "Root logger - Initial level WARNING", "logger <> logging level 30, history stack: []")
test_logs()

print_test_header (2, "Root logger - Save, set to DEBUG", "logger <> logging level 10, history stack: [30]")
set_logging_level (logging.DEBUG, save=True)
test_logs()

print_test_header (3, "Root logger - Restore to WARNING", "logger <> logging level 30, history stack: []")
restore_logging_level ()
test_logs()

print_test_header (4, "Root logger - Restore with no prior set (empty stack)", "logger <> logging level 30, history stack: []")
restore_logging_level ()
test_logs()

print_test_header (5, "Root logger - Save, set to INFO", "logger <> logging level 20, history stack: [30]")
set_logging_level (logging.INFO, save=True)
test_logs()

print_test_header (6, "Root logger - Save, set to ERROR", "logger <> logging level 40, history stack: [30, 20]")
set_logging_level (logging.ERROR, save=True)
test_logs()

print_test_header (7, "Root logger - Restore to INFO", "logger <> logging level 20, history stack: [30]")
restore_logging_level ()
test_logs()

print_test_header (8, "Root logger - Restore to WARNING", "logger <> logging level 30, history stack: []")
restore_logging_level ()
test_logs()


print_test_header (9, "Root logger - Load the stack, set with save=False", "See after each stage")
set_logging_level (logging.ERROR, save=True)               # default WARNING pushed    [30]
set_logging_level (logging.INFO, save=True)                # ERROR pushed              [30, 40]
test_logs()
print ("logger <> logging level 20, history stack: [30, 40]   <<< Expect")

print ()
set_logging_level (logging.DEBUG, save=False)
test_logs()
print ("logger <> logging level 10, history stack: [30, 40]   <<< Expect")

print ()
pop_logging_level_stack()
set_logging_level (logging.CRITICAL, save=False)
test_logs()
print ("logger <> logging level 50, history stack: [30]       <<< Expect")

print ()
restore_logging_level ()
test_logs()
print ("logger <> logging level 30, history stack: []         <<< Expect")


print_test_header (10, "Root logger - Load the stack, set_logging_level with clear=True", "See after each stage")
set_logging_level (logging.ERROR, save=True)                # default WARNING pushed    [30]
set_logging_level (logging.INFO, save=True)                 # ERROR pushed              [30, 40]
set_logging_level (logging.DEBUG, clear=True)
test_logs()
print ("logger <> logging level 10, history stack: []           <<< Expect")

print()
set_logging_level (logging.ERROR, save=True)                # default WARNING pushed    [20, 10]
set_logging_level (logging.INFO, save=True)                 # ERROR pushed              [20, 10, 40]
test_logs()
print ("logger <> logging level 20, history stack: [10, 40]     <<< Expect")

print()
set_logging_level (logging.ERROR, save=False, clear=True)
test_logs()
print ("logger <> logging level 40, history stack: []           <<< Expect")

print()
restore_logging_level ()                                    # Restore from empty stack sets to WARNING
test_logs()
print ("logger <> logging level 30, history stack: []           <<< Expect")


print_test_header (11, "Root logger - Load the stack, pop_logging_level with clear=True", "See after each stage")
set_logging_level (logging.ERROR, save=True)                # default WARNING pushed    [30]
set_logging_level (logging.INFO, save=True)                 # ERROR pushed              [30, 40]
set_logging_level (logging.ERROR, save=True)                # INFO pushed               [30, 40, 20]
set_logging_level (logging.INFO, save=True)                 # ERROR pushed              [30, 40, 20, 40]
pop_logging_level_stack ()
test_logs()
print ("logger <> logging level 20, history stack: [30, 40, 20]     <<< Expect")

print()
pop_logging_level_stack ()
test_logs()
print ("logger <> logging level 20, history stack: [30, 40]         <<< Expect")

print()
pop_logging_level_stack (clear=True)
test_logs()
print ("logger <> logging level 20, history stack: []               <<< Expect")


#-----------------------------
# Child logger is independent

print_test_header (21, "Child xyz logger - Initial level 0", "logger <xyz> logging level 0, history stack: []")
set_logging_level(15, save=False, clear=True)       # Set root logger to 25, with 15 on its stack
set_logging_level(25, save=True)
test_logs('xyz')
test_logs()

print_test_header ('21a', "Child xyz logger - uninitialized, pop stack", "logger <xyz> logging level 0, history stack: []")
print (f"logger xyz uninitialized.  pop_logging_level_stack('xyz') = <{pop_logging_level_stack('xyz')}>")
test_logs('xyz')

print_test_header (22, "Child xyz logger - Save, set to DEBUG", "logger <xyz> logging level 10, history stack: [0]")
set_logging_level (logging.DEBUG, logger_name='xyz', save=True)
test_logs('xyz')

print_test_header (23, "Child xyz logger - Restore to 0 (WARNING)", "logger <xyz> logging level 0, history stack: []")
restore_logging_level (logger_name='xyz')
test_logs('xyz')

print_test_header (24, "Child xyz logger - Save, set to INFO, ERROR", "logger <xyz> logging level 40, history stack: [0, 20]")
set_logging_level (logging.INFO, logger_name='xyz', save=True)
set_logging_level (logging.ERROR, logger_name='xyz', save=True)
test_logs('xyz')

print_test_header (25, "Child xyz logger - Save, Clear set to DEBUG", "logger <xyz> logging level 10, history stack: [40]")
set_logging_level (logging.DEBUG, logger_name='xyz', save=True, clear=True)
test_logs('xyz')


print_test_header (26, "Child xyz logger - Load stack to [10, 16], Pop stack to [10], Pop stack clear to [], restore to WARNING", "See after each stage")
set_logging_level (16, logger_name='xyz', save=True, clear=True)
test_logs('xyz')
print ("logger <xyz> logging level 16, history stack: [10]      <<< Expect")

set_logging_level (17, logger_name='xyz', save=True)
test_logs('xyz')
print ("logger <xyz> logging level 17, history stack: [10, 16]  <<< Expect")

pop_logging_level_stack('xyz')
test_logs('xyz')
print ("logger <xyz> logging level 17, history stack: [10]      <<< Expect")

pop_logging_level_stack('xyz', clear=True)
test_logs('xyz')
print ("logger <xyz> logging level 17, history stack: []        <<< Expect")

restore_logging_level('xyz')
test_logs('xyz')
print ("logger <xyz> logging level 30, history stack: []        <<< Expect")
test_logs()
print ("logger <> logging level 25, history stack: [15]         <<< Expect")



