#!/usr/bin/python
import re
from svgpathtools import *
from math import *
from bisect import *
from operator import attrgetter
from tools.cut import Pattern, MicroLine, Coordinate, Vertex
import numpy as np
from tools.mt import *

# overlap of two parallel lines
def line1_is_overlap_with_line2(line1, line2):
    b1 = line1.bbox()
    b2 = line2.bbox()
    if max(b1[0], b2[0]) <= min(b1[1], b2[1]) and b1[2] == b2[2] == b1[3] == b2[3]:
        return True
    elif max(b1[2], b2[2]) <= min(b1[3], b2[3]) and b1[0] == b2[0] == b1[1] == b2[1]:
        return True
    else:
        return False

def two_paths_intersection(path1, path2):
    intersect = []
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
        if line_is_contained_in_path(line1, path2):
            if line1 not in intersect:
                pathlines.append(line1)

    for line2 in path2:
        if line_is_contained_in_path(line2, path1):
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
    intersectpath = Pattern(l1, l2, l3, l4)
    return intersect, intersectpath

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
    path = Pattern()
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



def point_is_contained_in_path(point, path):
    xmin, xmax, ymin, ymax = path.bbox()
    B = (xmin + 1) + 1j * (ymax + 1)
    AB_line = Path(Line(point, B))
    number_of_intersections1 = len(AB_line.intersect(path))
    if number_of_intersections1 % 2:
        return True
    else:
        return False

#todo: change name into line in path
def line_is_contained_in_path(line, path):
    assert path.isclosed()  # This question isn't well-defined otherwise
    # find a point that's definitely outside path2
    # assert path1 is line
    #todo add logic for point on line to true
    mid = Coordinate((line.start.real+line.end.real)/2.0,(line.start.imag+line.end.imag)/2.0)
    if (point_is_contained_in_path(line.start, path) or point_on_path(line.start, path)) and (point_is_contained_in_path(line.end, path) or point_on_path(line.end, path)) and (point_is_contained_in_path(mid, path) or point_on_path(mid, path)):
        return True
    else:
        return False

# intersect point
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

def point_on_path(point, path):
    for line in path:
        if point_on_line(point, line):
            return True
    return False

def line_on_path(line, path):
    for pathline in path:
        if line == pathline:
            return path.index(pathline)
        elif line1_is_overlap_with_line2(line, pathline):
            return path.index(pathline)
    return None

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