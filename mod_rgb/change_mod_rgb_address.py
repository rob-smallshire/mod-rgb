#!/usr/bin/env python3

"""Change MOD-RGB address.

Usage:
  change-mod-rgb-address.py <old-address> <new-address>
      [--device=<dev-num>] [(-q | --quiet)] [(-n | --no-action)]
  change-mod-rgb-address.py -h | --help

Options:
  --device=<dev-num>  Device number [default: 1].
  -q --quiet          Do not prompt for jumper changes.
  -n --no-action      Omit reprogramming command.
  -h --help           Show this screen.
"""

import os
import sys

from docopt import docopt, DocoptExit
from smbus import SMBus

from mod_rgb.control import ensure_mod_rgb_device, change_address 

def main(args=None):
    if args is None:
        args = docopt(__doc__, version='Change MOD-RGB address 1.0')

    try:   
        old_address = int(args['<old-address>'], base=0)
        new_address = int(args['<new-address>'], base=0)
    except ValueError:
        print("Address must be an integer", file=sys.stderr)
        print(DocoptExit.usage, file=sys.stderr)
        return os.EX_USAGE
 
    try:
        device_num = int(args['--device'], base=0)
    except ValueError:
        print("Device number must be an integer", file=sys.stderr)
        print(DocoptExit.usage, file=sys.stderr)
        return os.EX_USAGE

    prompt = not args['--quiet']
    act = not args['--no-action']       

    bus = SMBus(device_num)

    try:
        ensure_mod_rgb_device(bus, old_address)
    except CompatibilityError as e:
        print(e, file=sys.stderr)
        return os.EX_UNAVAILABLE
    except AddressRangeError as e:
        print(e, file=sys.stderr)
        return os.EX_USAGE
    except IOError as e:
        print("I/O error:", e, file=sys.stderr)
        print("Incorrect <old-address> {} ({})?"
              .format(old_address, hex(old_address)), file=sys.stderr)
        return os.EX_IOERR
        
    if prompt:
        print("The DMX_EN jumper on device {} ({}) must be closed"
              .format(old_address, hex(old_address)))
        print("Press RETURN to continue.")
        input()
            
    try:
        change_address(bus, old_address, new_address, act)
    except AddressRangeError as e:
        print(e, file=sys.stderr)
        return os.EX_USAGE
    except IOError as e:
        print("I/O error:", e, file=sys.stderr)
        return os.EX_IOERR
    
    if prompt:
        print("Now open the DMX_EN jumper on device {} ({}) to "
              "avoid inadvertently changing it."
              .format(new_address, hex(new_address)))
        print("Press RETURN to continue.")
        input()

    try:
        ensure_mod_rgb_device(bus, new_address)
    except CompatibilityError as e:
        print("Reprogramming FAILED!", file=sys.stderr)
        print(e, file=sys.stderr)
        return os.EX_UNAVAILABLE
    except IOError as e:
        print("I/O error on device at <new-address> {} ({}): {}"
              .format(new_address, hex(new_address), e), file=sys.stderr)
        return os.EX_IOERR

    return os.EX_OK

if __name__ == '__main__':
    sys.exit(main())
