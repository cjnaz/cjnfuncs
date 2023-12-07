#!/usr/bin/env python3
# ***** configman_ex3.py *****

import time

from cjnfuncs.core      import set_toolname, logging
from cjnfuncs.configman import config_item
import cjnfuncs.core as core

TOOL_NAME =   'configman_ex3'
CONFIG_FILE = 'configman_ex3.cfg'


def service_loop():

    first = True
    while True:
        reloaded = my_config.loadconfig(flush_on_reload=True, tolerate_missing=True)

        if reloaded == -1:              # **** NOTE 2
            logging.warning("Config file not currently accessible.  Skipping reload check for this iteration.")
            
        else:
            if first or reloaded == 1:  # **** NOTE 3
                first = False

                if reloaded:            # **** NOTE 4
                    logging.warning("Config file reloaded.  Refreshing setup.")
                    # Stop any operations, threads, etc that will need to refresh their setups

                logging.warning (my_config)
                # Do resource setups    # **** NOTE 5
        
        # Do normal periodic operations

        time.sleep(0.5)


if __name__ == '__main__':

    set_toolname(TOOL_NAME)
    core.tool.config_dir = '.'

    my_config = config_item(CONFIG_FILE)
    my_config.loadconfig()              # **** NOTE 1

    service_loop()

