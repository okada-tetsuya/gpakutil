#!/usr/bin/env python3

import sys
import time
import copy
import argparse

import smbus2
import intelhex

class GPak:
    REG_CONFIG = 0x00
    NVM_CONFIG = 0x02
    EEPROM = 0x03

    def __init__(self, bus, addr=1):
        self.bus = bus
        self.slave_address = addr

    def i2caddr(self, area):
        return (self.slave_address << 3) + area

    def read(self, area, offset=0, length=256):
        addr = self.i2caddr(area)
        data = []
        while length > 0:
            xferlen = min(16, length)
            data.extend(self.bus.read_i2c_block_data(addr, offset, xferlen))
            offset += xferlen
            length -= xferlen
        return data
    
    def write(self, area, data, offset=0):
        addr = self.i2caddr(area)
        length = len(data)
        ptr = 0
        buf = [0] * 16
        print('Writing', end='', file=sys.stderr)
        sys.stderr.flush()
        while length - ptr > 0:
            xferlen = min(16, length - ptr)
            for i in range(xferlen):
                buf[i] = data[ptr + i]
            self.bus.write_i2c_block_data(addr, offset, buf[0:xferlen])
            print('.', end='', file=sys.stderr)
            sys.stderr.flush()
            time.sleep(0.01)
            offset += xferlen
            ptr += xferlen
        print('done', file=sys.stderr)

    def write_reg(self, reg, value):
        addr = self.i2caddr(self.REG_CONFIG)
        data = [value]
        self.bus.write_i2c_block_data(addr,reg, data)

    def read_reg(self, reg):
        addr = self.i2caddr(self.REG_CONFIG)
        return self.bus.read_i2c_block_data(addr, reg, 1)[0]

    def erase(self, area):
        print('Erasing', end='', file=sys.stderr)
        sys.stderr.flush()
        for i in range(16):
            try:
                if area == self.NVM_CONFIG:
                    self.write_reg(0xe3, 0x80 + i)
                elif area == self.EEPROM:
                    self.write_reg(0xe3, 0x90 + i)
            except OSError:
                # Workaround for SLG46826 Errata:
                #   Non-I2C Compliant ACK Behavior for the NVM and EEPROM
                #   Page Erase Byte
                pass
            print('.', end='', file=sys.stderr)
            sys.stderr.flush()
            time.sleep(0.01)
        print('done', file=sys.stderr)
            
def hexdump(data, showaddr=0):
    offset = 0
    while offset < len(data):
        line = format(showaddr + offset, '4x') + ':'
        count = min(len(data) - offset, 16)
        for i in range(count):
            line += ' ' + format(data[offset + i], '02x')
        print(line)
        offset += count

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('busno', type=int,
                        help='i2c bus number (number after /dev/i2c-)')
    parser.add_argument('addr', type=int,
                        help='i2c address A7-A4 (1 if unprogrammed)')
    parser.add_argument('area', choices=['reg', 'nvm', 'eeprom'],
                        help='area')
    parser.add_argument('-w', '--write', nargs=1, metavar='filename',
                        help='write file (Intel Hex format)')
    args = parser.parse_args()

    if args.area == 'reg':
        area = GPak.REG_CONFIG
        erase = False
    elif args.area == 'nvm':
        area = GPak.NVM_CONFIG
        erase = True
    else:
        area = GPak.EEPROM
        erase = True

    bus = smbus2.SMBus(args.busno)
    gpak = GPak(bus, args.addr)
    
    if args.write:
        # Write action
        if erase:
            gpak.erase(area)
        ih = intelhex.IntelHex(args.write[0])
        gpak.write(area, ih)
        
    else:
        # Read action
        hexdump(gpak.read(area))
