#!/usr/bin/env python3
# ***** get_next_dt_ex1.py *****

import datetime
import shutil
import time

from cjnfuncs.core          import set_toolname, setuplogging, logging
from cjnfuncs.timevalue     import get_next_dt

set_toolname('get_next_dt_ex1')
setuplogging()


meas_interval = '30s'
# times_list =    ['06:00', '12:00', '18:00', '00:00']                      # **** NOTE 1
# days_list =     ['Monday', 'Wednesday', 'Friday']

times_list =    ['15:56', '15:56:30', '15:56:50', '15:57:25']
days_list =     0


do_meas_dt =    datetime.datetime.now()
logging.warning (f"First scheduled do_meas   operation: <{do_meas_dt}>")    # **** NOTE 2
do_backup_dt =  get_next_dt(times_list, days_list)
logging.warning (f"First scheduled do_backup operation: <{do_backup_dt}>")
quit_dt =       get_next_dt('4m')                                           # **** NOTE 3
logging.warning (f"Scheduled to quit at:                <{quit_dt}>\n")

while True:
    now_dt = datetime.datetime.now()

    if now_dt > do_meas_dt:
        # take measurements and log to the trace file
        do_meas_dt = get_next_dt(meas_interval)
        logging.warning (f"Triggered do_meas   operation at <{now_dt}>, next do_meas   scheduled for <{do_meas_dt}>")


    if now_dt > do_backup_dt:
        # shutil.copy ('mytrace.csv', '~/.local/mytool/share')
        do_backup_dt = get_next_dt(times_list, days_list)
        logging.warning (f"Triggered do_backup operation at <{now_dt}>, next do_backup scheduled for <{do_backup_dt}>")

    # Do other stuff in the main loop, as needed...

    if now_dt > quit_dt:
        logging.warning (f"Triggered quit at <{now_dt}>")
        break

    time.sleep (1)