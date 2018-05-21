#!/usr/bin/python
import re
from bisect import *
from svgpathtools import svg2paths, wsvg
from svgpathtools import *
from tools.cut import LineNavigation, PointNavigation, MicroLine, Coordinate
from operator import attrgetter


def preconfig(paths):
    offsetx = paths[0][0].start.real
    offsety = paths[0][0].start.imag
    for path in paths:
        for line in path:
            if line.start.real < offsetx:
                offsetx = line.start.real
            if line.end.real < offsetx:
                offsetx = line.end.real
            if line.start.imag < offsety:
                offsety = line.start.imag
            if line.end.imag < offsety:
                offsety = line.end.imag

    if offsety >= 0:
        offsety = 0
    else:
        offsety -= 1
    if offsetx >= 0:
        offsetx = 0
    else:
        offsetx -= 1

    return offsetx, offsety


# process based on attributes
def svgpreprocess(paths, attributes):
    length = len(attributes)
    scale = [1] * length
    newPathList = []
    for i in range(0, length):
        if attributes[i].has_key(u'transform'):
            str = attributes[0].get(u'transform').encode('utf-8')
            scaleconfig = re.findall("scale\(+\d+\.\d+", str)
            if scaleconfig[0] != 0:
                scale[i] = float(re.findall("\d+\.\d+", scaleconfig[0])[0])
        else:
            scale[i] = 1
    for i in range(0, len(paths)):
        newPath = Path()
        for line in paths[i]:
            newPath.append(Line(line.start * scale[i], line.end * scale[i]))
        newPathList.append(newPath)
    return newPathList


def pathpreprocess(rawpath, offsetx, offsety):
    hlines = []
    vlines = []
    filteredPath = Path()
    filteredPointsObj = []
    filteredPoints = []
    path = []

    for line in rawpath:
        start = complex(round(line.start.real - offsetx, 3), round(line.start.imag - offsety, 3))
        end = complex(round(line.end.real - offsetx, 3), round(line.end.imag - offsety, 3))
        newline = Line(start, end)
        path.append(newline)

    for line in path:
        if line.start != line.end:
            b = line.bbox()
            if line.start.imag == line.end.imag:
                nline = Line(complex(b[0], b[2]), complex(b[1], b[2]))
                hlines.append(LineNavigation(b[2], b[0], b[1], nline))
            if line.start.real == line.end.real:
                nline = Line(complex(b[0], b[2]), complex(b[0], b[3]))
                vlines.append(LineNavigation(b[0], b[2], b[3], nline))

    sortedhlines = combineLines(hlines)
    sortedvlines = combineLines(vlines)
    filteredVlines = []
    filteredHlines = []
    for vline in sortedvlines:
        intersectpoints = []
        for hline in sortedhlines:
            x = line1_intersect_with_line2(vline.line, hline.line)
            if len(x) != 0:
                intersectpoints.append(x[0][0])
        if len(intersectpoints) >= 2:
            #points = sorted(intersectpoints)
            newvline = Line(vline.line.point(min(intersectpoints)), vline.line.point(max(intersectpoints)))
            b = newvline.bbox()
            newvlineobj = LineNavigation(b[0], b[2], b[3], newvline)
            filteredVlines.append(newvlineobj)
    for hline in sortedhlines:
        intersectpoints = []
        for vline in sortedvlines:
            x = x = line1_intersect_with_line2(hline.line, vline.line)
            if len(x) != 0:
                intersectpoints.append(x[0][0])
        if len(intersectpoints) >= 2:
            #points = sorted(intersectpoints)
            newhline = Line(hline.line.point(min(intersectpoints)), hline.line.point(max(intersectpoints)))
            b = newhline.bbox()
            newhlineobj = LineNavigation(b[2], b[0], b[1], newhline)
            filteredHlines.append(newhlineobj)

    # todo filteredPath not closed
    for line in path:
        if line.start != line.end:
            filteredPath.append(line)

    for line in filteredHlines:
        if line.line.start not in filteredPoints:
            filteredPoints.append(line.line.start)
            startPoint = PointNavigation(line.line.start, None, None)
            filteredPointsObj.append(startPoint)
        if line.line.end not in filteredPoints:
            filteredPoints.append(line.line.end)
            endPoint = PointNavigation(line.line.end, None, None)
            filteredPointsObj.append(endPoint)
        for pointobj in filteredPointsObj:
            if pointobj.point == line.line.start:
                pointobj.hline = line.line
            if pointobj.point == line.line.end:
                pointobj.hline = line.line

    for line in filteredVlines:
        if line.line.start not in filteredPoints:
            filteredPoints.append(line.line.start)
            startPoint = PointNavigation(line.line.start, None, None)
            filteredPointsObj.append(startPoint)
        if line.line.end not in filteredPoints:
            filteredPoints.append(line.line.end)
            endPoint = PointNavigation(line.line.end, None, None)
            filteredPointsObj.append(endPoint)
        for pointobj in filteredPointsObj:
            if pointobj.point == line.line.start:
                pointobj.vline = line.line
            if pointobj.point == line.line.end:
                pointobj.vline = line.line

    return sortedhlines, sortedvlines, filteredPath, filteredPointsObj


