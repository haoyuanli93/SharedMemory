import numpy as np
from scipy.stats import binned_statistic, binned_statistic_dd


class Bin_2d(object):
    def __init__(self, xbins, ybins):
        bins = np.asarray(xbins)
        binDiff = np.diff(bins)
        binDiff = np.append(binDiff, binDiff[-1])
        binEdges = bins+binDiff/2
        binEdges = np.append(binEdges[0]-binDiff[0], binEdges)
        self.xbins = binEdges
        
        bins = np.asarray(ybins)
        binDiff = np.diff(bins)
        binDiff = np.append(binDiff, binDiff[-1])
        binEdges = bins+binDiff/2
        binEdges = np.append(binEdges[0]-binDiff[0], binEdges)
        self.ybins = binEdges
        
        self.binned = [np.zeros((xbins.size, ybins.size)) for i in range(2)] # intensity, i0
        return
    
    def bin_new_data_(self, xs, ys, data):
        if isinstance(xs, float) or isinstance(xs, int):
            xs = [xs]
        if isinstance(ys, float) or isinstance(ys, int):
            ys = [ys]
        stats, bin_edges, bin_idx = binned_statistic_dd([xs,ys], data, 
                                                        bins=[self.xbins, self.ybins],
                                                        statistic='sum',
                                                        expand_binnumbers=True)
        for ii,stat in enumerate(stats):
            self.binned[ii]+=stat
        return