# astronode-python-hello-world
Python "Hello World" example for the Astronode S module.

# System requirements
## Python version
* python v2.7+
* python v3.4+
## Python modules
* [crcmod](https://pypi.org/project/crcmod)
* [pyserial](https://pypi.org/project/pyserial)

# How to run the application
## Standalone generic computer
1. Make sure you meet the system requirements.
2. Check the `SerialPort` device variable in main.py script:
   - Use `COMx` devices for Windows hosts.
   - Use `/dev/ttyUSBx` for Linux hosts.
3. Run the main.py script.

## Standalone Raspberry Pi 4 Model B
1. Make sure you meet the system requirements.
2. Using raspi-config, disable login shell over serial and enable serial interface.
3. Use `/dev/ttyS0` in main.py script.

### Hardware setup
    RASP 40-PIN              ASTRONODE FTDI TTL
    -------------------------------------------
    PIN1  3V3       <---->   3V3
    PIN9  GND       <---->   GND
    PIN14 UART_TX   <---->   RX
    PIN15 UART_RX   <---->   TX

## Docker
1. Build the docker image:
```
docker build -t astronode-python-hello-world .
```
2. Run the docker image, attaching the appropiate serial device file:
```
docker run -t -i --device=/dev/ttyUSB0 astronode-python-hello-world
```
