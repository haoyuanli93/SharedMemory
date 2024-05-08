import numpy as np
import logging
import psana
from collections import deque


def get_ds(run=None, exp=None, live=False, calib_dir=None):
    if not live:  # Run from offline data
        hutch = exp[:3]
        exp_dir = ''.join(['/cds/data/psdm/', hutch, '/', exp, '/xtc/'])
        dsname = ''.join(['exp=', exp, ':run=', str(run), ':smd:', 'dir=', exp_dir])
    else:  # Run on shared memeory
        dsname = 'shmem=psana.0:stop=no'
    if calib_dir is not None:
        psana.setOption('psana.calib-dir', calib_dir)
    return dsname


def get_logger(level='info'):
    if level == 'info':
        logging.basicConfig(level=logging.INFO)
    elif level == 'debug':
        logging.basicConfig(level=logging.DEBUG)
    return logging.getLogger(__name__)


def get_det_data(det, evt):
    """ Get relevant variable from a bunch of often-used detectors
    """
    if det.name == 'enc':
        x = det.data(evt)['lasDelay']
    elif 'ipm' in det.name:
        x = det.data(evt)['sum']
    else:  # assume epics detector
        x = det(evt)
    return x


class MovingAverage(object):
    """
    Args:
        n: n-moving average
        ts_len: length of the running average time series
        alpha: exponential average parameter. If None, linear average of length n is performed.
    """

    def __init__(self, n, alpha=None, ts_len=None, factor=1):
        self.n = n
        self.alpha = alpha
        self.ts_len = ts_len
        self.ravg = 0
        self.ravg_ts = deque(maxlen=self.ts_len)
        self.factor = factor

    def update_ravg(self, newData):
        if self.alpha is None:
            self.ravg = (newData + self.n * self.factor * self.ravg) / (self.n * self.factor + 1)
        else:
            self.ravg = self.alpha * newData + (1 - self.alpha) * self.ravg

    def update_ravg_ts(self, newData, needx=False):
        """ 
        Update self.ravg and self.ravg_ts
        needx: in case dummy x coordinates are needed for plotting
        """
        self.update_ravg(newData)
        if self.ts_len is not None:
            self.ravg_ts.append(self.ravg)
            if needx:
                self.ravg_tsx = np.arange(len(self.ravg_ts))

    def new_ts_len(self, newLen):
        self.ts_len = newLen
        self.ravg_ts = deque(maxlen=self.ts_len)
