#!/usr/bin/env python3
# ***** rwt_ex2.py *****

import time
from cjnfuncs.core      import set_toolname, setuplogging, set_logging_level, logging   # **** NOTE 1
from cjnfuncs.rwt       import run_with_timeout

set_toolname('rwt_ex2')
setuplogging(ConsoleLogFormat="{asctime} {module:>22}.{funcName:20} {levelname:>8}:  {message}")
set_logging_level(logging.INFO)

global_int =    7

def my_func(tnum, sleep_time, mult_term=2):
    global global_str, global_dict                                                      # **** NOTE 2
    logging.info (f"===== Test {tnum}:  Product: {global_int * mult_term} =====")
    global_str = 'Test number ' + str(tnum)
    global_dict['pi'] = 3.1415
    logging.info (f"Vars within my_func:  <{global_str}>, <{global_dict}>")
    time.sleep (sleep_time)
    logging.info ("Reached the end of my_func")
    return global_dict['pi'] * mult_term


# Test 1 - calling my_func directly
global_str =    '----'
global_dict =   {'pi': 3.14}
logging.info (f"Returned by my_func call: <{my_func(1, 1.0, mult_term=6)}>")
logging.info (f"Vars in main code after my_func call:  <{global_str}>, <{global_dict}>")# **** NOTE 3

# Test 2
global_str =    '----'                                                                  # **** NOTE 4
global_dict =   {'pi': 3.14}
logging.info (f"Returned by run_with_timeout call: <{run_with_timeout(my_func, 2, 1.0, rwt_timeout=1.5)}>")
logging.info (f"Vars in main code after my_func call:  <{global_str}>, <{global_dict}>")# **** NOTE 5

# Test 3
global_str =    '----'
global_dict =   {'pi': 3.14}
try:                                                                                    # **** NOTE 6
    logging.info (f"Returned by run_with_timeout call: <{run_with_timeout(my_func, 3, 1.0, mult_term=10, rwt_timeout=0.5)}>")
except Exception as e:
    logging.warning (f"Received exception:  {type(e).__name__}: {e}")
logging.info (f"Vars in main code after my_func call:  <{global_str}>, <{global_dict}>")
