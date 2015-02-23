#!/usr/bin/env python3

"""Set MOD-RGB output colour.

Usage:
  set_rgb.py <address> <red> <green> <blue> [--device=<dev-num>]
  set_rgb.py -h | --help

Options:
  --device=<dev-num>  Device number [default: 1].
  -h --help           Show this screen.
"""

import os
import sys

from docopt import docopt, DocoptExit
from smbus import SMBus

from mod_rgb.control import ensure_mod_rgb_device, start_pwm, set_rgb_color 

def main(args=None):
    if args is None:
        args = docopt(__doc__, version='Set MOD-RGB output color 1.0')

    try:   
        address = int(args['<address>'], base=0)
    except ValueError:
        print("Address must be an integer", file=sys.stderr)
        print(DocoptExit.usage, file=sys.stderr)
        return os.EX_USAGE
 
    try:   
        red = int(args['<red>'], base=0)
        green = int(args['<green>'], base=0)
        blue = int(args['<blue>'], base=0)
    except ValueError:
        print("Color channel values must integers", file=sys.stderr)
        print(DocoptExit.usage, file=sys.stderr)
        return os.EX_USAGE
 
    try:
        device_num = int(args['--device'], base=0)
    except ValueError:
        print("Device number must be an integer", file=sys.stderr)
        print(DocoptExit.usage, file=sys.stderr)
        return os.EX_USAGE

    bus = SMBus(device_num)

    try:
        start_pwm(bus, address)
        ensure_mod_rgb_device(bus, address)
    except CompatibilityError as e:
        print(e, file=sys.stderr)
        return os.EX_UNAVAILABLE
    except AddressRangeError as e:
        print(e, file=sys.stderr)
        return os.EX_USAGE
    except IOError as e:
        print("I/O error:", e, file=sys.stderr)
        print("Incorrect <address> {} ({})?"
              .format(old_address, hex(address)), file=sys.stderr)
        return os.EX_IOERR
        
    r = int(red)
    g = int(80 * green / 255)
    b = int(50 * blue / 255) 

    try:
        set_rgb_color(bus, address, r, g, b)
    except IOError as e:
        print("I/O error:", e, file=sys.stderr)
        return os.EX_IOERR
    
    return os.EX_OK

if __name__ == '__main__':
    sys.exit(main())
