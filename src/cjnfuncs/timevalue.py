#!/usr/bin/env python3
"""cjnfuncs.timevalue - Shorthand time values
"""

#==========================================================
#
#  Chris Nelson, 2018-2024
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
timevalues are generally an integer value with an attached single character time resolution, such as "5m".
Supported timevalue units are 's'econds, 'm'inutes, 'h'ours, 'd'ays, and 'w'eeks, and are case insensitive. 
`timevalue()` also accepts integer and float values, which are interpreted as seconds resolution. Also see retime().


### Parameters
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


### Parameters
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
