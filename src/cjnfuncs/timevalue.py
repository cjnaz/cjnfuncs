#!/usr/bin/env python3
"""cjnfuncs.timevalue - Shorthand time values and related time management functions
"""

import datetime

#==========================================================
#
#  Chris Nelson, 2018-2025
#
#==========================================================


#=====================================================================================
#=====================================================================================
#  C l a s s   t i m e v a l u e
#=====================================================================================
#=====================================================================================

class timevalue():
    def __init__(self, orig_val):
        """
## Class timevalue (orig_val) - Convert time value strings of various resolutions to seconds

`timevalue()` provides a convenience mechanism for working with time values and time/datetime calculations.
timevalues are generally an integer or float value with an attached single character time resolution, such as "5m".
`timevalue()` also accepts integer and float values, which are interpreted as seconds resolution. Also see retime().


### Args
`orig_val` (str, int, or float)
- The original, passed-in value
- str values support these case insensitive suffix characters: 's'econds, 'm'inutes, 'h'ours, 'd'ays, and 'w'eeks
- int and float values (and str values without suffix characters) have assumed resolution seconds (eg, 7.5 means 7.5 seconds)

### Returns
- Handle to instance
- Raises ValueError if the numeric value cannot be parsed or if given an unsupported time unit suffix.


### Instance attributes
- `.orig_val` - orig_val value passed in, type str (converted to str if int or float passed in)
- `.seconds` - time value in seconds resolution, type float, useful for time calculations
- `.unit_char` - the single character suffix unit of the `orig_val` value.  's' for int and float orig_val values.
- `.unit_str` - the long-form units of the `orig_val` value useful for printing/logging ("secs", "mins", "hours", "days", or "weeks")
        """
        self.orig_val = str(orig_val)

        if type(orig_val) in [int, float]:              # Case int or float
            self.seconds =  float(orig_val)
            self.unit_char = "s"
            self.unit_str =  "secs"
        else:
            try:
                self.seconds = float(orig_val)          # Case str without units
                self.unit_char = "s"
                self.unit_str = "secs"
                return
            except:
                pass
            self.unit_char =  orig_val[-1:].lower()     # Case str with units
            if self.unit_char == "s":
                self.seconds =  float(orig_val[:-1])
                self.unit_str = "secs"
            elif self.unit_char == "m":
                self.seconds =  float(orig_val[:-1]) * 60
                self.unit_str = "mins"
            elif self.unit_char == "h":
                self.seconds =  float(orig_val[:-1]) * 60*60
                self.unit_str = "hours"
            elif self.unit_char == "d":
                self.seconds =  float(orig_val[:-1]) * 60*60*24
                self.unit_str = "days"
            elif self.unit_char == "w":
                self.seconds =  float(orig_val[:-1]) * 60*60*24*7
                self.unit_str = "weeks"
            else:
                raise ValueError(f"Illegal time units <{self.unit_char}> in time string <{orig_val}>")

    def stats(self):
        return self.__repr__()

    def __repr__(self):
        stats = ""
        stats +=  f".orig_val   :  {self.orig_val:8} {type(self.orig_val)}\n"
        stats +=  f".seconds    :  {self.seconds:<8} {type(self.seconds)}\n"
        stats +=  f".unit_char  :  {self.unit_char:8} {type(self.unit_char)}\n"
        stats +=  f".unit_str   :  {self.unit_str:8} {type(self.unit_str)}"
        return stats


#=====================================================================================
#=====================================================================================
#  r e t i m e
#=====================================================================================
#=====================================================================================

def retime(time_sec, unitC):
    """
## retime (time_sec, unitC) - Convert time value in seconds to unitC resolution

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
    """
    unitC = unitC.lower()
    if type(time_sec) in [int, float]:
        if unitC == "s":  return time_sec
        if unitC == "m":  return time_sec /60
        if unitC == "h":  return time_sec /60/60
        if unitC == "d":  return time_sec /60/60/24
        if unitC == "w":  return time_sec /60/60/24/7
        raise ValueError(f"Invalid unitC value <{unitC}> passed to retime()")
    else:
        raise ValueError(f"Invalid seconds value <{time_sec}> passed to retime().  Must be type int or float.")


