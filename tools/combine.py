#!/usr/bin/python
from tools.conflict import *

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