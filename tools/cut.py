#!/usr/bin/python
import re
from svgpathtools import *
import math

class LineNavigation(object):
    def __init__(self, position, start, end, line):
        self.position = position
        self.start = start
        self.end = end
        self.line = line

    def __repr__(self):
        #return 'Path{} Line{} (start={}, end={}) \n' % (self.pathno, self.lineno, self.start, self.end)
        return '{} {} {}'.format(self.position, self.start, self.end)

    def __cmp__(self, other):
        if hasattr(other, 'position') and hasattr(other, 'start'):
            if(self.position > other.position):
                return 1
            elif(self.position < other.position):
                return -1
            else:
                if (self.start > other.start):
                    return 1
                elif (self.end < other.end):
                    return -1
                else:
                    return 0
# something like key define exist
class PointNavigation(object):
    def __init__(self, point, hline, vline):
        self.point = point
        self.hline = hline
        self.vline = vline

    def __repr__(self):
        #return 'Path{} Line{} (start={}, end={}) \n' % (self.pathno, self.lineno, self.start, self.end)
        return '{} {} {}'.format(self.point, self.hline, self.vline)

    def __cmp__(self, other):
        e = 0.0000001
        if hasattr(other, 'point'):
            if(self.point.imag - other.point.imag > e):
                return 1
            elif(self.point.imag - other.point.imag < -e ):
                return -1
            else:
                if (self.point.real - other.point.real > e ):
                    return 1
                elif (self.point.real  - other.point.real < -e):
                    return -1
                else:
                    return 0

class Coordinate(complex):

    def __lt__(self, other):
        e = 0.0000001
        if hasattr(other, 'imag') and hasattr(other, 'real'):
            if (self.real - other.real > e):
                return 0
            elif (self.real - other.real < -e):
                return 1
            else:
                if (self.imag - other.imag > e):
                    return 0
                elif (self.imag - other.imag < -e):
                    return 1
                else:
                    return 0
        else:
            return NotImplemented

    def __gt__(self, other):
        e = 0.0000001
        if hasattr(other, 'imag') and hasattr(other, 'real'):
            if (self.real - other.real > e):
                return 1
            elif (self.real - other.real < -e):
                return 0
            else:
                if (self.imag - other.imag > e):
                    return 1
                elif (self.imag - other.imag < -e):
                    return 0
                else:
                    return 0
        else:
            return NotImplemented

    def __le__(self, other):
        e = 0.0000001
        if hasattr(other, 'imag') and hasattr(other, 'real'):
            if (self.real - other.real > e):
                return 0
            elif (self.real - other.real < -e):
                return 1
            else:
                if (self.imag - other.imag > e):
                    return 0
                elif (self.imag - other.imag < -e):
                    return 1
                else:
                    return 1
        else:
            return NotImplemented

    def __ge__(self, other):
        e = 0.0000001
        if hasattr(other, 'imag') and hasattr(other, 'real'):
            if (self.real - other.real > e):
                return 1
            elif (self.real - other.real < -e):
                return 0
            else:
                if (self.imag - other.imag > e):
                    return 1
                elif (self.imag - other.imag < -e):
                    return 0
                else:
                    return 1
        else:
            return NotImplemented
    def __eq__(self, other):
        e = 0.0000001
        if hasattr(other, 'imag') and hasattr(other, 'real'):
            if (abs(self.real - other.real) < e) and (abs(self.imag - other.imag) < e):
                return 1
            else:
                return 0
        else:
            return NotImplemented

