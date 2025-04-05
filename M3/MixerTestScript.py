#!/usr/bin/env python
"""Subsystem A unit testing script.
This script measures the frequency response of the pre-mixer BPF."""


import matplotlib.pyplot as plt 
from numpy import *
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
    fxngenRF.write("OUTPut1 OFF")
    fxngenRF.write("OUTPut2 OFF")
    fxngenLO.write("OUTPut1 OFF")
    fxngenLO.write("OUTPut2 OFF")
    supply.write("OUTP 0, (@2)")
    scope.close()
    fxngenRF.close()
    fxngenLO.close()
    supply.close()
    print("closed connection")
    exit()

def check_scales():
    scale1 = scope.query(':CHAN1:SCAL?')
    scale2 = scope.query(':CHAN2:SCAL?')

    if (scale1 != scale2):
        print('The scales of the 2 channels do not match.')
        end_program()

# Open instrument connection(s)
rm = pyvisa.ResourceManager(r"C:\WINDOWS\system32\visa64.dll")
print(rm)
print(rm.list_resources("TCPIP0::?*"))

"""Connect to the different devices"""
supply = rm.open_resource("TCPIP0::192.168.0.251::5025::SOCKET")
scope = rm.open_resource("TCPIP0::192.168.0.253::hislip0::INSTR")
fxngenRF = rm.open_resource("TCPIP0::192.168.0.254::5025::SOCKET")
fxngenLO = rm.open_resource("TCPIP0::192.168.0.252::5025::SOCKET")

""" Set up the IO configuration"""
supply.timeout = 10000  # 10s
scope.timeout = 10000  # 10s
fxngenRF.timeout = 10000  # 10s
fxngenLO.timeout = 10000  # 10s


# Define string terminations
supply.write_termination = "\n"
supply.read_termination = "\n"
scope.write_termination = "\n"
scope.read_termination = "\n"
fxngenRF.write_termination = "\n"
fxngenRF.read_termination = "\n"
fxngenLO.write_termination = "\n"
fxngenLO.read_termination = "\n"


# Get ID info
print("supply ID string:\n  ", supply.query("*IDN?"), flush=True)
print("Connected to oscilloscope:", scope.query("*IDN?"), flush=True)
print("Connected to function generator 1:", fxngenRF.query("*IDN?"), flush=True)
print("Connected to function generator 2:", fxngenLO.query("*IDN?"), flush=True)

# write power supply
supply.write("VOLT 5, (@2)")
supply.write("CURR 0.005, (@2)")
print(supply.query("VOLT? (@2)"))

supply.write("OUTP 2, (@2)")

# Set probe scaling to 1:1
scope.write("CHANnel1:PROBe +1.0")
scope.write("CHANnel2:PROBe +1.0")

print("Connect the mixer to the machines to start testing!")
user_prompt()


"""
Set up the waveform generator 1 for LRF input

"""
# Set waveform generator output impedance to high Z
fxngenRF.write("OUTPUT1:LOAD INF")
fxngenRF.write("OUTPUT2:LOAD INF")
fxngenRF.write("UNIT:ANGL DEG")

# Setup waveform generator
fxngenRF.write("SOUR1:FUNCtion SIN")
fxngenRF.write("SOUR1:FREQuency +8.0E+06")  # * 8 MHz frequency
fxngenRF.write("SOUR1:VOLTage:HIGH +0.7")
fxngenRF.write("SOUR1:VOLTage:LOW -0.7")
fxngenRF.write("SOUR1:PHASe:SYNC")
fxngenRF.write("SOUR1:PHASe +0.0")
fxngenRF.write("OUTPut1 ON")

fxngenRF.write("SOUR2:FUNCtion SIN")
fxngenRF.write("SOUR2:FREQuency +8.0E+06")  # * 8 MHz frequency
fxngenRF.write("SOUR2:VOLTage:HIGH +0.7")
fxngenRF.write("SOUR2:VOLTage:LOW -0.7")
fxngenRF.write("SOUR2:PHASe:SYNC")
fxngenRF.write("SOUR2:PHASe +180.0")
fxngenRF.write("OUTPut2 ON")

"""
Set up the waveform generator 2 for LO input

"""
# Set waveform generator output impedance to high Z
fxngenLO.write("OUTPUT1:LOAD INF")
fxngenLO.write("OUTPUT2:LOAD INF")
fxngenLO.write("UNIT:ANGL DEG")

# Setup waveform generator
fxngenLO.write("SOUR1:FUNCtion SIN")
fxngenLO.write("SOUR1:FREQuency +7.904E+06")  # * 8 MHz frequency
fxngenLO.write("SOUR1:VOLTage:HIGH +1.65")
fxngenLO.write("SOUR1:VOLTage:LOW -1.65")
fxngenLO.write("SOUR1:PHASe:SYNC")
fxngenLO.write("SOUR1:PHASe +0.0")
fxngenLO.write("OUTPut1 ON")

fxngenLO.write("SOUR2:FUNCtion SIN")
fxngenLO.write("SOUR2:FREQuency +7.904E+06")  # * 8 MHz frequency
fxngenLO.write("SOUR2:VOLTage:HIGH +1.65")
fxngenLO.write("SOUR2:VOLTage:LOW -1.65")
fxngenLO.write("SOUR2:PHASe:SYNC")
fxngenLO.write("SOUR2:PHASe +180.0")
fxngenLO.write("OUTPut2 ON")


# Setup acquisition
scope.write(":TIMebase:SCAL +1.0E-06")  # 10! us/div
scope.write(":CHAN1:COUP AC")
scope.write(":CHAN2:COUP AC")



# TODO: add the response plot and output

print("Ready to start testing!")
user_prompt()
check_scales()

scope.query(":MEAS:VPP? CHAN1")
scope.query(":MEAS:VPP? CHAN2")
scope.query(":MEAS:FREQ? CHAN1")
scope.query(":MEAS:FREQ? CHAN2")


# sean hum code
# phdiff = float(scope.query(':MEAS:PHASe? CHAN1'))
# print('Measured phase shift between I and Q for 10 kHz message signal:', phdiff, 'deg')

# if (phdiff > 0):
#     print('WARNING: the phase shift is leading when it should be lagging. Ensure the function')
#     print('generator and oscilloscope are connected as shown in the wiring diagram.')
# else:
#     print('Q is lagging I as expected.')
# print('About to initiate frequency sweep.')
# user_prompt()

I_phase = float(scope.query(':MEAS:PHASe? CHAN1'))
Q_phase = float(scope.query(':MEAS:PHASe? CHAN2'))

print("I_phase =", I_phase)
print("Q_phase =", Q_phase)

N = 61
fm = logspace(3, 6, N)

# Plot and save the result
plt.figure()
plt.plot(fm, I_phase, label="I_phase")
plt.plot(fm, Q_phase, label="Q_phase")

plt.xlabel("Message frequency [Hz]")
plt.ylabel("Phase shift between I and Q [deg]")
plt.title("Frequency Response of IQ Amplifier")
plt.legend()
plt.grid(True, which="both", ls="--")
plt.savefig("amp_response.png")
plt.savefig('balance_phase.png')
plt.show()

end_program()
exit()