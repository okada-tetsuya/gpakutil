# gpakutil

GreenPAK programmer in Python

# Environment

Tested on Raspberry Pi (Raspberry Pi OS 32bit), Python 3.7.3.
May work on any platform that works `smbus2` package hopefully.

Only supports SLG46826 device.

# usage

```
usage: gpakutil.py [-h] [-w filename] busno addr {reg,nvm,eeprom}

positional arguments:
  busno                 i2c bus number (number after /dev/i2c-)
  addr                  i2c address A7-A4 (1 if unprogrammed)
  {reg,nvm,eeprom}      area

optional arguments:
  -h, --help            show this help message and exit
  -w filename, --write filename
                        write file (Intel Hex format)
```
