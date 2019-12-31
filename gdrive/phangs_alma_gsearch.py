#!/usr/bin/env python
# 
# Aim:
#   Search files in google team drive
# 
# Dependency:
#   phangs_alma_gdio.py
# 
# Last updates:
#   20180822 13h59m
# 

from __future__ import print_function

import os, sys, io, re, copy, json
import pkg_resources
pkg_resources.require('google-api-python-client') # pip install --user --upgrade oauth2client google-api-python-client
#pkg_resources.require('httplib2')
pkg_resources.require('oauth2client')

if not os.path.dirname(__file__) in sys.path:
    sys.path.append(os.path.dirname(__file__))

#if not os.path.isdir(os.getenv('HOME')+os.sep+'.almacosmos'):
#    print('Error! "%s" was not found! Please ask dzliu@mpia.de for that folder!' % (os.getenv('HOME')+os.sep+'.almacosmos') )
#    #scp -r ~/.almacosmos <DESTINATION>:~/

from phangs_alma_gdio import CAAP_Google_Drive_Operator





#foo = CAAP_Google_Drive_Operator()
##foo.print_files_in_drive()
##foo.print_all_team_drives()
##foo.get_folder_by_name('Samples')
##foo.search_files('Samples')
##folders = foo.search_folders('Samples', verbose=True)
#folders = foo.search_files('OptiLIB_bc03_highz.params', verbose=True)




def phangs_alma_gsearch(input_filenames, output_filename, drive = '', verbose = False):
    # 
    if drive == '':
        drive = 'PHANGS'
    # 
    if type(input_filenames) is not list:
        input_filenames = [input_filenames]
    # 
    gdo = CAAP_Google_Drive_Operator(drive)
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
            if output_filename == '':
                print('Absolute paths: ')
                for j in range(len(g_items)):
                    g_item = g_items[j]
                    g_item_abspath = g_items_abspaths[j]
                    #g_item_abspath = gdo.get_absolute_path_str(g_item)
                    print('  %s' % (g_item_abspath))
                print('')
            else:
                print('Writing to "%s"'%(output_filename))
                output_items = copy.copy(g_items)
                for j in range(len(output_items)):
                    output_items[j]['abspath'] = g_items_abspaths[j]
                if output_filename.find(os.sep) >= 0:
                    if not os.path.isdir(os.path.dirname(output_filename)):
                        os.makedirs(os.path.dirname(output_filename))
                with open(output_filename, 'w') as fp:
                    json.dump(output_items, fp, sort_keys=True, indent=4)
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
        output_filename = ''
        #input_ispath = []
        test_mode = False
        verbose = False
        i = 1
        while i < len(sys.argv):
            if sys.argv[i].lower().replace('--','-') == '-verbose':
                verbose = True
            elif sys.argv[i].lower().replace('--','-') == '-test':
                test_mode = True
            elif sys.argv[i].lower().replace('--','-') == '-drive':
                if i+1 < len(sys.argv):
                    i = i+1
                    input_drivename = sys.argv[i]
            elif sys.argv[i].lower().replace('--','-') == '-output':
                if i+1 < len(sys.argv):
                    i = i+1
                    output_filename = sys.argv[i]
            else:
                input_filenames.append(sys.argv[i])
                #if sys.argv[i].find('/') >= 0:
                #    input_ispath.append(True)
                #else:
                #    input_ispath.append(False)
            i = i + 1
        # 
        phangs_alma_gsearch(input_filenames, output_filename, drive = input_drivename, verbose = verbose)
        # 
    else:
        print('Usage: ')
        print('       ./phangs_alma_gsearch.py "/path/**/to/a/file" # absolute path')
        print('       ./phangs_alma_gsearch.py "some_file_name_*"')
        print('       ./phangs_alma_gsearch.py "some_folder_*/" # must has the trailing slash')
    





