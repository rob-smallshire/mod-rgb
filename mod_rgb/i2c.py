class AddressRangeError(Exception):
    pass


def is_i2c_reserved(address):
    """Determine whether address is reserved according to the I2C specification.

    Args:
        address: A 7-bit address in the range 0-127.

    Returns:
        An empty string (False in a boolean context) if the address is not reserved,
        or if the address is reserved a non-empty string (True in a boolean context)
        with a description of the reserved purpose. 
    """
    if not (0 <= address < 128):
        raise AddressRangeError("address {} ({}) out of range 0-127 (0x00-0x7f)".format(address, hex(address)))
    
    if address == 0b0000000:
        return "General Call Address/START byte"

    if address == 0b0000001:
        return "CBUS address"

    if address == 0b0000010:
        return "Address reserved for different bus format"

    if address == 0b0000011:
        return "Reserved for future use"        

    masked_address = address & 0b1111100
    
    if masked_address == 0b0000100:
        return "Reserved for future use"

    if masked_address == 0b1111000:
        return "10-bit slave addressing"

    if masked_address == 0b1111100:
        return "Reserved for future use"
    
    return ""

def is_smbus_reserved(address):
    """Determine whether address is reserved according to the SMBus specification.

    Args:
        address: A 7-bit address in the range 0-127.

    Returns:
        An empty string (False in a boolean context) if the address is not reserved,
        or if the address is reserved a non-empty string (True in a boolean context)
        with a description of the reserved purpose. 
    """
    if not (0 <= address < 128):
        raise AddressRangeError("address {} ({}) out of range 0-127 (0x00-0x7f)".format(address, hex(address)))
    
    if address == 0b0001000:
        return "SMBus Host"

    if address == 0b0001100:
        return "SMBus Alert Response Address"

    if address == 0b1100001:
        return "SMBus Device Default Address"

    if address == 0b0101000:
        return "Reserved for ACCESS.bus host"

    if address == 0b0110111:
        return "Reserved for ACCESS.bus default address"

    return ""
    

def is_reserved(address):
    """Determine whether address is reserved according to the I2C or SMBus specifications.

    Args:
        address: A 7-bit address in the range 0-127.

    Returns:
        An empty string (False in a boolean context) if the address is not reserved,
        or if the address is reserved a non-empty string (True in a boolean context)
        with a description of the reserved purpose. 
    """
    return is_i2c_reserved(address) or is_smbus_reserved(address)
