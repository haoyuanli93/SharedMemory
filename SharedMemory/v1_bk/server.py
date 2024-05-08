"""
As explained in the 'ProjectDescription.md' a few classes are created here to realize the function
that I would like to have.

Here, aside from those specified in the md file, I have a few other requirement regarding the algorithm.

1. You must understand every step of the algorithm.
2. The motion must be completely predictable to avoid moving beyond the limit of the motor.
3. There must not be any attempt to move the motor beyond the limit. We must have a check of the motor motion before
    moving it.
    i.e., we should never ask the motor to move beyond the limit and let the XPP control system to stop it since it is
    beyond the limit.

    This is because there is no guarantee that the XPP motor control system can work perfectly to
    protect the motor and the crystal and we know that the control system sometimes has un-predictable behavior.
    If our algorithm damages any of them, it is our fault. Therefore, we would rather
    do nothing than do something wrong. Therefore, our operation must be as conservative as possible.

    On the other hand, if we ask the motor to move to a location that we know within the limit, but somehow XPP
    controller is not working properly and damage something, it is okay. It is XPP controller's fault.
4. Always check if the motor has stopped or not before sending the next motion command. Do not rely on XPP control
    system to do this. You can overwhelm the system by sending commandline too frequently.
5. After the motor stopped, wait for 1 second before moving the motor.
6. Implement the functionality to stop motor motion at anytime required by the operator.Or at least keep this in mind
    that the algorithm can always do something stupid and it is us that should be blamed if that happens and lead to the
    damage of the equipment and the stop of the beamtime.
7. Do not use any package aside from the most common ones, including
    h5py, numpy, scipy, matplotlib. tinker, numba

    a. Because the XPP controller has a special python environment which we are not permitted to install new things as
        we wish
    b. We have limited calcluation resource. By implement everything by ourselves, we have a better understanding and
        estimation of the resource we used in the process.
    c. By implementing everything, we understand better what we are doing. With this, I hope it can protect the
        equipment better.
"""

# import sys
from psmon import publish
from psmon.plots import XYPlot, Image, MultiPlot
# import numpy as np
# import collections
import time

import config
import utils
from mpi_data import mpidata

# user parameters
updaterate = 1  # plot-push frequency, measured in "client updates"


class Server(object):
    def __init__(self, nClients):
        self.nClients = nClients
        self.run()
        return

    def run(self):
        while True:
            print('**** New Run ****')
            nClientsInRun = self.nClients
            myplotter = Plotter()
            while nClientsInRun > 0:
                md = mpidata()
                md.recv()
                if md.small.endrun:
                    nClientsInRun -= 1
                else:
                    myplotter.update(md)
            print('**** End Run ****')


class Plotter:
    def __init__(self):
        self.nupdate = 0
        self.lasttime = None

        self.nevents = 0
        self.sum_img = 0
        self.sum_imgThres = 0
        self.sum_imgPhot = 0

        if config.RUNNING_AVERAGE:
            self.ravg = utils.MovingAverage(config.RUNNING_AVERAGE, factor=config.UPDATERATE_CLIENT)
            self.ravg_phot = utils.MovingAverage(config.RUNNING_AVERAGE, factor=config.UPDATERATE_CLIENT)

            print('Running average intialized for {} images'.format(
                config.RUNNING_AVERAGE * config.UPDATERATE_CLIENT))
        return

    def update(self, md):
        self.nupdate += 1

        self.img = md.img
        self.imgThres = md.imgThres
        try:
            self.imgPhot = md.imgPhot
        except:
            self.imgPhot = None

        # sums since running
        self.nevents += md.small.nevents
        self.sum_img += md.sum_img
        self.sum_imgThres += md.sum_imgThres
        if self.imgPhot is not None:
            self.sum_imgPhot += md.sum_imgPhot

        # running averages
        if config.RUNNING_AVERAGE:
            self.ravg.update_ravg(self.imgThres)
            self.avg_im = self.ravg.ravg
            if self.imgPhot is not None:
                self.ravg_phot.update_ravg(self.imgPhot)
                self.avg_phot = self.ravg_phot.ravg
        else:
            self.avg_im = self.sum_imgThres / self.nevents
            if self.imgPhot is not None:
                self.avg_phot = self.sum_imgPhot / self.nevents

        # push plots
        if self.nupdate % config.UPDATERATE == 0:
            self.update_plots()
        if self.lasttime is not None:
            print('Client updates {}, Server received {} events, Rate {}'.format(
                self.nupdate, self.nevents, (self.nevents - self.lastnevents) / (time.time() - self.lasttime)))
        self.lasttime = time.time()
        self.lastnevents = self.nevents
        return

    def update_plots(self):
        # Plot 1:
        imgThres = Image(self.nupdate, "Current image (thres)", self.imgThres,
                         xlabel='horizontal (pixel)', ylabel='vertical (pixel)', aspect_ratio=1)
        imgThres_sum = Image(self.nupdate, "Average image (thres)", self.avg_im,
                             xlabel='horizontal (pixel)', ylabel='vertical (pixel)', aspect_ratio=1)
        p1 = MultiPlot(self.nupdate, 'Image', ncols=2)
        p1.add(imgThres)
        p1.add(imgThres_sum)

        # Plot 2:
        if self.imgPhot is not None:
            phot = Image(self.nupdate, "Photons", self.imgPhot,
                         xlabel='horizontal (pixel)', ylabel='vertical (pixel)', aspect_ratio=1)
            phot_sum = Image(self.nupdate, "Average photons", self.avg_phot,
                             xlabel='horizontal (pixel)', ylabel='vertical (pixel)', aspect_ratio=1)
            p2 = MultiPlot(self.nupdate, 'Photon', ncols=2)
            p2.add(phot)
            p2.add(phot_sum)

        publish.send(config.TOPIC, p1)
        if self.imgPhot is not None:
            publish.send(config.TOPIC + '_PHOT', p2)
        return
