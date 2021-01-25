import threading
import _thread
import logging
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
import math as m
import numpy as np

import magdwickahrs as mdw
# For fake data generation
import random

import data_read


class FFS:
    def __init__(self, sleep=0.05):
        self.lock = threading.Lock()
        self.data = {}
        self.gyroscope = [0, 0, 0]
        self.sleep = sleep
        self.filtr = mdw.MadgwickAHRS(sampleperiod=sleep, quaternion=None, beta=None, zeta=None)

        self.start_acquisition()
        self.start_filtration()
        self.start_visualization()

    def start_acquisition(self):
        self.data_read = data_read.DataRead()
        self.acquisitionThread = threading.Thread(target=self.acquisition)
        self.acquisitionThread.start()
        logging.info('Acquisition started')

    def acquisition(self):
        while (True):
            self.lock.acquire()
            #            self.data = {'ACC0': [random.randrange(1000), random.randrange(1000), random.randrange(1000)],
            #                    'GYRO': [random.randrange(1000), random.randrange(1000), random.randrange(1000)],
            #                    'MAG': [random.randrange(1000), random.randrange(1000), random.randrange(1000)] }
            self.data = self.data_read.get_data()
            # self.gyroscope[0] += random.randint(-10, 10)
            # self.gyroscope[1] += random.randint(-10, 10)
            # self.gyroscope[2] += random.randint(-10, 10)
            self.lock.release()
            logging.debug(self.gyroscope)
            time.sleep(self.sleep)

    def start_filtration(self):
        self.filtrationThread = threading.Thread(target=self.filtration)
        self.filtrationThread.start()
        logging.info('Filtration started')

    def filtration(self):
        self.lock.acquire()
        self.filtr.update(self.data['ACC0'], self.data['GYRO'], self.data['MAG'])
        ahrs = self.filtr.quaternion.to_euler_angles()
        # ahrs = self.filtr.quaternion.to_angle_axis()
        self.gyroscope = list(ahrs)
        self.lock.release()

    def start_visualization(self):
        self.visualizationThread = threading.Thread(target=self.visualization)
        self.visualizationThread.start()
        logging.info('Visualizations started')

    def visualization(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        self.plotThread = _thread.start_new_thread(self.plotting, (fig, ax))
        plt.show()

    def plotting(self, fig, ax):
        logging.info('Plotting started')
        unit_vectors = np.eye(3)
        vec_zeros = np.zeros(3)

        while True:
            self.lock.acquire()
            gyroscope = self.gyroscope
            self.lock.release()
            logging.debug(gyroscope)
            ax.clear()

            # note: calculate  rotation matrix
            R = self._Rz(gyroscope[0]) * self._Ry(gyroscope[1]) * self._Rx(gyroscope[2])

            ax.quiver(vec_zeros, vec_zeros, vec_zeros, unit_vectors[0], unit_vectors[1], unit_vectors[2], color='grey',
                      linestyle='--')
            for u_vec in unit_vectors:
                rotated_vec = R * np.array([u_vec]).T
                ax.quiver(0, 0, 0, rotated_vec[0], rotated_vec[1], rotated_vec[2], color='red')

            ax.set_xlim([-1, 1])
            ax.set_ylim([-1, 1])
            ax.set_zlim([-1, 1])
            ax.set_zticks([-1, 0, 1])
            ax.set_yticks([-1, 0, 1])
            ax.set_xticks([-1, 0, 1])
            fig.canvas.draw_idle()  # use draw_idle instead of draw

            time.sleep(self.sleep)

    @staticmethod
    def _Rx(theta):
        return np.array([[1, 0, 0],
                         [0, m.cos(theta), -m.sin(theta)],
                         [0, m.sin(theta), m.cos(theta)]])

    @staticmethod
    def _Ry(theta):
        return np.array([[m.cos(theta), 0, m.sin(theta)],
                         [0, 1, 0],
                         [-m.sin(theta), 0, m.cos(theta)]])

    @staticmethod
    def _Rz(theta):
        return np.array([[m.cos(theta), -m.sin(theta), 0],
                         [m.sin(theta), m.cos(theta), 0],
                         [0, 0, 1]])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ffs = FFS(sleep=0.5)