# parallel overlap
def line1_is_overlap_with_line2(line1, line2):
    b1 = line1.bbox()
    b2 = line2.bbox()
    if len(line1.intersect(line2)) != 0:
        return True
    elif max(b1[0], b2[0]) <= min(b1[1], b2[1]) and b1[2] == b2[2] == b1[3] == b2[3]:
        return True
    elif max(b1[2], b2[2]) <= min(b1[3], b2[3]) and b1[0] == b2[0] == b1[1] == b2[1]:
        return True
    else:
        return False


def line1_intersect_with_line2(line1, line2):
    if line1.start == line2.start:
        return [(0.0, 0.0)]
    elif line1.start == line2.end:
        return [(0.0, 1.0)]
    elif line1.end == line2.start:
        return [(1.0, 0.0)]
    elif line1.end == line2.end:
        return [(1.0, 1.0)]
    elif len(line1.intersect(line2)) != 0:
        return line1.intersect(line2)
    else:
        return []


# sortedlines(h or v)
def combineLines(parallellineobjs):
    # todo: assert parallel
    result = []
    lines = []
    length = len(parallellineobjs)
    sortedlines = sorted(parallellineobjs)
    k = 0
    for i in range(0, length):
        if i < k:
            continue
        start = sortedlines[i].line.start
        end = sortedlines[i].line.end
        newL = sortedlines[i].line
        for j in range(i + 1, length):
            bj = sortedlines[j].line.bbox()
            bi = newL.bbox()
            if sortedlines[j].position == sortedlines[i].position and line1_is_overlap_with_line2(newL, sortedlines[
                j].line) is True:
                end = complex(max(bi[1], bj[1]), max(bi[3], bj[3]))
                newL = Line(start, end)
            else:
                break
        if sortedlines[i].line.end != end:
            # todo: bu neng tiao bu
            k = j
        newLine = Line(start, end)
        if newLine not in lines:
            lines.append(newLine)
    for newLine in lines:
        b = newLine.bbox()
        if b[0] == b[1]:
            result.append(LineNavigation(b[0], b[2], b[3], newLine))
        elif b[2] == b[3]:
            result.append(LineNavigation(b[2], b[0], b[1], newLine))
    return result


