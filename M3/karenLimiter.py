#!/usr/bin/env python
"""Subsystem A unit testing script.
This script measures the input output response of the limiter."""

import matplotlib.pyplot as plt 
import numpy as np
import pyvisa
import time
import sys

__author__ = "Mahir Khandaker"
__copyright__ = "Copyright 2025"
__license__ = "GPL"
__version__ = "1.0"
__email__ = "mahir.khandaker@mail.utoronto.ca"


def user_prompt():
    str = input("Hit Enter to proceed or ! to abort:")
    if str == "!":
        print("Measurement aborted")
        end_program()


def end_program():
    scope.write(":WGEN:OUTP OFF")
    fxngen.write("OUTPut1 OFF")
    fxngen.write("OUTPut2 OFF")
    # supply.write("OUTP 0, (@2)")
    scope.close()
    fxngen.close()
    # supply.close()
    print("closed connection")
    exit()


# Open instrument connection(s)
rm = pyvisa.ResourceManager(r"C:\WINDOWS\system32\visa64.dll")
print(rm)
print(rm.list_resources("TCPIP0::?*"))

"""Connect to the different devices"""
# supply = rm.open_resource("TCPIP0::192.168.0.251::5025::SOCKET")
scope = rm.open_resource("TCPIP0::192.168.0.253::hislip0::INSTR")
fxngen = rm.open_resource("TCPIP0::192.168.0.254::5025::SOCKET")

""" Set up the IO configuration"""
# supply.timeout = 10000  # 10s
scope.timeout = 10000  # 10s
fxngen.timeout = 10000  # 10s

# Define string terminations
# supply.write_termination = "\n"
# supply.read_termination = "\n"
scope.write_termination = "\n"
scope.read_termination = "\n"
fxngen.write_termination = "\n"
fxngen.read_termination = "\n"


# Get ID info
# print("supply ID string:\n  ", supply.query("*IDN?"), flush=True)
print("Connected to oscilloscope:", scope.query("*IDN?"), flush=True)
print("Connected to function generator:", fxngen.query("*IDN?"), flush=True)

# Set probe scaling to 1:1
scope.write("CHANnel1:PROBe +1.0")
scope.write("CHANnel2:PROBe +1.0")

print("Connect the amplifier to the machines to start testing!")
user_prompt()


"""
Set up the waveform generator for input

"""
# Set waveform generator output impedance to high Z
fxngen.write("OUTPUT1:LOAD INF")
fxngen.write("OUTPUT2:LOAD INF")
fxngen.write("UNIT:ANGL DEG")

# Setup waveform generator
fxngen.write("SOUR1:FUNCtion SIN")
fxngen.write("SOUR1:FREQuency +1E+05")  # * 100 KHz frequency
fxngen.write("SOUR1:VOLTage:HIGH +0.7")
fxngen.write("SOUR1:VOLTage:LOW -0.7")
fxngen.write("SOUR1:PHASe:SYNC")
fxngen.write("SOUR1:PHASe +0.0")
fxngen.write("OUTPut1 ON")

fxngen.write("SOUR2:FUNCtion SIN")
fxngen.write("SOUR1:FREQuency +1E+05")  # * 100 KHz frequency
fxngen.write("SOUR2:VOLTage:HIGH +0.7")
fxngen.write("SOUR2:VOLTage:LOW -0.7")
fxngen.write("SOUR2:PHASe:SYNC")
fxngen.write("SOUR2:PHASe +90.0")
fxngen.write("OUTPut2 ON")

# Setup acquisition
scope.write(":TIMebase:SCAL +20.0E-09")  # 20! ns/div
scope.write(":CHAN1:SCAL +50E-03")  # 20! ns/div
scope.write(":CHAN2:SCAL +50E-03")  # 20! ns/div

scope.write(":CHAN1:COUP AC")
scope.write(":CHAN2:COUP AC")


# Setup function generator on scope as stimulus
scope.write(":WGEN:FUNC SIN")
scope.write(":WGEN:FREQ 1.401E+07")  # 10 kHz test
scope.write(":WGEN:VOLT 50E-03")  # 50mVpp test

scope.write(":WGEN:OUTP ON")


# TODO: add the response plot and output

print("Ready to start testing!")
user_prompt()


scope.query(":MEAS:VPP? CHAN1")
scope.query(":MEAS:VPP? CHAN2")
scope.query(":MEAS:FREQ? CHAN1")
scope.query(":MEAS:FREQ? CHAN2")


voltage = 100
inputVoltage = []
outputVoltage = []

while voltage <= 5000:
    scope.write(f":CHAN1:SCAL {voltage/2}E-03")  # 20! ns/div
    scope.write(f":CHAN2:SCAL {voltage/2}E-03")  # 20! ns/div
    scope.write(f":WGEN:VOLT {voltage}E-03")  # voltage test
    inputVoltage.append(float(scope.query(":MEAS:VPP? CHAN2")))  # Ensure to convert to float
    outputVoltage.append(float(scope.query(":MEAS:VPP? CHAN1")))  # Ensure to convert to float
    time.sleep(0.5) # in seconds
    voltage += 100


for index in range(len(inputVoltage)):
    print(f"{inputVoltage[index]} : {outputVoltage[index]}")

# Plot the resulting temperatures
plt.figure()
plt.plot(inputVoltage, outputVoltage, label='N/A')
plt.xlabel('Input Voltage (Vpp)')
plt.ylabel('Output Voltage (Vpp)')
plt.title('Input RX_SIG to Output over Limiter')
plt.legend()

# Adjust the spacing between ticks
plt.xticks(np.arange(0, max(inputVoltage)+1000, 10))  # Modify step size if needed
plt.yticks(np.arange(0, max(outputVoltage)+1000, 10))  # Modify step size if needed
plt.ticklabel_format(style='plain', axis='both')  # Disable scientific notation

plt.savefig('limiter.png')
plt.show()

end_program()

exit()
