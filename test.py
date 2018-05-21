#!/usr/bin/python
import re
from bisect import *
from svgpathtools import *
from tools.cut import LineNavigation, PointNavigation, MicroLine, Coordinate
from operator import attrgetter

from os import getcwd, listdir, sep, remove, error, path
from svgpathtools import svg2paths, wsvg


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
        offsety = -10
    else:
        offsety -= 10
    if offsetx >= 0:
        offsetx = -10
    else:
        offsetx -= 10

    return offsetx, offsety

# process based on attributes
def svgpreprocess(paths, attributes):
    length = len(attributes)
    scale = [1] * length
    newPathList = []
    result = []
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

    for path in newPathList:
        newPath = Path()
        for line in path:
            start = Coordinate(round(line.start.real - offsetx, 3), round(line.start.imag - offsety, 3))
            end = Coordinate(round(line.end.real - offsetx, 3), round(line.end.imag - offsety, 3))
            newline = MicroLine(start, end)
            newPath.append(newline)
        result.append(newPath)
    return result

def pathpreprocess(rawpath, offsetx, offsety):
    hlines = []
    vlines = []
    filteredPath = Path()
    filteredPointsObj = []
    filteredPoints = []
    path = []

    for line in rawpath:
        start = Coordinate(round(line.start.real - offsetx, 3), round(line.start.imag - offsety, 3))
        end = Coordinate(round(line.end.real - offsetx, 3), round(line.end.imag - offsety, 3))
        newline = MicroLine(start, end)
        path.append(newline)

    for line in path:
        if line.start != line.end:
            if line.direction() == 'h':
                hlines.append(line)
            if line.direction() == 'v':
                vlines.append(line)

    sortedhlines = combineLines(hlines)
    sortedvlines = combineLines(vlines)
    filteredVlines = []
    filteredHlines = []

    for vline in sortedvlines:
        intersectpoints = []
        for hline in sortedhlines:
            x = line1_intersect_with_line2(vline, hline)
            if len(x) != 0:
                intersectpoints.append(x[0][0])
        if len(intersectpoints) >= 2:
            newvline = MicroLine(Coordinate(vline.point(min(intersectpoints))), Coordinate(vline.point(max(intersectpoints))))
            filteredVlines.append(newvline)
    for hline in sortedhlines:
        intersectpoints = []
        for vline in sortedvlines:
            x = line1_intersect_with_line2(hline, vline)
            if len(x) != 0:
                intersectpoints.append(x[0][0])
        if len(intersectpoints) >= 2:
            newhline = MicroLine(Coordinate(hline.point(min(intersectpoints))), Coordinate(hline.point(max(intersectpoints))))
            filteredHlines.append(newhline)

    # todo filteredPath not closed
    for line in path:
        if line.start != line.end:
            filteredPath.append(line)

    for line in filteredHlines:
        if line.start not in filteredPoints:
            filteredPoints.append(line.start)
            startPoint = PointNavigation(line.start, None, None)
            filteredPointsObj.append(startPoint)
        if line.end not in filteredPoints:
            filteredPoints.append(line.end)
            endPoint = PointNavigation(line.end, None, None)
            filteredPointsObj.append(endPoint)
        for pointobj in filteredPointsObj:
            if pointobj.point == line.start:
                pointobj.hline = line
            if pointobj.point == line.end:
                pointobj.hline = line

    for line in filteredVlines:
        if line.start not in filteredPoints:
            filteredPoints.append(line.start)
            startPoint = PointNavigation(line.start, None, None)
            filteredPointsObj.append(startPoint)
        if line.end not in filteredPoints:
            filteredPoints.append(line.end)
            endPoint = PointNavigation(line.end, None, None)
            filteredPointsObj.append(endPoint)
        for pointobj in filteredPointsObj:
            if pointobj.point == line.start:
                pointobj.vline = line
            if pointobj.point == line.end:
                pointobj.vline = line

    return sortedhlines, sortedvlines, filteredPath, filteredPointsObj


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

