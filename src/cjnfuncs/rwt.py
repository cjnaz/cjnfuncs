#==========================================================
#
#  Chris Nelson, 2025-
#
#==========================================================


from .core import logging
import cjnfuncs.core as core

import signal
import time
import os
import sys
import multiprocessing
import subprocess
import traceback

logging.getLogger('rwt').setLevel(logging.WARNING)

def run_with_timeout(func, *args, **kwargs):
    pass
    """
## run_with_timeout (func, *args, **kwargs, rwt_timeout=1.0, rwt_ntries=1, rwt_kill=True) - Run a function in a separate process with an enforced timeout.

`run_with_timeout` uses the multiprocessing module, and works by running the specified `func` in a managed 
external process that can be reliably killed on timeout.
For a non-timeout run, `run_with_timeout` returns what the `func` returns or any exception raised. 
On timeout, the process is killed (by default) and a TimeoutError exception is raised.


### Args

`func` (callable)
- The function to run
- May be any function - built-in, standard library, supplied by an installed package, or user-written
- On Windows `func` must be defined as a top level function of the module

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


### Returns
- With no timeout or exception, returns the value returned from `func`
- Any exception raised by `func`
- If rwt_timeout is exceeded, returns TimeoutError
- Exceptions raised for invalid rwt_timeout, rwt_ntries, or rwt_kill values


### Behaviors and rules
- Logging within the called `func` is done at the logging level in effect when run_with_timeout is called. 
`logging.getLogger('rwt').setLevel(logging.DEBUG)` enables additional status and trace info, intended for debug and regression testing.
- If making a subprocess call and the subprocess timeout limit is triggered, a
subprocess.TimeoutExpired exception is produce with an odd error message on Python 3.11.9: 
`TypeError: TimeoutExpired.__init__() missing 1 required positional argument: 'timeout'`. Generally, don't use
the subprocess timeout arg when using run_with_timeout.
- If `rwt_kill=False` then the forked/spawned process will not be killed, and if the process doesn't exit by itself 
then the tool script will hang on exit, waiting for the orphan process to terminate.
To solve this the tool script needs to kill any orphaned processes created by run_with_timeout before exiting. 
The pids of the orphaned processes are listed in the TimeoutError exception when `rwt_kill=False`, and can
be captured for explicitly killing of any unterminated orphaned processes before exiting the tool script, eg: 
`os.kill (pid, signal.OSKILL)`.  See `rwt.md` for a working example.
Note that if `rwt_ntries` is greater than 1 and `rwt_kill=False`, then potentially several processes may 
be created and orphaned, all attempting to doing the same work.
- On Windows, debug logging messages from the run_with_timeout internal `worker()` function (which calls `func`) are 
erratically produced, and not produced if `func` raises an exception.  Logging from within `func`, and any raised exception
operate normally.  On Linux, worker debug operates correctly.
"""

    #--------- Top_level ---------
