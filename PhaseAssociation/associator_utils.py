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


# 计算两点间距离
def geodistance(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    dis = 2 * asin(sqrt(a)) * 6371 * 1000
    return dis


def stadistsort(input_dir, outpu_dir):
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
            dists.append((code2, geodistance(lon1, lat1, lon2, lat2) / 1000))
        dists = np.array(dists, dtype=dtype)
        dists = np.sort(dists, order='dist')
        stadist[dists[0][0]] = dists
    np.savez('../dataset/stadist.npz', stadist)


def fang2npz(input_dir, output_dir, save_mode=False):
    """
    Performs preprocessing and conversion the phase data from prof.fang into npz

    :parameter:phase_file
    :parameter:output_dir

    """
    stadist = np.load('../dataset/stadist.npz', allow_pickle=True)['arr_0'].item()
    phase_file = os.path.join(input_dir, 'phase0.5.dat')
    # phase_file = os.path.join(input_dir, 'miniph.dat')
    phf = np.loadtxt(phase_file, dtype=str)
    association_state = False
    dtype = [('code', '<U10'), ('phasetype', '<U5'), ('arrival', UTCDateTime)]
    ailog = []
    eq = []
    for ln in phf:
        code = ln[0].split('/')[1]
        ph = ln[1]
        at = UTCDateTime(ln[2] + ' ' + ln[3])
        if code == 'XC15' and at == UTCDateTime('2018-05-16 16:44:22.970000'):
            breakpoint()
        # logic part
        if not association_state:
            center = (code, ph, at)
            eq = [(code, ph, at)]
            association_state = True
        else:
            ev = (code, ph, at)
            # Determine if this is one of near stations
            stnm = []
            for i in range(len(stadist[center[0]])):
                stnm.append(stadist[center[0]][i][0])
            sortdiff = abs(stnm.index(eq[-1][0]) - stnm.index(ev[0]))
            traveldiff = ev[2] - eq[-1][2]
            # The condition's parameters set manually
            if (traveldiff < 3) and \
                    (((sortdiff <= 3) and (not ((ev[0] == eq[-1][0]) and (ev[1] == eq[-1][1]))))
                     or ((ev[0] in ev2[0] for ev2 in eq) and
                         ((ev[0], ev[1]) not in [(ev2[0], ev2[1]) for ev2 in eq]))):
                eq.append(ev)
            else:
                eq = np.array(eq, dtype=dtype)
                ailog.append(eq)
                eq = [(code, ph, at)]
                center = (code, ph, at)
    n = 0
    for eq in ailog:
        lenst = list(set([ev[0] for ev in eq]))
        if len(lenst) >= 3:
            n += 1
    print(str(n)+'\n')
    n = 0
    for eq in ailog:
        lenst = list(set([ev[0] for ev in eq]))
        if len(lenst) >= 4:
            n += 1
    print(str(n)+'\n')
    if save_mode:
        roughass = open('../dataset/rough_association.dat', 'w')
        for eq in ailog:
            roughass.write('# \n')
            for ev in eq:
                roughass.write(ev[0] + ' ' + ev[1] + ' ' + ev[2].strftime('%Y-%m-%d %H:%M:%S.%f') + '\n')
        roughass.close()


def hyposat():
    print('hyposat')


if __name__ == '__main__':
    # stadistsort('../dataset', '../dataset')
    fang2npz('../dataset', '../dataset', save_mode=True)