def combineLinesx(microlines):
    # todo: assert parallel
    result = []
    lines = []
    length = len(microlines)
    orderedLines = []
    for line in microlines:
        newline = line.order()
        orderedLines.append(newline)
    sortedlines = sorted(orderedLines)
    k = 0
    for i in range(0, length):
        if i < k:
            continue
        start = sortedlines[i].start
        end = sortedlines[i].end
        newL = MicroLine(start,end)
        for j in range(i + 1, length):
            bj = sortedlines[j].bbox()
            bi = newL.bbox()
            if line1_is_overlap_with_line2x(newL, sortedlines[j]) is True:
                end = Coordinate(max(bi[1], bj[1]), max(bi[3], bj[3]))
                newL = MicroLine(start, end)
            else:
                break
        if sortedlines[i].end != end:
            # todo: bu neng tiao bu
            k = j
            if j == length-1:
                k = length
        newLine = MicroLine(start, end)
        if newLine not in lines:
            lines.append(newLine)
    last = two_lines_intersection(sortedlines[-1], lines[-1])
    if last is not None and last == sortedlines[-1]:
        pass
    elif last is not None and last != sortedlines[-1]:
        newLine = MicroLine(min(last.start,sortedlines[-1].start), max(last.end,sortedlines[-1].end))
        lines.remove(lines[-1])
        lines.append(newLine)
    else:
        lines.append(sortedlines[-1])
    for newLine in lines:
        result.append(newLine)
    return result


def point_on_hline(point, hline):
    if hline.start <= point.real <= hline.end and hline.position == point.imag:
        return True
    else:
        return False

# todo test this method
def combineLinesWithPoints(allLines, cutPoints):
    sortedhlines = sorted(allLines)
    sortedPoints = sorted(cutPoints)
    upcuthlines = []
    result = []
    #todo one line is missing
    remainLines = sortedhlines
    processedLineQueue = []
    for pointobj in sortedPoints:
        for lineobj in remainLines:
            if point_on_hline(pointobj.point, lineobj):
                start = lineobj.line.start
                end = pointobj.point
                if start != end:
                    leftLine = Line(start, end)
                    processedLineQueue.append(LineNavigation(start.imag, start.real, end.real, leftLine))
                indexofline = remainLines.index(lineobj)
                length = len(remainLines)
                tempLines = []
                for i in range(indexofline, length):
                    if point_on_hline(pointobj.point, remainLines[i]):
                        start = pointobj.point
                        end = remainLines[i].line.end
                        if start != end:
                            newLine = Line(start, end)
                            tempLines.append(LineNavigation(start.imag, start.real, end.real, newLine))
                    else:
                        tempLines.append(remainLines[i])
                remainLines = tempLines
                break
            else:
                processedLineQueue.append(lineobj)
        processedLine = combineLines(processedLineQueue)
        processedLineQueue = []
        for line in processedLine:
            if line not in result:
                result.append(line)
    if len(remainLines) != 0:
        processedLine = combineLines(remainLines)
    for line in processedLine:
        if line not in result:
            result.append(line)

    # todo collect curProcessedLine

    return result

def path1_is_contained_in_path2(path1, path2):
    assert path2.isclosed()  # This question isn't well-defined otherwise
    # find a point that's definitely outside path2
    xmin, xmax, ymin, ymax = path2.bbox()
    B = (xmin + 1) + 1j * (ymax + 1)

    A = (path1.start + path1.end) / 2  # pick an arbitrary point in path1
    AB_line = Path(Line(A, B))
    number_of_intersections = len(AB_line.intersect(path2))
    if number_of_intersections % 2:  # if number of intersections is odd
        return True
    else:
        return False

def line1_is_overlap_with_line2x(line1, line2):
    b1 = line1.bbox()
    b2 = line2.bbox()
    if max(b1[0], b2[0]) <= min(b1[1], b2[1]) and b1[2] == b2[2] == b1[3] == b2[3]:
        return True
    elif max(b1[2], b2[2]) <= min(b1[3], b2[3]) and b1[0] == b2[0] == b1[1] == b2[1]:
        return True
    else:
        return False

def line_on_path(line, path):
    for pathline in path:
        if line == pathline:
            return path.index(pathline)
        elif line1_is_overlap_with_line2x(line, pathline):
            return path.index(pathline)
    return None

def combinePaths(path1, path2, intersectline):
    #assert intersectline not one
    keepLines = []
    for line1 in path1:
        if line1_is_overlap_with_line2x(line1,intersectline[0]) == False:
            keepLines.append(line1)
        else:
            newLines = cutline(line1, intersectline[0])
            for line in newLines:
                keepLines.append(line)
    for line1 in path2:
        if line1_is_overlap_with_line2x(line1,intersectline[0]) == False:
            keepLines.append(line1)
        else:
            newLines = cutline(line1, intersectline[0])
            for line in newLines:
                keepLines.append(line)
    result = createPath(keepLines)
    return result