def run_with_timeout(func, *args, **kwargs):

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

    # _debug = False
    # if 'rwt_debug' in kwargs:
    #     del kwargs['rwt_debug']
        # _debug = kwargs['rwt_debug']
        # if not isinstance(_debug, bool):
        #     raise ValueError (f"rwt_debug must be type bool, received <{_debug}>")


    rwt_logger=logging.getLogger('rwt')
    # rwt_loglevel = rwt_logger.level
    xx =  f"\nrun_with_timeout switches:\n  rwt_timeout:  {_timeout}\n  rwt_ntries:   {_ntries}\n  rwt_kill:     {_kill}"
    xx += f"\n  Function:     {func}\n  args:         {args}\n  kwargs:       {kwargs}"
    rwt_logger.debug (xx)


    # if kwargs.get('rwt_debug', False):
    #     rwt_logger.setLevel(logging.DEBUG)
    #     _kwargs = kwargs.copy()
    #     del _kwargs['rwt_debug']
    #     xx =  f"\nrun_with_timeout switches:\n  rwt_timeout:  {_timeout}\n  rwt_ntries:   {_ntries}\n  rwt_kill:     {_kill}\n  rwt_debug:    {_debug}"
    #     xx += f"\n  Function:     {func}\n  args:         {args}\n  kwargs:       {_kwargs}"
    #     rwt_logger.debug (xx)
    # else:
    #     rwt_logger.setLevel(logging.WARNING)

    # kwargs['rwt_logger_q'] = core.logger_q
    kwargs['rwt_loglevel'] = rwt_logger.level
    kwargs['root_loglevel'] = logging.getLogger().level


    for ntry in range(_ntries):

        if _ntries > 1:
            rwt_logger.debug (f"T0  - Try {ntry}")

        # Run it
        rwt_logger.debug (f"T1  - Starting worker_p")
        # worker_to_toplevel_q = multiprocessing.Queue()
        # worker_to_toplevel_q = multiprocessing.SimpleQueue()
        worker_to_toplevel_q = multiprocessing.get_context().Queue()
        worker_p = multiprocessing.Process(target=worker, args=(worker_to_toplevel_q, func, args, kwargs), daemon=False, name=f'rwt_{func}')
        worker_p.start()
        worker_p.join(timeout=_timeout)
        status=None

        # Kill it if it did not exit normally
        if worker_p.is_alive():
            if _kill:                                       # worker_p is alive.  Kill it.
                rwt_logger.debug (f"T4  - terminate worker_p")
                worker_p.terminate()
                worker_p.join(timeout=1) #0.2)
                # for h in rwt_logger.handlers:
                #     h.flush()
                # time.sleep(2)
                if worker_p.is_alive():
                    try:
                        if sys.platform.startswith("win"):
                            rwt_logger.debug (f"T5  - taskkill worker_p pid {worker_p.pid}")
                            subprocess.run(["taskkill", "/PID", str(worker_p.pid), "/F"])
                        else:   # Linux
                            rwt_logger.debug (f"T5  - SIGKILL worker_p pid {worker_p.pid}")
                            os.kill(worker_p.pid, signal.SIGKILL)
                    except Exception as e:
                        if 'No such process' in str(e):     # Corner case of worker_p either ended normally, or the terminate finally happened
                            pass
                        else:
                            if ntry == _ntries-1:
                                # restore_logging_level()     # Restore External logging level before exit
                                raise
                if ntry == _ntries-1:
                    # restore_logging_level()
                    raise TimeoutError (f"Function <{func.__name__}> timed out after {_timeout} seconds (killed)")
            else:                                           # worker_p is alive, and DON'T kill it
                pid_list.append(str(worker_p.pid))
                # rwt_logger.debug (f"worker pid list <{pid_list}>")
                if ntry == _ntries-1:
                    # restore_logging_level()
                    raise TimeoutError (f"Function <{func.__name__}> timed out after {_timeout} seconds (not killed) orphaned pids: {' '.join(pid_list)}")
        else:
            rwt_logger.debug (f"T2  - worker_p exited before rwt_timeout")

            # Get returned result or exception
            try:
                status, payload = worker_to_toplevel_q.get(timeout=0.05)
            except Exception as e:
                rwt_logger.debug (f"T7  - Nothing returned from runner")
                status = None

        if status:
            # print (f"got item status <{status}>")
            rwt_logger.debug (f"T3  - <{status}> msg received from worker_p")
            if status == "result":
                # restore_logging_level()
                return payload
            elif status == "exception":
                if ntry == _ntries-1:
                    # restore_logging_level()
                    ex_type, ex_msg, ex_trace = payload     # ex_trace retained for possible future debug/use
                    raise ex_type(f"{ex_msg}")
        # except Exception as e:
        #     pass
            # rwt_logger.debug(f"T6  - No returned result in queue:\n  {e}")
            # raise

        # if not worker_to_toplevel_q.empty():                # On exit, worker_p returns either status='result' or ='exception'
        #     print ("item in the queue")
        #     status, payload = worker_to_toplevel_q.get()
        #     print (f"got item status <{status}>")
        #     rwt_logger.debug (f"T3  - <{status}> msg received from worker_p")
        #     if status == "result":
        #         # restore_logging_level()
        #         return payload
        #     elif status == "exception":
        #         if ntry == _ntries-1:
        #             # restore_logging_level()
        #             ex_type, ex_msg, ex_trace = payload     # ex_trace retained for possible future debug/use
        #             raise ex_type(f"{ex_msg}")


