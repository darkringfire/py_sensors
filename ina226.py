from smbus2 import *
from py_sensors.i2c_func import *

INA226_ADDRESS_DEFAULT = 0x40

INA226_REG_CONFIG = 0x00
INA226_REG_SHUNTVOLTAGE = 0x01
INA226_REG_BUSVOLTAGE = 0x02
INA226_REG_POWER = 0x03
INA226_REG_CURRENT = 0x04
INA226_REG_CALIBRATION = 0x05
INA226_REG_MASKENABLE = 0x06
INA226_REG_ALERTLIMIT = 0x07

INA226_BIT_SOL = 0x8000
INA226_BIT_SUL = 0x4000
INA226_BIT_BOL = 0x2000
INA226_BIT_BUL = 0x1000
INA226_BIT_POL = 0x0800
INA226_BIT_CNVR = 0x0400
INA226_BIT_AFF = 0x0010
INA226_BIT_CVRF = 0x0008
INA226_BIT_OVF = 0x0004
INA226_BIT_APOL = 0x0002
INA226_BIT_LEN = 0x0001

INA226_AVERAGES_1 = 0b000
INA226_AVERAGES_4 = 0b001
INA226_AVERAGES_16 = 0b010
INA226_AVERAGES_64 = 0b011
INA226_AVERAGES_128 = 0b100
INA226_AVERAGES_256 = 0b101
INA226_AVERAGES_512 = 0b110
INA226_AVERAGES_1024 = 0b111

INA226_BUS_CONV_TIME_140US = 0b000
INA226_BUS_CONV_TIME_204US = 0b001
INA226_BUS_CONV_TIME_332US = 0b010
INA226_BUS_CONV_TIME_588US = 0b011
INA226_BUS_CONV_TIME_1100US = 0b100
INA226_BUS_CONV_TIME_2116US = 0b101
INA226_BUS_CONV_TIME_4156US = 0b110
INA226_BUS_CONV_TIME_8244US = 0b111

INA226_SHUNT_CONV_TIME_140US = 0b000
INA226_SHUNT_CONV_TIME_204US = 0b001
INA226_SHUNT_CONV_TIME_332US = 0b010
INA226_SHUNT_CONV_TIME_588US = 0b011
INA226_SHUNT_CONV_TIME_1100US = 0b100
INA226_SHUNT_CONV_TIME_2116US = 0b101
INA226_SHUNT_CONV_TIME_4156US = 0b110
INA226_SHUNT_CONV_TIME_8244US = 0b111

INA226_MODE_POWER_DOWN = 0b000
INA226_MODE_SHUNT_TRIG = 0b001
INA226_MODE_BUS_TRIG = 0b010
INA226_MODE_SHUNT_BUS_TRIG = 0b011
INA226_MODE_ADC_OFF = 0b100
INA226_MODE_SHUNT_CONT = 0b101
INA226_MODE_BUS_CONT = 0b110
INA226_MODE_SHUNT_BUS_CONT = 0b111


class INA226:
    def __init__(self, i2c_bus=None, ina226_addr=INA226_ADDRESS_DEFAULT):
        if i2c_bus is None:
            i2c_bus = 0
        if type(i2c_bus) is int:
            self.i2c_bus = smbus2.SMBus(i2c_bus)
        elif type(i2c_bus) is SMBus:
            self.i2c_bus = i2c_bus
        self.ina226_address = ina226_addr

        self.current_lsb = 0
        self.power_lsb = 0
        self.shunt_r = 0
        self.current_max_possible = 0
        self.shunt_v_max = 0.08192

    def close(self):
        self.i2c_bus.close()

    def get_bus(self):
        return self.i2c_bus

    def read_shunt_voltage(self):
        voltage = read_int16(self.i2c_bus, self.ina226_address, INA226_REG_SHUNTVOLTAGE) / 400000
        return voltage

    def read_current(self):
        return read_int16(self.i2c_bus, self.ina226_address, INA226_REG_CURRENT) * self.current_lsb

    def read_calibration(self):
        return read_uint16(self.i2c_bus, self.ina226_address, INA226_REG_CALIBRATION)

    def calibrate_by_shunt(self, shunt_r=0.1, current_max_expected=0.8):
        self.shunt_r = float(shunt_r)
        self.current_lsb = current_max_expected / 2 ** 15

        self.power_lsb = self.current_lsb * 25

        calibration_value = int(0.00512 / self.current_lsb / self.shunt_r)

        write_int16(self.i2c_bus, self.ina226_address, INA226_REG_CALIBRATION, calibration_value)
        return

    def configure(self,
                  avg=INA226_AVERAGES_1,
                  bus_conv_time=INA226_BUS_CONV_TIME_1100US,
                  shunt_conv_time=INA226_SHUNT_CONV_TIME_1100US,
                  mode=INA226_MODE_SHUNT_BUS_CONT
                  ):
        config = 0
        config |= (avg << 9 | bus_conv_time << 6 | shunt_conv_time << 3 | mode)
        write_uint16(self.i2c_bus, self.ina226_address, INA226_REG_CONFIG, config)
        return
