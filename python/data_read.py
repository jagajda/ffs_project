import serial
import time
import threading


class DataRead:
    def __init__(self):
        self.ser = self.get_serial()
        self.ACC0_X = []
        self.ACC0_Y = []
        self.ACC0_Z = []
        self.GYRO_X = []
        self.GYRO_Y = []
        self.GYRO_Z = []
        self.ACC1_X = []
        self.ACC1_Y = []
        self.ACC1_Z = []
        self.MAG_X = []
        self.MAG_Y = []
        self.MAG_Z = []
        self.lock = threading.Lock()

    def get_data(self):
        self.lock.acquire()
        self.read_data()
        response = {'ACC0': [self.ACC0_X, self.ACC0_Y, self.ACC0_Z],
                    'GYRO': [self.GYRO_X, self.GYRO_Y, self.GYRO_Z],
                    'MAG': [self.MAG_X, self.MAG_Y, self.MAG_Z],
                    'ACC1': [self.ACC1_X, self.ACC1_Y, self.ACC1_Z]}
        self.lock.release()
        return response

    def get_serial(self):
        _serial = serial.Serial()
        _serial.baudrate = 115200
        _serial.port = 'COM3'
        _serial.parity = serial.PARITY_NONE
        _serial.stopbits = serial.STOPBITS_ONE
        _serial.bytesize = serial.EIGHTBITS
        _serial.timeout = 1
        return _serial

    def read_data(self):
        self.ser.open()
        time.sleep(0.05)
        line = self.ser.readline()
        print('Reading data, read line:')
        print(line)
        sensors = line.split(b';')
        self.lock.acquire()
        self.ACC0_X.append(int(sensors[0].split(b',')[0].strip(b' ')))
        self.ACC0_Y.append(int(sensors[0].split(b',')[1].strip(b' ')))
        self.ACC0_Z.append(int(sensors[0].split(b',')[2].strip(b' ')))
        self.GYRO_X.append(int(sensors[1].split(b',')[0].strip(b' ')))
        self.GYRO_Y.append(int(sensors[1].split(b',')[1].strip(b' ')))
        self.GYRO_Z.append(int(sensors[1].split(b',')[2].strip(b' ')))
        self.ACC1_X.append(int(sensors[2].split(b',')[0].strip(b' ')))
        self.ACC1_Y.append(int(sensors[2].split(b',')[1].strip(b' ')))
        self.ACC1_Z.append(int(sensors[2].split(b',')[2].strip(b' ')))
        self.MAG_X.append(int(sensors[3].split(b',')[0].strip(b' ')))
        self.MAG_Y.append(int(sensors[3].split(b',')[1].strip(b' ')))
        self.MAG_Z.append(int(sensors[3].split(b',')[2].strip(b' ')))
        self.lock.release()
        time.sleep(0.05)   
        self.ser.close()

    def run(self):
        if ser.isOpen():
            ser.close()
