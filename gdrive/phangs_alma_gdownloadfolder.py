#!/usr/bin/env python
# 
# Aim:
#   Download a file from google team drive
# 
# Dependency:
#   a3cosmos_gdio.py
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

if not os.path.isdir(os.getenv('HOME')+os.sep+'.almacosmos'):
    print('Error! "%s" was not found! Please ask dzliu@mpia.de for that folder!' % (os.getenv('HOME')+os.sep+'.almacosmos') )
    #scp -r ~/.almacosmos <DESTINATION>:~/

from a3cosmos_gdio import CAAP_Google_Drive_Operator





#foo = CAAP_Google_Drive_Operator()
##foo.print_files_in_drive()
##foo.print_all_team_drives()
##foo.get_folder_by_name('Samples')
##foo.search_files('Samples')
##folders = foo.search_folders('Samples', verbose=True)
#folders = foo.search_files('OptiLIB_bc03_highz.params', verbose=True)




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
        gdo = CAAP_Google_Drive_Operator(input_drivename)
        print('Team Drive: %s' % (gdo.team_drive_name))
        for i in range(len(input_filenames)):
            g_items = gdo.search_files_or_folders_by_path(input_filenames[i], verbose = verbose)
            if len(g_items)>0:
                #print(g_items)   #
                #gdo.download_files(g_items) # the input is google drive file resource class
                if not (input_filenames[i].find('*')>=0):
                    # we only download the first match if input_filenames[i] does not contain a wildcard
                    gdo.download_folders(g_items[0], verbose = verbose) # the input is google drive file resource class
                else:
                    gdo.download_folders(g_items, verbose = verbose) # the input is google drive file resource class
            else:
                error_message = 'Warning! Nothing was found for the input name "%s"! Please remember to add a trailing slash (/) if you are searching for folders!'%(input_filenames[i])
                print('*'*len(error_message))
                print(error_message)
                print('*'*len(error_message))
                print('')
    else:
        print('Usage: ')
        print('       ./a3cosmos_gdownloadfolder.py "folder_name"')
        print('       ./a3cosmos_gdownloadfolder.py "folder_name_with_*wildcard"')
        print('       ./a3cosmos_gdownloadfolder.py "or/parent/pathes/to/a/folder"')
        print('       ./a3cosmos_gdownloadfolder.py "or/parent/pathes/to/a/folder" -drive DeepFields')
    





