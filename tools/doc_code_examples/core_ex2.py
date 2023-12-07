#!/usr/bin/env python3
from cjnfuncs.core      import set_toolname, setuplogging, logging
import cjnfuncs.core as core

set_toolname('core_ex2')

setuplogging()
logging.warning(f"This is a warning-level log message to the console.\n{core.tool}")

setuplogging(call_logfile='mylogfile.txt', call_logfile_wins=True)
logging.warning(f"This is a warning-level log message to the log file <{core.tool.log_full_path}>.\n{core.tool}")