class MicroLine(Line):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if super(MicroLine, self).__eq__(other):
                return True
            elif self.end == other.start and self.start == other.end:
                return True
            else:
                return False
        else:
            return NotImplemented

    @property
    def direction(self):
        if self.start.imag == self.end.imag:
            return 'h'
        elif self.start.real == self.end.real:
            return 'v'
        else:
            return NotImplemented

    def __cmp__(self, other):
        if hasattr(other, 'start') and hasattr(other, 'end'):
            self = self.order()
            other = other.order()
            # assert if not parallel
            if self.direction == 'h' and other.direction == 'h':
                if (self.start.imag > other.start.imag):
                    return 1
                elif (self.start.imag < other.start.imag):
                    return -1
                else:
                    if (self.start.real > other.start.real):
                        return 1
                    elif (self.end.real < other.end.real):
                        return -1
                    else:
                        return 0
            elif self.direction == 'v' and other.direction == 'v':
                if (self.start.real > other.start.real):
                    return 1
                elif (self.start.real < other.start.real):
                    return -1
                else:
                    if (self.start.imag > other.start.imag):
                        return 1
                    elif (self.end.imag < other.end.imag):
                        return -1
                    else:
                        return 0
            else:
                return 0

    def order(self):
        orderedLine = MicroLine(min(self.start, self.end), max(self.start, self.end))
        return orderedLine

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
def svgpreprocess(paths, attributes, offsetx, offsety):
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
            if line.direction == 'h':
                hlines.append(line)
            if line.direction == 'v':
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
            newvline = MicroLine(Coordinate(vline.point(min(intersectpoints))),
                                 Coordinate(vline.point(max(intersectpoints))))
            filteredVlines.append(newvline)
    for hline in sortedhlines:
        intersectpoints = []
        for vline in sortedvlines:
            x = line1_intersect_with_line2(hline, vline)
            if len(x) != 0:
                intersectpoints.append(x[0][0])
        if len(intersectpoints) >= 2:
            newhline = MicroLine(Coordinate(hline.point(min(intersectpoints))),
                                 Coordinate(hline.point(max(intersectpoints))))
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
    x = None
    if line1 != line2:
        x = line1.intersect(line2)
    if line1.start == line2.start:
        return [(0.0, 0.0)]
    elif line1.start == line2.end:
        return [(0.0, 1.0)]
    elif line1.end == line2.start:
        return [(1.0, 0.0)]
    elif line1.end == line2.end:
        return [(1.0, 1.0)]
    elif x is not None:
        if len(x) != 0:
            a = round(x[0][0],3)
            b = round(x[0][1],3)
            return [(a,b)]
        else:
            return []
    else:
        return []


def combineLines(microlines):
    # todo: assert parallel lines
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
        newL = MicroLine(start, end)
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
            if j == length - 1:
                k = length
        newLine = MicroLine(start, end)
        if newLine not in lines:
            lines.append(newLine)
    last,p = two_lines_intersection(sortedlines[-1], lines[-1])
    if last is not None and last == sortedlines[-1]:
        pass
    elif last is not None and last != sortedlines[-1]:
        newLine = MicroLine(min(last.start, sortedlines[-1].start), max(last.end, sortedlines[-1].end))
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
    result = []
    sortedhlines = sorted(allLines)
    sortedPoints = sorted(cutPoints)
    processedLine = []
    # todo one line is missing
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


def path1_is_contained_in_path2x(path1, path2):
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


def path1_is_contained_in_path2(path1, path2):
    assert path2.isclosed()  # This question isn't well-defined otherwise
    # find a point that's definitely outside path2
    # assert path1 is line
    for line in path2:
        l, p = two_lines_intersection(path1, line)
        if l is not None and l != path1:
            return False
        elif l is not None and l == path1:
            return True
        elif l is None and p is not None:
            if p != path1.start and p != path1.end:
                return False

    xmin, xmax, ymin, ymax = path2.bbox()
    B = (xmin + 1) + 1j * (ymax + 1)
    C = (xmax + 1) + 1j * (ymax + 1)
    A = (path1.start + path1.end) / 2  # pick an arbitrary point in path1
    AB_line = Path(Line(A, B))
    AC_line = Path(Line(A, C))
    number_of_intersections1 = len(AB_line.intersect(path2))
    number_of_intersections2 = len(AC_line.intersect(path2))
    if number_of_intersections1 % 2 and number_of_intersections2 % 2:  # if number of intersections is odd
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
    # assert intersectline not one
    keepLines = []
    for line1 in path1:
        if line1_is_overlap_with_line2(line1, intersectline[0]) == False:
            keepLines.append(line1)
        else:
            newLines = cutline(line1, intersectline[0])
            for line in newLines:
                keepLines.append(line)
    for line1 in path2:
        if line1_is_overlap_with_line2(line1, intersectline[0]) == False:
            keepLines.append(line1)
        else:
            newLines = cutline(line1, intersectline[0])
            for line in newLines:
                keepLines.append(line)
    result = createPath(keepLines)
    return result


def cutline(line1, line2):
    # assert self longer than other or ...
    # assert overlapped line
    # assert line1 line2 overlapped
    result = []
    l1 = line1.order()
    l2 = line2.order()
    # start != end should inside init line
    if l1.start < l2.start:
        result.append(MicroLine(l1.start, l2.start))
    if l1.end > l2.end:
        result.append(MicroLine(l2.end, l1.end))
    return result


def createPath(lines):
    hlines = []
    vlines = []
    refinedLines = []
    roundLines = []
    for line in lines:
        start = Coordinate(round(line.start.real, 3), round(line.start.imag, 3))
        end = Coordinate(round(line.end.real, 3), round(line.end.imag, 3))
        newLine = MicroLine(start, end)
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
                    path.insert(0, newMLine)
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
    x = line1_intersect_with_line2(line1,line2)
    intersection = None
    intersectp = None
    if line1_is_overlap_with_line2(line1, line2):
        start = Coordinate(max(b1[0], b2[0]), max(b1[2], b2[2]))
        end = Coordinate(min(b1[1], b2[1]), min(b1[3], b2[3]))
        if start != end:
            intersection = MicroLine(start, end)
        else:
            intersectp = Coordinate(start)
    elif len(x) != 0:
        intersectp = line1.point(x[0][0])
    return intersection, intersectp

