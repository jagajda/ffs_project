import serial
import time
import threading
import numpy as np

CALIBRATION = True

ACC_OFFSET = [-16, -38, 34]   # [mg]
GYRO_OFFSET = [0.112, -3.368, 2.108]    # [dps]
MAG_OFFSET = [7, 1, -363] # [mgauss]
MAG_COEFFS = [[1.206, 0.093, 0.025],
              [0.093, 1.214, -0.005],
              [0.025, -0.005, 1.2450]]
              
  
class DataRead:
    def __init__(self):
        self.ser = self.get_serial()
        self.ACC0_X = 0
        self.ACC0_Y = 0
        self.ACC0_Z = 0
        self.GYRO_X = 0
        self.GYRO_Y = 0
        self.GYRO_Z = 0
        self.ACC1_X = 0
        self.ACC1_Y = 0
        self.ACC1_Z = 0
        self.MAG_X = 0
        self.MAG_Y = 0
        self.MAG_Z = 0
        self.lock = threading.Lock()

    def get_data(self):
        self.lock.acquire()
        self.read_data()
        if CALIBRATION == True:
            self.calibrate_data()
        self.normalize_data()
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
        line = self.ser.readline()
        sensors = line.split(b';')
        #while self.ser.in_waiting > 0:
        self.ACC0_X = int(sensors[0].split(b',')[0].strip(b' '))
        self.ACC0_Y = int(sensors[0].split(b',')[1].strip(b' '))
        self.ACC0_Z = int(sensors[0].split(b',')[2].strip(b' '))
        self.GYRO_X = int(sensors[1].split(b',')[0].strip(b' '))
        self.GYRO_Y = int(sensors[1].split(b',')[1].strip(b' '))
        self.GYRO_Z = int(sensors[1].split(b',')[2].strip(b' '))
        self.ACC1_X = int(sensors[2].split(b',')[0].strip(b' '))
        self.ACC1_Y = int(sensors[2].split(b',')[1].strip(b' '))
        self.ACC1_Z = int(sensors[2].split(b',')[2].strip(b' '))
        self.MAG_X = int(sensors[3].split(b',')[0].strip(b' '))
        self.MAG_Y = int(sensors[3].split(b',')[1].strip(b' '))
        self.MAG_Z = int(sensors[3].split(b',')[2].strip(b' '))
        time.sleep(0.05)   
        self.ser.close()

    def calibrate_data(self):
        # Accelerometer0 calibration
        self.ACC0_X = self.ACC0_X - ACC_OFFSET[0]
        self.ACC0_Y = self.ACC0_Y - ACC_OFFSET[1]
        self.ACC0_Z = self.ACC0_Z - ACC_OFFSET[2]
        
        # Gyroscope calibration
        self.GYRO_X = self.GYRO_X - GYRO_OFFSET[0]
        self.GYRO_Y = self.GYRO_Y - GYRO_OFFSET[1]
        self.GYRO_Z = self.GYRO_Z - GYRO_OFFSET[2]
        
        # Magnetometer calibration
        mag_uncal = np.array([self.MAG_X, self.MAG_Y, self.MAG_Z])
        mag_bias = np.array(MAG_OFFSET)
        mag_coeefs = np.array(MAG_COEFFS)
        mag_cal = np.dot(np.linalg.inv(mag_coeefs), np.transpose((mag_uncal - mag_bias)))
        self.MAG_X = mag_cal[0]
        self.MAG_Y = mag_cal[1]
        self.MAG_Z = mag_cal[2]
        
    def normalize_data(self):
        self.ACC0_X = self.ACC0_X / 1000    #value in [g]
        self.ACC0_Y = self.ACC0_Y / 1000    #value in [g]
        self.ACC0_Z = self.ACC0_Z / 1000    #value in [g]
        
        self.GYRO_X = self.GYRO_X * np.pi / 180 #value in [radians per second]
        self.GYRO_Y = self.GYRO_Y * np.pi / 180 #value in [radians per second]
        self.GYRO_Z = self.GYRO_Z * np.pi / 180 #value in [radians per second]
        
        self.ACC1_X = self.ACC0_X / 1000    #value in [g]
        self.ACC1_Y = self.ACC0_Y / 1000    #value in [g]
        self.ACC1_Z = self.ACC0_Z / 1000    #value in [g]
        
        self.MAG_X = self.MAG_X / 1000  #value in [gauss]
        self.MAG_Y = self.MAG_Y / 1000  #value in [gauss]
        self.MAG_Z = self.MAG_Z / 1000  #value in [gauss]
        
    def calculate_beta_zeta(self):
        gyro = np.array(GYRO_OFFSET)
        gyro_error = np.square(np.sum(gyro**2))
        self.beta = np.square(3.0 / 4.0) * gyro_error
        self.zeta = np.square(3.0 / 4.0) * gyro_error / 50
        
    def run(self):
        if ser.isOpen():
            ser.close()