def combineLines(microlines):
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
            if line1_is_overlap_with_line2(newL, sortedlines[j]) is True:
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

# todo changed hlineobj into hline
def point_on_line(point, line):
    l0 = line.order()
    if l0.start.imag == point.imag:
        if l0.start.real <= point.real <= l0.end.real:
            return True
    elif l0.start.real == point.real:
        if l0.start.imag <= point.imag <= l0.end.imag:
            return True
    else:
        return False

# todo test this method
def combineLinesWithPoints(allLines, cutPoints):
    sortedhlines = sorted(allLines)
    sortedPoints = sorted(cutPoints)
    result = []
    #todo one line is missing
    remainLines = sortedhlines
    processedLineQueue = []
    for pointobj in sortedPoints:
        for line in remainLines:
            if point_on_line(pointobj.point, line):
                start = line.start
                end = pointobj.point
                if start != end:
                    leftLine = MicroLine(start, end)
                    processedLineQueue.append(leftLine)
                indexofline = remainLines.index(line)
                length = len(remainLines)
                tempLines = []
                for i in range(indexofline, length):
                    if point_on_line(pointobj.point, remainLines[i]):
                        start = pointobj.point
                        end = remainLines[i].end
                        if start != end:
                            newLine = MicroLine(start, end)
                            tempLines.append(newLine)
                    else:
                        tempLines.append(remainLines[i])
                remainLines = tempLines
                break
            else:
                processedLineQueue.append(line)
        if len(processedLineQueue) != 0:
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

def line1_is_overlap_with_line2(line1, line2):
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
        elif line1_is_overlap_with_line2(line, pathline):
            return path.index(pathline)
    return None

def combinePaths(path1, path2, intersectline):
    #assert intersectline not one
    keepLines = []
    for line1 in path1:
        if line1_is_overlap_with_line2(line1,intersectline[0]) == False:
            keepLines.append(line1)
        else:
            newLines = cutline(line1, intersectline[0])
            for line in newLines:
                keepLines.append(line)
    for line1 in path2:
        if line1_is_overlap_with_line2(line1,intersectline[0]) == False:
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
            vlines.append(line)
        if line.start.imag == line.end.imag:
            hlines.append(line)
    combinevlines = combineLines(vlines)
    combinehlines = combineLines(hlines)
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
    if line1_is_overlap_with_line2(line1,line2):
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
            elif line1_is_overlap_with_line2(line1, line2):
                line = two_lines_intersection(line1, line2)
                if line is not None:
                    newline = MicroLine(Coordinate(line.start), Coordinate(line.end))
                    if newline not in intersect:
                        intersect.append(newline)
    return intersect

def two_lines_distance(line1,line2):
    if line1.direction() == line2.direction() == 'h':
        dis = line1.start.imag - line2.start.imag
    elif line1.direction() == line2.direction() == 'v':
        dis = line1.start.real - line2.start.real
    else:
        return NotImplemented
    return dis

# intersectlines in lines for line
def line_intersectlines(line, lines):
    direct = line.direction()
    l1 = line.order()
    intersectlines = []
    for l in lines:
        l2 = l.order()
        if l1 != l2:
            if l2.direction() == direct == 'h':
                if l1.start.real <= l2.end.real and l1.end.real >= l2.start.real:
                    intersectlines.append(l2)
            if l2.direction() == direct == 'v':
                if l1.start.imag <= l2.end.imag and l1.end.imag >= l2.start.imag:
                    intersectlines.append(l2)
    return intersectlines

def getDev(path, line):
    l0 = line.order()
    intersectlines = line_intersectlines(l0, path)
    dev = two_lines_distance(l0,intersectlines[0])
    for pl in intersectlines:
        if dev == 0:
            dev = two_lines_distance(l0,pl)
            continue
        dis = two_lines_distance(l0,pl)
        if abs(dis) < abs(dev) and dis != 0:
            dev = dis
    return dev

