#!/usr/bin/python
from os import getcwd, listdir, sep, remove, error, path
from tools.directories import Build
from tools.pdf import Explode, ConvertToSVG
from operator import attrgetter
from bisect import *
import time
from svgpathtools import svg2paths, wsvg
from svgpathtools import *
from tools.cut import LineNavigation, PointNavigation
import re


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
        start = complex(round(line.start.real - offsetx, 10), round(line.start.imag - offsety, 10))
        end = complex(round(line.end.real - offsetx, 10), round(line.end.imag - offsety, 10))
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
            points = sorted(intersectpoints)
            newvline = Line(vline.line.point(min(points)), vline.line.point(max(points)))
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
            points = sorted(intersectpoints)
            newhline = Line(hline.line.point(min(points)), hline.line.point(max(points)))
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


def point_on_hline(point, hline):
    if hline.start < point.real < hline.end and hline.position == point.imag:
        return True
    else:
        return False

def point_on_hline1(point, hline):
    if hline.start <= point.real <= hline.end and hline.position == point.imag:
        return True
    else:
        return False

# todo test this method
def combineLinesWithPoints(allLines, cutPoints):
    result = []
    lines = []
    length = len(allLines)
    sortedhlines = sorted(allLines)
    sortedPoints = sorted(cutPoints)
    lengthofPoint = len(sortedPoints)
    upcuthlines = []
    result = []
    k = 0
    pointindex = 0
    nextStartLine = None
    curLineQueue = []

    for pointobj in sortedPoints:
        lines = []
        start = pointobj.point
        end = pointobj.point
        lastpoint = None
        nextpoint = None
        for lineobj in sortedhlines:
            if point_on_hline1(pointobj.point, lineobj):
                #todo assert if not on any line
                tempend = lineobj.line.end
                start = lineobj.line.start
                if tempend.real < end.real or end.real == pointobj.point.real:
                    end = tempend

        leftline = Line(start, pointobj.point)
        rightline = Line(pointobj.point, end)
        rightlineobj = LineNavigation(rightline.start.imag, rightline.start.real, rightline.end.real, rightline)
        leftlineobj = LineNavigation(leftline.start.imag, leftline.start.real, leftline.end.real, leftline)
        index = sortedPoints.index(pointobj)
        if index > 0:
            lastpoint = sortedPoints[index-1].point
        if index < len(sortedPoints)-1:
            nextpoint = sortedPoints[index+1].point
        if lastpoint != None and point_on_hline1(lastpoint, leftlineobj):
            leftline = Line(lastpoint, pointobj.point)
        if nextpoint != None and point_on_hline1(nextpoint, rightlineobj):
            rightline = Line(pointobj.point, nextpoint)
        upcuthlines.append(LineNavigation(rightline.start.imag, rightline.start.real, rightline.end.real, rightline))
        upcuthlines.append(LineNavigation(leftline.start.imag, leftline.start.real, leftline.end.real, leftline))

    for i in range(0, length):
        if i <= k and k != 0:
            continue
        if pointindex < lengthofPoint:
            if point_on_hline(sortedPoints[pointindex].point, sortedhlines[i]):
                newLine = Line(sortedhlines[i].line.start, sortedPoints[pointindex].point)
                b = newLine.bbox()
                curLineQueue.append(LineNavigation(b[2], b[0], sortedPoints[pointindex].point.real, newLine))
                curProcessedLines = combineLines(curLineQueue)
                for line in curProcessedLines:
                    if line not in result:
                        result.append(line)
                curProcessedLines = []
                nextStartLine = Line(sortedPoints[pointindex].point, sortedhlines[i].line.end)
                b = nextStartLine.bbox()
                curLineQueue = []
                curLineQueue.append(LineNavigation(b[2], b[0], b[1], nextStartLine))
                # todo find next line which contains point (start > nextStartLine.start)
                k = i + 1
                for j in range(i + 1, length):
                    if sortedhlines[j].line.start.imag == nextStartLine.start.imag and sortedhlines[
                        j].line.start.real < nextStartLine.start.real:
                        k = j
                    else:
                        continue
                pointindex += 1
            else:
                curLineQueue.append(sortedhlines[i])
        elif i < length:
            curLineQueue.append(sortedhlines[i])
    curProcessedLines = combineLines(curLineQueue)
    # todo collect curProcessedLine
    for line in curProcessedLines:
        if line not in result:
            result.append(line)
    return result, upcuthlines


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


