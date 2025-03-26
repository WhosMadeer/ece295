import pyvisa as visa
import time

rm = visa.ResourceManager(r"C:\WINDOWS\system32\visa64.dll")
print(rm)
print(rm.list_resources("TCPIP0::?*"))

"""Connect to the Power Supply"""
supply = rm.open_resource("TCPIP0::192.168.0.251::5025::SOCKET")
meter = rm.open_resource("TCPIP0::192.168.0.252::5025::SOCKET")

""" Set up the power supply IO configuration"""
supply.timeout = 10000  # 10s
meter.timeout = 20000  # 10s

# Define string terminations
supply.write_termination = "\n"
supply.read_termination = "\n"


# Define string terminations
meter.write_termination = "\n"
meter.read_termination = "\n"

# Set string terminations
print(
    "\nVISA termination string (write) set to newline: ASCII ",
    ord(supply.write_termination),
)
print(
    "VISA termination string (read) set to newline: ASCII ",
    ord(supply.read_termination),
)


# Set string terminations
print(
    "\nVISA termination string (write) set to newline: ASCII ",
    ord(meter.write_termination),
)
print(
    "VISA termination string (read) set to newline: ASCII ", ord(meter.read_termination)
)


# Get the ID info of the power supply
print("supply ID string:\n  ", supply.query("*IDN?"), flush=True)


# Get the ID info of the digital multimeter
print("meter ID string:\n  ", meter.query("*IDN?"), flush=True)


supply.write("VOLT 5, (@1)")
supply.write("CURR 0.005, (@1)")
print(supply.query("VOLT? (@1)"))

supply.write("OUTP 1, (@1)")


meter.write("CONF:VOLT:DC")
print("meter conf: ", meter.query("READ?"))
print("meter volt dc ", meter.query("MEAS:VOLT:DC?"))

time.sleep(5)
supply.write("OUTP 0, (@1)")
print("off")