def changePath(path, index, dev, factor):
    newPath = Path()
    l0 = path[index]
    if l0.direction() == 'h':
        deviation = Coordinate(0, -(dev * factor))
    else:
        deviation = Coordinate(-(dev * factor), 0)
    for line in path:
        if line != l0:
            point = line1_intersect_with_line2(line,l0)
            if len(point) != 0:
                roundpoint = round(point[0][0],3)
                if roundpoint == 1:
                    end = Coordinate(line.end + deviation)
                    newPath.append(MicroLine(line.start, end))
                if roundpoint == 0:
                    start = Coordinate(line.start + deviation)
                    newPath.append(MicroLine(start, line.end))
            else:
                newPath.append(line)
        else:
            newLine = MicroLine(Coordinate(l0.start + deviation), Coordinate(l0.end + deviation))
            newPath.append(newLine)

    return newPath

def two_paths_distance(path1,path2):
    dev = 0
    b1 = path1.bbox()
    b2 = path2.bbox()
    if b1[1] < b2[0]:
        dev =b2[0] - b1[1]
    elif b1[3] < b2[2]:
        dev = b2[2] - b1[3]
    elif b2[1] < b1[0]:
        dev = b1[0] - b2[1]
    elif b2[3] < b1[2]:
        dev = b1[2] - b2[3]
    return dev

def no_merge_conflict(path1, path2, factor):
    if 0 < two_paths_distance(path1,path2) < factor:
        return True
    else:
        return False

def no_absorption_conflict(path1, path2, factor):
    x = two_paths_intersection(path1, path2)
    if len(x) == 0:
        return False, None, None
    #assert closed()
    #assert len(x) == 1
    print 'yoyo'
    length = float(x[0].length())
    print x[0]
    area = 0
    path = Path()
    if x[0] in path1:
        area = float(abs(path2.area()))
        path = path2
    elif x[0] in path2:
        area = float(abs(path1.area()))
        path = path1
    ratio = 1
    print ('path:%s'%(length))
    print path
    if area != 0:
        ratio = length / area
        print ratio
    #path: bigger path
    if ratio < factor:
        return True, x[0], path
    else:
        return False, x[0], path

logfile = 'conflict.txt'


try:
    if path.isfile(logfile):
        remove(logfile)
        out = open(logfile, 'w')
        out.close()
except error, value:
    print value[1]

currentpath = getcwd()

def logthis(newtext):
    log = currentpath + sep + logfile
    input = open(log, 'r')
    text = input.read()
    input.close()
    output = open(log, 'w')
    output.write(text + newtext)
    output.close()


#rawpaths, attributes = svg2paths('/Users/my/Desktop/MasterThesis/mt1git/ImageToTextDescriptor/svg/171130-IDELayout-final/171130-IDELayout-final.svg')
#rawpaths, attributes = svg2paths('/Users/my/Desktop/MasterThesis/mt1git/ImageToTextDescriptor/svg/171130-MicroHeaterLayout-final/171130-MicroHeaterLayout-final.svg')
rawpaths, attributes = svg2paths('/Users/my/Desktop/MasterThesis/mt1git/ImageToTextDescriptor/svg/LAYER1/LAYER1_01.svg')
#rawpaths, attributes = svg2paths('/Users/my/Desktop/MasterThesis/mt1git/ImageToTextDescriptor/svg/LAYER2/LAYER2_01.svg')
#rawpaths, attributes = svg2paths('/Users/my/Desktop/MasterThesis/mt1git/ImageToTextDescriptor/svg/LAYER3/LAYER3_01.svg')

pathss = []

kk = 5
ydev = 1
offsetx, offsety = preconfig(rawpaths)
paths = svgpreprocess(rawpaths, attributes)

frame = Path()
fakeframe = Path()
fb = paths[0].bbox()
xmin = fb[0]
xmax = fb[1]
ymin = fb[2]
ymax = fb[3]

