import threading
import _thread
import logging
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
import math as m
import numpy as np
import random

import magdwickahrs as mdw

from quaternion import Quaternion

import data_read


class FFS:
    def __init__(self, sleep=0.05):
        self.lock = threading.Lock()
        self.data = {}
        self.gyroscope = [0, 0, 0]
        self.sleep = sleep
        self.data_read = data_read.DataRead()
        self.data_read.calculate_beta_zeta()
        self.sleep = sleep
        self.filtr = mdw.MadgwickAHRS(sampleperiod=sleep, quaternion=Quaternion(1, 0, 0, 0), beta=self.data_read.beta,
                                      zeta=self.data_read.zeta)
        self.fig = plt.figure(figsize=plt.figaspect(2.))

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
            self.data = self.data_read.get_data()
            self.lock.release()
            logging.debug(self.gyroscope)
            time.sleep(self.sleep)

    def start_filtration(self):
        self.filtrationThread = threading.Thread(target=self.filtration)
        self.filtrationThread.start()
        logging.info('Filtration started')

    def filtration(self):
        while (True):
            self.lock.acquire()
            self.filtr.update(self.data['ACC0'], self.data['GYRO'], self.data['MAG'])
            ahrs = self.filtr.quaternion.to_euler_angles()
            #ahrs = self.filtr.quaternion.to_angle_axis()
            self.gyroscope = list(ahrs)
            self.lock.release()
            time.sleep(self.sleep)

    def start_visualization(self):
        self.visualizationThread = threading.Thread(target=self.visualization)
        self.visualizationThread.start()
        logging.info('Visualizations started')
        plt.show()

    def visualization(self):
        ax_1 = self.fig.add_subplot(211, projection='3d')
        ax_2 = self.fig.add_subplot(212)
        self.start_plottinng_position(self.fig, ax_1)
        self.start_plotting_angles(self.fig, ax_2)

    def start_plottinng_position(self, fig, ax):
        self.plotThread = _thread.start_new_thread(self.plotting, (fig, ax))

    def start_plotting_angles(self, fig, ax):
        start_time = time.time()
        self.plotThread_2 = _thread.start_new_thread(self.plotting_angles_time, (fig, ax, start_time))

    def plotting(self, fig, ax):
        logging.info('Plotting started')
        unit_vectors = np.eye(3)
        vec_zeros = np.zeros(3)

        colors_xyz = ['r', 'g', 'b']

        while True:
            self.lock.acquire()
            gyroscope = self.gyroscope
            self.lock.release()
            logging.debug(gyroscope)
            ax.clear()
            # note: calculate  rotation matrix
            R = np.matmul(np.matmul(self._Rz(gyroscope[0]), self._Ry(gyroscope[1])), self._Rz(gyroscope[2]))

            ax.quiver(vec_zeros, vec_zeros, vec_zeros, unit_vectors[0], unit_vectors[1], unit_vectors[2], color='grey',
                      linestyle='--')
            for u_vec, color_ in zip(unit_vectors, colors_xyz):
                rotated_vec = np.matmul(R, np.array([u_vec]).T)
                ax.quiver(0, 0, 0, rotated_vec[0], rotated_vec[1], rotated_vec[2], color=color_)

            ax.set_xlim([-1, 1])
            ax.set_ylim([-1, 1])
            ax.set_zlim([-1, 1])
            ax.set_zticks([-1, 0, 1])
            ax.set_yticks([-1, 0, 1])
            ax.set_xticks([-1, 0, 1])

            ax.legend(['unit vetors', 'x', 'y', 'z'], fontsize='x-small')
            fig.canvas.draw_idle()  # use draw_idle instead of draw
            time.sleep(self.sleep)

    def plotting_angles_time(self, fig, ax, started_time):
        colors_xyz = ['r', 'g', 'b']
        prev_elapsed_time = 0
        prev_gyro = [0, 0, 0]
        while True:
            self.lock.acquire()
            gyroscope = self.gyroscope
            self.lock.release()
            logging.debug(gyroscope)

            elapsed_time = time.time() - started_time
            for gyro_ax, prev_gyro_ax, color_ in zip(gyroscope, prev_gyro, colors_xyz):
                ax.plot([prev_elapsed_time, elapsed_time], [np.degrees(prev_gyro_ax), np.degrees(gyro_ax)],
                        '.-', color=color_, linewidth=1, markersize=1)

            prev_elapsed_time = elapsed_time
            prev_gyro = gyroscope


            ax.set_title("Angles in time")
            ax.set_xlabel("Time [s]")
            ax.set_ylabel("Angles [deg]")

            ax.grid(True)
            ax.legend(["roll", "pitch", 'yaw'], loc=3, fontsize='x-small')
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
