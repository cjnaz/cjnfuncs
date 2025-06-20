# Working with times

Function | What for?
--|--
`timevalue()` | Enables working with time durations such as '10s' (10 seconds) and '1.5h' (1.5 hours)
`retime()` | Translates a number of seconds into another time unit, such as minutes or hours
`get_next_dt()` | Returns a datetime for a future scheduled time

Skip to [API documentation](#links)


<br/>


## Using `timevalue()` and `retime()`

`timevalue()` is a class for dealing with time values (eg, 5 minutes, 2 weeks, 30 seconds) in a simple form.  timevalues are cleanly used in time/datetime calculations and print statements.  There's no magic here, just convenience and cleaner code.

`retime()` translates an int or float resolution-seconds value into a new target resolution.

Creating a timevalue instance gives ready access to the value in seconds, and useful `unit_chr` and `unit_str` strings for use in printing and logging.

Using timevalues in configuration files is quite convenient.  
- A service loop time param may be expressed as `5m` (5 minutes), rather than `300` (with hard coding for seconds), or `5` (with hard coding for minutes)
- A failed command retry interval param my be expressed a `3s` (3 seconds), rather than `3` (what are the time units again?)

### Example usage

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

## `get_next_dt()` - An event scheduler building block

`get_next_dt()` returns a datetime for a future scheduled time, based on lists of times and days of the week. The produced datetime can be checked in a while loop to see if the current time has reached the target scheduled datetime.  If so, do the scheduled operation and call `get_next_dt()` again to schedule the next occurrence.

It is suggested that the `times` and `days` args get their values from a config file, thus allowing for config-based scheduling of operations within the tool script.

A few examples to highlight `get_next_dt()`'s functionality:

times arg | days arg | Returns datetime
--|--|--
'30s' | don't care | 30 seconds from now
'12:00' | 0 |        Noon today if currently before noon, else noon tomorrow
['9:00', '15:00'] | 3 | If today is Wednesday and it's before 9AM then return datetime for 9AM today, or if after 9AM and before 3PM then return datetime for 3PM today.  Else return datetime for 9AM next Wednesday.
'03:10:15' | [1, 3, 5] | 3:10:15 AM on the next Monday, Wednesday, or Friday
['9:00', '15:00'] | [1, 3, 5] | The next 9AM or 3PM on Monday, Wednesday, or Friday


### Example usage

Given this code:

```
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
```

The output

```
$ ./get_next_dt_ex1.py 
get_next_dt_ex1.<module>             -  WARNING:  First scheduled do_meas   operation: <2025-06-18 15:56:03.805038>
get_next_dt_ex1.<module>             -  WARNING:  First scheduled do_backup operation: <2025-06-18 15:56:30>            # **** NOTE 4
get_next_dt_ex1.<module>             -  WARNING:  Scheduled to quit at:                <2025-06-18 16:00:03>

get_next_dt_ex1.<module>             -  WARNING:  Triggered do_meas   operation at <2025-06-18 15:56:03.805274>, next do_meas   scheduled for <2025-06-18 15:56:33>
get_next_dt_ex1.<module>             -  WARNING:  Triggered do_backup operation at <2025-06-18 15:56:30.809096>, next do_backup scheduled for <2025-06-18 15:56:50>
get_next_dt_ex1.<module>             -  WARNING:  Triggered do_meas   operation at <2025-06-18 15:56:33.810096>, next do_meas   scheduled for <2025-06-18 15:57:03>
get_next_dt_ex1.<module>             -  WARNING:  Triggered do_backup operation at <2025-06-18 15:56:50.812999>, next do_backup scheduled for <2025-06-18 15:57:25>
get_next_dt_ex1.<module>             -  WARNING:  Triggered do_meas   operation at <2025-06-18 15:57:03.815176>, next do_meas   scheduled for <2025-06-18 15:57:33>
get_next_dt_ex1.<module>             -  WARNING:  Triggered do_backup operation at <2025-06-18 15:57:25.818625>, next do_backup scheduled for <2025-06-19 15:56:00>  # **** NOTE 4
get_next_dt_ex1.<module>             -  WARNING:  Triggered do_meas   operation at <2025-06-18 15:57:33.820345>, next do_meas   scheduled for <2025-06-18 15:58:03>
get_next_dt_ex1.<module>             -  WARNING:  Triggered do_meas   operation at <2025-06-18 15:58:03.825035>, next do_meas   scheduled for <2025-06-18 15:58:33>
get_next_dt_ex1.<module>             -  WARNING:  Triggered do_meas   operation at <2025-06-18 15:58:33.829624>, next do_meas   scheduled for <2025-06-18 15:59:03>
get_next_dt_ex1.<module>             -  WARNING:  Triggered do_meas   operation at <2025-06-18 15:59:03.834010>, next do_meas   scheduled for <2025-06-18 15:59:33>
get_next_dt_ex1.<module>             -  WARNING:  Triggered do_meas   operation at <2025-06-18 15:59:33.838820>, next do_meas   scheduled for <2025-06-18 16:00:03>
get_next_dt_ex1.<module>             -  WARNING:  Triggered do_meas   operation at <2025-06-18 16:00:03.843111>, next do_meas   scheduled for <2025-06-18 16:00:33>
get_next_dt_ex1.<module>             -  WARNING:  Triggered quit at <2025-06-18 16:00:03.843111>
```

Notables
 1) A useful application might be to schedule backups of critical files every six hours.  In this example the times_list has been compressed for demo purposes.  `days_list = 0` means every day.
 2) `datetime.datetime.now()` returns microsecond resolution, while `get_next_dt()` returns 1 second resolution.
 3) get_next_dt() accepts either `times, days` lists or a timevalue offset/interval, eg `'4m'` (the days arg is ignored).
 4) The start time for this example code run was after the first time in the times_list, so the first scheduled do_backup time was at the _second time_ in the times_list. Once the times_list is 
 worked through for today, the next do_backup operation is scheduled for the first time (15:56) the next day.


