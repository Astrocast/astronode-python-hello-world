#!/usr/bin/env python3

import binascii
import codecs
import crcmod
import datetime
import serial
import sys
import time


#--------------------------------------------------------------------------------
# Initializations
#--------------------------------------------------------------------------------
ser = serial.Serial(
    port = 'COM15',
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
PLD_WR = "27"
GEO_WR = "35"
CFG_WR = "05"
WIF_WR = "06"
CFG_RD = "15"
DLN_RR = "65"
SAK_RR = "45"
SAK_CR = "46"
# debug sub-family
DBG_SET_RTC    = "01"
DBG_FAKE_ALARM = "03"

#--------------------------------------------------------------------------------
# Payloads
#
# Here you can declare you data.
#--------------------------------------------------------------------------------
configuration_0 = "0d"
configuration_1 = "03"
cfg_ack_geo = "03"

# Astrocast dev wifi
# ssid = b"Astrocast Corporate"
# password = b"GjrxFnm16HFYw"
# token = b"Hu3Y5QIdIdTLJUZyNombDsS0L2teutF1k1HAcMBRSHA1g5MnUpGrSxAoKcmcwDSoH1BRmywaVEr510UOpfteWniVAsY8zyup"
# configuration_wifi = binascii.hexlify(ssid).ljust(66, b'0') + binascii.hexlify(password).ljust(128, b'0') + binascii.hexlify(token).ljust(194, b'0')
# configuration_wifi = configuration_wifi.decode("utf-8")

geolocation_1 = "98badcfe98badcfe"
payload_1 = "00011574abbf"


#--------------------------------------------------------------------------------
# Function definitions
#--------------------------------------------------------------------------------
def debug_handler(opcode):
    if (opcode is DBG_SET_RTC):
        return ["0700", generate_datetime()]
    elif (opcode is DBG_FAKE_ALARM):
        return ["0100", ""]

def generate_length(hex_string):
    length_tmp = '{:04x}'.format(int(len(hex_string)/2))
    length = length_tmp[2]
    length += length_tmp[3]
    length += length_tmp[0]
    length += length_tmp[1]
    return length

def generate_datetime():
    date_time = datetime.datetime.utcnow()
    dt = format(date_time.year % 100, 'x').zfill(2)
    dt += format(date_time.month, 'x').zfill(2)
    dt += format(date_time.day, 'x').zfill(2)
    dt += format(date_time.hour, 'x').zfill(2)
    dt += format(date_time.minute, 'x').zfill(2)
    dt += format(date_time.second, 'x').zfill(2)
    return dt

def generate_geolocation(lon, lat):
    lon_tmp = '{:08x}'.format(int(lon * 1e7))
    lat_tmp = '{:08x}'.format(int(lat * 1e7))
    geolocation = lon_tmp[6]
    geolocation += lon_tmp[7]
    geolocation += lon_tmp[4]
    geolocation += lon_tmp[5]
    geolocation += lon_tmp[2]
    geolocation += lon_tmp[3]
    geolocation += lon_tmp[0]
    geolocation += lon_tmp[1]
    geolocation += lat_tmp[6]
    geolocation += lat_tmp[7]
    geolocation += lat_tmp[4]
    geolocation += lat_tmp[5]
    geolocation += lat_tmp[2]
    geolocation += lat_tmp[3]
    geolocation += lat_tmp[0]
    geolocation += lat_tmp[1]
    return geolocation

def generate_crc(data):
    crc_tmp = '{:04x}'.format(crc16(codecs.decode(data, 'hex')))
    crc = crc_tmp[2]
    crc += crc_tmp[3]
    crc += crc_tmp[0]
    crc += crc_tmp[1]
    return crc

def send(opcode, sub_opcode, data):
    msg = "7f"
    msg += opcode
    if (opcode is PLD_ER):
        msg += generate_length(data)
    elif (opcode is PLD_DR):
        msg += "0000"
    elif (opcode is PLD_WR):
        msg += "0000"
    elif (opcode is GEO_WR):
        msg += "0800"
    elif (opcode is CFG_WR):
        msg += generate_length(data)
    elif (opcode is WIF_WR):
        msg += generate_length(data)
    elif (opcode is CFG_RD):
        msg += "0000"
    elif (opcode is DLN_RR):
        msg += "0000"
    elif (opcode is SAK_RR):
        msg += "0000"
    elif (opcode is SAK_CR):
        msg += "0000"
    elif (opcode is DBG):
        len_and_param = debug_handler(sub_opcode)
        msg += len_and_param[0]
        msg += sub_opcode
        data = len_and_param[1]
    else:
        print("***ERROR Operation code not valid.")
    msg += data
    crc = generate_crc(msg)
    msg += crc
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

send(CFG_WR, "", "00")
# send(WIF_WR, "", configuration_wifi)
send(PLD_ER, "", "0100" + text_to_hex(b"A"))
#send(PLD_ER, "", "0200" + text_to_hex(b"B"))
#send(PLD_ER, "", "0300" + text_to_hex(b"C"))
#send(PLD_ER, "", "0400" + text_to_hex(b"D"))
#send(DLN_RR, "", "")
#send(SAK_RR, "", "")
#send(SAK_CR, "", "")
#send(CFG_RD, "", "")

# send(WIF_WR, "", configuration_wifi)
# send(PLD_ER, "", "0100" + text_to_hex(b"A"))
# send(PLD_ER, "", "0200" + text_to_hex(b"Ba1"))
# send(PLD_ER, "", "0300" + text_to_hex(b"C"))
# send(PLD_ER, "", "0400" + text_to_hex(b"D"))
# send(PLD_ER, "", "0500" + text_to_hex(b"E"))
# send(PLD_ER, "", "0600" + text_to_hex(b"F"))
# send(PLD_ER, "", "0700" + text_to_hex(b"G"))
# send(PLD_ER, "", "0800" + text_to_hex(b"H"))
# send(DBG, DBG_FAKE_ALARM, "")
# send(CFG_WR, "", "00")
# send(DLN_RR, "", "")
# send(SAK_RR, "", "")
# send(SAK_CR, "", "")

# ser.write(bytearray.fromhex(""))

# send(CFG_RD, "", "")
# send(CFG_WR, "", cfg_ack_geo)
# send(CFG_RD, "", "")

# send(CFG_WR, "", configuration_1)
# send(CFG_RD, "", "")
# send(GEO_WR, "", geolocation_1)
# send(GEO_WR, "", generate_geolocation(80.55, 90))
# send(PLD_ER, "", payload_1)
# send(DLN_RR, "", "")
# send(DBG, DBG_SET_RTC, "")
# send(PLD_ER, "", text_to_hex(b"Hello, world"))
# send(PLD_WR, "", "")
# send(PLD_DR, "", "")
# send(PLD_ER, "", "0100" + text_to_hex(b"A"))
#send(DBG, DBG_FAKE_ALARM, "")
# send(PLD_ER, "", "0200" + text_to_hex(b"B"))
# send(PLD_DR, "", "")
# send(PLD_DR, "", "")
#send(PLD_ER, "", "0300" + text_to_hex(b"C"))
#send(PLD_ER, "", "0400" + text_to_hex(b"D"))
#send(PLD_ER, "", "0500" + text_to_hex(b"E"))
# send(PLD_ER, "", "0600" + text_to_hex(b"F"))
# send(PLD_ER, "", "0700" + text_to_hex(b"G"))
# send(PLD_ER, "", "0800" + text_to_hex(b"H"))
# send(PLD_ER, "", "0900" + text_to_hex(b"I"))
# send(PLD_ER, "", "0a00" + text_to_hex(b"12345"))
# send(PLD_ER, "", "0b00" + text_to_hex(b"67890"))
# send(PLD_ER, "", text_to_hex(b"BBBBBBBBBBBBBBBB"))
# send(PLD_ER, "", "0100" + text_to_hex(b"BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"))
# send(PLD_ER, "", "0000" + text_to_hex(b"BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"))

# Wi-Fi devkit
# send(CFG_WR, "", configuration_wifi)
# send(PLD_WR, "", "01020304")

# sys.exit()
