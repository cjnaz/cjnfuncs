#!/usr/bin/env python3
from cjnfuncs.core import set_toolname, logging, set_logging_level, restore_logging_level, get_logging_level_stack

set_toolname('core_ex3')    # Configures the root logger to defaults, including default logging level WARNING/30


def myfunction():
    # With set and restore_logging_level calls uncommented I get debug logging within myfunction

    set_logging_level(logging.DEBUG)    # Save current WARNING/30 level to the stack and set DEBUG/10 level
    # Do complicated stuff in this function
    logging.debug   (f"2 - Within myfunction()        - logging level: {logging.getLogger().level}. On the stack: {get_logging_level_stack()}")

    restore_logging_level()             # Restore (and pop) the pre-existing level from from stack
    return


logging.warning (f"1 - Before myfunction() call   - logging level: {logging.getLogger().level}. On the stack: {get_logging_level_stack()}")
myfunction()
logging.warning (f"3 - After  myfunction() return - logging level: {logging.getLogger().level}. On the stack: {get_logging_level_stack()}")
