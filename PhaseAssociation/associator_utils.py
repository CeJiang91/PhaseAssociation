#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
# @Time    : 2020/11/26 下午2:22
# @Author  : jiang ce
# @Email   : cehasone@outlk.com
# @File    : associator_utils.py
# @Software: PyCharm

from obspy import UTCDateTime
import numpy as np
import os
from obspy.core.inventory import Station
from math import radians, cos, sin, asin, sqrt


# 计算两点间距离-m
def geodistance(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    dis = 2 * asin(sqrt(a)) * 6371 * 1000
    return dis


def fang2npz(input_dir, output_dir):
    """
    Performs preprocessing and conversion the phase data from prof.fang into npz

    :parameter
    phase_file
    output_dir

    """
    phase_file = os.path.join(input_dir, 'phase0.5.dat')
    station_file = os.path.join(input_dir, 'station.dat')
    stf = np.loadtxt(station_file, dtype=str)
    stations = {}
    for line in stf:
        code = line[1]
        lat = float(line[4])
        lon = float(line[5])
        ele = float(line[6])
        stations[code] = Station(code=code, latitude=lat, longitude=lon, elevation=ele)
    dtype = [('code', '<U10'), ('dist', float)]
    stadist = {}
    for code1 in stations:
        lon1 = stations[code1].longitude
        lat1 = stations[code1].latitude
        dists = []
        for code2 in stations:
            lon2 = stations[code2].longitude
            lat2 = stations[code2].latitude
            dists.append((code2, geodistance(lon1, lat1, lon2, lat2)/1000))
        dists = np.array(dists, dtype=dtype)
        dists = np.sort(dists, order='dist')
        stadist[dists[0][0]] = dists
    breakpoint()
    # phf = np.loadtxt(phase_file, dtype=str)
    # for line in phf:
    #     sta = line[0].split('/')[1]
    #     phtype = line[1]
    #     at = line[2] + ' ' + line[3]
    #     lat = float(line[4])
    #     lon = float(line[5])
    #     depth = float(line[6])
    #     prob = float(line[7])
    #     breakpoint()


if __name__ == '__main__':
    fang2npz('../dataset', '../dataset')