#=====================================================================================
#=====================================================================================
#   g e t _ n e x t _ d t
#=====================================================================================
#=====================================================================================

str_to_daynum_map = {'monday':1, 'tuesday':2, 'wednesday':3, 'thursday':4, 'friday':5, 'saturday':6, 'sunday':7}

def get_next_dt(times, days=0, usec_resolution=False, test_dt=None):
    """
## get_next_dt (times, days=0, usec_resolution=False, test_dt=None) - Return next scheduled datetime occurrence

Given a list of days of the week and a list of clock times, return the next datetime after now.
The times arg may be a timevalue (eg '20m'), which allows user script code to accept/pass either a clock time or a 
time offset with the same syntax, simplifying the script code.


### Args
`times` (timevalue, or str or list of strs)
- If timevalue (eg, '20m'), then value is taken as a time offset from now, equivalent to `datetime.datetime.now() + timevalue`.
Note that using timevalue offsets may accumulate a time drift.
- If single time (eg, '17:20') or list of str times (eg ['12:13:14', '14:00']), then taken as specific times.
- times format is hour:minute with optional :second (default :00 seconds) using a 24-hour clock and local time zone.
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
    """

    now_dt = datetime.datetime.now()  if test_dt is None  else test_dt


    # ----- Timevalue case -----
    try:
        offset_sec = timevalue(times).seconds
        if not usec_resolution:
            return now_dt.replace(microsecond=0) + datetime.timedelta(seconds=offset_sec)
        else:
            return now_dt + datetime.timedelta(seconds=offset_sec)
    except:
        pass


    # ----- Days/Times lists case -----
    _days_list = days
    if isinstance(_days_list, int)  or  isinstance(_days_list, str):
        _days_list = [_days_list]
    elif not isinstance(_days_list, list):
        raise ValueError (f"Invalid days arg <{days}>")

    if len(_days_list) == 0:
        raise ValueError (f"Invalid days arg <{days}>")

    for n in range(len(_days_list)):                                    # Scrub the days list
        day_value = _days_list[n]
        if isinstance(day_value, int):
            if day_value < 0  or  day_value > 7:
                raise ValueError (f"Invalid day number <{day_value}>")
        elif isinstance(day_value, str):
            try:
                _days_list[n] = str_to_daynum_map[day_value.lower()]
            except:
                raise ValueError (f"Invalid day string <{day_value}>")
        else:
            raise ValueError (f"Invalid days arg <{days}>")

    today_daynum = now_dt.isoweekday()
    _next_dt = now_dt + datetime.timedelta(days=10)                     # start way out there and work back to now_dt

    _times_list = times
    if isinstance(_times_list, str):
        _times_list = [_times_list]

    for daynum in _days_list:
        if daynum > 0:
            offset_num_days = daynum - today_daynum
            if offset_num_days < 0:
                offset_num_days += 7
        else:
            offset_num_days = 0
        plus_day_dt =  now_dt + datetime.timedelta(days=offset_num_days)

        for tme in _times_list:
            try:
                _time = tme.split(':')
                if len(_time) in [2, 3]:
                    target_hour = int(_time[0])
                    target_minute = int(_time[1])
                    if len(_time) == 3:
                        target_second = int(_time[2])
                    else:
                        target_second = 0
                else:
                    raise ValueError (f"Invalid times arg <{tme}>")
            except:
                raise ValueError (f"Invalid times arg <{tme}>")

            with_time_dt = plus_day_dt.replace(hour=target_hour, minute=target_minute, second=target_second, microsecond=0)
            # if not usec_resolution:
            #     with_time_dt = with_time_dt.replace(microsecond=0)
            if with_time_dt <= now_dt:
                if daynum == 0:
                    with_time_dt += datetime.timedelta(days=1)
                else:
                    with_time_dt += datetime.timedelta(days=7)
            if with_time_dt < _next_dt:
                _next_dt = with_time_dt
    return _next_dt
