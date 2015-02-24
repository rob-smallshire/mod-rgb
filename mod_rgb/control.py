from mod_rgb.i2c import (AddressRangeError, is_i2c_reserved, is_smbus_reserved)


GET_ID_COMMAND = 0x20
START_PWM_COMMAND = 0x01
STOP_PWM_COMMAND = 0x02
SET_RGB_COMMAND = 0x03
SET_ADDRESS_COMMAND = 0xF0
MOD_RGB_ID = 0x64


class CompatibilityError(Exception):
    pass


def start_pwm(bus, address):
    """Start PWM.

    Args:
        bus: An SMBus instance.
        address: The address of a MOD-RGB device.

    Raises:
        AddressRangeError: Of the address is out of range.
        IOError: Communication with the device could not be established.
    """
    if not (0 <= address < 128):
        raise AddressRangeError("address {} ({}) out of range 0-127".format(address, hex(address)))

    bus.write_byte(address, START_PWM_COMMAND) 


def stop_pwm(bus, address):
    """Stop PWM.

    Args:
        bus: An SMBus instance.
        address: The address of a MOD-RGB device.

    Raises:
        AddressRangeError: If the address is out of range.
        IOError: Communication with the device could not be established.
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

    Raise:
        AddressRangeError: If the address is out of range.
        AddressReservedError: If the address is reserved.
        ValueError: If red, green or blue are out of range.
        IOError: Communication with the device could not be established.
    """
    if not (0 <= address < 128):
        raise AddressRangeError("address {} ({}) out of range 0-127 (0x00-0x7f)".format(address, hex(address)))
    
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
        AddressReservedError: The address is reserved.
        IOError: Communication with the device could not be established.
    """
    if not (0 <= old_address < 128):
        raise AddressRangeError("old_address {} ({}) out of range 0-127 (0x00-0x7f)".format(old_address, hex(old_address)))

    if not (0 <= new_address < 128):
        raise AddressRangeError("new_address {} ({}) out of range 0-127 (0x00-0x7f)".format(new_address, hex(old_address)))

    reserved = is_reserved(new_address)
    if reserved:
        raise AddressReservedError("new_address {} ({}) is reserved: {}".format(new_address, hex(new_address), reserved))
    
    if act:
        bus.write_byte_data(old_address, SET_ADDRESS_COMMAND, new_address)


def is_mod_rgb_device(bus, address):
    """Determine whether there is a MOD-RGB at the specified address.

    Args:
        bus: An SMBus instance.
        address: The address to check.

    Returns:
        True if there is a MOD-RGB device at the address, otherwise False.

    Raises:
        IOError: If communication could not be established with the device.
        AddressRangeError: If address is out of range.
    """
    if not (0 <= address < 128):
        raise AddressRangeError("Address {} ({}) out of range 0-127 (0x00-0x7f)".format(address, hex(address)))

    ident = bus.read_byte_data(address, GET_ID_COMMAND)
    return ident == MOD_RGB_ID

                                   

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
    if not is_mod_rgb_device(bus, address):
        raise CompatibilityError("Device at address {} ({}) has unexpected "
                                 "identity {}, not {}".format(address, hex(address), ident, MOD_RGB_ID))

                                   
def find_devices(bus, reserved_i2c_addresses=False, reserved_smbus_addresses=False):
    """Generate all device addresses at which there is a MOD-RGB.

    Args:
        bus: An SMBus instance.
        reserved_i2c_addresses: Optional flag to force tests of reserved I2C addresses.
        reserved_smbus_addresses: Optional flag to force tests of resered SMBus addresses. This
            option implies reserved_i2c_addresses.
    
    Yields:
        An integer device address for each MOD-RGB device found on the bus.

    Raises:
        IOError: If communication over the bus could not be established.
    """
    reserved_i2c_addresses = reserved_i2c_addresses or reserved_smbus_addresses
                                   
    for address in range(0, 128):
        if (not reserved_i2c_addresses) and is_i2c_reserved(address):
            continue

        if (not reserved_smbus_addresses) and is_smbus_reserved(address):
            continue
                                   
        try:
            is_mod_rgb = is_mod_rgb_device(bus, address)
        except IOError:
            pass
        else:
            if is_mod_rgb:
                yield address