#todo find frame
for path1 in paths:
    b1 = path1.bbox()
    if len(path1) != 4:
        break
    frame = path1
    for path2 in paths:
        if path1 != path2:
            b2 = path2.bbox()
            if b1[0]<=b2[0]<=b1[1] and b1[0]<=b2[1]<=b1[1] and b1[2]<=b2[2]<=b1[3] and b1[2]<=b2[3]<=b1[3]:
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
    offset = max(xmax-xmin, ymax-ymin)*0.05
    frame = Path(MicroLine(Coordinate(xmin-offset, ymin-offset), Coordinate(xmax+offset, ymin-offset)), MicroLine(Coordinate(xmax+offset, ymin-offset), Coordinate(xmax+offset, ymax+offset)), MicroLine(Coordinate(xmax+offset, ymax+offset), Coordinate(xmin-offset, ymax+offset)), MicroLine(Coordinate(xmin-offset, ymax+offset), Coordinate(xmin-offset, ymin-offset)))

if frame in paths:
    paths.remove(frame)

offsetframe = Path()
for line in frame:
    start = Coordinate(line.start.real - offsetx, line.start.imag - offsety)
    end = Coordinate(line.end.real - offsetx, line.end.imag - offsety)
    newline = MicroLine(start, end)
    offsetframe.append(newline)


curdistincthlines = []
cuthlines = []
cutvpointobjs = []
allhlines = []
cutlines = []
distincthpaths = []
curdistincthlinesobjs = []
curdistincthlines = []
cutlineobjs = []
curdistinctpaths = []
removecutline = []
no_merge = {}
no_absorption = {}
allcurcutlines = []
orginalsPaths = []

all = []
narrow_factor = 0.05

absorb = 0
merge = 0

