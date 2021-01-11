import serial
import time

ser = serial.Serial()
ser.baudrate = 115200
ser.port = 'COM1'
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE
ser.bytesize = serial.EIGHTBITS
ser.timeout = 1

ACC0_X = []
ACC0_Y = []
ACC0_Z = []
GYRO_X = []
GYRO_Y = []
GYRO_Z = []
ACC1_X = []
ACC1_Y = []
ACC1_Z = []
MAG_X = []
MAG_Y = []
MAG_Z = []

if ser.isOpen():
    ser.close()
ser.open()
while ser.inWaiting() > 0:
    line = ser.readline()
    print(line)
    sensors = line.split(b';')
    ACC0_X.append(int(sensors[0].split(b',')[0].strip(b' ')))
    ACC0_Y.append(int(sensors[0].split(b',')[1].strip(b' ')))
    ACC0_Z.append(int(sensors[0].split(b',')[2].strip(b' ')))
    GYRO_X.append(int(sensors[1].split(b',')[0].strip(b' ')))
    GYRO_Y.append(int(sensors[1].split(b',')[1].strip(b' ')))
    GYRO_Z.append(int(sensors[1].split(b',')[2].strip(b' ')))
    ACC1_X.append(int(sensors[2].split(b',')[0].strip(b' ')))
    ACC1_Y.append(int(sensors[2].split(b',')[1].strip(b' ')))
    ACC1_Z.append(int(sensors[2].split(b',')[2].strip(b' ')))
    MAG_X.append(int(sensors[3].split(b',')[0].strip(b' ')))
    MAG_Y.append(int(sensors[3].split(b',')[1].strip(b' ')))
    MAG_Z.append(int(sensors[3].split(b',')[2].strip(b' ')))
    time.sleep(0.05)   
ser.close()
