#!/usr/bin/env python
# 
# Aim:
#   Download a file from google team drive
# 
# Dependency:
#   phangs_alma_gdio.py
# 
# Last updates:
#   20180822 13h59m
# 

from __future__ import print_function

import os, sys, io, re
import pkg_resources
pkg_resources.require('google-api-python-client') # pip install --user --upgrade oauth2client google-api-python-client
pkg_resources.require('httplib2')
pkg_resources.require('oauth2client')

if not os.path.dirname(__file__) in sys.path:
    sys.path.append(os.path.dirname(__file__))

from phangs_alma_gdio import CAAP_Google_Drive_Operator





#foo = CAAP_Google_Drive_Operator()
##foo.print_files_in_drive()
##foo.print_all_team_drives()
##foo.get_folder_by_name('Samples')
##foo.search_files('Samples')
##folders = foo.search_folders('Samples', verbose=True)
#folders = foo.search_files('OptiLIB_bc03_highz.params', verbose=True)



# 
# phangs_alma_gdownload
# 
def phangs_alma_gdownload(input_filenames, input_drivename, verbose = False):
    # 
    gdo = CAAP_Google_Drive_Operator(input_drivename)
    print('Team Drive: %s' % (gdo.team_drive_name))
    # 
    for i in range(len(input_filenames)):
        #
        # If the input path is an absolute path, which startswith '/' and does not include wildcard '*' in its dir path, 
        # then we can use the more efficient search function 'search_files_or_folders_by_absolute_path()'. 
        # This will save some query quota. 
        if input_filenames[i].startswith('/') and (os.path.dirname(input_filenames[i]).find('*') < 0):
            g_items, g_items_abspaths = gdo.search_files_or_folders_by_absolute_path(input_filenames[i], verbose = verbose, return_abspath = True)
        else:
            g_items, g_items_abspaths = gdo.search_files_or_folders_by_path(input_filenames[i], verbose = verbose, return_abspath = True)
        # 
        if len(g_items)>0:
            #print(g_items)   #
            #gdo.download_files(g_items) # the input is google drive file resource class
            if not (input_filenames[i].find('*')>=0):
                # we only download the first match if input_filenames[i] does not contain a wildcard
                output_directory = '.'+os.path.dirname(g_items_abspaths[i])
                if gdo.is_folder_resource(g_items[0]):
                    gdo.download_folders(g_items[0], output_directory = output_directory, verbose = verbose) # the input is google drive file resource class
                else:
                    gdo.download_files(g_items[0], output_directory = output_directory, verbose = verbose) # the input is google drive file resource class
            else:
                #for j in range(len(g_items)):
                #    output_directories = g_items_abspaths[i]
                output_directory = '.'+os.path.dirname(g_items_abspaths[i])
                gdo.download_files(g_items, output_directory = output_directory, verbose = verbose) # the input is google drive file resource class
        else:
            error_message = 'Warning! Nothing was found for the input name "%s"! Please remember to add a trailing slash (/) if you are searching for folders!'%(input_filenames[i])
            print('*'*len(error_message))
            print(error_message)
            print('*'*len(error_message))
            print('')



# 
# Main Code
# 
if __name__ == '__main__':
    if len(sys.argv)>1:
        input_filenames = []
        input_drivename = ''
        #input_ispath = []
        verbose = False
        i = 1
        while i < len(sys.argv):
            if sys.argv[i].lower().replace('--','-') == '-verbose':
                verbose = True
            elif sys.argv[i].lower().replace('--','-') == '-drive':
                if i+1 < len(sys.argv):
                    i = i+1
                    input_drivename = sys.argv[i]
            else:
                input_filenames.append(sys.argv[i])
                #if sys.argv[i].find('/') >= 0:
                #    input_ispath.append(True)
                #else:
                #    input_ispath.append(False)
            i = i + 1
        # 
        # 
        phangs_alma_gdownload(input_filenames, input_drivename, verbose = verbose)
    else:
        print('Usage: ')
        print('       ./phangs_alma_gdownload.py "/path/to/a/file"')
    





