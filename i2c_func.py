import smbus2


def read_int(bus, address, register, length, msb=True, signed=True):
    """
    :type bus: smbus2.SMBus
    :type address: int
    :type register: int
    :type length: int
    :type msb: bool
    :type signed: bool
    :return: int
    """
    data = bus.read_i2c_block_data(address, register, length)
    return int.from_bytes(data, 'big' if msb else 'little', signed=signed)


def write_int(bus, address, register, value, length, msb=True, signed=True):
    """
    :type bus: smbus2.SMBus
    :type address: int
    :type register: int
    :type value: int
    :type length: int
    :type msb: bool
    :type signed: bool
    """
    bus.write_i2c_block_data(
        address,
        register,
        list(int(value).to_bytes(length, 'big' if msb else 'little', signed=signed))
    )


def read_int16(bus, addr, reg):
    return read_int(bus=bus, address=addr, register=reg, length=2, msb=True, signed=True)


def read_uint16(bus, addr, reg):
    return read_int(bus=bus, address=addr, register=reg, length=2, msb=True, signed=False)


def write_int16(bus, addr, reg, val):
    write_int(bus=bus, address=addr, register=reg, value=val, length=2, msb=True, signed=True)


def write_uint16(bus, addr, reg, val):
    write_int(bus=bus, address=addr, register=reg, value=val, length=2, msb=True, signed=False)
