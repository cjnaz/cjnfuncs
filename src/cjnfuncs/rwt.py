#==========================================================
#
#  Chris Nelson, 2025-
#
#==========================================================

# from pathlib import PurePath
# import shutil
# import __main__

from .core import logging, set_logging_level, restore_logging_level
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
## run_with_timeout(func, *args, **kwargs, rwt_timeout=1, rwt_ntries=1, rwt_kill=True, rwt_debug=False) - Run a function in a separate process with an enforced timeout.

On timeout kill the process by default.

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
- Number of attempts to run `func` if func times out
- Does not pertain to func's return results or any exceptions raised by func.

`rwt_kill` Additional kwarg (bool, default True)
- If True, on timeout kill the process
- If False, on timeout let the process continue to run.  It will be orphaned - be careful.

`rwt_debug` Additional kwarg (bool (lose type))
- Log run_with_timeout call arguments and mode setups
- False value is bool False, int 0, or None.  Else evaluates True. TODO

### Returns
- With no timeout or exception, returns the value returned from `func`
- Any exception thrown by `func`
- If rwt_timeout is exceeded, returns TimeoutError
- Exceptions thrown for invalid rwt_timeout, rwt_ntries, rwt_kill values

### Behaviors and rules
- If func is a subprocess call then include `timeout=` in the subprocess args  TODO
- subprocess.TimeoutExpired is producing an odd exception on Python 3.11.9:  `TypeError: TimeoutExpired.__init__() missing 1 required positional argument: 'timeout'`
- rwt_kill=False with rwt_ntries > 1 will result in that many orphan processes, each attempting to doing the same work.
- rwt_kill=False with rwt_debug=True results in debug level logging active until func (the spawned runner sub-process) terminates - or may be just left with debug logging???  TODO)
"""

    def _runner(q, func, args, kwargs):
        def runner_int_handler(sig, frame):
            logging.debug(f"RH1 - Signal {sig} received {os.getpid()}") #\n {frame}")     # TODO debug
            time.sleep(0.1)                             # allow time for logging
            sys.exit()
        
        signal.signal(signal.SIGTERM, runner_int_handler)      # kill    (15)
        
        os.setpgrp()                # Force to run in separate process group so that kill doesn't also kill the calling process
        logging.debug(f"R1 - Starting  {os.getpid()}")
        try:
            result = func(*args, **kwargs)
            q.put(("result", result))
        except Exception as e:
            q.put(("exception", (e.__class__, str(e), traceback.format_exc())))


    def _worker(worker_to_rwt_q, *args, **kwargs):
        def worker_int_handler(sig, frame):
            logging.debug(f"WH1 - Signal {sig} received  {os.getpid()}") #\n {frame}")     # TODO debug
            if runner_p.is_alive():
                logging.debug (f"WH2 - Sending terminate to runner_p  {os.getpid()}")
                runner_p.terminate()
                runner_p.join(timeout=0.2)

                if runner_p.is_alive():
                    logging.debug (f"WH3 - SIGKILL runner_p  {os.getpid()}")
                    os.kill (runner_p.pid, signal.SIGKILL)
                    time.sleep(0.1)                             # allow time for logging
            logging.debug (f"WH4 - runner_p.is_alive? {runner_p.is_alive()}  {os.getpid()}")
            sys.exit(0)

        signal.signal(signal.SIGTERM, worker_int_handler)      # kill    (15)

        # logging.getLogger().handlers.clear()        # Block root logger in child
        # logging.disable(logging.CRITICAL)
        os.setpgrp()
        logging.debug (f"W1 - starting runner_p  {os.getpid()}")
        runner_to_worker_q = multiprocessing.Queue()
        runner_p = multiprocessing.Process(target=_runner, args=(runner_to_worker_q, func, args, kwargs))
        runner_p.start()

        do_exit = False
        msg = ('result', None)
        while 1:
            # Normal exit when msg received or runner_p is dead (default msg ('result', None))
            # If func does not terminate, then Top_level will send worker_terminate, forcing worker_int_handler
            if not runner_p.is_alive():
                logging.debug (f"W2 - runner_p is DEAD  {os.getpid()}")
                do_exit = True
            try:
                logging.debug (f"W3 - Check for runner_to_worker_q msg  {os.getpid()}")
                msg = runner_to_worker_q.get(timeout=0.2)
                do_exit = True
                logging.debug (f"W4 - runner_to_worker_q msg received  {os.getpid()}")
            except Exception as e:
                # Nothing is in runner_to_worker_q
                logging.debug (f"W5 - NO runner_to_worker_q msg received  {os.getpid()}")

            if do_exit:
                logging.debug (f"W6 - pass up msg, runner_p.join(0.2)  {os.getpid()}")
                worker_to_rwt_q.put(msg)
                runner_p.join(timeout=0.2)

                if runner_p.is_alive():
                    logging.debug (f"W7 - terminating runner_p  {os.getpid()}")
                    runner_p.terminate()
                    runner_p.join(timeout=0.2)
                    if runner_p.is_alive():
                        logging.debug (f"W8 - SIGKILL runner_p  {os.getpid()}")
                        os.kill (runner_p.pid, signal.SIGKILL)
                logging.debug (f"W9 - exiting  {os.getpid()}")
                break                                               # Exit while loop, worker_p exits



    #--------- Top_level ---------
    _timeout = 1                    # Default
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

    _kill = True                    # Default
    if 'rwt_kill' in kwargs:
        _kill = kwargs['rwt_kill']
        del kwargs['rwt_kill']
    if not isinstance(_kill, bool):
        raise ValueError (f"rwt_kill must be type bool, received <{_kill}>")

    if _debug := kwargs.get('rwt_debug', False):
        del kwargs['rwt_debug']
        set_logging_level(logging.DEBUG)
        xx =  f"\nrun_with_timeout switches:\n  rwt_timeout:  {_timeout}\n  rwt_ntries:   {_ntries}\n  rwt_kill:     {_kill}\n  rwt_debug:    {_debug}"
        xx += f"\n  Function:     {func}\n  args:         {args}\n  kwargs:       {kwargs}"
        logging.debug (xx)
    else:
        set_logging_level(logging.INFO)     # Debug level logging in called function is suppressed.  TODO only if level is currently debug ??


    for ntry in range(_ntries):
        if _ntries > 1:
            logging.debug (f"T0 - Try {ntry}")
        worker_to_rwt_q = multiprocessing.Queue()
        worker_p = multiprocessing.Process(target=_worker, args=(worker_to_rwt_q, *args), kwargs=kwargs)
        logging.debug ("T1 - starting worker_p")
        worker_p.start()
        worker_p.join(timeout=_timeout)

        # Normal passing exit
        if not worker_p.is_alive():
            logging.debug ("T2 - worker_p exited without timeout")
            restore_logging_level()
            if not worker_to_rwt_q.empty():
                status, payload = worker_to_rwt_q.get()

                if status == "result":
                    return payload
                elif status == "exception":
                    ex_type, ex_msg, ex_trace = payload     # ex_trace retained for possible future debug/use
                    raise ex_type(f"{ex_msg}")
            else:
                return None

        # Timed out - still running
        if _kill:                           
            logging.debug (f"T3 - worker_p timed out - Killing worker_p")
            worker_p.terminate()
            worker_p.join()
        

    restore_logging_level()
    if _kill:
        raise TimeoutError (f"Function <{func.__name__}> timed out after {_timeout} seconds (killed)")
    else:
        raise TimeoutError (f"Function <{func.__name__}> timed out after {_timeout} seconds (not killed)")
