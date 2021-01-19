# This is a multithread program for data acquisition, filtration and visualization
import threading
import _thread
import logging
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

# For fake data generation
import random

import data_read


class FFS:
    def __init__(self, sleep=0.05):
        self.lock = threading.Lock()
        self.data = {}
        self.gyroscope = [0, 0, 0]
        self.sleep = sleep

        self.start_acquisition()
        # self.start_filtration()
        self.start_visualization()

    def start_acquisition(self):
        self.data_read = data_read.DataRead()
        self.acquisitionThread = threading.Thread(target=self.acquisition)
        self.acquisitionThread.start()
        logging.info('Acquisition started')

    def acquisition(self):
        while(True):
            self.lock.acquire()
            self.data = self.data_read.get_data()
            self.gyroscope[0] += random.randint(-10, 10)
            self.gyroscope[1] += random.randint(-10, 10)
            self.gyroscope[2] += random.randint(-10, 10)
            self.lock.release()
            logging.debug(self.gyroscope)
            time.sleep(self.sleep)

    def start_filtration(self):
        self.filtrationThread = threading.Thread(target=self.filtration)
        self.filtrationThread.start()
        logging.info('Filtration started')


    def filtration(self):
        # TODO
        pass

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
        while True:
            self.lock.acquire()
            gyroscope = self.gyroscope
            self.lock.release()
            logging.debug(gyroscope)
            ax.clear()
            ax.quiver(0, 0, 0, gyroscope[0], gyroscope[1], gyroscope[2])
            ax.set_xlim([-1, 1])
            ax.set_ylim([-1, 1])
            ax.set_zlim([-1, 1])
            fig.canvas.draw_idle()  # use draw_idle instead of draw
            time.sleep(self.sleep)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ffs = FFS(sleep=0.5)
