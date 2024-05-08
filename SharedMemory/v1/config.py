import logging
import numpy as np

# General config
EXP = 'xpplw3319'
HUTCH = EXP[:3]
CALIBDIR = ''.join(['/cds/data/psdm/', HUTCH, '/', EXP, '/calib/'])
LIVE = False  # If LIVE is true, work with real time data. Otherwise, use existing data
UPDATERATE_CLIENT = 1  # how many shots to process before pushing to master
UPDATERATE = 1  # visualization update (in number of client pushes)
LOGLVL = logging.DEBUG
TOPIC = 'TOPIC'

# Detectors
DETNAME = 'jungfrau1M'
DETI0 = 'ipm2'
DETTT = 'tt'
DETX = 'enc'
DETY = 'ccm_E'

# Filters
FILT_I0 = [0, 1e6]
FILT_TT_FWHM = [0, 1e6]
FILT_TT_AMPL = [0, 1e6]

# Ana config
XBINS = np.arange(-10, 60, 0.4)  # time [ps]
YBINS = np.arange(-10, 60, 0.4)  # energy [keV]
ROI = [[0, 200], [0, 200]]
PHOT = True
PHOTON_ADU = 173.
RUNNING_AVERAGE = 3  # In mulitple of UPDATERATE_CLIENT. Set to 0 for infinite average
THRES = 40  # Pixel threshold
PHOTON_ADU = 173.  # for photonizing
PIX = 50  # um