# for silly intersect method
# why wrong method is being called
def two_paths_intersectionx(path1, path2):
    intersect = []
    for line1 in path1:
        for line2 in path2:
            line1 = MicroLine(Coordinate(line1.start), Coordinate(line1.end))
            line2 = MicroLine(Coordinate(line2.start), Coordinate(line2.end))
            if line1 == line2:
                if line1 not in intersect:
                    intersect.append(line1)
            elif line1_is_overlap_with_line2(line1, line2):
                line,p = two_lines_intersection(line1, line2)
                if line is not None:
                    newline = MicroLine(Coordinate(line.start), Coordinate(line.end))
                    if newline not in intersect:
                        intersect.append(newline)
    return intersect, None

# intersect = intersect lines on the paths
# intersectpath = intersect path if exists
def two_paths_intersection(path1, path2):
    intersect = []
    intersectpath = Path()
    intersectpoints = []
    pathlines = []
    for line1 in path1:
        for line2 in path2:
            line1 = MicroLine(Coordinate(line1.start), Coordinate(line1.end))
            line2 = MicroLine(Coordinate(line2.start), Coordinate(line2.end))
            if line1 == line2:
                if line1 not in intersect:
                    intersect.append(line1)
                    pathlines.append(line1)
            else:
                line, interpoint = two_lines_intersection(line1, line2)
                if line is not None:
                    newline = MicroLine(Coordinate(line.start), Coordinate(line.end))
                    if newline not in intersect:
                        intersect.append(newline)
                        pathlines.append(newline)
                if interpoint is not None:
                    if interpoint not in intersectpoints:
                        intersectpoints.append(interpoint)

    for line1 in path1:
        if path1_is_contained_in_path2(line1, path2):
            if line1 not in intersect:
                pathlines.append(line1)

    for line2 in path2:
        if path1_is_contained_in_path2(line2, path1):
            if line2 not in intersect:
                pathlines.append(line2)

    for l in pathlines:
        if l.start not in intersectpoints:
            intersectpoints.append(l.start)
        if l.end not in intersectpoints:
            intersectpoints.append(l.end)
    x = []
    y = []
    for p in intersectpoints:
        if p.real not in x:
            x.append(p.real)
        if p.imag not in y:
            y.append(p.imag)
    x.sort()
    y.sort()
    if len(x) != 2 or len(y) != 2:
        return intersect, None
    l1 = MicroLine(Coordinate(x[0], y[0]), Coordinate(x[1], y[0]))
    l2 = MicroLine(Coordinate(x[1], y[0]), Coordinate(x[1], y[1]))
    l3 = MicroLine(Coordinate(x[1], y[1]), Coordinate(x[0], y[1]))
    l4 = MicroLine(Coordinate(x[0], y[1]), Coordinate(x[0], y[0]))
    intersectpath = Path(l1, l2, l3, l4)
    return intersect, intersectpath

def two_lines_distance(line1, line2):
    if line1.direction == line2.direction == 'h':
        dis = line1.start.imag - line2.start.imag
    elif line1.direction == line2.direction == 'v':
        dis = line1.start.real - line2.start.real
    else:
        return NotImplemented
    return dis


# intersectlines in lines for line
def line_intersectlines(line, lines):
    direct = line.direction
    l1 = line.order()
    intersectlines = []
    for l in lines:
        l2 = l.order()
        if l1 != l2:
            if l2.direction == direct == 'h':
                if l1.start.real <= l2.end.real and l1.end.real >= l2.start.real:
                    intersectlines.append(l2)
            if l2.direction == direct == 'v':
                if l1.start.imag <= l2.end.imag and l1.end.imag >= l2.start.imag:
                    intersectlines.append(l2)
    return intersectlines


def getDev(path, line):
    l0 = line.order()
    intersectlines = line_intersectlines(l0, path)
    dev = two_lines_distance(l0, intersectlines[0])
    for pl in intersectlines:
        if dev == 0:
            dev = two_lines_distance(l0, pl)
            continue
        dis = two_lines_distance(l0, pl)
        if abs(dis) < abs(dev) and dis != 0:
            dev = dis
    return dev


def changePath(path, index, dev, factor, large_ratio):
    newPath = Path()
    l0 = path[index]
    if abs(dev * factor) < large_ratio:
        devx = dev * 0.7
    else:
        devx = dev * factor
    if l0.direction == 'h':
        deviation = Coordinate(0, -devx)
    else:
        deviation = Coordinate(-devx, 0)
    for line in path:
        if line != l0:
            point = line1_intersect_with_line2(line, l0)
            if len(point) != 0:
                roundpoint = round(point[0][0], 3)
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

