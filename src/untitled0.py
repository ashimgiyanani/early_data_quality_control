# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 10:55:15 2022

@author: giyash
"""

from filecmp import dircmp
def print_diff_files(dcmp):
    for name in dcmp.diff_files:
        print("diff_file %s found in %s and %s" % (name, dcmp.left,
              dcmp.right))
    for sub_dcmp in dcmp.subdirs.values():
        print_diff_files(sub_dcmp)

dir1 = 
dir2 = 
dcmp = dircmp('dir1', 'dir2') 
print_diff_files(dcmp)