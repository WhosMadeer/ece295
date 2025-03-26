#!/usr/bin/env python
"""Subsystem A unit testing script.
This script measures the frequency response of the pre-mixer BPF."""

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
scope.write(":TIMebase:SCAL +5.0E-05")  # 50! us/div
scope.write(":CHAN1:COUP DC")
scope.write(":CHAN2:COUP DC")

# TODO: add the response plot and output

print("Ready to start testing!")
user_prompt()


scope.query(":MEAS:VPP? CHAN1")
scope.query(":MEAS:VPP? CHAN2")
time.sleep(5)
end_program()