# rawpaths, attributes = svg2paths('/Users/my/Desktop/MasterThesis/mt1git/ImageToTextDescriptor/svg/171130-IDELayout-final/171130-IDELayout-final.svg')
rawpaths, attributes = svg2paths('/Users/my/Desktop/MasterThesis/mt1git/ImageToTextDescriptor/svg/171130-MicroHeaterLayout-final/171130-MicroHeaterLayout-final.svg')
#rawpaths, attributes = svg2paths('/Users/my/Desktop/MasterThesis/mt1git/ImageToTextDescriptor/svg/LAYER1/LAYER1_01.svg')
#rawpaths, attributes = svg2paths('/Users/my/Desktop/MasterThesis/mt1git/ImageToTextDescriptor/svg/LAYER2/LAYER2_01.svg')

a = complex(0,0)
b = complex(1,0)
c = complex(2,0)
d = complex(3,0)

l1 = LineNavigation(a.imag, a.real, b.real, Line(a,b))
l2 = LineNavigation(a.imag, a.real, c.real, Line(a,c))
l3 = LineNavigation(b.imag, b.real, c.real, Line(b,c))
l4 = LineNavigation(b.imag, b.real, d.real, Line(b,d))

p1 = PointNavigation(c, None, None)
p2 = PointNavigation(complex(1.5,0), None, None)

ls  = []
ls.append(l1)
ls.append(l2)
ls.append(l3)
ls.append(l4)

p = []
p.append(p1)
p.append(p2)

combineLinesWithPoints(ls, p)

test = []

pathss = Path()
for i in range(0, 16):
    pathss.append(rawpaths[0][i])
length = len(rawpaths)
pathss.append(Line(rawpaths[0][15].end, rawpaths[0][length - 16].start))
for i in range(16, 0, -1):
    pathss.append(rawpaths[0][length - i -1])
pathsss = []
pathsss.append(pathss)

ydev = 1
offsetx, offsety = preconfig(pathsss)
paths = svgpreprocess(pathsss, attributes)


curdistincthlines = []
cuthlineobjs = []
cutvpointobjs = []
allhlineobjs = []
cutlines = []
distincthpaths = []
curdistincthlinesobjs = []
cutlineobjs = []

all = []
# todo: collect h lines
for path in pathsss:
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
    combinedhlines, upcuthlines = combineLinesWithPoints(allhlineobjs, cutvpointobjs)
    for line in combinedhlines:
        curdistincthlinesobjs.append(line)
    # todo add cuthline to cur
    for line in cuthlineobjs:
        if line not in curdistincthlines:
            curdistincthlinesobjs.append(line)
            cutlines.append(line.line)
    for line in upcuthlines:
        if line in upcuthlines:
            if line not in curdistincthlines:
                curdistincthlinesobjs.append(line)

        # todo: create rect with last hline, in order to redraw the pic
    curdistincthlinesobjs = sorted(curdistincthlinesobjs)
    for obj in curdistincthlinesobjs:
        curdistincthlines.append(obj.line)

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
                        if curdistincthlines[i] in cutlines:
                            cuty = curdistincthlines[i].start.imag - ydev
                            UperLine = Line(complex(curdistincthlines[i].start.real, cuty),
                                            complex(curdistincthlines[i].end.real, cuty))
                        else:
                            UperLine = curdistincthlines[i]
                        if intersectlines[j] in cutlines:
                            cuty = intersectlines[j].start.imag + ydev
                            Lowerline = Line(complex(intersectlines[j].start.real, cuty),
                                             complex(intersectlines[j].end.real, cuty))
                        else:
                            Lowerline = intersectlines[j]
                    newPath = Path(UperLine, Line(UperLine.end, Lowerline.end),
                                   Line(Lowerline.end, Lowerline.start),
                                   Line(Lowerline.start, UperLine.start))
                    used[curdistincthlines.index(intersectlines[j])] = 1
                    distincthpaths.append(newPath)
    curdistincthlines = []
    curdistincthlinesobjs = []
    cutlines = []
    allhlineobjs = []
    cuthlineobjs = []


wsvg(test, filename='output.svg', openinbrowser=True)






