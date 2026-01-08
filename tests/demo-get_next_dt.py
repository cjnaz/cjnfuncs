#!/usr/bin/env python3
"""Demo/test for get_next_dt()

Produce / compare to golden results:
    ./demo-get_next_dt.py -t 0 | diff demo-get_next_dt-golden.txt -
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
import re

from cjnfuncs.core              import set_toolname, setuplogging, logging #, set_logging_level
from cjnfuncs.timevalue         import get_next_dt

set_toolname(TOOLNAME)
setuplogging()

parser = argparse.ArgumentParser(description=__doc__ + __version__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-t', '--test', default='0',
                    help="Test number to run (default 0).  0 runs all tests")
args = parser.parse_args()


# --------------------------------------------------------------------

def dotest (desc, expect, *args, **kwargs):
    logging.warning (f"\n\n==============================================================================================\n" +
                     f"Test {tnum} - {desc}\n" +
                     f"  Given:      {args}, {kwargs}\n"
                     f"  EXPECT:     {expect}")
    try:
        result = get_next_dt(*args, **kwargs)
        logging.warning (f"\n  RETURNED:   {result}, day # {result.isoweekday()}")
        return result
    except Exception as e:
        logging.error (f"\n  EXCEPTION:  {type(e).__name__}: {e}")
        return e


tnum_parse = re.compile(r"([\d]+)([\w]*)")
def check_tnum(tnum_in, include0='0'):
    global tnum
    tnum = tnum_in
    if args.test == include0  or  args.test == tnum_in:  return True
    try:
        if int(args.test) == int(tnum_parse.match(tnum_in).group(1)):  return True
    except:  pass
    return False

# --------------------------------------------------------------------
# Setups, functions, and vars

days_list = [1, 3, 4, 7]
times_list = ['02:15', '10:25', '18:55']
# test_dt = datetime.datetime.strptime('2023-12-27 10:43:12.123456', '%Y-%m-%d %H:%M:%S.%f')    # A Wednesday (day 3)
test_dt = datetime.datetime(2023, 12, 27, 10, 43, 12, 123456)

#===============================================================================================


if __name__ == '__main__':

    # Test datetime lookups from time/day lists
    if check_tnum('1a'):
        dotest('Find next time within day 3',     '2023-12-27 18:55:00, day # 3',
            times_list, days_list,   test_dt=test_dt)

    if check_tnum('1b'):
        dotest('Find next time within day 3, usec_resolution ignored',  '2023-12-27 18:55:00, day # 3',
            times_list, days_list,   True,   test_dt=test_dt)

    if check_tnum('2'):
        dotest('Find next time within day 4',     '2023-12-28 18:55:00, day # 4',
            times_list, days_list,   test_dt=test_dt + datetime.timedelta(days=1))

    if check_tnum('3'):
        dotest('Find day 7',                      '2023-12-31 02:15:00, day # 7',
            times_list, days_list,   test_dt=test_dt + datetime.timedelta(days=2))

    if check_tnum('4'):
        dotest('Find day 1',                      '2024-01-01 02:15:00, day # 1',
            times_list, [1, 3, 4],   test_dt=test_dt + datetime.timedelta(days=2))

    if check_tnum('5'):
        dotest('Find first time in day 4',        '2023-12-28 02:15:00, day # 4',
            times_list, days_list,   test_dt=test_dt.replace(hour=19))

    if check_tnum('6'):
        dotest('Find first time in day 3',        '2023-12-27 02:15:00, day # 3',
            times_list, 0,           test_dt=test_dt.replace(hour=1))

    if check_tnum('7'):
        dotest('Find second time in day 3',       '2023-12-27 10:25:00, day # 3',
            times_list, 0,           test_dt=test_dt.replace(hour=3))

    if check_tnum('8'):
        dotest('Find third time in day 3',        '2023-12-27 18.55:00, day # 3',
            times_list, 0,           test_dt=test_dt.replace(hour=12))

    if check_tnum('9'):
        dotest('Find first time in day 4',        '2023-12-28 02:15:00, day # 4',
            times_list, 0,           test_dt=test_dt.replace(hour=19))

    if check_tnum('10'):
        dotest('Find first time in day 2',        '2024-01-02 02:15:00, day # 2',
            times_list, 2,           test_dt=test_dt)

    if check_tnum('11'):
        dotest('Single time not in list, with seconds', '2024-01-02 14:59:29, day # 2',
            '14:59:29', 2,           test_dt=test_dt)

    if check_tnum('12'):
        dotest('Single str day',                  '2024-01-02 14:00:00, day # 2',
            '14:00', 'Tuesday',      test_dt=test_dt)

    if check_tnum('13'):
        dotest('Single day list',                 '2024-01-02 14:00:00, day # 2',
            '14:00', ['Tuesday'],    test_dt=test_dt)

    if check_tnum('14'):
        dotest('Multi-day list',                  '2023-12-29 14:00:00, day # 5',
            '14:00', ['sunday', 'Tuesday', 'FrIdaY'],   test_dt=test_dt)

    if check_tnum('15'):
        dotest('Mixed str/int days list',         '2023-12-29 14:00:00, day # 5',
            '14:00', [7, 'Tuesday', 5],   test_dt=test_dt)

    if check_tnum('15a'):
        dotest('Day value = 0',                   '2023-12-27 14:00:00, day # 3',
            '14:00', 0,              test_dt=test_dt)


    # Test time offsets
    if check_tnum('16a'):
        dotest('Time offset',                     '2023-12-28 13:43:12, day # 4',
            '27h',   [],             test_dt=test_dt)

    if check_tnum('16b'):
        dotest('Time offset',                     '2024-01-13 22:43:12, day # 6',
            '2.5w',  [],             test_dt=test_dt)

    if check_tnum('16c'):
        dotest('Time offset',                     '2023-12-27 10:48:12, day # 3',
            '5m', 'Dont care',       test_dt=test_dt)

    if check_tnum('16d'):
        dotest('Time offset with usec res',       '2023-12-27 10:48:12.123456, day # 3',
            '5m', 'Dont care',   usec_resolution=True,    test_dt=test_dt)

    if check_tnum('16e'):
        dotest('Partial sec offset with usec res', '2023-12-27 10:43:13.623456, day # 3',
            '1.5', {'Dont care'},   usec_resolution=True,    test_dt=test_dt)


    # Test errors
    if check_tnum('17a'):
        dotest('Invalid day name',                'ValueError: Invalid day string <TuesdayX>',
            '14:00', ['Sunday', 'TuesdayX', 5], test_dt=test_dt)

    if check_tnum('17b'):
        dotest('Day num out of range',            'ValueError: Invalid day number <8>',
            '14:00',  8,             test_dt=test_dt)

    if check_tnum('17c'):
        dotest('Day num out of range',            'ValueError: Invalid day number <-3>',
            '14:00', -3,             test_dt=test_dt)

    if check_tnum('17d'):
        dotest('Invalid days list (dict order may vary)',  "ValueError: Invalid days arg <{'Tuesday', 5, 7}>",
            '14:00', {7, 'Tuesday', 5}, test_dt=test_dt)

    if check_tnum('17e'):
        dotest('Invalid days list',               "ValueError: Invalid days arg <(7, 'Tuesday', 5)>",
            '14:00', (7, 'Tuesday', 5), test_dt=test_dt)

    if check_tnum('17f'):
        dotest('Empty days_list',                 'ValueError: Invalid days arg <[]>',
            '14:00',     [],        test_dt=test_dt)


    if check_tnum('18a'):
        dotest('Invalid time',                    'ValueError: Invalid times arg <14.10.05>',
            '14.10.05',    0,       test_dt=test_dt)

    if check_tnum('18b'):
        dotest('Invalid time',                    'ValueError: Invalid times arg <xyz>',
            'xyz',         0,       test_dt=test_dt)

    if check_tnum('18c'):
        dotest('Invalid time',                    'ValueError: Invalid times arg <3y>',
            '3y',          0,       test_dt=test_dt)

    if check_tnum('18d'):
        dotest('Invalid time',                    'ValueError: Invalid times arg <13;45>',
            ['12:15', '13;45'], 0,  test_dt=test_dt)


    # days offset tests
    if check_tnum('19a'):
        dotest('Find 8:00 3 days from now',         '2023-12-30 08:00:00, day # 6',
            '8:00', '3d',           test_dt=test_dt)

    if check_tnum('19b'):
        dotest('Find 8:00 3 days from now with times list',  '2023-12-30 08:00:00, day # 6',
            ['23:23', '8:00', '9:45:10'], '3D',  test_dt=test_dt)

    if check_tnum('19c'):
        dotest('Find 8:00 12 days from now',        '2024-01-08 08:00:00, day # 1',
            '8:00', '12d',          test_dt=test_dt)

    if check_tnum('19d'):
        dotest('Find 8:00:23 365 days from now',    '2024-12-26 08:00:23, day # 4',
            '8:00:23', '365d',      test_dt=test_dt)

    if check_tnum('19e'):
        dotest('Find 8:00 0 days from now',         '2023-12-27 08:00:00, day # 3',
            '8:00', '0d',           test_dt=test_dt)

    if check_tnum('19f'):
        dotest('Find 1 week from now',              '2024-01-03 08:00:00, day # 3',
            ['12:34', '08:00'], '1w',  test_dt=test_dt)

    if check_tnum('19g'):
        dotest('Find 0 week from now',              '2023-12-27 08:00:00, day # 3',
            '8:00', '0w',           test_dt=test_dt)

    if check_tnum('19h'):
        dotest('Find 52 week from now',             '2024-12-25 08:00:00, day # 3',
            '8:00', '52w',          test_dt=test_dt)


    # days offset error tests
    if check_tnum('20a'):
        dotest('Invalid days value',                'ValueError: Invalid days arg <-1d>',
            '8:00', '-1d',          test_dt=test_dt)

    if check_tnum('20b'):
        dotest('Invalid days value',                "ValueError: Invalid days arg <1dd>:  invalid literal for int() with base 10: '1d'",
            '8:00', '1dd',          test_dt=test_dt)

    if check_tnum('20c'):
        dotest('Invalid days value',                "ValueError: Invalid days arg <1.1d>:  invalid literal for int() with base 10: '1.1'",
            '8:00', '1.1d',         test_dt=test_dt)

    if check_tnum('20d'):
        dotest('Invalid days value',                "ValueError: Invalid days arg <d>:  invalid literal for int() with base 10: ''",
            '8:00', 'd',            test_dt=test_dt)

    if check_tnum('20e'):
        dotest('Invalid days value',                "ValueError: Invalid days arg <1.1w>:  invalid literal for int() with base 10: '1.1'",
            '8:00', '1.1w',         test_dt=test_dt)


