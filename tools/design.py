from os import system, listdir, sep
from svgpathtools import svg2paths, wsvg
from tools.segment import *
from tools.conflict import *
from tools.combine import combinePaths
from tools.shift import getDev, shiftPattern
from tools.save import output_conflict,output_unit
import logging


class ExtractObj:
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
    def cutSVG(self, svgdir, resultdir, no_merge_factor, lp_factor):
        svgpath = svgdir + sep
        resultpath = resultdir + sep
        svgs = listdir(svgpath)
        if len(listdir(resultpath)) == 0:
            for svg in svgs:
                if '.svg' in svg:
                    objfile = svg

                    thefile = resultpath + objfile

                    rawpaths, attributes = svg2paths(svgpath + svg)

                    offsetx, offsety = preconfig(rawpaths)
                    paths, offsetframe= design_preprocess(rawpaths, attributes, offsetx, offsety)

                    #multiply perimeter
                    large_factor = 0.02
                    small_factor = 0.005

                    # determine the small and large dimension of the design
                    # offsetframe: chip frame
                    halfgirth = abs(offsetframe[0].length() + offsetframe[1].length())
                    large_ratio = large_factor * halfgirth
                    small_ratio = small_factor * halfgirth

                    # unitrect: edge of unit rect
                    unitrect = unitdivision(offsetframe)
                    if no_merge_factor != 0:
                        merging_threshold = no_merge_factor
                    else:
                        merging_threshold = small_ratio

                    distinctpathsDict = {}
                    path_no = 0
                    distinctPaths = []
                    no_merge = {}
                    no_absorption = {}

                    for path in paths:
                        # wsvg(curdistinctpaths, filename='testoutput.svg', openinbrowser=True)
                        # curdistinctpaths: redraw of the design before conflict detection and deviation!h.
                        # create rect with last hline, in order to redraw the pic
                        curdistinctpaths, allcurcutlines = rectangular_partition(path)
                        removecutlines = []
                        for curcutline in allcurcutlines:
                            if large_ratio != 0:
                                if curcutline.length() >= large_ratio:
                                    removecutlines.append(curcutline)
                        curcombinedPaths = []
                        curMicdistinctpaths = []

                        for path in curdistinctpaths:
                            curcombinedPaths.append(path)
                            curMicdistinctpaths.append(path)
                        cur_no_merge = {}
                        for path1 in curMicdistinctpaths:
                            cur_no_merge[path1] = []
                            for path2 in curMicdistinctpaths:
                                if path1 != path2:
                                    conflict, dis = no_merge_conflict(path1, path2, merging_threshold, in_pattern = 1)
                                    if conflict:
                                        cur_no_merge[path1].append(path2)
                        cur_no_absorption = {}
                        keepcutlines = []
                        for path1 in curMicdistinctpaths:
                            cur_no_absorption[path1] = []
                            for path2 in curMicdistinctpaths:
                                if path1 != path2:
                                    conflict, line = lp_conflict(path1, path2, lp_factor)
                                    if conflict:
                                        keepcutlines.append(line)
                                        cur_no_absorption[path1].append(path2)

                        for cutl in allcurcutlines:
                            if cutl not in keepcutlines:
                                if cutl not in removecutlines:
                                    removecutlines.append(cutl)

                        # object combination
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
                                            for cut in removecutlines:
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

                        # intersect not mean no nomerge thus removed some lines -> hao xiang hen dui -> testcases1014
                        # -> if combined, means both paths doesnt have conflict with each other? Yes
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
                                                newPath = shiftPattern(path1, path1.index(inter[0]), dev, 0.2, large_ratio)
                                                curdevPaths.remove(path1)
                                                curdevPaths.append(newPath)
                                                # start path1, cur_no_merge, newPath
                                                update_conflict(cur_no_merge, path1, newPath)
                                                update_conflict(cur_no_absorption, path1, newPath)
                                                flag = 1
                                            if inter[0] in path2:
                                                dev = getDev(path1, inter[0])
                                                newPath = shiftPattern(path2, path2.index(inter[0]), dev, 0.2, large_ratio)
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
                            distinctPaths.append(path)
                            distinctpathsDict[path] = path_no
                        for con in cur_no_merge.items():
                            if con[1] != []:
                                no_merge[con[0]] = con[1]
                        for con in cur_no_absorption.items():
                            if con[1] != []:
                                no_absorption[con[0]] = con[1]

                        path_no += 1

                    distance = {}
                    min_distance = 0
                    #distinctPaths = distinctpathsDict.keys()
                    if len(distinctPaths) >= 2:
                        min_distance = two_paths_distance(distinctPaths[0], distinctPaths[1])
                    length = len(distinctPaths)
                    for p in distinctPaths:
                        distance[p] = {}
                    for i in range(0,length):
                        for j in range(i+1,length):
                            dis = two_paths_distance(distinctPaths[i], distinctPaths[j])
                            if dis > 0 and (dis < min_distance or min_distance <= 0):
                                min_distance = dis
                            if dis != 0:
                                s1 = abs(distinctPaths[i].area())
                                s2 = abs(distinctPaths[j].area())
                                if s1 <= s2:
                                    try:
                                        distance[distinctPaths[i]][distinctPaths[j]] = dis
                                    except KeyError:
                                        print 'key error'
                                        print len(distinctPaths)
                                        print j
                                        print i
                                else:
                                    distance[distinctPaths[j]][distinctPaths[i]] = dis
                    for k,v in distance.items():
                        if v == {}:
                            del distance[k]
                    min_distance = max(0, min_distance)
                    if min_distance != 0:
                        min_distance = min(min_distance, small_ratio)
                        merging_threshold = min_distance * 3
                    else:
                        merging_threshold = small_ratio
                    if no_merge_factor != 0:
                        merging_threshold = no_merge_factor
                    no_mergex = {}
                    for p in distinctPaths:
                        no_mergex[p] = []
                    for i in range(0,length):
                        for j in range(i+1, length):
                            dis = 0
                            conflict = None
                            if distinctPaths[i] in distance.keys():
                                if distinctPaths[j] in distance[distinctPaths[i]].keys():
                                    dis = distance[distinctPaths[i]][distinctPaths[j]]
                            if distinctPaths[j] in distance.keys():
                                if distinctPaths[i] in distance[distinctPaths[j]].keys():
                                    dis = distance[distinctPaths[j]][distinctPaths[i]]
                            if distinctpathsDict[distinctPaths[i]] != distinctpathsDict[distinctPaths[j]]:
                                conflict, disss = no_merge_conflict(distinctPaths[i], distinctPaths[j], merging_threshold, dis, in_pattern = 0)
                            else:
                                conflict, disss = no_merge_conflict(distinctPaths[i], distinctPaths[j], merging_threshold, dis, in_pattern = 1)
                            if conflict:
                                no_mergex[distinctPaths[i]].append(distinctPaths[j])
                                no_mergex[distinctPaths[j]].append(distinctPaths[i])
                    for p in distinctPaths:
                        if no_mergex[p] == []:
                            del no_mergex[p]

                    #no_merge_all = no_mergex + no_merge same key combine
                    """
                    for con in no_mergex:
                        if con[0] in no_merge.keys():
                            for p in con[1]:
                                no_merge[con[0]].append(p)
                        else:
                            no_merge[con[0]] = con[1]
                    """
                    for i in range(0, length):
                        for j in range(i+1, length):
                            if distinctPaths[i] in no_absorption.keys():
                                if distinctPaths[j] in no_absorption[distinctPaths[i]]:
                                    break
                            conflict, line = lp_conflict(distinctPaths[i], distinctPaths[j], lp_factor)
                            if conflict:
                                if distinctPaths[i] not in no_absorption.keys():
                                    no_absorption[distinctPaths[i]] = []
                                if distinctPaths[j] not in no_absorption[distinctPaths[i]]:
                                    no_absorption[distinctPaths[i]].append(distinctPaths[j])
                                if distinctPaths[j] not in no_absorption.keys():
                                    no_absorption[distinctPaths[j]] = []
                                if distinctPaths[i] not in no_absorption[distinctPaths[j]]:
                                    no_absorption[distinctPaths[j]].append(distinctPaths[i])
                    subunits = {}
                    for i in range(0, length):
                        subunits[i+1] = []
                        subunits[i+1] = distinctPaths[i].subunit(unitrect, offsetframe)

                    distinctPaths.insert(0, offsetframe)
                    wsvg(distinctPaths, filename=thefile, openinbrowser=False)

                    output_unit(resultpath, 'unit.txt', subunits, unitrect, offsetframe)

                    # hao duo wen ti
                    conflicts = [no_mergex, no_absorption, distance]
                    output_conflict(resultpath, 'conflict.txt', conflicts, distinctPaths)

                    tf = merging_threshold == small_factor
                    logger = logging.getLogger('__main__')
                    logger.info('svg file %s finished partition.' % (svg))
                    logger.info('merging threshold = %s, it %s equals to small_factor' % (merging_threshold, tf))
                    logger.info('absorption threshold = %s' % (lp_factor))




