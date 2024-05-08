import sys
import numpy as np
import time
import psana as ps
import logging

from ImgAlgos.PyAlgos import photons
import psana as ps

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

sys.path.append('../common')
import config
import utils
from mpi_data import mpidata
from bin_fun import Bin_2d

sys.path.append('/cds/home/e/espov/lcls_software_tools/smalldata_tools/')
from smalldata_tools import DetObject as dobj
from smalldata_tools.SmallDataUtils import defaultDetectors, getUserData
from smalldata_tools.ana_funcs import roi_rebin

logger = logging.getLogger(__name__)


class Worker(object):
    def __init__(self, run=None, rank=None):
        dsname = utils.get_ds(run=run,
                              exp=config.EXP,
                              live=config.LIVE,
                              calib_dir=config.CALIBDIR)
        logger.info('DATASOURCE: {}'.format(dsname))
        self.ds = ps.DataSource(dsname)
        self.default_dets = defaultDetectors(config.HUTCH)
        self.x_det, self.y_det = None, None
        
        for det in self.default_dets:
            if det.name==config.DETI0:
                self.i0_det = det
            elif det.name==config.DETTT:
                self.tt_det = det
            elif det.name==config.DETX:
                self.x_det = det
            elif det.name==config.DETY:
                self.y_det = det
            elif det.name=='lightStatus':
                self.ls_det = det
        
        self.det = ps.Detector(config.DETNAME)
        self.mask = self.det.mask(1, calib=True, status=True, central=True, edges=True)
        self.roi = config.ROI
        
        # Make placeholder array
        self.shape = (config.YBINS.size, config.XBINS.size)
        self.arr = np.zeros(self.shape)
        self.i0 = np.ones(self.shape)*1e-9
        self.counts = np.zeros(self.shape)
        
        
        self.run()
        return
    
    def run(self):
        bin_2d = Bin_2d(config.XBINS, config.YBINS)
        for run in self.ds.runs():
            neventsInBatch = 0
            neventsInRank = 0
            for nevt,evt in enumerate(self.ds.events()):
                if not config.LIVE:
                    if nevt%(size-1)!=rank-1:
                        continue
                    time.sleep(0.01)
                
                ls = self.ls_det.data(evt)
                if ls['xray']==0: # skip events with no x-ray
                    continue
                
                try:
                    # I0 and tt + apply filters
                    i0 = self.i0_det.data(evt)['sum']
                    if i0<config.FILT_I0[0] or i0>config.FILT_I0[1]:
                        continue
                    tt_corr = self.tt_det.data(evt)
                    if tt_corr['FLTPOSFWHM']<config.FILT_TT_FWHM[0] or tt_corr['FLTPOSFWHM']>config.FILT_TT_FWHM[1]:
                        continue
                    if tt_corr['AMPL']<config.FILT_TT_AMPL[0] or tt_corr['AMPL']>config.FILT_TT_AMPL[1]:
                        continue

                    # x-axis detector
                    x = utils.get_det_data(self.x_det, evt)
                    if self.x_det.name=='enc':
                        x = x + tt_corr['ttCorr']
                        
                    # y-axis detector
                    y = utils.get_det_data(self.x_det, evt)
                    
                    # analyze images
                    img = self.det.calib(evt)
                    if config.PHOT:
                        img = photons(img/config.PHOTON_ADU, self.mask)
                    if self.roi is not None:
                        intensity = img[self.roi[0][0]:self.roi[0][1],self.roi[1][0]:self.roi[1][1]].sum()
                    
                    bin_2d.bin_new_data([x],[y],[[intensity],[i0]]) # need to put in list properly to work with binned_statistic_dd
                    
                except Exception as e:
                    print('Could not analyze this shot:\n{}'.format(e))
                    continue

                neventsInBatch += 1
                neventsInRank += 1
                if ((nevt!=0)&((neventsInRank)%config.UPDATERATE_CLIENT == 0)):
                    senddata=mpidata()
                    #send full sum.
                    senddata.addarray('binned',np.ascontiguousarray(bin_2d.binned))

                    senddata.small.nevents = neventsInBatch
                    senddata.send()
                    #print('sent data',neventsInBatch, neventsInRank, updaterate)
                    #print(imgar.shape, imgThres.shape, sum_img.shape)
                    #print('image std:',img.std(), (imgThres>0).sum())
                    
                    #resetting binned data.
                    bin_2d = Bin_2d(config.XBINS, config.YBINS)
            md = mpidata()
            md.endrun()