# Calculate distance when path length is larger than 4
def two_paths_distancex(path1, path2):
    dis = 0
    points1 = []
    points2 = []
    lines1 = []
    lines2 = []
    points1.append(path1.start)
    points2.append(path2.start)
    inter = path1.intersect(path2)
    if len(inter) != 0:
        return dis
    for l1 in path1:
        points1.append(l1.end)
        l = l1.order()
        lines1.append(l)
    for l2 in path2:
        points2.append(l2.end)
        l = l2.order()
        lines2.append(l)
    for p1 in points1:
        for l2 in lines2:
            if l2.direction == 'h' and l2.start.real < p1.real < l2.end.real:
                tmpdis = abs(l2.start.imag - p1.imag)
            elif l2.direction == 'v' and l2.start.imag < p1.imag < l2.end.imag:
                tmpdis = abs(l2.start.real - p1.real)
            else:
                tmpdis = min(math.sqrt((l2.start.real-p1.real) ** 2 + (l2.start.imag-p1.imag) ** 2), math.sqrt((l2.end.real-p1.real) ** 2 + (l2.end.imag-p1.imag) ** 2))
            if tmpdis < dis or dis == 0:
                dis = tmpdis
    for p2 in points2:
        for l1 in lines1:
            if l1.direction == 'h' and l1.start.real < p2.real < l1.end.real:
                tmpdis = abs(l1.start.imag - p2.imag)
            elif l1.direction == 'v' and l1.start.imag < p2.imag < l1.end.imag:
                tmpdis = abs(l1.start.real - p2.real)
            else:
                tmpdis = min(math.sqrt((l1.start.real-p2.real) ** 2 + (l1.start.imag-p2.imag) ** 2), math.sqrt((l1.end.real-p2.real) ** 2 + (l1.end.imag-p2.imag) ** 2))
            if tmpdis < dis or dis == 0:
                dis = tmpdis
    return dis

def two_paths_distance(path1, path2):
    dev = 0
    if len(path1) > 4 or len(path2) > 4:
        return two_paths_distancex(path1, path2)
    b1 = path1.bbox()
    b2 = path2.bbox()
    ls,path = two_paths_intersection(path1, path2)
    if len(ls) != 0 or path is not None:
        return 0
    if b1[1] < b2[0] and b1[2] > b2[2]:
        dev = math.sqrt((b2[0] - b1[1]) ** 2 + (b2[2] - b1[3]) ** 2)
    elif b2[1] < b1[0] and b2[3] < b1[2]:
        dev = math.sqrt((b2[1] - b1[0]) ** 2 + (b2[3] - b1[2]) ** 2)
    if b1[1]<b2[0] and b1[3]<b2[2]:
        dev = math.sqrt((b2[0]-b1[1])**2+(b2[2]-b1[3])**2)
    elif b1[1]<b2[0] and b1[2]>b2[3]:
        dev = math.sqrt((b2[0]-b1[1])**2+(b1[2]-b2[3])**2)
    elif b1[0]>b2[1] and b1[3]<b2[2]:
        dev = math.sqrt((b1[0]-b2[1])**2+(b2[2]-b1[3])**2)
    elif b1[0]>b2[1] and b1[2]>b2[3]:
        dev = math.sqrt((b1[0]-b2[1])**2+(b1[2]-b2[3])**2)
    elif b1[1] < b2[0]:
        dev = b2[0] - b1[1]
    elif b1[3] < b2[2]:
        dev = b2[2] - b1[3]
    elif b2[1] < b1[0]:
        dev = b1[0] - b2[1]
    elif b2[3] < b1[2]:
        dev = b1[2] - b2[3]
    return dev

def no_merge_conflict(path1, path2, factor, user_factor = 0, dis = None):
    if user_factor != 0:
        factor = user_factor
    if dis is None:
        dis = two_paths_distance(path1, path2)
    if 0 < dis < factor:
        return True,dis
    else:
        return False,dis



def no_absorption_conflict(path1, path2, factor):
    assert path1.isclosed() and path2.isclosed(), '%s is not closed' % (path1 if path1.isclosed() is False else path2)
    x, p = two_paths_intersection(path1, path2)
    factor_sqrt = math.sqrt(factor)
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
            if ((ratio1 < factor and lengthratio1 < factor_sqrt) and lengthratio2 > selflengthfactor) or (
                    (ratio2 < factor and lengthratio2 < factor_sqrt) and lengthratio1 > selflengthfactor):
                return True, None
    return False, interl

#test git ssh
