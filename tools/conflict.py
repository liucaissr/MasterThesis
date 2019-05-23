#!/usr/bin/python
import re
from svgpathtools import *
from tools.segment import *

def no_merge_conflict(path1, path2, factor, dis = None, in_pattern = 0):
    """
    for in-pattern conflict -  t > threshold > 0
    for between-pattern conflict - t > threshold
    :param path1:
    :param path2:
    :param factor:
    :param dis:
    :return:

    """
    if dis is None:
        dis = two_paths_distance(path1, path2)
    if in_pattern == 1:
        if 0 < dis < factor:
            return True, dis
    else:
        if dis < factor:
            return True, dis
    return False,dis

def lp_conflict(path1, path2, factor):
    # factor = 0.2
    assert path1.isclosed() and path2.isclosed(), '%s is not closed' % (path1 if path1.isclosed() is False else path2)
    x, p = two_paths_intersection(path1, path2)
    factor_sqrt = sqrt(factor)
    selflengthfactor = 0.8
    interl = None
    if len(x) == 0 and p is None:
        return False,interl
    # assert len(x) == 1
    elif len(x) != 0 and p is None:
        length = float(x[0].length())
        interl = x[0]
        area = 0
        wholelength = 0
        if x[0] in path1:
            for line in path2:
                l, p = two_lines_intersection(x[0], line)
                if l is not None:
                    wholelength = float(line.length())
            area = float(abs(path2.area()))
        elif x[0] in path2:
            for line in path1:
                l, p = two_lines_intersection(x[0], line)
                if l is not None:
                    wholelength = float(line.length())
            area = float(abs(path1.area()))
        ratio = 1
        lengthratio = 1
        if area != 0:
            ratio = length / area
        if wholelength != 0:
            lengthratio = length / wholelength
        if ratio < factor or lengthratio < factor_sqrt:
            return True, interl
    elif p is not None:
        lengths = {}
        for l in p:
            lens = float(l.length())
            if lens not in lengths.keys():
                lengths[lens] = [0] * 2
            for line in path1:
                interl, p = two_lines_intersection(l, line)
                if interl is not None:
                    wholelength = float(line.length())
                    lengths[lens][0] = wholelength
            if lengths[lens][0] == 0:
                d = l.direction
                dist = 0
                for ll in path1:
                    dd = ll.direction
                    if d == dd:
                        temp = abs(two_lines_distance(l, ll))
                        if temp < dist or dist == 0:
                            dist = temp
                            lengths[lens][0] = float(ll.length())
            for line in path2:
                interl, p = two_lines_intersection(l, line)
                if interl is not None:
                    wholelength = float(line.length())
                    lengths[lens][1] = wholelength
            if lengths[lens][1] == 0:
                d = l.direction
                dist = 0
                for ll in path2:
                    dd = ll.direction
                    if d == dd:
                        temp = abs(two_lines_distance(l, ll))
                        if temp < dist or dist == 0:
                            dist = temp
                            lengths[lens][1] = float(ll.length())
        for k in lengths.keys():
            area1 = float(abs(path1.area()))
            area2 = float(abs(path2.area()))
            ratio1 = 1
            ratio2 = 1
            if area1 != 0:
                ratio1 = k / area1
            if area2 != 0:
                ratio2 = k / area2
            lengthratio1 = k / lengths[k][0]
            lengthratio2 = k / lengths[k][1]
            const12_1 = ratio1 < factor and lengthratio1 < factor_sqrt
            const12_2 = ratio2 < factor and lengthratio2 < factor_sqrt
            #turn off const3
            #const3_1 = lengthratio2 > selflengthfactor
            const3_1 = True
            #const3_2 = lengthratio1 > selflengthfactor
            const3_2 = True
            #if ((ratio1 < factor and lengthratio1 < factor_sqrt) and lengthratio2 > selflengthfactor) or ((ratio2 < factor and lengthratio2 < factor_sqrt) and lengthratio1 > selflengthfactor):
            if (const12_1 and const3_1) or (const12_2 and const3_2):
                return True, None
    return False, interl

def update_conflict(conflict, oldPath, newPath):
    if newPath not in conflict.keys():
        conflict[newPath] = []
    if oldPath in conflict.keys():
        for conflictpath in conflict[oldPath]:
            if conflictpath not in conflict[newPath]:
                conflict[newPath].append(conflictpath)
        del conflict[oldPath]
    for k, v in conflict.items():
        if oldPath in v:
            v.remove(oldPath)
            if newPath not in v:
                v.append(newPath)