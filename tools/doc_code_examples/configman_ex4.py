#!/usr/bin/env python3
# ***** configman_ex4.py *****

from cjnfuncs.core      import set_toolname, logging, set_logging_level
from cjnfuncs.configman import persistent_config

set_toolname('configman_ex4')
set_logging_level(logging.INFO, logger_name='cjnfuncs.configman')

persist = persistent_config('persist.cfg', safe_mode=True)      # Load persistent config data

if persist.new:                                                 # If new then initialize user params/values
    persist.setcfg('abc', 5)                                    # Access by setcfg()
    persist.setcfg('counter', 0, section='my_section')

print (f"sections:  {persist.sections()}")

for _ in range(5):
    persist.cfg['my_section']['counter'] += 1                   # Access directly
    xx = persist.getcfg('counter', section='my_section')        # Access by getcfg()
    print (f"counter value:  {xx}")

persist.save()                                                  # Save on exit
