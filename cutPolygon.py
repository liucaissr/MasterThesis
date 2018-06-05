from filecmp import dircmp
from os import getcwd, listdir, sep, remove, error, path


dir1 = {'a':[1,2],'c':[3,4], 'b':[2,1,3]}

dir2 = {'a':[2],'b':[1,3,4]}




cur = '/Users/my/Desktop/MasterThesis/source/output/'

print listdir(cur)
print max(listdir(cur))

print cur + max(listdir(cur)) +sep
'''
for f in listdir(cur):
    print f
'''