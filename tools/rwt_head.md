# rwt / run_with_timeout - run any function with an enforced timeout

Skip to [API documentation](#links)

Some built-in, standard library, installed packages, and user-written functions can hang awaiting a response from
an intermittent resource.  EG, attempting to check the existence of a file on a network drive when the server hosting
the file is non-responsive.  

`run_with_timeout()` provides a method to execute any function with an enforced timeout.

To run any function using `run_with_timeout()`, simply change the call structure to pass the function
pointer as the first argument to `run_with_timeout()`, then specify the timeout limit using the additional `rwt_timeout` 
keyword argument.

<br>

## Basic example

Given:
```
#!/usr/bin/env python3
# ***** rwt_ex1.py *****

import time
from cjnfuncs.rwt import run_with_timeout

# Case 1
print ("0.5 sec delay")
run_with_timeout (time.sleep, 0.5, rwt_timeout=1)

# Case 2
print ("0.5 sec delay, killed after 0.2 sec")
run_with_timeout (time.sleep, 0.5, rwt_timeout=0.2)
```

The output:
```
$ ./rwt_ex1.py 
0.5 sec delay
0.5 sec delay, killed after 0.2 sec
Traceback (most recent call last):
  File "/mnt/share/dev/packages/cjnfuncs/tools/doc_code_examples/./rwt_ex1.py", line 13, in <module>
    run_with_timeout (time.sleep, 0.5, rwt_timeout=0.2)
  File "/mnt/share/dev/packages/cjnfuncs/src/cjnfuncs/rwt.py", line 159, in run_with_timeout
    raise TimeoutError (f"Function <{func.__name__}> timed out after {_timeout} seconds (killed)")
TimeoutError: Function <sleep> timed out after 0.2 seconds (killed)
```

What's going on?  Of note:
- The standard library time.sleep() function is being called in both cases.  Note that `time.sleep` has no parens since
we're passing the _callable_ to `run_with_timeout()`, not actually calling it directly.
- In Case 2, we set `rwt_timeout` to less than the sleep time, causing `run_with_timeout()` to terminate the sleep early and raise
a `TimeoutError` exception.  In real usage the exception should be trapped and handled.

<br>

## A detailed, annotated example

Given:
```
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

```

The output:
```
$ ./rwt_ex2.py 
2025-05-23 10:39:25,395                rwt_ex2.my_func                  INFO:  ===== Test 1:  Product: 42 =====
2025-05-23 10:39:25,395                rwt_ex2.my_func                  INFO:  Vars within my_func:  <Test number 1>, <{'pi': 3.1415}>
2025-05-23 10:39:26,395                rwt_ex2.my_func                  INFO:  Reached the end of my_func
2025-05-23 10:39:26,395                rwt_ex2.<module>                 INFO:  Returned by my_func call: <18.849>
2025-05-23 10:39:26,396                rwt_ex2.<module>                 INFO:  Vars in main code after my_func call:  <Test number 1>, <{'pi': 3.1415}>
2025-05-23 10:39:26,426                rwt_ex2.my_func                  INFO:  ===== Test 2:  Product: 14 =====
2025-05-23 10:39:26,426                rwt_ex2.my_func                  INFO:  Vars within my_func:  <Test number 2>, <{'pi': 3.1415}>
2025-05-23 10:39:27,427                rwt_ex2.my_func                  INFO:  Reached the end of my_func
2025-05-23 10:39:27,429                rwt_ex2.<module>                 INFO:  Returned by run_with_timeout call: <6.283>
2025-05-23 10:39:27,430                rwt_ex2.<module>                 INFO:  Vars in main code after my_func call:  <---->, <{'pi': 3.14}>
2025-05-23 10:39:27,433                rwt_ex2.my_func                  INFO:  ===== Test 3:  Product: 70 =====
2025-05-23 10:39:27,433                rwt_ex2.my_func                  INFO:  Vars within my_func:  <Test number 3>, <{'pi': 3.1415}>
2025-05-23 10:39:27,945                rwt_ex2.<module>              WARNING:  Received exception:  TimeoutError: Function <my_func> timed out after 0.5 seconds (killed)
2025-05-23 10:39:27,947                rwt_ex2.<module>                 INFO:  Vars in main code after my_func call:  <---->, <{'pi': 3.14}>
```

Notables:
1. Logging to the console with timestamps is used in this example to show the enforced timeout in Test 3.
2. A function executed by run_with_timeout has read/write access to a _copy_ of the vars, functions, classes, etc that are available in the main thread.
3. A direct call to my_func is executed in the main thread, and changes to global variables are applied.
4. When calling my_func with run_with_timeout, leave off the `()` off of the `my_func` reference, and include my_func's args and keyword args exactly as with a direct call to my_func.  Add run_with_timeout's keyword args, as needed.  The default rwt_timeout value is 1.0 sec.
5. Since run_with_timeout gets a _copy_ of the global vars, the change made within my_func is not applied to the main thread's globals.
6. All calls to run_with_timeout should handle the possible TimeoutError exception.  Note that there is an addition 10ms delay in the process
termination handling for rwt debug logging.

<br>

## Using rwt_kill=False and manually killing orphaned processes

This example creates three orphaned processes who's pids are returned in the timeout exception raised by
run_with_timeout.  The code extracts the pids and kills the processes.

Code:
```
#!/usr/bin/env python3
# ***** rwt_ex3.py *****

import time
import os
import signal

from cjnfuncs.core      import set_toolname, logging
from cjnfuncs.rwt       import run_with_timeout

set_toolname('rwt_ex3')


def wont_terminate():
    # This function is hard to kill.  SIGTERM doesn't break the loop.
    while 1:
        try:
            time.sleep (0.2)
        except:
            pass


try:
    run_with_timeout(wont_terminate, rwt_timeout=0.5, rwt_kill=False, rwt_ntries=3)
except Exception as e:
    logging.error (f"EXCEPTION received:  {type(e).__name__}: {e}")

    # Kill the orphaned processes
    runner_pids = str(e).split('orphaned pids: ')[1].split(' ')
    for runner_pid in runner_pids:
        os.kill(int(runner_pid), signal.SIGKILL)
```

Output from the exception log:
```
rwt_ex3.<module>             -    ERROR:  EXCEPTION received:  TimeoutError: Function <wont_terminate> timed out after 0.5 seconds (not killed) orphaned pids: 2069926 2069931 2069969
```

<br>

## Controlling logging from within rwt code

Logging within the rwt module uses the `cjnfuncs.rwt` named/child logger.  By default this logger is set to the `logging.WARNING` level, 
meaning that no logging messages are produced from within the rwt code.  For validation and debug purposes, logging from within rwt code 
can be enabled by setting the logging level for this module's logger from within the tool script code:

        logging.getLogger('cjnfuncs.rwt').setLevel(logging.DEBUG)

        # Or alternately, use the core module set_logging_level() function:
        set_logging_level (logging.DEBUG, 'cjnfuncs.rwt')

Note that on Windows, debug logging messages from the run_with_timeout internal `worker()` function (which calls `func`) are 
erratically produced, and not produced if `func` raises an exception.  Logging from within `func`, and any raised exception
operate normally.  On Linux, worker debug logging operates correctly.
