#!/usr/bin/env python3

"""Find all MOD-RGB device addresses.

Usage:
  find-mod-rgb [--device=<dev-num>] [--reserved=<spec>]
  find-mod-rgb -h | --help

Options:
  --device=<dev-num>  Device number [default: 1].
  --reserved=<spec>   Check addresses reserved according to either the 'I2C' or 'SMBus' specifications.
"""

import os
import sys

from docopt import docopt, DocoptExit
from smbus import SMBus

from mod_rgb.control import find_devices

def main(args=None):
    if args is None:
        args = docopt(__doc__, version='Find MOD-RGB addresses 1.0')

    try:
        device_num = int(args['--device'], base=0)
    except ValueError:
        print("Device number must be an integer", file=sys.stderr)
        print(DocoptExit.usage, file=sys.stderr)
        return os.EX_USAGE


    if args['--reserved'] is not None:
        reserved = args['--reserved'].lower()
        if reserved not in ('i2c', 'smbus'):
            print("Reserved address <spec> {!r} is neither 'I2C' nor 'SMBus'".format(args['--reserved']), file=sys.stderr)
            print(DocoptExit.usage, file=sys.stderr)
            return os.EX_USAGE
        check_i2c_reserved = reserved == 'i2c'
        check_smbus_reserved = reserved == 'smbus'
    else:
        check_i2c_reserved = False
        check_smbus_reserved = False
        
    try:
        bus = SMBus(device_num)
    except OverflowError as e:
        print("Could not attach to I2C/SMBus. Device number {!r} is invalid".format(device_num), file=sys.stderr)
        return os.EX_DATAERR
    except IOError as e:
        print("Could not attach to I2C/SMBus. I/O error:", e, file=sys.stderr)
        return os.EX_IOERR        

    try:
        for address in find_devices(bus, check_i2c_reserved, check_smbus_reserved):
            print(hex(address))
    except IOError as e:
        print("I/O error:", e, file=sys.stderr)
        return os.EX_IOERR

    return os.EX_OK

if __name__ == '__main__':
    sys.exit(main())
