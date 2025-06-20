#!/usr/bin/env python3
"""Demo/test for cjnfuncs.timevalue get_next_dt()

Produce / compare to golden results:
    ./demo_get_next_dt.py -t 0 | diff demo_get_next_dt-golden.txt -
        Or use bcompare
        Differences will be order of days dictionary in test # 17d
"""

#==========================================================
#
#  Chris Nelson, 2025
#
#==========================================================

__version__ =   '2.0'
TOOLNAME =      'demo-get_next_dt'

import argparse
import datetime

from cjnfuncs.core              import set_toolname, setuplogging, logging #, set_logging_level
from cjnfuncs.timevalue         import get_next_dt

set_toolname(TOOLNAME)
setuplogging()

parser = argparse.ArgumentParser(description=__doc__ + __version__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-t', '--test', default='0',
                    help="Test number to run (default 0).  0 runs all tests")
args = parser.parse_args()


# --------------------------------------------------------------------

def dotest (testnum, desc, expect, *args, **kwargs):
    logging.warning (f"\n\n==============================================================================================\n" +
                     f"Test {testnum} - {desc}\n" +
                     f"  Given:      {args}, {kwargs}\n"
                     f"  EXPECT:     {expect}")
    try:
        result = get_next_dt(*args, **kwargs)
        logging.warning (f"\n  RETURNED:   {result}, day # {result.isoweekday()}")
        return result
    except Exception as e:
        logging.error (f"\n  EXCEPTION:  {type(e).__name__}: {e}")
        return e


# --------------------------------------------------------------------
# Setups, functions, and vars

days_list = [1, 3, 4, 7]
times_list = ['02:15', '10:25', '18:55']
# test_dt = datetime.datetime.strptime('2023-12-27 10:43:12.123456', '%Y-%m-%d %H:%M:%S.%f')    # A Wednesday (day 3)
test_dt = datetime.datetime(2023, 12, 27, 10, 43, 12, 123456)

#===============================================================================================


# Test datetime lookups from time/day lists
tnum = '1'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Find next time within day 3',     '2023-12-27 18:55:00, day # 3',
           times_list, days_list,   test_dt=test_dt)

tnum = '1a'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Find next time within day 3, usec_resolution ignored',  '2023-12-27 18:55:00, day # 3',
           times_list, days_list,   True,   test_dt=test_dt)

tnum = '2'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Find next time within day 4',     '2023-12-28 18:55:00, day # 4',
           times_list, days_list,   test_dt=test_dt + datetime.timedelta(days=1))

tnum = '3'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Find day 7',                      '2023-12-31 02:15:00, day # 7',
           times_list, days_list,   test_dt=test_dt + datetime.timedelta(days=2))

tnum = '4'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Find day 1',                      '2024-01-01 02:15:00, day # 1',
           times_list, [1, 3, 4],   test_dt=test_dt + datetime.timedelta(days=2))

tnum = '5'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Find first time in day 4',        '2023-12-28 02:15:00, day # 4',
           times_list, days_list,   test_dt=test_dt.replace(hour=19))

tnum = '6'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Find first time in day 3',        '2023-12-27 02:15:00, day # 3',
           times_list, 0,           test_dt=test_dt.replace(hour=1))

tnum = '7'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Find second time in day 3',       '2023-12-27 10:25:00, day # 3',
           times_list, 0,           test_dt=test_dt.replace(hour=3))

tnum = '8'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Find third time in day 3',        '2023-12-27 18.55:00, day # 3',
           times_list, 0,           test_dt=test_dt.replace(hour=12))

tnum = '9'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Find first time in day 4',        '2023-12-28 02:15:00, day # 4',
           times_list, 0,           test_dt=test_dt.replace(hour=19))

tnum = '10'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Find first time in day 2',        '2024-01-02 02:15:00, day # 2',
           times_list, 2,           test_dt=test_dt)

tnum = '11'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Single time not in list, with seconds', '2024-01-02 14:59:29, day # 2',
           '14:59:29', 2,           test_dt=test_dt)

tnum = '12'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Single str day',                  '2024-01-02 14:00:00, day # 2',
           '14:00', 'Tuesday',      test_dt=test_dt)

tnum = '13'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Single day list',                 '2024-01-02 14:00:00, day # 2',
           '14:00', ['Tuesday'],    test_dt=test_dt)

tnum = '14'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Multi-day list',                  '2023-12-29 14:00:00, day # 5',
           '14:00', ['sunday', 'Tuesday', 'FrIdaY'],   test_dt=test_dt)

tnum = '15'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Mixed str/int days list',         '2023-12-29 14:00:00, day # 5',
           '14:00', [7, 'Tuesday', 5],   test_dt=test_dt)

tnum = '15a'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Day value = 0',                   '2023-12-27 14:00:00, day # 3',
           '14:00', 0,              test_dt=test_dt)


# Test time offsets
tnum = '16a'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Time offset',                     '2023-12-28 13:43:12, day # 4',
           '27h',   [],             test_dt=test_dt)

tnum = '16b'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Time offset',                     '2024-01-13 22:43:12, day # 6',
           '2.5w',  [],             test_dt=test_dt)

tnum = '16c'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Time offset',                     '2023-12-27 10:48:12, day # 3',
           '5m', 'Dont care',       test_dt=test_dt)

tnum = '16d'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Time offset with usec res',       '2023-12-27 10:48:12.123456, day # 3',
           '5m', 'Dont care',   usec_resolution=True,    test_dt=test_dt)

tnum = '16e'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Partial sec offset with usec res', '2023-12-27 10:43:13.623456, day # 3',
           '1.5', {'Dont care'},   usec_resolution=True,    test_dt=test_dt)


# Test errors
tnum = '17a'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Invalid day name',                'ValueError: Invalid day string <TuesdayX>',
           '14:00', ['Sunday', 'TuesdayX', 5], test_dt=test_dt)

tnum = '17b'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Day num out of range',            'ValueError: Invalid day number <8>',
           '14:00',  8,             test_dt=test_dt)

tnum = '17c'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Day num out of range',            'ValueError: Invalid day number <-3>',
           '14:00', -3,             test_dt=test_dt)

tnum = '17d'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Invalid days list (dict order may vary)',  "ValueError: Invalid days arg <{'Tuesday', 5, 7}>",
           '14:00', {7, 'Tuesday', 5}, test_dt=test_dt)

tnum = '17e'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Invalid days list',               "ValueError: Invalid days arg <(7, 'Tuesday', 5)>",
           '14:00', (7, 'Tuesday', 5), test_dt=test_dt)

tnum = '17f'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Empty days_list',                 'ValueError: Invalid days arg <[]>',
           '14:00',     [],         test_dt=test_dt)


tnum = '18a'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Invalid time',                    'ValueError: Invalid times arg <14.10.05>',
           '14.10.05',    0,        test_dt=test_dt)

tnum = '18b'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Invalid time',                    'ValueError: Invalid times arg <xyz>',
           'xyz',         0,        test_dt=test_dt)

tnum = '18c'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Invalid time',                    'ValueError: Invalid times arg <3y>',
           '3y',          0,        test_dt=test_dt)

tnum = '18d'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, 'Invalid time',                    'ValueError: Invalid times arg <13;45>',
           ['12:15', '13;45'], 0,   test_dt=test_dt)
