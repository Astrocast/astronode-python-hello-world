# astronode-python-hello-world
Python "Hello World" example for the Astronode S module.

# System requirements
## Python version
python v3.8+
## Python modules
* [crcmod](https://pypi.org/project/crcmod)
* [pyserial](https://pypi.org/project/pyserial)

# How to run the application
## Standalone
1. Make sure you meet the system requirements.
2. Check the `SerialPort` device variable in main.py script:
   - Use `COMx` devices for Windows hosts.
   - Use `/dev/ttyUSBx` for Linux hosts.
3. Run the main.py script.

## Docker
1. Build the docker image:
```
docker build -t astronode-python-hello-world .
```
2. Run the docker image, attaching the appropiate serial device file:
```
docker run -t -i --device=/dev/ttyUSB0 astronode-python-hello-world
```
