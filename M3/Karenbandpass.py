#!/usr/bin/env python
"""Subsystem A unit testing script.
This script measures the frequency response of the pre-mixer BPF."""

import matplotlib.pyplot as plt 
import numpy as np
import math
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

# # write power supply
# supply.write("VOLT 5, (@2)")
# supply.write("CURR 0.005, (@2)")
# print(supply.query("VOLT? (@2)"))

# supply.write("OUTP 2, (@2)")

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
fxngen.write("SOUR1:VOLTage:HIGH +0.5")
fxngen.write("SOUR1:VOLTage:LOW -0.5")
fxngen.write("SOUR1:PHASe:SYNC")
fxngen.write("SOUR1:PHASe +0.0")
fxngen.write("OUTPut1 ON")

fxngen.write("SOUR2:FUNCtion SIN")
fxngen.write("SOUR1:FREQuency +1E+05")  # * 100 KHz frequency
fxngen.write("SOUR2:VOLTage:HIGH +0.5")
fxngen.write("SOUR2:VOLTage:LOW -0.5")
fxngen.write("SOUR2:PHASe:SYNC")
fxngen.write("SOUR2:PHASe +90.0")
fxngen.write("OUTPut2 ON")

# Setup acquisition
scope.write(":TIMebase:SCAL +1.0E-06")  # 10! us/div
scope.write(":CHAN1:COUP AC")
scope.write(":CHAN2:COUP AC")


# TODO: add the response plot and output

print("Ready to start testing!")
user_prompt()


scope.query(":MEAS:VPP? CHAN1")
scope.query(":MEAS:VPP? CHAN2")
scope.query(":MEAS:FREQ? CHAN1")
scope.query(":MEAS:FREQ? CHAN2")

frequencies = np.logspace(np.log10(1e6), np.log10(2e7), num=100)
RX_db = []

for freq in frequencies:
    freq_str = f"{freq:.2E}"  # SCPI prefers scientific notation
    fxngen.write(f"SOUR1:FREQ {freq_str}")
    time.sleep(0.5)  # Allow time for signal to stabilize

    RX_vpp = float(scope.query(":MEAS:VPP? CHAN1"))

    db = 20 * math.log10(RX_vpp)
    
    RX_db.append(db)

# Plot and save the result
plt.figure()
plt.semilogx(frequencies, RX_db, label="RX dB (CH1)")
plt.xlabel("Frequency (Hz)")
plt.ylabel("RX Gain (dB)")
plt.title("Frequency Response of Bandpass")
plt.legend()
plt.grid(True, which="both", ls="--")
plt.savefig("bpf_response.png")
plt.show()


end_program()
exit()
