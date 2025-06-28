#==========================================================
#
#  Chris Nelson, 2025-
#
#==========================================================


from .core import logging, set_logging_level, restore_logging_level

import signal
import time
import os
import sys
import multiprocessing
import traceback

def run_with_timeout(func, *args, **kwargs):
    """
## run_with_timeout (func, *args, **kwargs, rwt_timeout=1.0, rwt_ntries=1, rwt_kill=True, rwt_debug=False) - Run a function in a separate process with an enforced timeout.

`run_with_timeout` uses the multiprocessing module, and works by running the specified `func` in a managed 
external process that can be reliably killed on timeout.
For a non-timeout run, `run_with_timeout` returns what the `func` returns or any exception raised. 
On timeout, the process is killed (by default) and a TimeoutError exception is raised.


### Args

`func` (callable)
- The function to run
- May be any function - built-in, standard library, supplied by an installed package, or user-written.

`*args` (0+)
- Positional args required by func

`**kwargs` (0+)
- Keyword args to be passed to func

`rwt_timeout` additional kwarg (int or float, default 1.0)
- Enforced timeout in seconds

`rwt_ntries` additional kwarg (int, default 1)
- Number of attempts to run `func` if rwt_timeout is exceeded or `func` raises an exception

`rwt_kill` additional kwarg (bool, default True)
- If True, on timeout kill the process
- If False, on timeout let the process continue to run.  It will be orphaned - see Behavior notes, below.

`rwt_debug` additional kwarg (bool, default False)
- Intended for regression testing.  Logs rwt internal status and trace info.


### Returns
- With no timeout or exception, returns the value returned from `func`
- Any exception raised by `func`
- If rwt_timeout is exceeded, returns TimeoutError
- Exceptions raised for invalid rwt_timeout, rwt_ntries, rwt_kill, or rwt_debug values


### Behaviors and rules
- Logging within the called `func` is done at the logging level in effect when run_with_timeout is called. 
rwt_debug=True enables additional status and trace info, intended for debug and regression testing.
- If making a subprocess call and the subprocess timeout limit is triggered, a
subprocess.TimeoutExpired exception is produce with an odd error message on Python 3.11.9: 
`TypeError: TimeoutExpired.__init__() missing 1 required positional argument: 'timeout'`. Generally, don't use
the subprocess timeout arg when using run_with_timeout.
- If `rwt_kill=False` then the spawned process will not be killed, and if the process doesn't exit by itself 
then the tool script will hang on exit, waiting for the orphan process to terminate.
To solve this the tool script needs to kill any orphaned processes created by run_with_timeout before exiting. 
The pids of the orphaned processes are listed in the TimeoutError exception when `rwt_kill=False`, and can
be captured for explicitly killing of any unterminated orphaned processes before exiting the tool script, eg: 
`os.kill (pid, signal.OSKILL)`.  See `rwt.md` for a working example.
Note that if `rwt_ntries` is greater than 1 and `rwt_kill=False`, then potentially several processes may 
be created and orphaned, all attempting to doing the same work.
"""

    def _runner(q, func, args, kwargs):
        def runner_int_handler(sig, frame):
            if _debug:
                set_logging_level(logging.DEBUG)
                logging.debug(f"RH1 - Signal {sig} received")
                time.sleep(0.01)                            # allow time for logging before terminating
            sys.exit()
        
        signal.signal(signal.SIGTERM, runner_int_handler)   # kill (15)
        
        logging.debug(f"R1  - runner_p pid {os.getpid()}")
        try:
            restore_logging_level()                         # External logging level restored for running target function
                                                            # The stack pop is meaningless since running with a copy of the stack in a separate process
            result = func(*args, **kwargs)
            q.put(("result", result))
        except Exception as e:
            q.put(("exception", (e.__class__, str(e), traceback.format_exc())))


    #--------- Top_level ---------

    _timeout = 1.0
    if 'rwt_timeout' in kwargs:
        _timeout = kwargs['rwt_timeout']
        del kwargs['rwt_timeout']
        if not isinstance(_timeout, (int, float)):
            raise ValueError (f"rwt_timeout must be type int or float, received <{_timeout}>")

    _ntries = 1
    if 'rwt_ntries' in kwargs:
        _ntries = kwargs['rwt_ntries']
        del kwargs['rwt_ntries']
        if not isinstance(_ntries, (int)):
            raise ValueError (f"rwt_ntries must be type int, received <{_ntries}>")

    _kill = True
    if 'rwt_kill' in kwargs:
        _kill = kwargs['rwt_kill']
        del kwargs['rwt_kill']
        if not isinstance(_kill, bool):
            raise ValueError (f"rwt_kill must be type bool, received <{_kill}>")
    if _kill == False:
        pid_list = []

    _debug = False
    if 'rwt_debug' in kwargs:
        _debug = kwargs['rwt_debug']
        del kwargs['rwt_debug']
        if not isinstance(_debug, bool):
            raise ValueError (f"rwt_debug must be type bool, received <{_debug}>")

    if _debug:
        set_logging_level(logging.DEBUG)                    # External value saved on stack, restored by runner and on exit
    else:
        set_logging_level(logging.INFO)


    for ntry in range(_ntries):
        if ntry == 0:
            xx =  f"\nrun_with_timeout switches:\n  rwt_timeout:  {_timeout}\n  rwt_ntries:   {_ntries}\n  rwt_kill:     {_kill}\n  rwt_debug:    {_debug}"
            xx += f"\n  Function:     {func}\n  args:         {args}\n  kwargs:       {kwargs}"
            logging.debug (xx)

        if _ntries > 1:
            logging.debug (f"T0  - Try {ntry}")

        logging.debug (f"T1  - Starting runner_p")
        runner_to_toplevel_q = multiprocessing.Queue()
        runner_p = multiprocessing.Process(target=_runner, args=(runner_to_toplevel_q, func, args, kwargs), daemon=False, name=f'rwt_{func}')
        runner_p.start()
        runner_p.join(timeout=_timeout)

        if _debug:
            set_logging_level(logging.DEBUG, save=False)
        else:
            set_logging_level(logging.INFO, save=False)     # Disable logging from rwt itself


        if runner_p.is_alive():
            if _kill:                                       # runner_p is alive.  Kill it.
                logging.debug (f"T4  - terminate runner_p")
                runner_p.terminate()
                runner_p.join(timeout=0.2)
                if runner_p.is_alive():
                    logging.debug (f"T5  - SIGKILL runner_p")
                    try:
                        os.kill (runner_p.pid, signal.SIGKILL)
                    except Exception as e:
                        if 'No such process' in str(e):     # Corner case of runner_p either ended normally, or the terminate finally happened
                            pass
                        else:
                            if ntry == _ntries-1:
                                restore_logging_level()     # Restore External logging level before exit
                                raise
                if ntry == _ntries-1:
                    restore_logging_level()
                    raise TimeoutError (f"Function <{func.__name__}> timed out after {_timeout} seconds (killed)")
            else:                                           # runner_p is alive, and DON'T kill it
                pid_list.append(str(runner_p.pid))
                if ntry == _ntries-1:
                    restore_logging_level()
                    raise TimeoutError (f"Function <{func.__name__}> timed out after {_timeout} seconds (not killed) orphaned pids: {' '.join(pid_list)}")

        else:
            logging.debug (f"T2  - runner_p exited before rwt_timeout")


        if not runner_to_toplevel_q.empty():                # On exit, runner_p returns either status='result' or ='exception'
            status, payload = runner_to_toplevel_q.get()
            logging.debug (f"T3  - <{status}> msg received from runner_p")
            if status == "result":
                restore_logging_level()
                return payload
            elif status == "exception":
                if ntry == _ntries-1:
                    restore_logging_level()
                    ex_type, ex_msg, ex_trace = payload     # ex_trace retained for possible future debug/use
                    raise ex_type(f"{ex_msg}")
