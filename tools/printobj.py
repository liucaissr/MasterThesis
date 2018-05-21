from os import system, listdir, sep
from svgpathtools import svg2paths, wsvg

class PrintObj:
    #def divideObjects(self, svgdir):

    def orderObjects(self, svgdir, printdir):
        #todo: assert all path should be rectangle
        svgpath = svgdir + sep
        printdir = printdir + sep
        svgs = listdir(svgpath)
        if len(listdir(printdir)) == 0:
            for svg in svgs:
                if '.svg' in svg:
                    printfile = svg.replace('.svg', '.txt')
                    thefile = open(printdir + printfile, 'w')
                    paths, attributes = svg2paths(svgpath + svg)
                    size = [0] * len(paths)
                    for currentPath in paths:
                        pathno = paths.index(currentPath) + 1
                        thefile.write("o%s (%s):" % (pathno, abs(currentPath.area())))
                        for path in (paths[:pathno - 1] + paths[pathno:]):
                            objno = paths.index(path) + 1
                            if len(currentPath.intersect(path)) != 0:
                                thefile.write(" o%s" % objno)
                                if pathno < objno:
                                    if abs(currentPath.area()) > abs(path.area()):
                                        size[pathno - 1] = size[objno - 1] + 1
                                    elif abs(currentPath.area()) < abs(path.area()):
                                        size[objno - 1] = size[pathno - 1] + 1
                        thefile.write("\n")
                    minsize = min(size)
                    thefile.write("\n")
                    for i in range(0, len(size)):
                        size[i] = size[i] - minsize
                    for i in range(0, len(size)):
                        thefile.write("%d: %d\n" % (i+1, size[i]))
                    thefile.close()

