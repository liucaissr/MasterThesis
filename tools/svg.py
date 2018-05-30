from os import system, listdir, sep
from svgpathtools import svg2paths, wsvg
from tools.cut import *
from bisect import *
from operator import attrgetter
import logging

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
    def cutSVG(self, svgdir, resultdir, no_merge_factor, no_absorption_factor):
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

                    large_factor = 0.04
                    small_factor = 0.01
                    large_ratio = large_factor * abs(offsetframe[0].length())
                    small_ratio = small_factor * abs(offsetframe[0].length())

                    cuthlines = []
                    cutvpointobjs = []
                    allhlines = []
                    distincthpaths = []
                    curdistincthlines = []
                    curdistinctpaths = []
                    removecutline = []
                    no_merge = {}
                    no_absorption = {}
                    allcurcutlines = []
                    orginalsPaths = []


                    test = []
                    # todo: collect h lines
                    for path in paths:
                        sortedhlines, sortedvlines, filteredPath, filteredPoints = pathpreprocess(path, offsetx, offsety)
                        # todo pick one shorter line
                        # todo if vline
                        # todo if hline
                        for pointobj in filteredPoints:
                            # todo point to two cutlines
                            cuthline = None
                            cutvline = None
                            intersecthlines = [x for x in sortedhlines if
                                               x.start.real <= pointobj.point.real <= x.end.real]
                            intersectvlines = [x for x in sortedvlines if
                                               x.start.imag <= pointobj.point.imag <= x.end.imag]
                            intersecthlinesy = map(attrgetter('start.imag'), intersecthlines)
                            intersectvlinesx = map(attrgetter('start.real'), intersectvlines)
                            if pointobj.point == pointobj.hline.start:
                                # todo left extend
                                end = pointobj.point
                                leftvlineno = bisect_left(intersectvlinesx, end.real) - 1
                                if len(intersectvlines) > leftvlineno >= 0:
                                    start = Coordinate(intersectvlines[leftvlineno].start.real, end.imag)
                                    leftcuthline = MicroLine(start, end)
                                    if path1_is_contained_in_path2(leftcuthline, filteredPath):
                                        # todo add to cutlines hou bu
                                        cuthline = leftcuthline
                            else:
                                # todo right extend
                                start = pointobj.point
                                rightvlineno = bisect_right(intersectvlinesx, start.real)
                                if 0 < rightvlineno < len(intersectvlines):
                                    end = Coordinate(intersectvlines[rightvlineno].start.real, start.imag)
                                    rightcuthline = MicroLine(start, end)
                                    if path1_is_contained_in_path2(rightcuthline, filteredPath):
                                        # todo add to cutlines hou bu
                                        cuthline = rightcuthline

                            if pointobj.point == pointobj.vline.start:
                                # todo up extend
                                end = pointobj.point
                                uphlineno = bisect_left(intersecthlinesy, end.imag) - 1
                                if len(intersecthlines) > uphlineno >= 0:
                                    start = Coordinate(end.real, intersecthlines[uphlineno].start.imag)
                                    upcutvline = MicroLine(start, end)
                                    if path1_is_contained_in_path2(upcutvline, filteredPath):
                                        # todo add to cutlines hou bu
                                        cutvline = upcutvline
                                        cutvpoint = PointNavigation(start, intersecthlines[uphlineno], None)
                            else:
                                # todo down extend
                                start = pointobj.point
                                downhlineno = bisect_right(intersecthlinesy, start.imag)
                                if 0 < downhlineno < len(intersecthlines):
                                    end = Coordinate(start.real, intersecthlines[downhlineno].start.imag)
                                    downcutvline = MicroLine(start, end)
                                    if path1_is_contained_in_path2(downcutvline, filteredPath):
                                        # todo add to cutlines hou bu
                                        cutvline = downcutvline
                                        cutvpoint = PointNavigation(end, intersecthlines[downhlineno], None)

                            # todo compare two line:
                            cutvlinelength = 0
                            cuthlinelength = 0
                            curcutline = None
                            if cutvline is not None:
                                cutvlinelength = cutvline.length()
                            if cuthline is not None:
                                cuthlinelength = cuthline.length()
                            if cutvlinelength != 0 and (cuthlinelength > cutvlinelength or cuthlinelength == 0):
                                curcutline = cutvline
                                cutvpointobjs.append(cutvpoint)
                                # todo add above hline
                            elif cuthlinelength != 0 and (cutvlinelength >= cuthlinelength or cutvlinelength == 0):
                                curcutline = cuthline
                                # todo change cuthlines, allhlines to cuthlines
                                cuthlines.append(curcutline)
                                allhlines.append(curcutline)
                            if curcutline is not None:
                                allcurcutlines.append(curcutline)
                                if curcutline.length() >= large_ratio:
                                    removecutline.append(curcutline)

                        cline_num = len(allcurcutlines)
                        cutcutlines = []
                        cutlinevpointobjs = []
                        for i in range(0, cline_num):
                            for j in range(i+1, cline_num):
                                x = line1_intersect_with_line2(allcurcutlines[i], allcurcutlines[j])
                                if len(x) != 0:
                                    if x != [(0.0, 0.0)] and x != [(0.0, 1.0)] and x != [(1.0, 0.0)] and x != [(1.0, 1.0)]:
                                        if allcurcutlines[i].direction() == 'h':
                                            hcline = allcurcutlines[i]
                                            vcline = allcurcutlines[j]
                                        else:
                                            hcline = allcurcutlines[j]
                                            vcline = allcurcutlines[i]
                                        intersectp = Coordinate(vcline.start.real, hcline.start.imag)
                                        newvpoint = PointNavigation(intersectp, None, None)
                                        cutvpointobjs.append(newvpoint)
                                        cutlinevpointobjs.append(newvpoint)
                                        for replacehline in [allcurcutlines[i], allcurcutlines[j]]:
                                            cutcutlines.append(replacehline)
                                    else:
                                        continue
                        replacehlines = []
                        for h in allhlines:
                            replacehlines.append(h)
                        if len(cutlinevpointobjs):
                            replacehlines = combineLinesWithPoints(allhlines, cutlinevpointobjs)
                        # todo remove after testing
                        for line in sortedhlines:
                            allhlines.append(line)
                        combinedhlines = combineLinesWithPoints(allhlines, cutvpointobjs)
                        for line in combinedhlines:
                            # todo delete obj
                            curdistincthlines.append(line)
                        # todo add cuthline to cur
                        for line in cutcutlines:
                            if line in cuthlines:
                                cuthlines.remove(line)
                        for line in replacehlines:
                            curdistincthlines.append(line)
                        # todo: create rect with last hline, in order to redraw the pic
                        curdistincthlines = sorted(curdistincthlines)
                        length = len(curdistincthlines)
                        used = length * [0]
                        curdistincthlinesy = map(attrgetter('start.imag'), curdistincthlines)
                        for i in range(0, length):
                            # todo add intersect
                            if used[i] == 0:
                                intersectlines = []
                                intersectlines_ind = []
                                for k in range(i+1,length):
                                    if curdistincthlines[k].start.real == curdistincthlines[i].start.real and curdistincthlines[
                                        i].end.real == curdistincthlines[k].end.real:
                                        intersectlines.append(curdistincthlines[k])
                                        intersectlines_ind.append(k)
                                intersectlinesy = map(attrgetter('start.imag'), intersectlines)
                                nextstart = bisect(intersectlinesy, curdistincthlinesy[i])
                                lens = len(intersectlines)
                                if nextstart >= lens:
                                    continue
                                nextend = bisect(intersectlinesy, intersectlinesy[nextstart])
                                if nextend > lens:
                                    continue
                                for j in range(nextstart, nextend):
                                    if used[intersectlines_ind[j]] == 0 and used[i] == 0:
                                        if curdistincthlines[i].start.real == intersectlines[j].start.real and \
                                                curdistincthlines[
                                                    i].end.real == \
                                                intersectlines[j].end.real:
                                            UperLine = curdistincthlines[i]
                                            Lowerline = intersectlines[j]
                                            newPath = Path(UperLine, Line(UperLine.end, Lowerline.end),
                                                           Line(Lowerline.end, Lowerline.start),
                                                           Line(Lowerline.start, UperLine.start))
                                            used[intersectlines_ind[j]] = 1
                                            used[i] = 1
                                            curdistinctpaths.append(newPath)
                        #wsvg(curdistinctpaths, filename='testoutput.svg', openinbrowser=True)
                        for pp in curdistinctpaths:
                            test.append(pp)
                        # todo: inside a path.
                        curcombinedPaths = []
                        curMicdistinctpaths = []
                        # todo: conflict detection
                        for path in curdistinctpaths:
                            p = Path()
                            for line in path:
                                l = MicroLine(Coordinate(line.start), Coordinate(line.end))
                                p.append(l)
                            curcombinedPaths.append(p)
                            curMicdistinctpaths.append(p)
                        cur_no_merge = {}
                        for path1 in curMicdistinctpaths:
                            cur_no_merge[path1] = []
                            for path2 in curMicdistinctpaths:
                                if path1 != path2:
                                    #conflict, dis = no_merge_conflict(path1, path2, small_ratio)
                                    conflict, dis = no_merge_conflict(path1, path2, small_ratio,no_merge_factor)
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
                        for cutl in allcurcutlines:
                            if cutl not in keepcutlines:
                                if cutl not in removecutline:
                                    removecutline.append(cutl)
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
                                                    cur_no_merge[newPath] = []
                                                    for conflictpath in cur_no_merge[path1]:
                                                        if conflictpath not in cur_no_merge[newPath] and conflictpath != path2:
                                                            # todo any unique list
                                                            cur_no_merge[newPath].append(conflictpath)
                                                    for conflictpath in cur_no_merge[path2]:
                                                        if conflictpath not in cur_no_merge[
                                                            newPath] and conflictpath != path1:
                                                            cur_no_merge[newPath].append(conflictpath)
                                                    del cur_no_merge[path2]
                                                    del cur_no_merge[path1]
                                                    for k, v in cur_no_merge.items():
                                                        if path1 in v:
                                                            v.remove(path1)
                                                            if newPath not in v:
                                                                v.append(newPath)
                                                        if path2 in v:
                                                            v.remove(path2)
                                                            if newPath not in v:
                                                                v.append(newPath)
                                                    cur_no_absorption[newPath] = []
                                                    for conflictpath in cur_no_absorption[path1]:
                                                        if conflictpath not in cur_no_absorption[
                                                            newPath] and conflictpath != path2:
                                                            # todo any unique list
                                                            cur_no_absorption[newPath].append(conflictpath)
                                                    for conflictpath in cur_no_absorption[path2]:
                                                        if conflictpath not in cur_no_absorption[
                                                            newPath] and conflictpath != path1:
                                                            cur_no_absorption[newPath].append(conflictpath)
                                                    del cur_no_absorption[path2]
                                                    del cur_no_absorption[path1]
                                                    for k, v in cur_no_absorption.items():
                                                        if path1 in v:
                                                            v.remove(path1)
                                                            if newPath not in v:
                                                                v.append(newPath)
                                                        if path2 in v:
                                                            v.remove(path2)
                                                            if newPath not in v:
                                                                v.append(newPath)
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
                        for p in curcombinedPaths:
                            orginalsPaths.append(p)
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
                                                cur_no_merge[newPath] = []
                                                if path1 in cur_no_merge.keys():
                                                    for conflictpath in cur_no_merge[path1]:
                                                        if conflictpath not in cur_no_merge[newPath]:
                                                            # todo any unique list
                                                            cur_no_merge[newPath].append(conflictpath)
                                                    del cur_no_merge[path1]
                                                for k, v in cur_no_merge.items():
                                                    if path1 in v:
                                                        v.remove(path1)
                                                        if newPath not in v:
                                                            v.append(newPath)
                                                cur_no_absorption[newPath] = []
                                                if path1 in cur_no_absorption.keys():
                                                    for conflictpath in cur_no_absorption[path1]:
                                                        if conflictpath not in cur_no_absorption[newPath]:
                                                            # todo any unique list
                                                            cur_no_absorption[newPath].append(conflictpath)
                                                    del cur_no_absorption[path1]
                                                for k, v in cur_no_absorption.items():
                                                    if path1 in v:
                                                        v.remove(path1)
                                                        if newPath not in v:
                                                            v.append(newPath)
                                                flag = 1
                                            if inter[0] in path2:
                                                dev = getDev(path1, inter[0])
                                                newPath = changePath(path2, path2.index(inter[0]), dev, 0.2, large_ratio)
                                                curdevPaths.remove(path2)
                                                curdevPaths.append(newPath)
                                                cur_no_merge[newPath] = []
                                                if path2 in cur_no_merge.keys():
                                                    for conflictpath in cur_no_merge[path2]:
                                                        if conflictpath not in cur_no_merge[newPath]:
                                                            # todo any unique list
                                                            cur_no_merge[newPath].append(conflictpath)
                                                    del cur_no_merge[path2]
                                                for k, v in cur_no_merge.items():
                                                    if path2 in v:
                                                        v.remove(path2)
                                                        if newPath not in v:
                                                            v.append(newPath)

                                                cur_no_absorption[newPath] = []
                                                if path2 in cur_no_absorption.keys():
                                                    for conflictpath in cur_no_absorption[path2]:
                                                        if conflictpath not in cur_no_absorption[newPath]:
                                                            # todo any unique list
                                                            cur_no_absorption[newPath].append(conflictpath)
                                                    del cur_no_absorption[path2]
                                                for k, v in cur_no_absorption.items():
                                                    if path2 in v:
                                                        v.remove(path2)
                                                        if newPath not in v:
                                                            v.append(newPath)

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
                        curdistincthlines = []
                        allhlines = []
                        cuthlines = []
                        curdistinctpaths = []
                        allcurcutlines = []
                        removecutline = []
                    distance = {}
                    no_merge_threshold = 0
                    if len(distincthpaths) >= 2:
                        no_merge_threshold = two_paths_distance(distincthpaths[0], distincthpaths[1])
                    length = len(distincthpaths)
                    for p in distincthpaths:
                        distance[p] = {}
                    for i in range(0,length):
                        for j in range(i+1,length):
                            dis = two_paths_distance(distincthpaths[i], distincthpaths[j])
                            if dis > 0 and (dis < no_merge_threshold or no_merge_threshold <= 0):
                                no_merge_threshold = dis
                            if dis != 0:
                                s1 = abs(distincthpaths[i].area())
                                s2 = abs(distincthpaths[j].area())
                                if s1 <= s2:
                                    distance[distincthpaths[i]][distincthpaths[j]] = dis
                                else:
                                    distance[distincthpaths[j]][distincthpaths[i]] = dis
                    for k,v in distance.items():
                        if v == {}:
                            del distance[k]
                    no_merge_threshold = max(0, no_merge_threshold)
                    if no_merge_threshold != 0:
                        no_merge_threshold = min(no_merge_threshold, small_ratio)
                    else:
                        no_merge_threshold = small_ratio
                    no_mergex = {}
                    for p in distincthpaths:
                        no_mergex[p] = []
                    print 'nomergethr:'
                    print no_merge_threshold*3
                    print small_ratio
                    print large_ratio == no_merge_threshold
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
                                conflict, disss = no_merge_conflict(distincthpaths[i], distincthpaths[j], no_merge_threshold * 3, no_merge_factor, dis)
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
                    distincthpaths.insert(0, offsetframe)
                    wsvg(distincthpaths, filename=thefile, openinbrowser=False)

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


