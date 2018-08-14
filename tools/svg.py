from os import system, listdir, sep
from svgpathtools import svg2paths, wsvg
from tools.cut import *
from bisect import *
from operator import attrgetter
import logging
import math
import numpy as np

class ExtractObj:
#todo change format
    def extractObjects(self, resultdir):
        resultpath = resultdir + sep
        svgs = listdir(resultpath)
        pathno = 0
        for svg in svgs:
            if '.svg' in svg:
                objfile = 'objects.txt'
                thefile = open(resultpath + objfile, 'w')
                paths, attributes = svg2paths(resultpath + svg)
                for path in paths:
                    s = abs(path.area())
                    if pathno == 0:
                        thefile.write('Chip %f\n' % (s))
                    else:
                        thefile.write("o%s %f\n" % (pathno, s))
                    pathno += 1
                    lineno = 0
                    for line in path:
                        lineno += 1
                        thefile.write('line%s: %.3f+%.3fi,%.3f+%.3fi\n' % (lineno, line.start.real, line.start.imag, line.end.real, line.end.imag))
                thefile.close()
                logger = logging.getLogger('__main__')
                logger.info('svg file %s finished conversion.' % (svg))

class cutPolygon:
    def cutSVG(self, svgdir, resultdir, no_merge_factor, no_absorption_factor, test_ratio = 1.0):
        svgpath = svgdir + sep
        resultpath = resultdir + sep
        svgs = listdir(svgpath)
        if len(listdir(resultpath)) == 0:
            for svg in svgs:
                if '.svg' in svg:
                    objfile = svg
                    confile = 'conflict.txt'
                    thefile = resultpath + objfile
                    conflictfile = open(resultpath + confile, 'w')
                    rawpaths, attributes = svg2paths(svgpath + svg)
                    offsetx, offsety = preconfig(rawpaths)
                    paths = svgpreprocess(rawpaths, attributes, offsetx, offsety)
                    frame = Path()
                    fb = paths[0].bbox()
                    xmin = fb[0]
                    xmax = fb[1]
                    ymin = fb[2]
                    ymax = fb[3]
                    # create the frame of the layout
                    for path1 in paths:
                        b1 = path1.bbox()
                        if len(path1) != 4:
                            break
                        frame = path1
                        for path2 in paths:
                            if path1 != path2:
                                b2 = path2.bbox()
                                if b1[0] <= b2[0] <= b1[1] and b1[0] <= b2[1] <= b1[1] and b1[2] <= b2[2] <= b1[3] and \
                                        b1[2] <= b2[3] <= b1[3]:
                                    pass
                                else:
                                    frame = Path()
                                    break
                        if frame != Path():
                            break
                    if frame == Path():
                        for path in paths:
                            b = path.bbox()
                            if b[0] < xmin:
                                xmin = b[0]
                            if b[1] > xmax:
                                xmax = b[1]
                            if b[2] < ymin:
                                ymin = b[2]
                            if b[3] > ymax:
                                ymax = b[3]
                        offset = max(xmax - xmin, ymax - ymin) * 0.05
                        frame = Path(MicroLine(Coordinate(xmin - offset, ymin - offset),
                                               Coordinate(xmax + offset, ymin - offset)),
                                     MicroLine(Coordinate(xmax + offset, ymin - offset),
                                               Coordinate(xmax + offset, ymax + offset)),
                                     MicroLine(Coordinate(xmax + offset, ymax + offset),
                                               Coordinate(xmin - offset, ymax + offset)),
                                     MicroLine(Coordinate(xmin - offset, ymax + offset),
                                               Coordinate(xmin - offset, ymin - offset)))
                    if frame in paths:
                        paths.remove(frame)
                    offsetframe = Path()
                    for line in frame:
                        start = Coordinate(line.start.real - offsetx, line.start.imag - offsety)
                        end = Coordinate(line.end.real - offsetx, line.end.imag - offsety)
                        newline = MicroLine(start, end)
                        offsetframe.append(newline)

                    #multiply perimeter
                    large_factor = 0.02
                    small_factor = 0.005 * float(test_ratio) # default = 1

                    # determine the small and large dimension of the design
                    # offsetframe: chip frame
                    # dimension: chip area
                    dimension = offsetframe[0].length() * offsetframe[1].length()
                    halfgirth = abs(offsetframe[0].length() + offsetframe[1].length())

                    # todo: multiple of area but not one edge?
                    large_ratio = large_factor * halfgirth
                    small_ratio = small_factor * halfgirth

                    # todo: add coordinate
                    # unitrect: edge of unit rect
                    unitrect = unitdivision(offsetframe)
                    if no_merge_factor != 0:
                        merging_threshold = no_merge_factor
                    else:
                        merging_threshold = small_ratio
                    distincthpaths = []
                    no_merge = {}
                    no_absorption = {}
                    # todo: collect h lines
                    for path in paths:
                        #wsvg(curdistinctpaths, filename='testoutput.svg', openinbrowser=True)
                        # curdistinctpaths: redraw of the design before conflict detection and deviation!h.
                        # create rect with last hline, in order to redraw the pic
                        curdistinctpaths, allcurcutlines, removecutline = rectangular_partition(path, offsetx, offsety,
                                                                                                large_ratio)
                        curcombinedPaths = []
                        curMicdistinctpaths = []
                        # todo: conflict detection
                        for path in curdistinctpaths:
                            curcombinedPaths.append(path)
                            curMicdistinctpaths.append(path)
                        cur_no_merge = {}
                        for path1 in curMicdistinctpaths:
                            cur_no_merge[path1] = []
                            for path2 in curMicdistinctpaths:
                                if path1 != path2:
                                    #conflict, dis = no_merge_conflict(path1, path2, small_ratio)
                                    conflict, dis = no_merge_conflict(path1, path2, merging_threshold)
                                    if conflict:
                                        cur_no_merge[path1].append(path2)
                        cur_no_absorption = {}
                        keepcutlines = []
                        for path1 in curMicdistinctpaths:
                            cur_no_absorption[path1] = []
                            for path2 in curMicdistinctpaths:
                                if path1 != path2:
                                    conflict, line = no_absorption_conflict(path1, path2, no_absorption_factor)
                                    if conflict:
                                        keepcutlines.append(line)
                                        cur_no_absorption[path1].append(path2)
                        #todo + - list
                        for cutl in allcurcutlines:
                            if cutl not in keepcutlines:
                                if cutl not in removecutline:
                                    removecutline.append(cutl)
                        # merge objects
                        flag = 1
                        while (flag == 1):
                            curMicdistinctpaths = curcombinedPaths
                            flag = 0
                            for path1 in curMicdistinctpaths:
                                for path2 in curMicdistinctpaths:
                                    if path1 != path2:
                                        if path2 in cur_no_merge[path1]:
                                            continue
                                        inter,p = two_paths_intersection(path1, path2)
                                        if len(inter) != 0:
                                            for cut in removecutline:
                                                cutMline = MicroLine(Coordinate(cut.start), Coordinate(cut.end))
                                                interl, p = two_lines_intersection(cutMline, inter[0])
                                                if interl is not None:
                                                    flag = 1
                                                    newPath = combinePaths(path1, path2, inter)
                                                    curcombinedPaths.remove(path1)
                                                    curcombinedPaths.remove(path2)
                                                    curcombinedPaths.append(newPath)
                                                    # start newPath, path1, path2, cur_no_merge
                                                    update_conflict(cur_no_merge, path1, newPath)
                                                    update_conflict(cur_no_merge, path2, newPath)
                                                    update_conflict(cur_no_absorption, path1, newPath)
                                                    update_conflict(cur_no_absorption, path2, newPath)

                                                    break
                                            if flag == 1:
                                                break
                                if flag == 1:
                                    break
                        # intersect not mean no nomerge thus removed some lines
                        temp_no_merge = cur_no_merge
                        for con in temp_no_merge.items():
                            for i in con[1]:
                                x, p = two_paths_intersection(con[0], i)
                                if len(x) != 0:
                                    del cur_no_merge[con[0]]
                                    break
                        flag = 1
                        curdevPaths = []
                        for path in curcombinedPaths:
                            curdevPaths.append(path)
                        while (flag == 1):
                            flag = 0
                            curcombinedPaths = curdevPaths
                            for path1 in curcombinedPaths:
                                for path2 in curcombinedPaths:
                                    if path1 != path2:
                                        inter,p = two_paths_intersection(path1, path2)
                                        if len(inter) != 0:
                                            if inter[0] in path1:
                                                dev = getDev(path2, inter[0])
                                                newPath = changePath(path1, path1.index(inter[0]), dev, 0.2, large_ratio)
                                                curdevPaths.remove(path1)
                                                curdevPaths.append(newPath)
                                                # start path1, cur_no_merge, newPath
                                                update_conflict(cur_no_merge, path1, newPath)
                                                update_conflict(cur_no_absorption, path1, newPath)
                                                flag = 1
                                            if inter[0] in path2:
                                                dev = getDev(path1, inter[0])
                                                newPath = changePath(path2, path2.index(inter[0]), dev, 0.2, large_ratio)
                                                curdevPaths.remove(path2)
                                                curdevPaths.append(newPath)
                                                update_conflict(cur_no_merge, path2, newPath)
                                                update_conflict(cur_no_absorption, path2, newPath)
                                                flag = 1
                                            if flag == 1:
                                                break
                                if flag == 1:
                                    break
                        for path in curdevPaths:
                            distincthpaths.append(path)
                        for con in cur_no_merge.items():
                            if con[1] != []:
                                no_merge[con[0]] = con[1]
                        for con in cur_no_absorption.items():
                            if con[1] != []:
                                no_absorption[con[0]] = con[1]
                        # todo conflict2 connected conflict: compare area(ratio of cut areas)
                        # todo conflict1 near cannot be combined (refresh removecutline)
                        # todo at the end detect no_merge_conflict again
                    distance = {}
                    min_distance = 0
                    if len(distincthpaths) >= 2:
                        min_distance = two_paths_distance(distincthpaths[0], distincthpaths[1])
                    length = len(distincthpaths)
                    for p in distincthpaths:
                        distance[p] = {}
                    for i in range(0,length):
                        for j in range(i+1,length):
                            dis = two_paths_distance(distincthpaths[i], distincthpaths[j])
                            if dis > 0 and (dis < min_distance or min_distance <= 0):
                                min_distance = dis
                            if dis != 0:
                                s1 = abs(distincthpaths[i].area())
                                s2 = abs(distincthpaths[j].area())
                                if s1 <= s2:
                                    try:
                                        distance[distincthpaths[i]][distincthpaths[j]] = dis
                                    except KeyError:
                                        print 'key error'
                                        print len(distincthpaths)
                                        print j
                                        print i
                                else:
                                    distance[distincthpaths[j]][distincthpaths[i]] = dis
                    for k,v in distance.items():
                        if v == {}:
                            del distance[k]
                    min_distance = max(0, min_distance)
                    # todo change the logic
                    if min_distance != 0:
                        min_distance = min(min_distance, small_ratio)
                        merging_threshold = min_distance * 3
                    else:
                        merging_threshold = small_ratio
                    if no_merge_factor != 0:
                        merging_threshold = no_merge_factor
                    no_mergex = {}
                    for p in distincthpaths:
                        no_mergex[p] = []
                    for i in range(0,length):
                        for j in range(i+1, length):
                            dis = 0
                            conflict = None
                            if distincthpaths[i] in distance.keys():
                                if distincthpaths[j] in distance[distincthpaths[i]].keys():
                                    dis = distance[distincthpaths[i]][distincthpaths[j]]
                            if distincthpaths[j] in distance.keys():
                                if distincthpaths[i] in distance[distincthpaths[j]].keys():
                                    dis = distance[distincthpaths[j]][distincthpaths[i]]
                            if dis != 0:
                                conflict, disss = no_merge_conflict(distincthpaths[i], distincthpaths[j], merging_threshold, dis)
                            if conflict:
                                no_mergex[distincthpaths[i]].append(distincthpaths[j])
                                no_mergex[distincthpaths[j]].append(distincthpaths[i])
                    for p in distincthpaths:
                        if no_mergex[p] == []:
                            del no_mergex[p]
                    for i in range(0, length):
                        for j in range(i+1, length):
                            if distincthpaths[i] in no_absorption.keys():
                                if distincthpaths[j] in no_absorption[distincthpaths[i]]:
                                    break
                            conflict, line = no_absorption_conflict(distincthpaths[i], distincthpaths[j], no_absorption_factor)
                            if conflict:
                                if distincthpaths[i] not in no_absorption.keys():
                                    no_absorption[distincthpaths[i]] = []
                                if distincthpaths[j] not in no_absorption[distincthpaths[i]]:
                                    no_absorption[distincthpaths[i]].append(distincthpaths[j])
                                if distincthpaths[j] not in no_absorption.keys():
                                    no_absorption[distincthpaths[j]] = []
                                if distincthpaths[i] not in no_absorption[distincthpaths[j]]:
                                    no_absorption[distincthpaths[j]].append(distincthpaths[i])
                    subunits = {}
                    for i in range(0, length):
                        subunits[i+1] = []
                        subunits[i+1] = subunit(distincthpaths[i], unitrect, offsetframe)

                    distincthpaths.insert(0, offsetframe)
                    wsvg(distincthpaths, filename=thefile, openinbrowser=False)

                    output_unit(resultpath, 'unit.txt', subunits, unitrect, offsetframe)

                    tf = merging_threshold == small_factor
                    logger = logging.getLogger('__main__')
                    logger.info('svg file %s finished partition.' % (svg))
                    logger.info('merging threshold = %s, it %s equals to small_factor' % (merging_threshold, tf))
                    logger.info('absorption threshold = %s' % (no_absorption_factor))

                    conflictfile.write('no merge conflict:\n')
                    for k, v in no_mergex.items():
                        index = distincthpaths.index(k)
                        if len(v) != 0:
                            l = len(v)
                            conflictfile.write('o%s %d' % (index, l))
                            for li in v:
                                indexl = distincthpaths.index(li)
                                conflictfile.write(' o%s' % (indexl))
                            conflictfile.write('\n')
                    conflictfile.write('FIN\n')
                    conflictfile.write('\nno absorption conflict:\n')
                    for k, v in no_absorption.items():
                        index = distincthpaths.index(k)
                        if len(v) != 0:
                            stri = []
                            for l in v:
                                if abs(k.area()) < abs(l.area()):
                                    indexl = distincthpaths.index(l)
                                    if indexl not in stri:
                                        stri.append('o' + str(indexl))
                        if len(stri) != 0:
                            l = len(stri)
                            conflictfile.write('o%s %d' % (index, l))
                            for s in stri:
                                conflictfile.write(' %s' % (s))
                            conflictfile.write('\n')
                    conflictfile.write('FIN\n\n')
                    conflictfile.write('distance:\n')
                    for k,v in distance.items():
                        index = distincthpaths.index(k)
                        if len(v) != 0:
                            for o,d in v.items():
                                indexl = distincthpaths.index(o)
                                conflictfile.write('o%s o%s %f\n' % (index, indexl, d))
                    conflictfile.write('FIN\n')
                    conflictfile.close()


