#!/usr/bin/env python2
"""linkScrape Arguments."""
import argparse
import getpass
import sys
import time
from argparse import RawTextHelpFormatter

Version = 'v2.1'

timestr = time.strftime("%Y%m%d-%H%M")


class Colors:
    """Terminal color options."""

    white = "\033[1;37m"
    normal = "\033[0;00m"
    red = "\033[1;31m"
    blue = "\033[1;34m"
    green = "\033[1;32m"
    lightblue = "\033[0;34m"

banner = (Colors.lightblue + r"""
 ___                __      ____
/\_ \    __        /\ \    /\  _`\
\//\ \  /\_\    ___\ \ \/'\\ \,\L\_\    ___   _ __    __     _____      __
  \ \ \ \/\ \ /' _ `\ \ , < \/_\__ \   /'___\/\`'__\/'__`\  /\ '__`\  /'__`\
   \_\ \_\ \ \/\ \/\ \ \ \\`\ /\ \L\ \/\ \__/\ \ \//\ \L\.\_\ \ \L\ \/\  __/
   /\____\\ \_\ \_\ \_\ \_\ \_\ `\____\ \____\\ \_\\ \__/.\_\\ \ ,__/\ \____\
   \/____/ \/_/\/_/\/_/\/_/\/_/\/_____/\/____/ \/_/ \/__/\/_/ \ \ \/  \/____/
                                                               \ \_\
                                                                \/_/
""" + 
'\nlinkScrape.py ' + Version + Colors.normal +
'\nDescription: Enumerates employee names from LinkedIn.com ' +
'\nDevelopers: Nick Sanzotta & Jacob Robles.\n' + '*' * 80 + '\n')


def valid_range(pages):
    """..."""
    pages = pages.strip()
    if pages.isdigit():
        # Use this as last page
        return
    elif '-' in pages:
        # May have a range
        pages = pages.split('-')
        if len(pages) != 2:
            print 'Invalid Range'
            sys.exit(1)
        else:
            first, last = pages[0].strip(), pages[1].strip()
            if first.isdigit() and last.isdigit() and int(first) >= 1 and int(first) < int(last):
                # print int(first), int(last), 'Valid'
                pass
            else:
                print 'Invalid Range'
                sys.exit(1)
    else:
        # Invalid range
        print 'Invalid Range'
        sys.exit(1)


def parse_args():
    """Argparse arguments."""
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter, description=banner +
    "Usage: python linkScrape.py <OPTIONS> \n" +
    "Example 1: python linkScrape.py -e LinkedInUser@email.com -c 'example company' -r 1-3 -t 15 -m 10 -d example.com\n" +
    "Example 2: python linkScrape.py -e LinkedInUser@email.com -c 'example company' -r 3 -t 15 -m 10 -d example.com\n" +
    "Example 3: python linkScrape.py -m 7 -i ~/Company/names.txt\n")

    auth_group = parser.add_argument_group(Colors.lightblue + 'Login options' + Colors.normal)
    auth_group.add_argument('-e', '--email', help="Your LinkedIn.com Email Address")
    auth_group.add_argument('-p', '--password', help="Your LinkedIn.com Password.\n" + "If -p is not defined, you'll be prompted")

    search_group = parser.add_argument_group(Colors.lightblue + 'Search options' + Colors.normal)
    search_group.add_argument('-c', '--company', help="Search company name or company ID.")
    search_group.add_argument('-u', '--university', action='count', help="University flag if searching for university. (Default is False)")
    search_group.add_argument('-r', '--range', default='1-3', help="The number/range of page searches.\n" + "(Default is 1-3)")
    search_group.add_argument('-t', '--timeout', type=int, default=3, help="Timeout value. (Default is 3)")
    mangle_help = (
        "1)FirstLast\n"
        "2)LastFirst\n"
        "3)First.Last\n"
        "4)Last.First\n"
        "5)First_Last\n"
        "6)Last_First\n"
        "7)FLast\n"
        "8)LFirst\n"
        "9)FirstL\n"
        "10)F.Last\n"
        "11)L.Firstname\n"
        "12)FirLa\n"
        "13)LastFir\n"
        "14)FLastnam\n"
        "15)LastF\n"
        "16)LasFi\n"
        "99)All\tMangle using all types")

    mangle_group = parser.add_argument_group(Colors.lightblue + 'Mangle options' + Colors.normal)
    mangle_group.add_argument('-m', '--mangle', type=int, choices=list(range(1, 17)) + [99], default=7, help=mangle_help)
    mangle_group.add_argument('-d', '--domain', help='Append @domain.com to enumerater user list')
    mangle_group.add_argument('-i', '--input', help='Use local file to perform name Mangle.')

    args = parser.parse_args()

    # Only ask for user/pass when doing LinkedIn search
    if not args.input:
        if not args.email:
            args.email = raw_input('Enter LinkedIn Email account[user@email.com]:')
            print('ENTERED: {0}\n'.format(args.email))
        if not args.password:
            args.password = getpass.getpass('Enter LinkedIn Password: ')
    while not args.company:
        args.company = raw_input('Enter Company[ex:Example Company]: ').strip()
        print('ENTERED: {0}\n'.format(args.company))
    if not args.domain:
        args.domain = raw_input('Enter Domain suffix[ex:example.com]: ')
        print('ENTERED: {0}\n'.format(args.domain))
    valid_range(args.range)

    return args

if __name__ == "__main__":
    args = parse_args()
    print args
