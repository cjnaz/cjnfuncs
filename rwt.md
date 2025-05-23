# rwt / run_with_timeout - run any function with an enforced timeout

Skip to [API documentation](#links)

Some built-in, standard library, installed packages, and user-written functions can hang awaiting a response from
an intermittent resource.  EG, attempting to check the existence of a file on a network drive when the server hosting
the file is non-responsive.  

run_with_timeout provides a method to executed any function with an enforced timeout.

To run any function using run_with_timeout, simply change the call structure to pass the function
pointer as the first argument to run_with_timeout, then specify the timeout limit using the additional `rwt_timeout` 
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
we're passing the callable to run_with_timeout, not actually calling it directly.
- In Case 2, we set rwt_timeout to less than the sleep time, causing run_with_timeout to terminate the sleep early and raise
a TimeoutError exception.  In real usage the exception should be trapped and handled.

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
2. A user-defined function has at least read access the vars, functions, classes, etc that are available in the main thread.
3. A direct call to my_func is executed in the main thread, and changes to global variables are applied.
4. When calling my_func with run_with_timeout, leave off the `()` off of the `my_func` reference, and include my_func's args and keyword args exactly as with a direct call to my_func.  Add run_with_timeout's keyword args, as needed.  The default rwt_timeout value is 1.0 sec.
5. Since run_with_timeout gets a _copy_ of the global vars, the change made within my_func is not applied to the main thread's globals.
6. All calls to run_with_timeout should handle the possible TimeoutError exception.  Note that there is an addition 10ms delay in the process
termination handling for rwt debug logging.


<a id="links"></a>
         
<br>

---

# Links to classes, methods, and functions

- [run_with_timeout](#run_with_timeout)



<br/>

<a id="run_with_timeout"></a>

---

# run_with_timeout (func, *args, **kwargs, rwt_timeout=1, rwt_ntries=1, rwt_kill=True, rwt_debug=False) - Run a function in a separate process with an enforced timeout.

For a non-timeout run, return what the `func` returns or any exception raised.  On timeout kill the process (by default) and
raise a TimeoutError exception.


### Args

`func` (callable)
- The function to run

`*args` (0+)
- Positional args required by func

`**kwargs` (0+)
- Keyword args to be passed to func

`rwt_timeout` Additional kwarg (int or float, default 1)
- Enforced timeout in seconds

`rwt_ntries` Additional kwarg (int, default 1)
- Number of attempts to run `func` if `func` times out or raises an exception

`rwt_kill` Additional kwarg (bool, default True)
- If True, on timeout kill the process
- If False, on timeout let the process continue to run.  It will be orphaned - see Behavior notes, below.

`rwt_debug` Additional kwarg (bool, default False)
- Log run_with_timeout call arguments and mode setups


### Returns
- With no timeout or exception, returns the value returned from `func`
- Any exception raised by `func`
- If rwt_timeout is exceeded, returns TimeoutError
- Exceptions raised for invalid rwt_timeout, rwt_ntries, rwt_kill, or rwt_debug values

### Behaviors and rules
- The logging level is set to INFO for the called `func` by default.  To achieve debug level logging
for the called `func` set `rwt_debug=True`. TODO leave logging level alone unless its set to DEBUG?
- If func is a subprocess call then include `timeout=` in the subprocess args  TODO confirm.  Why?
- subprocess.TimeoutExpired is producing an odd exception on Python 3.11.9: 
`TypeError: TimeoutExpired.__init__() missing 1 required positional argument: 'timeout'`
- If `rwt_kill=False` then the spawned process will not be killed, and if the process doesn't exit by itself 
then the tool script will hang on exit, waiting for the orphan process to terminate.
To solve this the tool script needs to kill any orphaned processes created by run_with_timeout before exiting. 
The pid of the orphaned process is listed in the TimeoutError exception when `rwt_kill=False`, and can
be captured for explicitly killing any unterminated orphaned processes before exiting the tool script, eg: 
`os.kill (pid, signal.OSKILL)`.  See the `demo-run_with_timeout.py` test 15 for a working example.
Note that if `rwt_ntries` is greater than 1 and `rwt_kill=False`, then potentially several processes may 
be created and orphaned, all attempting to doing the same work.  The final TimeoutError exception only 
lists the process pid of the last try.
