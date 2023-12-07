#!/usr/bin/env python3
from cjnfuncs.core      import set_toolname
import cjnfuncs.core as core

set_toolname('core_ex1')
print ("Path to the config dir:", core.tool.config_dir)
print (core.tool)