def cutline(line1, line2):
    #assert self longer than other or ...
    #assert overlapped line
    # assert line1 line2 overlapped
    result = []
    l1 = line1.order()
    l2 = line2.order()
    #start != end should inside init line
    if l1.start < l2.start:
        result.append(MicroLine(l1.start,l2.start))
    if l1.end > l2.end:
        result.append(MicroLine(l2.end,l1.end))
    return result

def createPath(lines):
    hlines = []
    vlines = []
    refinedLines = []
    roundLines = []
    for line in lines:
        start = Coordinate(round(line.start.real,3), round(line.start.imag,3))
        end = Coordinate(round(line.end.real, 3), round(line.end.imag, 3))
        newLine = MicroLine(start,end)
        roundLines.append(newLine)
    for line in roundLines:
        b = line.bbox()
        if line.start.real == line.end.real:
            #vlines.append(LineNavigation(b[0], b[2], b[3], line))
            vlines.append(line)
        if line.start.imag == line.end.imag:
            #hlines.append(LineNavigation(b[2], b[0], b[1], line))
            hlines.append(line)
    combinevlines = combineLinesx(vlines)
    combinehlines = combineLinesx(hlines)
    for line in combinevlines:
        refinedLines.append(line)
    for line in combinehlines:
        refinedLines.append(line)
    path = Path()
    path.append(refinedLines[0])
    length = len(refinedLines)
    used = [0] * length
    used[0] = 1

    for i in range(1, length):
        for j in range(1, length):
            if used[j] == 0:
                if path.start == refinedLines[j].start:
                    newLine = refinedLines[j].reversed()
                    newMLine = MicroLine(newLine.start, newLine.end)
                    path.insert(0,newMLine)
                    used[j] = 1
                    break
                elif path.start == refinedLines[j].end:
                    path.insert(0, refinedLines[j])
                    used[j] = 1
                    break
                elif path.end == refinedLines[j].start:
                    path.append(refinedLines[j])
                    used[j] = 1
                    break
                elif path.end == refinedLines[j].end:
                    newLine = refinedLines[j].reversed()
                    newMLine = MicroLine(newLine.start, newLine.end)
                    path.append(newMLine)
                    used[j] = 1
                    break
    return path

def two_lines_intersection(line1, line2):
    b1 = line1.bbox()
    b2 = line2.bbox()
    if line1_is_overlap_with_line2x(line1,line2):
        start = Coordinate(max(b1[0],b2[0]), max(b1[2],b2[2]))
        end = Coordinate(min(b1[1],b2[1]), min(b1[3],b2[3]))
        if start != end:
            intersection = MicroLine(start, end)
            return intersection
    else:
        return None
#for silly intersect method
def two_paths_intersection(path1,path2):
    intersect = []
    for line1 in path1:
        for line2 in path2:
            line1 = MicroLine(Coordinate(line1.start), Coordinate(line1.end))
            line2 = MicroLine(Coordinate(line2.start), Coordinate(line2.end))
            if line1 == line2:
                if line1 not in intersect:
                    intersect.append(line1)
            elif line1_is_overlap_with_line2x(line1, line2):
                line = two_lines_intersection(line1, line2)
                if line is not None:
                    newline = MicroLine(Coordinate(line.start), Coordinate(line.end))
                    if newline not in intersect:
                        intersect.append(newline)
    return intersect

#rawpaths, attributes = svg2paths('/Users/my/Desktop/MasterThesis/mt1git/ImageToTextDescriptor/svg/171130-IDELayout-final/171130-IDELayout-final.svg')
rawpaths, attributes = svg2paths('/Users/my/Desktop/MasterThesis/mt1git/ImageToTextDescriptor/svg/171130-MicroHeaterLayout-final/171130-MicroHeaterLayout-final.svg')
#rawpaths, attributes = svg2paths('/Users/my/Desktop/MasterThesis/mt1git/ImageToTextDescriptor/svg/LAYER1/LAYER1_01.svg')
#rawpaths, attributes = svg2paths('/Users/my/Desktop/MasterThesis/mt1git/ImageToTextDescriptor/svg/LAYER2/LAYER2_01.svg')

