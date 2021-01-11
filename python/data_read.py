import serial
import time

ser = serial.Serial()
ser.baudrate = 115200
ser.port = 'COM1'
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE
ser.bytesize = serial.EIGHTBITS
ser.timeout = 1

if ser.isOpen():
    ser.close()
ser.open()
while ser.inWaiting() > 0:
    line = ser.readline()
    print(line)
    time.sleep(0.05)   
ser.close()