def worker(result_q, func, args, kwargs):
    # from logging.handlers import QueueHandler

    def worker_int_handler(sig, frame):
        rwt_logger.debug(f"WH1 - Signal {sig} received")
        # for h in rwt_logger.handlers:
        #     h.flush()
        time.sleep(0.01)                            # allow time for logging before terminating
        sys.exit()
    signal.signal(signal.SIGTERM, worker_int_handler)   # kill (15)

    # Set up root logger and rwt_logger
    # logger_q = kwargs['rwt_logger_q']
    # del kwargs['rwt_logger_q']
    logging.getLogger().setLevel(kwargs['root_loglevel'])
    del kwargs['root_loglevel']
    # root_logger.handlers.clear()  
    # root_logger.addHandler(QueueHandler(logger_q))
    # root_logger.setLevel(logging.DEBUG)

    rwt_logger = logging.getLogger('rwt')
    rwt_logger.setLevel(kwargs['rwt_loglevel'])
    del kwargs['rwt_loglevel']
    # if kwargs.get('rwt_debug', False):
    #     rwt_logger.setLevel(logging.DEBUG)
    # else:
    #     rwt_logger.setLevel(logging.WARNING)
    # if 'rwt_debug' in kwargs:
    #     del kwargs['rwt_debug']

    # Run it
    rwt_logger.debug(f"W1  - worker_p pid {os.getpid()}")
    # for h in rwt_logger.handlers:
    #     h.flush()
    # rwt_logger.debug(f"W1a")

    try:
        # result = print ("Hello")
        result = func(*args, **kwargs)
        # rwt_logger.debug(f"W2")
        result_q.put(("result", result))
    except Exception as e:
        result_q.put(("exception", (e.__class__, str(e), traceback.format_exc())))

    # try:
    #     time.sleep(0.05)
    #     result_q.close()
    #     result_q.join_thread()
    #     time.sleep(0.05)
    # except Exception as e:
    #     rwt_logger.debug(f"exception: {e.__class__} {str(e)} {traceback.format_exc()}")

# def _runner(q, func, args, kwargs):
#     from logging.handlers import QueueHandler

#     def runner_int_handler(sig, frame):
#         rwt_logger.debug(f"RH1 - Signal {sig} received")
#         time.sleep(0.01)                            # allow time for logging before terminating
#         # if _debug:
#         #     set_logging_level(logging.DEBUG)
#         #     logging.debug(f"RH1 - Signal {sig} received")
#         #     time.sleep(0.01)                            # allow time for logging before terminating
#         sys.exit()
    
#     signal.signal(signal.SIGTERM, runner_int_handler)   # kill (15)

#     logger_q = kwargs['rwt_logger_q']
#     del kwargs['rwt_logger_q']
#     root_logger = logging.getLogger()
#     root_logger.handlers.clear()
#     root_logger.addHandler(QueueHandler(logger_q))
#     root_logger.setLevel(logging.DEBUG)

#     # setuplogging()
#     # _debug = False
#     # rwt_logger = logging.getLogger('rwt')
#     # if 'rwt_debug' in kwargs:
#     #     _debug = kwargs['rwt_debug']
#     #     del kwargs['rwt_debug']
#     # if _debug:
#     #     rwt_logger.setLevel(logging.DEBUG)
#     # else:
#     #     rwt_logger.setLevel(logging.WARNING)
#     #     set_logging_level(10, save=False)    
#     rwt_logger = logging.getLogger('rwt')
#     if kwargs.get('rwt_debug', False):
#     # if 'rwt_debug' in kwargs:
#         del kwargs['rwt_debug']
#         rwt_logger.setLevel(logging.DEBUG)
#     else:
#         rwt_logger.setLevel(logging.WARNING)

#     rwt_logger.debug(f"R1  - runner_p pid {os.getpid()}")
#     rwt_logger.debug(f"R1a")

#     try:
#         # print (get_logging_level_stack())
#         # restore_logging_level()                         # External logging level restored for running target function
#                                                         # The stack pop is meaningless since running with a copy of the stack in a separate process
#         # result = func(*args, **kwargs)
#         result = print ("Hello")
#         time.sleep (0.1)
#         rwt_logger.debug(f"R2")
#         q.put(("result", result))
#     except Exception as e:
#         q.put(("exception", (e.__class__, str(e), traceback.format_exc())))

#     time.sleep(0.2)