# todo: collect h lines
for path in paths:

    sortedhlines, sortedvlines, filteredPath, filteredPoints = pathpreprocess(path, offsetx, offsety)
    ran = max(abs(sortedhlines[-1].start.imag - sortedhlines[0].start.imag),abs(sortedvlines[-1].start.real - sortedvlines[0].start.real))
    narrowratio = narrow_factor * ran
    sortedhlinesy = map(attrgetter('start.imag'), sortedhlines)
    sortedvlinesx = map(attrgetter('start.real'), sortedvlines)
    # todo pick one shorter line
    # todo if vline
    # todo if hline

    for pointobj in filteredPoints:
        # todo point to two cutlines
        cuthline = None
        cutvline = None
        intersecthlines = [x for x in sortedhlines if x.start.real <= pointobj.point.real <= x.end.real]
        intersectvlines = [x for x in sortedvlines if x.start.imag <= pointobj.point.imag <= x.end.imag]
        intersecthlinesy = map(attrgetter('start.imag'), intersecthlines)
        intersectvlinesx = map(attrgetter('start.real'), intersectvlines)
        if pointobj.point == pointobj.hline.start:
            # left extend
            end = pointobj.point
            leftvlineno = bisect_left(intersectvlinesx, end.real) - 1
            if len(intersectvlines) > leftvlineno >= 0:
                start = Coordinate(intersectvlines[leftvlineno].start.real, end.imag)
                leftcuthline = MicroLine(start, end)
                if path1_is_contained_in_path2(leftcuthline, filteredPath):
                    # todo add to cutlines hou bu
                    cuthline = leftcuthline
        else:
            # right extend
            start = pointobj.point
            rightvlineno = bisect_right(intersectvlinesx, start.real)
            if 0 < rightvlineno < len(intersectvlines):
                end = Coordinate(intersectvlines[rightvlineno].start.real, start.imag)
                rightcuthline = MicroLine(start, end)
                if path1_is_contained_in_path2(rightcuthline, filteredPath):
                    # todo add to cutlines hou bu
                    cuthline = rightcuthline

        if pointobj.point == pointobj.vline.start:
            # up extend
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
            # down extend
            start = pointobj.point
            downhlineno = bisect_right(intersecthlinesy, start.imag)
            if 0 < downhlineno < len(intersecthlines):
                end = Coordinate(start.real, intersecthlines[downhlineno].start.imag)
                downcutvline = MicroLine(start, end)
                if path1_is_contained_in_path2(downcutvline, filteredPath):
                    # todo add to cutlines hou bu
                    cutvline = downcutvline
                    cutvpoint = PointNavigation(end, intersecthlines[downhlineno], None)

        # compare two line:
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
            if curcutline.length() >= narrowratio:
                removecutline.append(curcutline)
    #todo remove after testing

    for line in sortedhlines:
        allhlines.append(line)

    combinedhlines = combineLinesWithPoints(allhlines, cutvpointobjs)
    for line in combinedhlines:
        #todo delete obj
        curdistincthlines.append(line)
    # todo add cuthline to cur
    for line in cuthlines:
        if line not in curdistincthlinesobjs:
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
    #wsvg(curdistinctpaths, filename='output.svg', openinbrowser=True)
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

    cur_no_merge = {}
    for path1 in curMicdistinctpaths:
        cur_no_merge[path1] = []
        for path2 in curMicdistinctpaths:
            if path1 != path2:
                if no_merge_conflict(path1, path2, narrowratio*kk):
                    cur_no_merge[path1].append(path2)

    cur_no_absorption = {}
    keepcutlines = []
    for path1 in curMicdistinctpaths:
        cur_no_absorption[path1] = []
        for path2 in curMicdistinctpaths:
            if path1 != path2:
                conflict, line, bigpath = no_absorption_conflict(path1, path2, 0.2)
                if conflict:
                    keepcutlines.append(line)
                    cur_no_absorption[path1].append(path2)

    for cutl in allcurcutlines:
        if cutl not in keepcutlines:
            if cutl not in removecutline:
                removecutline.append(cutl)

    #wsvg(curMicdistinctpaths, filename='output1.svg', openinbrowser=True)
    flag = 1
    while(flag == 1):
        curMicdistinctpaths = curcombinedPaths
        flag = 0
        for path1 in curMicdistinctpaths:
            for path2 in curMicdistinctpaths:
                if path1 != path2:
                    if path2 in cur_no_merge[path1]:
                        merge += 1
                        continue
                    inter = two_paths_intersection(path1, path2)
                    if len(inter) != 0:
                        for cut in removecutline:
                            cutMline = MicroLine(Coordinate(cut.start), Coordinate(cut.end))
                            if two_lines_intersection(cutMline, inter[0]) is not None:
                                flag = 1
                                newPath = combinePaths(path1, path2, inter)
                                curcombinedPaths.remove(path1)
                                curcombinedPaths.remove(path2)
                                curcombinedPaths.append(newPath)
                                cur_no_merge[newPath] = []
                                for conflictpath in cur_no_merge[path1]:
                                    if conflictpath not in cur_no_merge[newPath] and conflictpath !=path2:
                                        #todo any unique list
                                        cur_no_merge[newPath].append(conflictpath)
                                for conflictpath in cur_no_merge[path2]:
                                    if conflictpath not in cur_no_merge[newPath] and conflictpath !=path1:
                                        cur_no_merge[newPath].append(conflictpath)
                                del cur_no_merge[path2]
                                del cur_no_merge[path1]
                                for k,v in cur_no_merge.items():
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
                                    if conflictpath not in cur_no_absorption[newPath] and conflictpath !=path2:
                                        #todo any unique list
                                        cur_no_absorption[newPath].append(conflictpath)
                                for conflictpath in cur_no_absorption[path2]:
                                    if conflictpath not in cur_no_absorption[newPath] and conflictpath !=path1:
                                        cur_no_absorption[newPath].append(conflictpath)
                                del cur_no_absorption[path2]
                                del cur_no_absorption[path1]
                                for k,v in cur_no_absorption.items():
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
    temp_no_merge = cur_no_merge
    for con in temp_no_merge.items():
        for i in con[1]:
            x = two_paths_intersection(con[0], i)
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
                    inter = two_paths_intersection(path1, path2)
                    if len(inter) != 0:
                        if inter[0] in path1:
                            dev = getDev(path2, inter[0])
                            newPath = changePath(path1, path1.index(inter[0]), dev, 0.2)
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
                            newPath = changePath(path2, path2.index(inter[0]), dev, 0.2)
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



    # todo: conflict2 connected conflict: compare area(ratio of cut areas)
    # todo: conflict1 near cannot be combined (refresh removecutline)
