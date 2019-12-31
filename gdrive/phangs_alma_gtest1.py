#!/usr/bin/env python
# 
# Aim:
#   Test 1: print team drive info
# 
# Dependency:
#   phangs_alma_gdio.py
# 
# Last updates:
#   20191206
# 

from __future__ import print_function

import os, sys, io, re
import pkg_resources

if not os.path.dirname(__file__) in sys.path:
    sys.path.append(os.path.dirname(__file__))

from phangs_alma_gdio import CAAP_Google_Drive_Operator




# 
# Main Code
# 
if __name__ == '__main__':
    if len(sys.argv) >= 0:
        input_drivename = ''
        verbose = False
        i = 1
        while i < len(sys.argv):
            if sys.argv[i].lower().replace('--','-') == '-verbose':
                verbose = True
            i = i + 1
        # 
        gdo = CAAP_Google_Drive_Operator(input_drivename)
        print('Team Drive: %s' % (gdo.team_drive_name))
        
    else:
        print('Usage: ')
        print('    phangs_alma_gtest1.py')
    





