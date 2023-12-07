# timevalue() and retime() - Cleanly translate time values with units to seconds and other units

Skip to [API documentation](#links)


`timevalue()` is a class for dealing with time values (eg, 5 minutes, 2 weeks, 30 seconds) in a simple form.  timevalues are cleanly used in time/datetime calculations and print statements.  There's no magic here, just convenience and cleaner code.

`retime()` translates an int or float resolution-seconds value into a new target resolution.

Creating a timevalue instance gives ready access to the value in seconds, and useful `unit_chr` and `unit_str` strings for use in printing and logging.

Using timevalues in configuration files is quite convenient.  
- A service loop time param may be expressed as `5m` (5 minutes), rather than `300` (hard coded for seconds), or `5` (hard coded for minutes)
- A failed command retry interval param my be expressed a `3s` (3 seconds), rather than `3` (what are the time units again?)

## Example usage

Given
```
#!/usr/bin/env python3
# ***** timevalue_ex1.py *****

import time
from cjnfuncs.timevalue import timevalue, retime

xx = timevalue('0.5m')
print (xx)
print (f"Sleep <{xx.seconds}> seconds")
time.sleep(xx.seconds)

print()
yy = timevalue("1w")
print (f"{yy.orig_val} = {yy.seconds} seconds = {retime(yy.seconds, 'h')} hours")
```

Output:
```
$ ./timevalue_ex1.py 
.orig_val   :  0.5m     <class 'str'>
.seconds    :  30.0     <class 'float'>
.unit_char  :  m        <class 'str'>
.unit_str   :  mins     <class 'str'>
Sleep <30.0> seconds

1w = 604800.0 seconds = 168.0 hours
```

`timevalue()` accepts int and float values, with assumed seconds resolution, and accepts int and float values with a case insensitive time unit suffix character:


unit_char suffix | unit_str
--|--
s | secs
m | mins
h | hours
d | days
w | weeks

<br>

