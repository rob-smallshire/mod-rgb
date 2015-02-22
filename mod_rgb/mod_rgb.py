GET_ID_COMMAND = 0x20
START_PWM_COMMAND = 0x01
STOP_PWM_COMMAND = 0x02
SET_RGB_COMMAND = 0x03
SET_ADDRESS_COMMAND = 0xF0
MOD_RGB_ID = 0x64


class CompatibilityError(Exception):
    pass


class AddressRangeError(Exception):
    pass


def start_pwm(bus, address):
    """Start PWM.

    Args:
        bus: An SMBus instance.
        address: The address of a MOD-RGB device.
    """
    if not (0 <= address < 128):
        raise AddressRangeError("address {} ({}) out of range 0-127".format(address, hex(address)))

    bus.write_byte(address, START_PWM_COMMAND) 


def stop_pwm(bus, address):
    """Stop PWM.

    Args:
        bus: An SMBus instance.
        address: The address of a MOD-RGB device.
    """
    if not (0 <= address < 128):
        raise AddressRangeError("address {} ({}) out of range 0-127".format(address, hex(address)))

    bus.write_byte(address, STOP_PWM_COMMAND) 


def set_rgb_color(bus, address, red, green, blue):
    """Set the MOD-RGB output color.

    Args:
        bus: An SMBus instance.
        address: The address of a MOD-RGB device.
        red: Red brighness 0-255.
        green: Green brightness 0-255.
        blue: Blue brightness 0-255.
    """
    if not (0 <= address < 128):
        raise AddressRangeError("address {} ({}) out of range 0-127".format(address, hex(address)))

    if not (0 <= red < 256):
        raise ValueError("red value {} out of range 0-255".format(red))

    if not (0 <= green < 256):
        raise ValueError("green value {} out of range 0-255".format(green))

    if not (0 <= blue < 256):
        raise ValueError("blue value {} out of range 0-255".format(blue))

    print(red, green, blue)
    bus.write_i2c_block_data(address, SET_RGB_COMMAND, [red, green, blue])


def change_address(bus, old_address, new_address, act=True):
    """Change the address of a MOD-RGB device.

    Args:
        bus: An SMBus instance.
        old_address: The existing address of a MOD-RGB device.
        new_address: The new address of a MOD-RGB device.
        act: If False the address change will not be performed.

    Raises:
        AddressRangeError: An address is out of range.
        IOError: Communication with the device could not be established.
    """
    if not (0 <= old_address < 128):
        raise AddressRangeError("old_address {} ({}) out of range 0-127".format(old_address, hex(address)))

    if not (0 <= new_address < 128):
        raise AddressRangeError("new_address {} out of range 0-127".format(new_address))
    
    if act:
        bus.write_byte_data(old_address, SET_ADDRESS_COMMAND, new_address)


def ensure_mod_rgb_device(bus, address):
    """Check that there is a MOD-RGB at the specified address.

    Args:
        bus: An SMBus instance.
        address: The address to check.

    Raises:
        CompatibilityError: If an unexpected device was found.
        IOError: If communication could not be established with the device.
        AddressRangeError: If address is out of range.
    """
    if not (0 <= address < 128):
        raise AddressRangeError("Address {} ({}) out of range 0-127 (0x00-0x7f)".format(address, hex(address)))

    ident = bus.read_byte_data(address, GET_ID_COMMAND)

    if ident != MOD_RGB_ID:
        raise CompatibilityError("Device at address {} ({}) has unexpected "
                                 "identity {}, not {}".format(address, hex(address), ident, MOD_RGB_ID))
