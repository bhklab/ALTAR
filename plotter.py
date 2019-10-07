import os
import time
import numpy as np
# import matplotlib
# matplotlib.use('Qt5Agg')
# import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget
import pyqtgraph as pg

print("done importing")


class IndexTracker(object):
    ''' Class which handles scrolling through the image stack.
        adapted from this example:
        https://matplotlib.org/gallery/animation/image_slices_viewer.html
    '''
    def __init__(self, ax):
        self.ax = ax
        ax.set_title('Run label.py to begin')

    def new_img_stack(self, img) :
        self.X = img
        self.z_slices, x_len, y_len = np.shape(self.X)
        # self.ind = self.z_slices//2
        self.ind = 0

        self.im = self.ax.imshow(self.X[self.ind, :, :])
        # time.sleep(1)
        self.update()

    def onscroll(self, event):
        print("%s %s" % (event.button, event.step))
        if event.button == 'up':
            self.ind = (self.ind + 1) % self.z_slices
        else:
            self.ind = (self.ind - 1) % self.z_slices
        self.update()

    def on_key(self, event):
        print('you pressed', event.key, event.xdata, event.ydata)
        if event.key == 'up':
            self.ind = (self.ind + 1) % self.z_slices
        else:
            self.ind = (self.ind - 1) % self.z_slices
        self.update()

    def update(self):
        self.im.set_data(self.X[:, :, self.ind])
        self.ax.set_ylabel('slice %s' % self.ind)
        self.im.axes.figure.canvas.draw()
        plt.pause(1)



class Watcher():
    def __init__(self):
        # Initiate the directory in which to "listen" for images
        self.dir = "/cluster/home/carrowsm/logs/label"
        self.last_dir = os.listdir(self.dir)

        # Initiate GUI
        # self.app = QApplication([])
        # self.w = QWidget()
        # self.w.show()
        # im = p

        # Initiate a blank figure
        self.im = pg.ImageItem()
        self.im.show()
        # self.fig, self.ax = self.blank_fig()
        # self.tracker = IndexTracker(self.ax)
        # # self.fig.canvas.mpl_connect('scroll_event', self.tracker.onscroll)
        # self.fig.canvas.mpl_connect('key_press_event', self.tracker.on_key)

        # self.app.exec_()


    def blank_fig(self) :
        # Get an instance of Figure object
        fig = plt.figure(figsize=[4, 4])
        ax = fig.add_subplot(1,1,1)
        ax.set_xlabel('x-axis pixels')
        ax.set_ylabel('y-axis pixels')
        ax.set_title('Patient Scan')
        # plt.ion() # Initiate interactive mode
        plt.show()
        plt.pause(1)
        # plt.ioff()
        return fig, ax

    def update_plot(self, nd_array, patient_id) :
        # self.ax.clear()  # Clear the current figure
        # # self.ax.imshow(nd_array[50, :, :])
        # self.ax.set_title('Patient {}'.format(patient_id))
        # # plt.draw()
        # self.tracker.new_img_stack(nd_array)
        # # plt.pause(1)
        self.im.setImage(nd_array)



    def run(self):
        while True:
            # Get a list containing all the files currently in the directory
            current_dir = os.listdir(self.dir)
            # print(current_dir)

            if current_dir == self.last_dir :
                # The directory is the same as last iteration
                time.sleep(0.001)
                continue
            else :
                if len(current_dir) > 0 :
                    # Something in the directory changed
                    print("Something changed")
                    time.sleep(5)   # Allow file to be fully-written

                    # Load the new image
                    image_file = os.path.join(self.dir, current_dir[0])
                    image = np.load(image_file, mmap_mode='r')
                    '''Note: Using memmap_mode='r' allows numpy to load the npy file as
                    a memory-mapped array, meaning we can load subsets of the array
                    directly from disk'''

                    # Refresh the plot with the new image
                    self.update_plot(image, current_dir[0].split("_")[0])

                    # Update the state of the last directory
                    self.last_dir = current_dir
                else :
                    # If the directory is empty, wait until it has something in it
                    continue


if __name__ == '__main__':
    w = Watcher()

    try :
        w.run()
    except KeyboardInterrupt :
        print( "\nClosing Plotter")
        exit()