pathss = []


ydev = 1
offsetx, offsety = preconfig(rawpaths)
paths = svgpreprocess(rawpaths, attributes)


curdistincthlines = []
cuthlineobjs = []
cutvpointobjs = []
allhlineobjs = []
cutlines = []
distincthpaths = []
curdistincthlinesobjs = []
cutlineobjs = []
curdistinctpaths = []

all = []



# todo: collect h lines
for path in paths:

    sortedhlines, sortedvlines, filteredPath, filteredPoints = pathpreprocess(path, offsetx, offsety)
    sortedhlinesy = map(attrgetter('position'), sortedhlines)
    sortedvlinesx = map(attrgetter('position'), sortedvlines)
    # todo pick one shorter line
    # todo if vline
    # todo if hline

    for pointobj in filteredPoints:
        # todo point to two cutlines
        cuthline = None
        cutvline = None
        intersecthlines = [x for x in sortedhlines if x.start <= pointobj.point.real <= x.end]
        intersectvlines = [x for x in sortedvlines if x.start <= pointobj.point.imag <= x.end]
        intersecthlinesy = map(attrgetter('position'), intersecthlines)
        intersectvlinesx = map(attrgetter('position'), intersectvlines)
        if pointobj.point == pointobj.hline.start:
            # left extend
            end = pointobj.point
            leftvlineno = bisect_left(intersectvlinesx, end.real) - 1
            if len(intersectvlines) > leftvlineno >= 0:
                start = complex(intersectvlines[leftvlineno].position, end.imag)
                leftcuthline = Line(start, end)
                if path1_is_contained_in_path2(leftcuthline, filteredPath):
                    # todo add to cutlines hou bu
                    cuthline = leftcuthline
        else:
            # right extend
            start = pointobj.point
            rightvlineno = bisect_right(intersectvlinesx, start.real)
            if 0 < rightvlineno < len(intersectvlines):
                end = complex(intersectvlines[rightvlineno].position, start.imag)
                rightcuthline = Line(start, end)
                if path1_is_contained_in_path2(rightcuthline, filteredPath):
                    # todo add to cutlines hou bu
                    cuthline = rightcuthline

        if pointobj.point == pointobj.vline.start:
            # up extend
            end = pointobj.point
            uphlineno = bisect_left(intersecthlinesy, end.imag) - 1
            if len(intersecthlines) > uphlineno >= 0:
                start = complex(end.real, intersecthlines[uphlineno].position)
                upcutvline = Line(start, end)
                if path1_is_contained_in_path2(upcutvline, filteredPath):
                    # todo add to cutlines hou bu
                    cutvline = upcutvline
                    cutvpoint = PointNavigation(start, intersecthlines[uphlineno].line, None)
        else:
            # down extend
            start = pointobj.point
            downhlineno = bisect_right(intersecthlinesy, start.imag)
            if 0 < downhlineno < len(intersecthlines):
                end = complex(start.real, intersecthlines[downhlineno].position)
                downcutvline = Line(start, end)
                if path1_is_contained_in_path2(downcutvline, filteredPath):
                    # todo add to cutlines hou bu
                    cutvline = downcutvline
                    cutvpoint = PointNavigation(end, intersecthlines[downhlineno].line, None)

        # compare two line:
        cutvlinelength = 0
        cuthlinelength = 0
        curcutline = None

        if cutvline != None:
            cutvlinelength = cutvline.length()
        if cuthline != None:
            cuthlinelength = cuthline.length()

        if cutvlinelength != 0 and (cuthlinelength > cutvlinelength or cuthlinelength == 0):
            curcutline = cutvline
            cutvpointobjs.append(cutvpoint)
            # todo add above hline
        elif cuthlinelength != 0 and (cutvlinelength >= cuthlinelength or cutvlinelength == 0):
            curcutline = cuthline
            b = curcutline.bbox()
            newLine = LineNavigation(b[2], b[0], b[1], curcutline)
            cuthlineobjs.append(newLine)
            allhlineobjs.append(newLine)

    for line in sortedhlines:
        allhlineobjs.append(line)

    combinedhlines = combineLinesWithPoints(allhlineobjs, cutvpointobjs)
    for line in combinedhlines:
        curdistincthlinesobjs.append(line)
    # todo add cuthline to cur
    for line in cuthlineobjs:
        if line not in curdistincthlinesobjs:
            curdistincthlinesobjs.append(line)
            cutlines.append(line.line)

        # todo: create rect with last hline, in order to redraw the pic
    curdistincthlinesobjs = sorted(curdistincthlinesobjs)
    for obj in curdistincthlinesobjs:
        curdistincthlines.append(obj.line)
        all.append(obj.line)
    length = len(curdistincthlines)
    used = length * [0]
    curdistincthlinesy = map(attrgetter('start.imag'), curdistincthlines)
    for i in range(0, length):
        # todo add intersect
        if used[i] == 0:
            intersectlines = []
            for x in curdistincthlines:
                if curdistincthlines.index(x) > i:
                    if x.start.real == curdistincthlines[i].start.real and curdistincthlines[i].end.real == x.end.real:
                        intersectlines.append(x)
            intersectlinesy = map(attrgetter('start.imag'), intersectlines)
            nextstart = bisect(intersectlinesy, curdistincthlinesy[i])
            lens = len(intersectlines)
            if nextstart >= lens:
                continue
            nextend = bisect(intersectlinesy, intersectlinesy[nextstart])
            if nextend > lens:
                continue
            for j in range(nextstart, nextend):
                if used[curdistincthlines.index(intersectlines[j])] == 0:
                    if curdistincthlines[i].start.real == intersectlines[j].start.real and curdistincthlines[
                        i].end.real == \
                            intersectlines[j].end.real:
                            UperLine = curdistincthlines[i]
                            Lowerline = intersectlines[j]
                            newPath = Path(UperLine, Line(UperLine.end, Lowerline.end),
                                   Line(Lowerline.end, Lowerline.start),
                                   Line(Lowerline.start, UperLine.start))
                            used[curdistincthlines.index(intersectlines[j])] = 1
                            curdistinctpaths.append(newPath)
    #wsvg(curdistinctpaths, filename='ooutput.svg', openinbrowser=True)
    #todo: inside a path.
    curcombinedPaths = []
    curMicdistinctpaths = []
    for path in curdistinctpaths:
        p = Path()
        for line in path:
            l = MicroLine(Coordinate(line.start), Coordinate(line.end))
            p.append(l)
        curcombinedPaths.append(p)
        curMicdistinctpaths.append(p)

    #wsvg(curMicdistinctpaths, filename='outputj.svg', openinbrowser=True)
    flag = 1
    while(flag == 1):
        curMicdistinctpaths = curcombinedPaths
        flag = 0
        for path1 in curMicdistinctpaths:
            for path2 in curMicdistinctpaths:
                if path1 != path2:
                    inter = two_paths_intersection(path1, path2)
                    if len(inter) != 0:
                        flag = 1
                        newPath = combinePaths(path1, path2, inter)
                        curcombinedPaths.remove(path1)
                        curcombinedPaths.remove(path2)
                        curcombinedPaths.append(newPath)
                        break
            if flag == 1:
                break


    for path in curcombinedPaths:
        distincthpaths.append(path)
    #wsvg(curcombinedPaths, filename='outputj.svg', openinbrowser=True)

    curdistincthlines = []
    curdistincthlinesobjs = []
    cutlines = []
    allhlineobjs = []
    cuthlineobjs = []
    curdistinctpaths = []

wsvg(distincthpaths, filename='lastoutput.svg', openinbrowser=True)

print len(distincthpaths)


#todo: add condition to inter (some combine, some not)