#todo: at the end detect no_merge_conflict again

    curdistincthlines = []
    curdistincthlinesobjs = []
    cutlines = []
    allhlines = []
    cuthlines = []
    curdistinctpaths = []
    allcurcutlines = []
    keepcutlines = []
    removecutline = []

no_merge_threshold = two_paths_intersection(distincthpaths[0], distincthpaths[1])
for path1 in distincthpaths:
    for path2 in distincthpaths:
        if path1 != path2:
            dis = two_paths_distance(path1, path2)
            if dis != 0 and dis < no_merge_threshold:
                no_merge_threshold = dis


no_mergex = {}
kk = 2
for path1 in distincthpaths:
    no_mergex[path1] = []
    for path2 in distincthpaths:
        if path1 != path2:
            if no_merge_conflict(path1, path2, no_merge_threshold*kk):
                no_mergex[path1].append(path2)
    if no_mergex[path1] == []:
        del no_mergex[path1]
'''
no_absorptionx = {}
print 'yoyoyoy'
no_absorp = 0.2
for path1 in distincthpaths:
    no_absorptionx[path1] = []
    for path2 in distincthpaths:
        if path1 != path2:
            conflict, line, bigpath = no_absorption_conflict(path1, path2, no_absorp)
            if conflict:
                no_absorptionx[path1].append(path2)
    if no_absorptionx[path1] == []:
        del no_absorptionx[path1]
'''
'''
if offsetframe != Path():
    s = abs(offsetframe.area())
    logthis('Chip %f' %(s))
    lineno = 0
    for line in offsetframe:
        lineno += 1
        logthis('line%s: %.3f+%.3fi,%.3f+%.3fi' % (lineno, line.start.real, line.start.imag, line.end.real, line.end.imag))

for path in distincthpaths:
    lineno = 0
    index = distincthpaths.index(path)+1
    s = abs(path.area())
    logthis('o%s %f' % (index, s))
    for line in path:
        lineno += 1
        logthis('line%s: %.3f+%.3fi,%.3f+%.3fi' % (lineno, line.start.real, line.start.imag, line.end.real, line.end.imag))
'''

logthis('no merge conflict:\n')
for k,v in no_mergex.items():
    index = distincthpaths.index(k)+1
    if len(v) != 0:
        l = len(v)
        logthis('o%s %d' %(index,l))
        for li in v:
            indexl = distincthpaths.index(li)+1
            logthis(' o%s' % (indexl))
        logthis('\n')
logthis('FIN\n')

logthis('\nno absorption conflict:\n')
for k,v in no_absorption.items():
    index = distincthpaths.index(k)+1
    x = ''
    if len(v) != 0:
        stri = []
        for l in v:
            if k.area() < l.area():
                indexl = distincthpaths.index(l)+1
                if indexl not in stri:
                    stri.append('o'+str(indexl))
    if len(stri) != 0:
        l = len(stri)
        logthis('o%s %d' % (index, l))
        for s in stri:
            logthis(' %s' % (s))
        logthis('\n')
logthis('FIN\n')


distincthpaths.append(offsetframe)
wsvg(distincthpaths, filename='output.svg', openinbrowser=True)

#todo: add condition to inter (some combine, some not)
#todo: not all combine in heater??

