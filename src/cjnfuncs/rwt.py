#==========================================================
#
#  Chris Nelson, 2025-
# TODOS
#   set debug level as globally defined for the func call
#   why set timeout on subprocess call?
#   Return full list of pids for rwt_kill=False
#==========================================================

# from pathlib import PurePath
# import shutil
# import __main__

from .core import logging, set_logging_level, restore_logging_level #, get_logging_level_stack
# from .mungePath import mungePath, check_path_exists
# import cjnfuncs.core as core

# from importlib_resources import files as ir_files


import signal
import time
import os
import sys
import multiprocessing
import traceback

def run_with_timeout(func, *args, **kwargs):
    """
## run_with_timeout (func, *args, **kwargs, rwt_timeout=1, rwt_ntries=1, rwt_kill=True, rwt_debug=False) - Run a function in a separate process with an enforced timeout.

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
- Number of attempts to run `func` if rwt_timeout is exceeded or `func` raises an exception

`rwt_kill` Additional kwarg (bool, default True)
- If True, on timeout kill the process
- If False, on timeout let the process continue to run.  It will be orphaned - see Behavior notes, below.

`rwt_debug` Additional kwarg (bool, default False)
- Intended for regression testing.  Logs rwt internal status and trace info.


### Returns
- With no timeout or exception, returns the value returned from `func`
- Any exception raised by `func`
- If rwt_timeout is exceeded, returns TimeoutError
- Exceptions raised for invalid rwt_timeout, rwt_ntries, rwt_kill, or rwt_debug values


### Behaviors and rules
- Logging within the called `func` is done at the logging level in effect when run_with_timeout is called. 
rwt_debug=True enables additional status and trace info.
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
"""

    def _runner(q, func, args, kwargs):
        def runner_int_handler(sig, frame):
            if _debug:
                set_logging_level(logging.DEBUG)
                logging.debug(f"RH1 - Signal {sig} received")
                time.sleep(0.01)                                # allow time for logging
            sys.exit()
        
        signal.signal(signal.SIGTERM, runner_int_handler)       # kill    (15)
        
        # os.setpgrp()    # Force to run in separate process group so that kill doesn't also kill the calling process
        # logging.warning (f"_runner entry logging level: {logging.getLogger().level}")
        logging.debug(f"R1  - runner_p pid {os.getpid()}")
        try:
            # logging.warning (f"Pre-func call logging level stack: {get_logging_level_stack()}")
            restore_logging_level()                             # normal logging level restored
            # logging.warning (f"After runner restore_logging_level stack: {get_logging_level_stack()}")
            # logging.warning (f"Pre-func call logging level: {logging.getLogger().level}")
            result = func(*args, **kwargs)
            q.put(("result", result))
        except Exception as e:
            q.put(("exception", (e.__class__, str(e), traceback.format_exc())))


    #--------- Top_level ---------

    # logging.warning (f"Top_level entry logging level: {logging.getLogger().level}")
    _timeout = 1                    # Default
    if 'rwt_timeout' in kwargs:
        _timeout = kwargs['rwt_timeout']
        del kwargs['rwt_timeout']
        if not isinstance(_timeout, (int, float)):
            raise ValueError (f"rwt_timeout must be type int or float, received <{_timeout}>")

    _ntries = 1                     # Default
    if 'rwt_ntries' in kwargs:
        _ntries = kwargs['rwt_ntries']
        del kwargs['rwt_ntries']
        if not isinstance(_ntries, (int)):
            raise ValueError (f"rwt_ntries must be type int, received <{_ntries}>")

    _kill = True                    # Default
    if 'rwt_kill' in kwargs:
        _kill = kwargs['rwt_kill']
        del kwargs['rwt_kill']
        if not isinstance(_kill, bool):
            raise ValueError (f"rwt_kill must be type bool, received <{_kill}>")

    _debug = False
    if 'rwt_debug' in kwargs:
        _debug = kwargs['rwt_debug']
        del kwargs['rwt_debug']
    # if _debug := kwargs.get('rwt_debug', False):
    #     del kwargs['rwt_debug']
        if not isinstance(_debug, bool):
            raise ValueError (f"rwt_debug must be type bool, received <{_debug}>")
        # set_logging_level(logging.DEBUG)
        # xx =  f"\nrun_with_timeout switches:\n  rwt_timeout:  {_timeout}\n  rwt_ntries:   {_ntries}\n  rwt_kill:     {_kill}\n  rwt_debug:    {_debug}"
        # xx += f"\n  Function:     {func}\n  args:         {args}\n  kwargs:       {kwargs}"
        # logging.debug (xx)
    # else:
    #     set_logging_level(logging.INFO)         # Debug level logging in called function is suppressed.  TODO only if level is currently debug ??

    # logging.warning (f"Pre ntries loop logging level stack: {get_logging_level_stack()}")
    # logging.warning (f"Pre ntries loop logging level: {logging.getLogger().level}")

    for ntry in range(_ntries):
        if _debug:
            set_logging_level(logging.DEBUG)
        else:
            set_logging_level(logging.INFO)         # No logging from rwt

        # logging.warning (f"After set_ll top of ntries loop logging level stack: {get_logging_level_stack()}")
        # logging.warning (f"After set_ll top of loop logging level: {logging.getLogger().level}")

        if ntry == 0:
            xx =  f"\nrun_with_timeout switches:\n  rwt_timeout:  {_timeout}\n  rwt_ntries:   {_ntries}\n  rwt_kill:     {_kill}\n  rwt_debug:    {_debug}"
            xx += f"\n  Function:     {func}\n  args:         {args}\n  kwargs:       {kwargs}"
            logging.debug (xx)

        if _ntries > 1:
            logging.debug (f"T0 - Try {ntry}")

        logging.debug (f"T1  - Starting runner_p")
        runner_to_toplevel_q = multiprocessing.Queue()
        runner_p = multiprocessing.Process(target=_runner, args=(runner_to_toplevel_q, func, args, kwargs), daemon=False, name=f'rwt_{func}')
        # logging.warning (f"Pre-runner call logging level stack: {get_logging_level_stack()}")

        runner_p.start()
        runner_p.join(timeout=_timeout)

        # logging.warning (f"After runner_p.join logging level stack: {get_logging_level_stack()}")
        # logging.warning (f"After runner_p.join logging level: {logging.getLogger().level}")

        if _debug:
            set_logging_level(logging.DEBUG, save=False)
        else:
            set_logging_level(logging.INFO, save=False)

        if not runner_p.is_alive():             # runner_p completed without timeout - normal exit
            logging.debug (f"T2  - runner_p exited before rwt_timeout")
            status, payload = runner_to_toplevel_q.get(timeout=0.2)     # runner_p always returns status 'result' or 'exception'
            logging.debug (f"T3  - <{status}> msg received from runner_p")

            if status == "result":
                restore_logging_level()
                return payload
            elif status == "exception":
                if ntry == _ntries-1:
                    restore_logging_level()
                    ex_type, ex_msg, ex_trace = payload     # ex_trace retained for possible future debug/use
                    raise ex_type(f"{ex_msg}")

        else:                                   # runner_p is still running - hung
            if _kill:
                logging.debug (f"T4  - terminate runner_p")
                runner_p.terminate()
                runner_p.join(timeout=0.2)
                if runner_p.is_alive():
                    logging.debug (f"T5  - SIGKILL runner_p")
                    os.kill (runner_p.pid, signal.SIGKILL)
                if ntry == _ntries-1:
                    restore_logging_level()
                    raise TimeoutError (f"Function <{func.__name__}> timed out after {_timeout} seconds (killed)")
            else:
                if ntry == _ntries-1:
                    restore_logging_level()
                    raise TimeoutError (f"Function <{func.__name__}> timed out after {_timeout} seconds (not killed, pid {runner_p.pid})")



    # def _runner(q, func, args, kwargs):
    #     def runner_int_handler(sig, frame):
    #         logging.debug(f"RH1 - Signal {sig} received {os.getpid()}") #\n {frame}")     # TODO debug
    #         time.sleep(0.1)                             # allow time for logging
    #         sys.exit()
        
    #     signal.signal(signal.SIGTERM, runner_int_handler)      # kill    (15)
        
    #     os.setpgrp()                # Force to run in separate process group so that kill doesn't also kill the calling process
    #     logging.debug(f"R1 - Starting  {os.getpid()}")
    #     try:
    #         result = func(*args, **kwargs)
    #         q.put(("result", result))
    #     except Exception as e:
    #         q.put(("exception", (e.__class__, str(e), traceback.format_exc())))


    # def _worker(worker_to_rwt_q, *args, **kwargs):
    #     def worker_int_handler(sig, frame):
    #         logging.debug(f"WH1 - Signal {sig} received  {os.getpid()}") #\n {frame}")     # TODO debug
    #         if runner_p.is_alive():
    #             logging.debug (f"WH2 - Sending terminate to runner_p  {os.getpid()}")
    #             runner_p.terminate()
    #             runner_p.join(timeout=0.2)

    #             if runner_p.is_alive():
    #                 logging.debug (f"WH3 - SIGKILL runner_p  {os.getpid()}")
    #                 os.kill (runner_p.pid, signal.SIGKILL)
    #                 time.sleep(0.1)                             # allow time for logging
    #         logging.debug (f"WH4 - runner_p.is_alive? {runner_p.is_alive()}  {os.getpid()}")
    #         sys.exit(0)

    #     signal.signal(signal.SIGTERM, worker_int_handler)      # kill    (15)

    #     # logging.getLogger().handlers.clear()        # Block root logger in child
    #     # logging.disable(logging.CRITICAL)
    #     os.setpgrp()
    #     logging.debug (f"W1 - starting runner_p  {os.getpid()}")
    #     runner_to_worker_q = multiprocessing.Queue()
    #     runner_p = multiprocessing.Process(target=_runner, args=(runner_to_worker_q, func, args, kwargs))
    #     runner_p.start()

    #     do_exit = False
    #     msg = ('result', None)
    #     while 1:
    #         # Normal exit when msg received or runner_p is dead (default msg ('result', None))
    #         # If func does not terminate, then Top_level will send worker_terminate, forcing worker_int_handler
    #         if not runner_p.is_alive():
    #             logging.debug (f"W2 - runner_p is DEAD  {os.getpid()}")
    #             do_exit = True
    #         try:
    #             logging.debug (f"W3 - Check for runner_to_worker_q msg  {os.getpid()}")
    #             msg = runner_to_worker_q.get(timeout=0.2)
    #             do_exit = True
    #             logging.debug (f"W4 - runner_to_worker_q msg received  {os.getpid()}")
    #         except Exception as e:
    #             # Nothing is in runner_to_worker_q
    #             logging.debug (f"W5 - NO runner_to_worker_q msg received  {os.getpid()}")

    #         if do_exit:
    #             logging.debug (f"W6 - pass up msg, runner_p.join(0.2)  {os.getpid()}")
    #             worker_to_rwt_q.put(msg)
    #             runner_p.join(timeout=0.2)

    #             if runner_p.is_alive():
    #                 logging.debug (f"W7 - terminating runner_p  {os.getpid()}")
    #                 runner_p.terminate()
    #                 runner_p.join(timeout=0.2)
    #                 if runner_p.is_alive():
    #                     logging.debug (f"W8 - SIGKILL runner_p  {os.getpid()}")
    #                     os.kill (runner_p.pid, signal.SIGKILL)
    #             logging.debug (f"W9 - exiting  {os.getpid()}")
    #             break                                               # Exit while loop, worker_p exits



    # #--------- Top_level ---------
    # _timeout = 1                    # Default
    # if 'rwt_timeout' in kwargs:
    #     _timeout = kwargs['rwt_timeout']
    #     del kwargs['rwt_timeout']
    # if not isinstance(_timeout, (int, float)):
    #     raise ValueError (f"rwt_timeout must be type int or float, received <{_timeout}>")

    # _ntries = 1
    # if 'rwt_ntries' in kwargs:
    #     _ntries = kwargs['rwt_ntries']
    #     del kwargs['rwt_ntries']
    # if not isinstance(_ntries, (int)):
    #     raise ValueError (f"rwt_ntries must be type int, received <{_ntries}>")

    # _kill = True                    # Default
    # if 'rwt_kill' in kwargs:
    #     _kill = kwargs['rwt_kill']
    #     del kwargs['rwt_kill']
    # if not isinstance(_kill, bool):
    #     raise ValueError (f"rwt_kill must be type bool, received <{_kill}>")

    # if _debug := kwargs.get('rwt_debug', False):
    #     del kwargs['rwt_debug']
    #     set_logging_level(logging.DEBUG)
    #     xx =  f"\nrun_with_timeout switches:\n  rwt_timeout:  {_timeout}\n  rwt_ntries:   {_ntries}\n  rwt_kill:     {_kill}\n  rwt_debug:    {_debug}"
    #     xx += f"\n  Function:     {func}\n  args:         {args}\n  kwargs:       {kwargs}"
    #     logging.debug (xx)
    # else:
    #     set_logging_level(logging.INFO)     # Debug level logging in called function is suppressed.  TODO only if level is currently debug ??


    # for ntry in range(_ntries):
    #     if _ntries > 1:
    #         logging.debug (f"T0 - Try {ntry}")
    #     worker_to_rwt_q = multiprocessing.Queue()
    #     worker_p = multiprocessing.Process(target=_worker, args=(worker_to_rwt_q, *args), kwargs=kwargs)
    #     logging.debug ("T1 - starting worker_p")
    #     worker_p.start()
    #     worker_p.join(timeout=_timeout)

    #     # Normal passing exit
    #     if not worker_p.is_alive():
    #         logging.debug ("T2 - worker_p exited without timeout")
    #         restore_logging_level()
    #         if not worker_to_rwt_q.empty():
    #             status, payload = worker_to_rwt_q.get()

    #             if status == "result":
    #                 return payload
    #             elif status == "exception":
    #                 ex_type, ex_msg, ex_trace = payload     # ex_trace retained for possible future debug/use
    #                 raise ex_type(f"{ex_msg}")
    #         else:
    #             return None

    #     # Timed out - still running
    #     if _kill:                           
    #         logging.debug (f"T3 - worker_p timed out - Killing worker_p")
    #         worker_p.terminate()
    #         worker_p.join()
        

    # restore_logging_level()
    # if _kill:
    #     raise TimeoutError (f"Function <{func.__name__}> timed out after {_timeout} seconds (killed)")
    # else:
    #     raise TimeoutError (f"Function <{func.__name__}> timed out after {_timeout} seconds (not killed)")
