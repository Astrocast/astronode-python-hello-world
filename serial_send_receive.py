"""

File:               serial_send_receive.py
Author:             Gildas Seimbille
E-mail:             gseimbille@astrocast.com

Created on:         30.06.2021
Python Version:     3.8
Supported Hardware: Astronode S DevKit

"""

#!/usr/bin/env python3

import binascii
import codecs
import crcmod
import datetime
import serial
from binascii import hexlify
from random import *

SerialPort = 'COM7'
#--------------------------------------------------------------------------------
# Initializations
#--------------------------------------------------------------------------------
ser = serial.Serial(
    port = SerialPort,
    baudrate = 9600,
    bytesize = serial.EIGHTBITS,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    timeout = 3,
    inter_byte_timeout = 0.001
)

crc16 = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0xffff, xorOut=0x0000)


#--------------------------------------------------------------------------------
# Operation codes
#--------------------------------------------------------------------------------
# main family
DBG    = "01"
PLD_ER = "25"
PLD_DR = "26"
PLD_FR = "27"
GEO_WR = "35"
CFG_WR = "05"
WIF_WR = "06"
CFG_RR = "15"
EVT_RR = "65"
SAK_RR = "45"
SAK_CR = "46"
# debug sub-family
DBG_SET_RTC    = "01"
DBG_FAKE_ALARM = "03"

#--------------------------------------------------------------------------------
# Payload, Geolocation and Wi-Fi configuration
#
# Here you can declare you data.
#--------------------------------------------------------------------------------
payload = b"Hello world"
latitude = 46.534363896181624
longitude = 6.578710272772917

ssid = b"YOUR_WIFI_SSID"
password = b"YOUR_WIFI_PASSWORD"
token = b"YOUR_ASTROCAST_TOKEN"

configuration_wifi = binascii.hexlify(ssid).ljust(66, b'0') + binascii.hexlify(password).ljust(128, b'0') + binascii.hexlify(token).ljust(194, b'0')
configuration_wifi = configuration_wifi.decode("utf-8")


#--------------------------------------------------------------------------------
# Function definitions
#--------------------------------------------------------------------------------

def generate_geolocation(lat, lng):
    lat_tmp = '{:08x}'.format(int(lat * 1e7))
    lng_tmp = '{:08x}'.format(int(lng * 1e7))
    geolocation = lat_tmp[6]
    geolocation += lat_tmp[7]
    geolocation += lat_tmp[4]
    geolocation += lat_tmp[5]
    geolocation += lat_tmp[2]
    geolocation += lat_tmp[3]
    geolocation += lat_tmp[0]
    geolocation += lat_tmp[1]
    geolocation += lng_tmp[6]
    geolocation += lng_tmp[7]
    geolocation += lng_tmp[4]
    geolocation += lng_tmp[5]
    geolocation += lng_tmp[2]
    geolocation += lng_tmp[3]
    geolocation += lng_tmp[0]
    geolocation += lng_tmp[1]
    return geolocation

def generate_crc(data):
    crc_tmp = '{:04x}'.format(crc16(codecs.decode(data, 'hex')))
    crc = crc_tmp[2]
    crc += crc_tmp[3]
    crc += crc_tmp[0]
    crc += crc_tmp[1]
    return crc

def send(opcode, data):
    msg = opcode
    msg += data
    crc = generate_crc(msg)
    msg += crc
    msg = hexlify(msg.encode())
    msg = "02" + msg.decode()
    msg += "03"
    msg = bytearray.fromhex(msg)
    ser.write(msg)
    print("")
    print("[sent]      -->  " + " ".join(["{:02x}".format(x) for x in msg]))
    receive()

def receive():
    output = ser.read(160)
    print("[received]  <--  " + " ".join(["{:02x}".format(x) for x in output]))

def text_to_hex(text):
    return binascii.hexlify(text).decode('ascii')

def generate_message(payload):
    return str(randint(0, 9999)) + text_to_hex(payload)


#--------------------------------------------------------------------------------
# Send and receive on UART
#
# Here you can call the send function with the command and data you want.
# Use the send(OPCODE, SUB-OPCODE, DATA) function.
# OPCODE is one of the terminal<->asset protocol command (PLD_WR, CFG_RD...) or
# it can be DEBUG to send command like setting the RTC date and time.
# SUB-OPCODE is needed only for the DEBUG operation code.
# DATA is the data related to the operation code and sub-operation code you use.
#--------------------------------------------------------------------------------


# If Astronode S DevKit Wi-Fi
#send(WIF_WR, configuration_wifi)

# If you want to specify geolocation
send(GEO_WR, generate_geolocation(latitude, longitude))

send(PLD_ER, generate_message(payload))
