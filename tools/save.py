from math import ceil

def output_unit(folder, filename, context, unitrect, offsetframe):
    file = open(folder + filename, 'w')
    num_x = ceil(offsetframe[0].length() / unitrect)
    num_y = ceil(offsetframe[1].length() / unitrect)
    file.write('%d %d %f\n' % (num_x, num_y, unitrect))
    for k, v in context.items():
        index = k
        if len(v) != 0:
            l = len(v)
            file.write('o%s %d' % (index, l))
            for li,per in v.items():
                file.write(' (%d,%d, %f)' % (li[0], li[1], per))
            file.write('\n')
    file.write('FIN\n')
    file.close()

def output_conflict(folder, filename, context, distincthpaths):
    conflictfile = open(folder + filename, 'w')
    conflictfile.write('no merge conflict:\n')
    for k, v in context[0].items():
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
    for k, v in context[1].items():
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
    for k, v in context[2].items():
        index = distincthpaths.index(k)
        if len(v) != 0:
            for o, d in v.items():
                indexl = distincthpaths.index(o)
                conflictfile.write('o%s o%s %f\n' % (index, indexl, d))
    conflictfile.write('FIN\n')
    conflictfile.close()