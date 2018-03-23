#!/usr/bin/env python
# -*- coding: utf-8 -*-

from smbus2 import *
import time

am2320_address = 0x5c

AM2320_CMD_READ = 0x03
AM2320_CMD_WRITE = 0x10

AM2320_REG_DATA = 0x00
AM2320_REG_DATA_NUM = 4
AM2320_REG_DEV_INFO = 0x08
AM2320_REG_DEV_INFO_NUM = 7


def crc16(buf):
    crc = 0xFFFF
    for c in buf:
        crc ^= c
        for i in range(8):
            if crc & 0x01:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc


class AM2320:

    def __init__(self, i2c_bus_number=0):
        self.bus = SMBus(i2c_bus_number)

    def _wake(self):
        """
        Initialize the AM 2320 sensor
        """
        try:
            self.bus.write_i2c_block_data(am2320_address, 0x00, [])
        except OSError as e:
            print(e)

        time.sleep(0.001)

    @staticmethod
    def _check_crc(buf):
        response_crc = int.from_bytes(buf[-2:], 'little')
        crc = crc16(buf[:-2])
        return response_crc == crc

    def _read(self, reg, num):
        self._wake()

        wr = i2c_msg.write(
            am2320_address,
            [AM2320_CMD_READ, reg, num]
        )
        try:
            self.bus.i2c_rdwr(wr)
        except OSError as e:
            print(e)

        time.sleep(0.001)

        rd = i2c_msg.read(am2320_address, 2 + num + 2)
        self.bus.i2c_rdwr(rd)

        buf = rd.buf[0:2 + num + 2]

        if not self._check_crc(buf):
            raise Exception("checksum error")

        return buf[2:-2]

    def read_ht(self):
        """
        Read sensor value from AM 2320
        """
        response = self._read(AM2320_REG_DATA, AM2320_REG_DATA_NUM)

        humidity = int.from_bytes(response[0:2], 'big') / 10.0
        temperature = (int.from_bytes(response[2:4], 'big') & 0x7FFF) / 10.0
        if response[2] & 0x80:
            temperature *= -1

        return {
            # 'response': response,
            # 'address': address,
            # 'command': command,
            'temperature': temperature,
            'humidity': humidity,
        }

    def read_info(self):
        response = self._read(AM2320_REG_DEV_INFO, AM2320_REG_DEV_INFO_NUM)
        return response
