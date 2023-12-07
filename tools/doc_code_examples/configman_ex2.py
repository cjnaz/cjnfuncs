#!/usr/bin/env python3
# ***** configman_ex2.py *****

from cjnfuncs.core      import set_toolname
from cjnfuncs.configman import config_item
import cjnfuncs.core as core

set_toolname('configman_ex2')
core.tool.config_dir = '.'                              # **** NOTE 6

my_config = config_item('configman_ex2.cfg')            # **** NOTE 1
my_config.loadconfig()                                  # **** NOTE 1

print (my_config)
print (my_config.dump())
print ()
print (f"Sections list: {my_config.sections()}")        # **** NOTE 7

print ()
print (f"a_float:       {my_config.getcfg('a_float', types=[int, float])}") # **** NOTE 10
print (f"a_list:        {my_config.getcfg('a_list', types=list)}")
print (f"my_def_param:  {my_config.getcfg('my_def_param')}")
print (f"EmailUser:     {my_config.getcfg('EmailUser', section='SMTP')}")
# **** NOTE 8
print (f"not_defined:   {my_config.getcfg('not_defined', fallback='Using fallback value')}")

r = my_config.getcfg('a_list')[2]['abc']
print (f"Given radius {r}, the circle's area is {my_config.getcfg('a_dict')['pi'] * r ** 2}")

print (f"a_float:       {my_config.cfg['a_float']}")    # **** NOTE 9
print (f"bad_float:     {my_config.cfg['Bad params']['bad_float']}")
