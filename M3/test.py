
import pyvisa as visa
rm = visa.ResourceManager(r'C:\WINDOWS\system32\visa64.dll')
print(rm)
print(rm.list_resources('TCPIP0::?*'))

try:
    #Connect to the instruments
    waveform =  rm.open_resource('TCPIP0::192.168.0.253::5025::SOCKET')
    
    #Set up the digital multiwaveform IO configuration
    waveform.timeout = 20000

    # Define string terminations
    waveform.write_termination = '\n'
    waveform.read_termination = '\n'

    waveform.write("")
    
except(KeyboardInterrupt):
    print('Keyboard Interrupted execution!')