<a id="links"></a>
         
<br>

---

# Links to classes, methods, and functions

- [timevalue](#timevalue)
- [retime](#retime)
- [get_next_dt](#get_next_dt)



<br/>

<a id="timevalue"></a>

---

# Class timevalue (orig_val) - Convert time value strings of various resolutions to seconds

`timevalue()` provides a convenience mechanism for working with time values and time/datetime calculations.
timevalues are generally an integer value with an attached single character time resolution, such as "5m".
Supported timevalue units are 's'econds, 'm'inutes, 'h'ours, 'd'ays, and 'w'eeks, and are case insensitive. 
`timevalue()` also accepts integer and float values, which are interpreted as seconds resolution. Also see retime().


### Args
`orig_val` (str, int, or float)
- The original, passed-in value


### Returns
- Handle to instance
- Raises ValueError if given an unsupported time unit suffix.


### Instance attributes
- `.orig_val` - orig_val value passed in, type str (converted to str if int or float passed in)
- `.seconds` - time value in seconds resolution, type float, useful for time calculations
- `.unit_char` - the single character suffix unit of the `orig_val` value.  's' for int and float orig_val values.
- `.unit_str` - the long-form units of the `orig_val` value useful for printing/logging ("secs", "mins", "hours", "days", or "weeks")
        
<br/>

<a id="retime"></a>

---

# retime (time_sec, unitC) - Convert time value in seconds to unitC resolution

`retime()` translates a value is resolution seconds into a new target resolution


### Args
`time_sec` (int or float)
- The time value in resolution seconds to be converted

`unitC` (str)
- Target time resolution: "s", "m", "h", "d", or "w" (case insensitive)


### Returns
- `time_sec` value scaled for the specified `unitC`, type float
- Raises ValueError if not given an int or float value for `time_sec`, or given an unsupported 
  unitC time unit suffix.
    
<br/>

<a id="get_next_dt"></a>

---

# get_next_dt (times, days=0, usec_resolution=False, test_dt=None) - Return next scheduled datetime occurrence

Given a list of days of the week and a list of clock times, return the next datetime after now.
The times arg may be a timevalue (eg '20m'), which allows user script code to accept/pass either a clock time or a 
time offset with the same syntax, simplifying the script code.


### Args
`times` (timevalue, or str or list of strs)
- If timevalue (eg, '20m'), then value is taken as a time offset from now, equivalent to `datetime.datetime.now() + timevalue`.
Note that using timevalue offsets may accumulate a time drift.
- If single time (eg, '17:20') or list of str times (eg ['12:13:14', '14:00']), then taken as specific times.
- times format is hour:minute with optional :second (default :00 seconds) using a 24-hour clock.
- Note: A typo on a time replacing a ':' with '.' will be interpreted as a valid decimal number of seconds of a timevalue.

`days` (int/str or list of int/str, default 0)
- Single day or list of days.  Day numbers or string names accepted.
- Day numbers:  1 = Monday, 7 = Sunday (`isoweekday()` numbering)
- Day names accepted, case insensitive, eg 'MonDay'
- `days = 0` means every day, equiv [1,2,3,4,5,6,7]

`usec_resolution` (bool, default False)
- If True, timevalue offsets retain sub-second resolution
- If False, timevalue offsets are rounded to 1-second resolution
- When working with `times, days` values/lists the returned values are alway 1-second resolution

`test_dt` (datetime, default None)
- overrides datetime.datetime.now() for testing purposes


### Returns 
- datetime of next day/time match, or now+timevalue
- Raises ValueError with invalid input args
    