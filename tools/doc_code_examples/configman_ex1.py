#!/usr/bin/env python3
# ***** configman_ex1.py *****

from cjnfuncs.core      import set_toolname
from cjnfuncs.configman import config_item
import cjnfuncs.core as core

set_toolname('configman_ex1')
core.tool.config_dir = '.'          # See Note below

my_config = config_item('configman_ex1.cfg')
my_config.loadconfig()

print (f"My name is {my_config.getcfg('My_name_is')}")
my_dog = my_config.getcfg('The_Dog')
dogs_age = my_config.getcfg("Dog's_age")
print (f"My dog's name is {my_dog}.  He is {dogs_age} years old.")
print (f"The_Dog {type(my_dog)}, Dogs_age {type(dogs_age)}")