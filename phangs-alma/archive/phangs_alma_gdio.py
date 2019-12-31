#!/usr/bin/env python
# 
# 
# code are mainly from 
# -- https://developers.google.com/drive/v3/web/quickstart/python
# 
# before runing this code, make sure you have created credential via the following link: 
# https://console.developers.google.com/start/api?id=drive
# 
# Last updates:
#   20180822 13h59m copied from "Github/AlmaCosmos/Softwares/almacosmos_gdio_py3.py", updated
# 

from __future__ import print_function

import os, sys, io, re
import pkg_resources
pkg_resources.require('google-api-python-client') # pip install --user --upgrade oauth2client google-api-python-client
pkg_resources.require('httplib2')
pkg_resources.require('oauth2client')
#pkg_resources.require('hashlib')

import httplib2

import hashlib

from apiclient import discovery
from apiclient import errors
from apiclient.http import MediaIoBaseDownload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import time

#try:
#    import argparse
#    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
#except ImportError:
#    flags = None

if sys.version_info.major >= 3:
    long = int




class CAAP_Google_Drive_Operator(object):
    # 
    def __init__(self, team_drive_name = ''):
        self.scopes = 'https://www.googleapis.com/auth/drive.readonly'
        #self.credential_dir = '.' # os.path.join(os.path.expanduser('~'), '.caap')
        self.credential_dir = os.path.dirname(os.path.abspath(__file__))
        # -- visit -- https://console.developers.google.com/iam-admin/serviceaccounts?pli=1 -- to set up serviceaccounts
        self.credential_file = os.path.join(self.credential_dir, 'PHANGS-04b53ef53996.json') # r
        self.client_email = 'phangs@phangs.iam.gserviceaccount.com'
        self.quota_user = '04b53ef5399645e3048c0e1ad167dbe1ff3d1209' # 'a3cosmos-readonly'+'-'+datetime.today().strftime('%Y%m%d-%H%M%S.%f')
        self.credential_store = None
        #self.application_name = 'CAAP Google Drive Operator'
        self.credential = None
        self.http = None
        self.service = None
        self.team_drive = None
        self.team_drive_name = team_drive_name
        if self.team_drive_name == '':
            self.team_drive_name = 'PHANGS' # default drive
        self.get_credential()
        self.get_team_drive()
    # 
    def get_credential(self):
        if not os.path.exists(self.credential_dir):
            print('Warning! "%s" does not exist! Creating it!'%(self.credential_dir))
            os.makedirs(self.credential_dir)
        if not os.path.exists(self.credential_file):
            print('Error! Key "%s" was not found! Please ask A3COSMOS for the "CAAP Google Drive Operator-93fcdd7331f1.json" then put it there!'%(self.credential_file))
            sys.exit()
        #if not os.path.exists(self.credential_file+'.ok'):
            #self.credential_store = Storage(self.credential_file)
            #self.credential = []
            #flow = client.flow_from_clientsecrets(self.credential_file, self.scopes)
            #flow.user_agent = self.application_name
            #if flags:
            #    credential = tools.run_flow(flow, self.credential_store, flags)
            #else: # Needed only for compatibility with Python 2.6
            #    credential = tools.run(flow, self.credential_store)
            #print('Storing credential to ' + self.credential_file)
            #os.system('touch "%s"'%(self.credential_file+'.ok'))
            # 
        #self.credential_store = Storage(self.credential_file)
        #self.credential = self.credential_store.get()
        # --
        # -- 20171023
        # -- use serveraccount
        # -- https://developers.google.com/drive/v3/web/handle-errors (403: Rate Limit Exceeded)
        # -- https://developers.google.com/identity/protocols/OAuth2ServiceAccount (Preparing to make an authorized API call)
        self.credential = ServiceAccountCredentials.from_json_keyfile_name(self.credential_file, scopes=self.scopes)
        # 
        self.http = self.credential.authorize(httplib2.Http())
        self.service = discovery.build('drive', 'v3', http=self.http)
        #print(self.service)
        #self.print_files_in_drive()
    # 
    def print_files_in_drive(self):
        if self.service:
            time.sleep(0.25) # Google Drive has a limit of 10 query per second per user
            results = self.service.files().list(pageSize=30, 
                                                fields="nextPageToken, files(id, name, size, mimeType, parents, md5Checksum)", 
                                                quotaUser=self.quota_user
                                                ).execute()
            items = results.get('files', [])
            if not items:
                print('No file found.')
            else:
                print('Files:')
                for item in items:
                    print('{0} ({1})'.format(item['name'], item['id']))
        else:
            print('Error! Not initialized!')
    # 
    def get_team_drive(self, name = ''):
        # Teamdrives
        # -- https://developers.google.com/drive/v3/reference/teamdrives
        # -- https://developers.google.com/drive/v3/reference/teamdrives/list
        if self.service:
            self.team_drive = None
            #if name != '':
            #    self.team_drive_name = name
            token = None
            while True:
                try:
                    time.sleep(0.25) # Google Drive has a limit of 10 query per second per user
                    query = self.service.teamdrives().list(
                                                            pageSize=1, 
                                                            pageToken=token, 
                                                            quotaUser=self.quota_user
                                                          ).execute()
                    #print(query)
                    for item in query.get('teamDrives'):
                        #print('Team Drive Id: %s; Name: %s;'%(item['id'], item['name']))
                        #print(self.team_drive_name)
                        if item['name'] == self.team_drive_name:
                            self.team_drive = item
                            break
                    token = query.get('nextPageToken')
                    if not token:
                        break
                except errors.HttpError as error:
                    print('An error occurred: %s'%(error))
                    break
                token = query.get('nextPageToken', None)
            if not self.team_drive:
                print('Error! Failed to find the Team Drive "%s"!'%(self.team_drive_name))
                sys.exit()
                return
            # 
            #print('Team Drive: "%s" (Id: %s)'%(self.team_drive['name'], self.team_drive['id']))
        else:
            print('Error! Not initialized!')
    # 
    def print_all_team_drives(self):
        # TODO: not printing all team drives, but fine for now
        # REF: https://developers.google.com/drive/api/v3/manage-teamdrives
        if self.service:
            time.sleep(0.25) # Google Drive has a limit of 10 query per second per user
            token = None
            while True:
                query = self.service.teamdrives().list(
                                fields='nextPageToken, teamDrives(id, name)', 
                                quotaUser=self.quota_user, 
                                pageToken=token
                            ).execute()
                            # q='organizerCount = 0' -- find team drives without organizer
                            # fields='nextPageToken, teamDrives(id, name)', 
                            # useDomainAdminAccess = True, 
                for item_team_drive in query.get('teamDrives', []):
                    print('Found Team Drive: %s (%s)' % (
                            item_team_drive.get('name'), 
                            item_team_drive.get('id')
                            # REF is wrong: item_team_drive.get('title') is not working
                        )
                    )
                token = query.get('nextPageToken', None)
                if token is None:
                    break
        else:
            print('Error! Not initialized!')
    # 
    def print_files_in_team_drive(self, pageSize=30):
        # TODO: untested
        if self.service:
            time.sleep(0.25) # Google Drive has a limit of 10 query per second per user
            results = self.service.teamdrives().list(
                                                      pageSize=pageSize, 
                                                      fields="nextPageToken, files(id, name, size, mimeType, parents, md5Checksum)", 
                                                      quotaUser=self.quota_user
                                                    ).execute()
            items = results.get('files', [])
            if not items:
                print('No file found.')
            else:
                print('Files:')
                for item in items:
                    print('{0} ({1})'.format(item['name'], item['id']))
        else:
            print('Error! Not initialized!')
    # 
    def search_folders(self, names, verbose=False):
        return self.search_files_or_folders_by_names(names=names, folderOnly=True, verbose=verbose)
    # 
    def search_files(self, names, verbose=False):
        return self.search_files_or_folders_by_names(names=names, fileOnly=True, verbose=verbose)
    # 
    def search_files_or_folders_by_names(self, names, parents=None, fileOnly=False, folderOnly=False, trash=False, pageSize=30, verbose=False):
        # REF: https://developers.google.com/drive/api/v3/search-parameters#team_drive_fields
        found_items = []
        if self.service:
            time.sleep(0.25) # Google Drive has a limit of 10 query per second per user
            # check input
            if (type(names) is not list) and (type(names) is not tuple):
                names = [names]
            # search option
            if fileOnly and folderOnly:
                folderOnly = False
                fileOnly = False # if both False or both True, we do the search for both files and folders
            # mimeType
            item_mime_type = '' # if both False or both True, we do the search for both files and folders
            if folderOnly:
                item_mime_type = 'mimeType = \'application/vnd.google-apps.folder\''
            if fileOnly:
                item_mime_type = 'mimeType != \'application/vnd.google-apps.folder\''
            # prepare looping all inputs to setup the query string
            if trash:
                query_str = '(trashed = true)'
            else:
                query_str = '(trashed = false)'
            # 
            item_count = 0
            item_name_query_str = ''
            for item_name in names:
                if item_count > 0:
                    item_name_query_str = item_name_query_str + ' or ' # Note that names are combined with OR operation!
                # 
                if item_name.find('*') == 0:
                    if parents is not None:
                        pass
                    else:
                        raise Exception('Error! The file name can not start with a wildcard!') # no name constrain <TODO> this is dangerous
                elif item_name.find('*') > 0:
                    #item_name_split = item_name.split('*')
                    #for item_name_piece in item_name_split:
                    #    if item_name_piece != '':
                    #        item_name_query_str = item_name_query_str + ' and name contains \'%s\'' % (item_name_piece)
                    item_name_query_str = item_name_query_str + 'name contains \'%s\'' % (item_name[0:item_name.find('*')])
                else:
                    item_name_query_str = 'name = \'%s\'' % (item_name)
                # 
                item_count = item_count + 1
            # 
            if item_mime_type != '':
                if item_name_query_str != '':
                    item_name_query_str = item_name_query_str + ' and ' + item_mime_type
                else:
                    item_name_query_str = item_mime_type
            # 
            query_str = query_str + ' and (%s)'%(item_name_query_str)
            # 
            if parents is not None:
                parent_id_count = 0
                parent_id_query_str = ''
                if type(parents) is list:
                    for parent_obj in parents:
                        if parent_id_count > 0:
                            parent_id_query_str = parent_id_query_str + ' or ' # Note that parents are combined with OR operation!
                        parent_id_query_str = parent_id_query_str + '\'%s\' in parents'%(parent_obj['id'])
                        parent_id_count = parent_id_count + 1
                else:
                    parent_obj = parents
                    parent_id_query_str = '\'%s\' in parents'%(parent_obj['id'])
                # 
                query_str = query_str + ' and (%s)'%(parent_id_query_str)
            # 
            # print query string if verbose
            if verbose:
                print('Query string: %s'%(query_str))
                print('Team drive id: %s (name: %s)'%(self.team_drive['id'], self.team_drive_name))
            # 
            # prepare to do the query
            token = 'INIT'
            while token is not None:
                if token == 'INIT':
                    token = None
                results = self.service.files().list(
                                                      q=query_str, 
                                                      supportsTeamDrives=True, 
                                                      includeTeamDriveItems=True, 
                                                      teamDriveId=self.team_drive['id'], 
                                                      corpora='teamDrive', 
                                                      fields="nextPageToken, files(id, name, size, mimeType, parents, md5Checksum)", 
                                                      pageToken=token, 
                                                      pageSize=pageSize, 
                                                      quotaUser=self.quota_user
                                                    ).execute()
                items = results.get('files', [])
                token = results.get('nextPageToken', None)
                if not items:
                    if folderOnly:
                        print('No folder found!')
                    else:
                        print('No file found!')
                else:
                    if len(found_items) == 0:
                        if verbose:
                            if folderOnly:
                                print('')
                                print('Found folders:')
                            else:
                                print('')
                                print('Found files:')
                    for item in items:
                        if item['mimeType'].find('folder') >= 0:
                            item['url'] = 'http://drive.google.com/open?id=%s' % (item['id'])
                            item['download_url'] = ''
                        else:
                            item['url'] = 'http://drive.google.com/uc?export=view&id=%s' % (item['id'])
                            item['download_url'] = 'http://drive.google.com/uc?export=download&id=%s' % (item['id'])
                        if verbose:
                            print('  {0} ({1})'.format(item['name'], item['url']))
                        found_items.append(item)
                    if verbose:
                        print('')
        else:
            print('Error! Not initialized!')
        return found_items
    # 
    def search_files_or_folders_by_path(self, path, verbose = False, return_abspath = False):
        # We will search by the last name of the input path, 
        # then get absolute path for each found file 
        # and match to the input path to find the right ones. 
        # 
        # Note that limited by the Google Drive API, file name search can only use prefix matching. 
        # 
        # for example, if the input is "PathA/PathB/File*Name"
        # then we will first search "File*" first, 
        # then loop each found files to match the input pattern,
        # and keep the matched ones. 
        # 
        found_items = []
        found_items_abspaths = []
        paths = [t for t in path.split(os.sep) if t]
        current_name = ''
        parent_path = ''
        is_folder = False
        has_wildcard = False
        if len(paths) > 0:
            if path.endswith(os.sep):
                path = path[:-1]
                is_folder = True # is_folder if there has a trailing slash
            # 
            if len(paths) > 1:
                parent_path = os.sep.join(paths[0:-1]) + os.sep
            # 
            current_name = paths[-1]
            # 
            if current_name.find('*') >= 0:
                has_wildcard = True
        else:
            return None
        # 
        if verbose:
            print('Input of search_files_or_folders_by_path(): %s' % (paths))
        # 
        # We will search by the last item of input path after splitting by os.sep, 
        # then check the parent paths to make sure they are consistent with what user has input
        # 
        # We first check the parent_path, if it does not contain wildcard, we can search 
        if parent_path.find('*') >= 0:
            if current_name.find('*') >= 0:
                print('Warning! The input file path contains multiple wildcard asterisk! The search might not be so accurate due to google API!')
        # 
        # search for all items
        if verbose:
            print('Running search_files_or_folders_by_names(\"%s\")'%(current_name))
        if is_folder:
            items = self.search_files_or_folders_by_names(current_name, folderOnly=True, verbose=verbose) # search folder
        else:
            items = self.search_files_or_folders_by_names(current_name, fileOnly=True, verbose=verbose) # search file
        # 
        # Here we prepare regex pattern for the sanity check. We allow user to input a path like:
        # -- 'magphys_highz/OptiLIB_bc03_highz.params'
        # -- 'magphys/*/OptiLIB_bc03_highz.params'
        # -- 'magphys/**/OptiLIB_bc03_highz.params'
        # -- '/SED_Fitting/Softwares/**/OptiLIB_bc03_highz.params'
        if path.startswith(os.sep):
            check_abspath_regex = re.compile(r'%s$' % (path.replace('+',r'\+').replace('-',r'\-').replace('.',r'\.').replace('*','[^/]+').replace('[^/]+[^/]+','.*')) )
        else:
            check_abspath_regex = re.compile(r'.*/%s$' % (path.replace('+',r'\+').replace('-',r'\-').replace('.',r'\.').replace('*','[^/]+').replace('[^/]+[^/]+','.*')) )
        # 
        # do sanity check
        for item in items:
            if verbose:
                print('Running get_absolute_paths(\"%s\")'%(item))
            check_abspath_items = self.get_absolute_paths(item) # this returns a list of google drive folder resource items
            abspath = os.sep + os.sep.join([t.get('name') for t in check_abspath_items]) # abspath like /aaa/bbb/ccc
            check_abspath_regex_is_matched = False
            if check_abspath_regex.match(abspath):
                found_items.append(item)
                found_items_abspaths.append(abspath)
                check_abspath_regex_is_matched = True
            if verbose:
                print('Comparing abspath: %s vs %s (regex: %s) (matched? %s)' % (path, abspath, check_abspath_regex.pattern, check_abspath_regex_is_matched ) )
        if verbose:
            print('')
        if return_abspath:
            return found_items, found_items_abspaths
        else:
            return found_items
    # 
    def search_files_or_folders_by_absolute_path(self, path, verbose = False, return_abspath = False):
        # (New 20191127)
        # Search items according to the input absolute path
        # We will search for each parent folder ID, then search last filename. 
        # 
        # check path
        if path.find('*') == 0:
            raise Exception('Error! The input file path starts with a wildcard! This is not allowed!')
        if path.find('**') >= 0:
            raise Exception('Error! The input file path contains "**"! This is not allowed! <TODO>') #<TODO># what if providing ** for unknown level of parent folders?
        if path.find('/') != 0:
            raise Exception('Error! The input file path should start with "/"!')
        # prepare output
        found_items = []
        found_items_abspaths = []
        # split path
        paths = [t for t in path.split(os.sep) if t]
        # check validity
        if len(paths) == 1:
            if paths[0] == '':
                return None
        # print message
        if verbose:
            print('Input of search_files_or_folders_by_absolute_path(): %s' % (paths))
        # loop paths and find parents
        parent_path = '/'
        found_parents = [self.team_drive]
        for i in range(len(paths)-1):
            if verbose:
                print('Running search_files_or_folders_by_names(\"%s\")'%(paths[i]))
            temp_items = self.search_files_or_folders_by_names(paths[i], parents=found_parents[-1], folderOnly=True, verbose=False) # search folder
            if temp_items is not None:
                #if len(temp_items) > 0:
                #    for temp_item in temp_items:
                #        print(temp_item)
                if len(temp_items) > 0:
                    found_parents.append(temp_items[0])
                    parent_path = parent_path + paths[i] + '/'
                else:
                    raise Exception('Error! Folder "%s" could not be found!'%(parent_path + paths[i]))
            else:
                raise Exception('Error! Folder "%s" could not be found!'%(parent_path + paths[i]))
        # 
        #print('parent_path', parent_path)
        #print('found_parents', found_parents)
        #for i,found_parent in enumerate(found_parents):
        #    print('found_parent at %d level: %s'%(i, str(found_parent)))
        # 
        #print('found_parents', found_parents)
        #print('found_parents[2]', found_parents[2])
        parent_abspath = os.sep + os.sep.join([t['name'] for t in found_parents[1:]]) # excluding the first parent
        # 
        # search for all items
        print('Searching files under "%s"'%(parent_abspath))
        if paths[-1].startswith('*'):
            print('Note that limited by the Google Drive API, searching files with name starting with "*" is very time consuming...') # see -- https://developers.google.com/drive/api/v3/ref-search-terms#fn1
        if verbose:
            print('Running search_files_or_folders_by_names(\"%s\")'%(paths[-1]))
        if path.endswith('/'):
            items = self.search_files_or_folders_by_names(paths[-1], parents=found_parents[-1], folderOnly=True, verbose=verbose) # search folder
        else:
            items = self.search_files_or_folders_by_names(paths[-1], parents=found_parents[-1], fileOnly=True, verbose=verbose) # search file
        # 
        #if len(items) > 0:
        #    for item in items:
        #        print(item)
        # 
        #raise NotImplementedError()
        # 
        # 
        # Here we prepare regex pattern for the sanity check. 
        check_abspath_regex = re.compile(r'%s$'%(paths[-1].replace('+',r'\+').replace('-',r'\-').replace('.',r'\.').replace('*',r'.*')))
        # 
        # do sanity check
        for item in items:
            check_abspath_regex_is_matched = False
            if check_abspath_regex.match(item['name']):
                found_items.append(item)
                found_items_abspaths.append(os.path.join(parent_abspath, item['name']))
                check_abspath_regex_is_matched = True
            if verbose:
                print('Sanity check for file name: %s vs %s (regex: %s) (matched? %s)' % (paths[-1], item['name'], check_abspath_regex.pattern, str(check_abspath_regex_is_matched) ) )
        # 
        print('Found %d files'%(len(found_items)))
        # 
        if verbose:
            print('')
        # 
        # return
        if return_abspath:
            return found_items, found_items_abspaths
        else:
            return found_items
    # 
    def get_parents(self, input_resource):
        return self.get_absolute_paths(input_resource)
    # 
    def get_absolute_path_str(self, input_resource):
        abs_path_items = self.get_absolute_path(input_resource)
        abs_path_list = [t.get('name') for t in abs_path_items]
        abs_path_str = os.sep+os.sep.join(abs_path_list)
        return abs_path_str
    # 
    def get_absolute_path(self, input_resource):
        return self.get_absolute_paths(input_resource)
    # 
    def get_absolute_paths(self, input_resource):
        # Get absolute paths and return a list which includes all parent folders and the input_resource itself at the last.
        # Search for Files
        # -- https://developers.google.com/drive/v3/reference/files/list
        # -- https://developers.google.com/drive/v3/web/search-parameters
        output_parents = []
        if self.service and self.team_drive and len(input_resource)>0:
            # 
            item_id = input_resource.get('id')
            while item_id is not None:
                # 
                try:
                    time.sleep(0.25) # Google Drive has a limit of 10 query per second per user
                    query = self.service.files().get(
                                                      fileId=item_id, 
                                                      supportsTeamDrives=True, 
                                                      fields="id, name, size, mimeType, parents, md5Checksum", 
                                                      quotaUser=self.quota_user
                                                    ).execute()
                    #print(query)
                    if query is not None:
                        item = query
                        item_parents = item.get('parents')
                        if item_parents is not None:
                            item_id = item_parents[0]
                            if item_id != input_resource.get('id'):
                                output_parents.insert(0,item)
                        else:
                            item_id = None
                            break
                except errors.HttpError as error:
                    print('An error occurred: %s'%(error))
                    break
        # 
        return output_parents
    # 
    def get_folder_by_path(self, folder_path, verbose = True):
        return self.get_folder_by_name(folder_name=folder_path, verbose=verbose)
    # 
    def get_folder_by_name(self, folder_name, verbose = True):
        # File List Search
        # -- https://developers.google.com/drive/v3/reference/files/list
        # -- https://developers.google.com/drive/v3/web/search-parameters
        folder_resources = []
        if self.service and self.team_drive and len(folder_name)>0:
            # 
            if folder_name == '*':
                return folder_resources
            # 
            if folder_name.find('/')>=0:
                folder_paths = folder_name.split('/')
                for folder_pathi in range(len(folder_paths)):
                    folder_name = folder_paths[folder_pathi]
            else:
                folder_paths = []
            # 
            query_str = "trashed = false and mimeType='application/vnd.google-apps.folder'"
            # 
            #if folder_name.find('*')>=0:
            #    folder_names = folder_name.split('*')
            #    query_str = "trashed = false and mimeType='application/vnd.google-apps.folder'"
            #    for folder_namei in range(len(folder_names)):
            #        if folder_names[folder_namei] != '':
            #            query_str = query_str + " and name contains '"+folder_names[folder_namei]+"'"
            #else:
            #    query_str = " and name = '"+folder_name+"'"
            # 
            if len(folder_paths)>=2:
                # if the input folder name is an absolute or relative path, we make sure the parent folders are correct
                folder_pathi = len(folder_paths)-2
                # len(folder_paths)-2 is the parent directory of the last element [len(folder_paths)-1]
                if folder_paths[folder_pathi] != '*' and folder_paths[folder_pathi] != '':
                    folder_parents = self.get_folder_by_name(folder_paths[folder_pathi], verbose = verbose)
                    if len(folder_parents)>0:
                        query_str = query_str + str(' and ('%(folder_parent.get('id')))
                        for folder_parenti in range(len(folder_parents)):
                            folder_parent = folder_parents[folder_parenti]
                            if folder_parenti != len(folder_parents)-1:
                                query_str = query_str + str('\'%s\' in parents or '%(folder_parent.get('id')))
                            else:
                                query_str = query_str + str('\'%s\' in parents)'%(folder_parent.get('id')))
                        else:
                            print('Error! "%s" could not be found! Because its parent directory could not be found!'%('/'.join(folder_paths)))
                            sys.exit()
            # 
            if verbose:
                print('Query with: "%s"'%(query_str))
            # 
            token = None
            while True:
                try:
                    time.sleep(0.25) # Google Drive has a limit of 10 query per second per user
                    query = self.service.files().list(
                                                        q=query_str, 
                                                        supportsTeamDrives=True, 
                                                        includeTeamDriveItems=True, 
                                                        teamDriveId=self.team_drive['id'], 
                                                        corpora='teamDrive', 
                                                        fields='nextPageToken, files(id, name, size, mimeType, parents, md5Checksum)', 
                                                        pageSize=10, 
                                                        pageToken=token, 
                                                        quotaUser=self.quota_user
                                                    ).execute()
                    #print(query)
                    for item in query.get('files'):
                        if verbose:
                            print('Found folder: "%s" (Id: %s)' % (item.get('name'), item.get('id')))
                        folder_resources.append(item)
                        #break
                    # 
                    token = query.get('nextPageToken')
                    if not token:
                        break
                except errors.HttpError as error:
                    print('An error occurred: %s'%(error))
                    break
                token = query.get('nextPageToken', None)
            # 
            # check parent directories are consistent with the input if len(folder_paths)>=3
            if len(folder_paths)>=3:
                folder_itemi = 0
                while folder_itemi < len(folder_resources):
                    folder_item = folder_resources[folder_itemi]
                    folder_check = True
                    # now we need to get the all the folder_parents for folder_item
                    folder_parents = self.get_parents(folder_item)
                    folder_pathi = 3
                    while folder_pathi <= len(folder_paths):
                        folder_pathj = len(folder_paths) - folder_pathi
                        folder_pathk = len(folder_parents) - folder_pathi
                        if folder_pathj>=0 and folder_pathk>=0:
                            if folder_paths[folder_pathj] != '*' and folder_paths[folder_pathj] != '':
                                if verbose:
                                    print('Checking parent directories "%s" to "%s"'%(folder_paths[folder_pathj], folder_parents[folder_pathk].get('name')))
                                if folder_paths[folder_pathj].find('*')>=0 :
                                    folder_name_match = re.match(folder_paths[folder_pathj], folder_parents[folder_pathk].get('name'))
                                else:
                                    if folder_paths[folder_pathj] == folder_parents[folder_pathk].get('name'):
                                        folder_name_match = [1]
                                    else:
                                        folder_name_match = None
                                if folder_name_match is None:
                                    folder_check = False
                                    break
                        else:
                            break
                        folder_pathi = folder_pathi + 1
                    # 
                    if folder_check == True:
                        folder_itemi = folder_itemi + 1
                    else:
                        del folder_resources[folder_itemi]
            # 
        return folder_resources
    # 
    def get_file_by_path(self, file_path, verbose = True):
        return self.get_file_by_name(file_name=file_path, verbose=verbose)
    # 
    def get_file_by_name(self, file_name, verbose = True):
        # File List Search
        # -- https://developers.google.com/drive/v3/reference/files/list
        # -- https://developers.google.com/drive/v3/web/search-parameters
        file_resources = []
        if self.service and self.team_drive and len(file_name)>0:
            # 
            if file_name == '*':
                return file_resources
            # 
            if file_name.find('/')>=0:
                file_paths = file_name.split('/')
                for file_pathi in range(len(file_paths)):
                    file_name = file_paths[file_pathi]
            else:
                file_paths = []
            # 
            if file_name.find('*')>=0:
                file_names = file_name.split('*')
                query_str = "trashed = false"
                for file_namei in range(len(file_names)):
                    if file_names[file_namei] != '':
                        query_str = query_str + " and name contains '"+file_names[file_namei]+"'"
            else:
                query_str = "trashed = false and name = '"+file_name+"'"
            # 
            if len(file_paths)>=2:
                file_pathi = len(file_paths)-2
                # len(file_paths)-2 is the parent directory of the last element [len(file_paths)-1]
                if file_paths[file_pathi] != '*' and file_paths[file_pathi] != '':
                    file_parents = self.get_folder_by_name(file_paths[file_pathi], verbose = verbose)
                    if len(file_parents)>0:
                        query_str = query_str + str(' and (')
                        for file_parenti in range(len(file_parents)):
                            file_parent = file_parents[file_parenti]
                            if file_parenti != len(file_parents)-1:
                                query_str = query_str + str('\'%s\' in parents or '%(file_parent.get('id')))
                            else:
                                query_str = query_str + str('\'%s\' in parents)'%(file_parent.get('id')))
                    else:
                        print('Error! "%s" could not be found! Because its parent directory could not be found!'%('/'.join(file_paths)))
                        sys.exit()
            # 
            if verbose:
                print('Query with: "%s"'%(query_str))
            # 
            token = None
            while True:
                try:
                    time.sleep(0.25) # Google Drive has a limit of 10 query per second per user
                    query = self.service.files().list(
                                                        q=query_str, 
                                                        supportsTeamDrives=True, 
                                                        includeTeamDriveItems=True, 
                                                        teamDriveId=self.team_drive['id'], 
                                                        corpora='teamDrive', 
                                                        fields='nextPageToken, files(id, name, size, mimeType, parents, md5Checksum)', 
                                                        pageSize=10, 
                                                        pageToken=token, 
                                                        quotaUser=self.quota_user
                                                    ).execute()
                    #print(query)
                    for item in query.get('files'):
                        if verbose:
                            print('Found file: "%s" (Id: %s; MD5: %s)' % (item.get('name'), item.get('id'), item.get('md5Checksum')))
                        file_resources.append(item)
                        #break
                    # 
                    token = query.get('nextPageToken')
                    if not token:
                        break
                except errors.HttpError as error:
                    print('An error occurred: %s'%(error))
                    break
                token = query.get('nextPageToken', None)
            # 
            # check parent directories are consistent with the input if len(file_paths)>=3
            if len(file_paths)>=3:
                file_itemi = 0
                while file_itemi < len(file_resources):
                    file_item = file_resources[file_itemi]
                    file_check = True
                    # now we need to get the all the file_parents for file_item
                    file_parents = self.get_parents(file_item)
                    file_pathi = 3
                    if verbose:
                        print('Checking file item "%s"'%(file_item))
                    while file_pathi <= len(file_paths):
                        file_pathj = len(file_paths) - file_pathi
                        file_pathk = len(file_parents) - file_pathi
                        if file_pathj>=0 and file_pathk>=0:
                            if file_paths[file_pathj] != '*' and file_paths[file_pathj] != '':
                                if verbose:
                                    print('Checking parent directories "%s" to "%s"'%(file_paths[file_pathj], file_parents[file_pathk].get('name')))
                                if file_paths[file_pathj].find('*')>=0 :
                                    file_name_match = re.match(file_paths[file_pathj], file_parents[file_pathk].get('name'))
                                else:
                                    if file_paths[file_pathj] == file_parents[file_pathk].get('name'):
                                        file_name_match = [1]
                                    else:
                                        file_name_match = None
                                if file_name_match is None:
                                    file_check = False
                                    break
                        else:
                            break
                        file_pathi = file_pathi + 1
                    # 
                    if file_check == True:
                        file_itemi = file_itemi + 1
                    else:
                        del file_resources[file_itemi]
            # 
        return file_resources
    # 
    def print_files_in_folder(self, folder_name):
        return self.get_files_and_folders_in_a_folder_by_name(folder_name)
    # 
    def get_files_in_a_folder(self, folder_resource):
        return self.get_files_and_folders_in_a_folder_by_name(folder_name)
    # 
    def get_files_and_folders_in_a_folder_by_name(self, folder_name):
        if self.service and self.team_drive and len(folder_name)>0:
            # first find the folder
            if folder_name.find(os.sep)>=0:
                folder_resources = self.search_files_or_folders_by_path(folder_name, folderOnly=True)
            else:
                folder_resources = self.search_files_or_folders_by_names(folder_name, folderOnly=True)
            # report error if any
            if len(folder_resources)==0:
                print('Error! Folder "%s" was not found!'%(folder_name))
                return
            elif len(folder_resources)>=2:
                print('Warning! Found multpile folders with the name "%s"! Will only consider the first one!' % (folder_name) )
            # then get child items
            return self.get_files_and_folders_in_a_folder_resource(folder_resources[0])
        return []
    # 
    def is_folder_resource(self, input_resource):
        if type(input_resource) is list or type(input_resource) is tuple:
            output_boolean = []
            for input_resource1 in input_resource:
                if input_resource1.get('mimeType') == 'application/vnd.google-apps.folder':
                    output_boolean.append(True)
                else:
                    output_boolean.append(False)
            return output_boolean
        else:
            if input_resource.get('mimeType') == 'application/vnd.google-apps.folder':
                return True
            else:
                return False
    # 
    def get_files_and_folders_in_a_folder_resource(self, folder_resources, fileOnly=False, folderOnly=False, verbose=False):
        # Get files and folders under a folder resource.
        # -- We can actually input a list of folder_resources
        # File List Search
        # -- https://developers.google.com/drive/v3/reference/files/list
        # -- https://developers.google.com/drive/v3/web/search-parameters
        file_resources = []
        # 
        if self.service and self.team_drive and folder_resources:
            # check input
            if type(folder_resources) is not list and type(folder_resources) is not tuple:
                folder_resources = [folder_resources]
            # check input
            if fileOnly == folderOnly:
                fileOnly = False
                folderOnly = False
            # prepare query string
            if folderOnly:
                query_str = 'mimeType = \'application/vnd.google-apps.folder\' and '
            elif fileOnly:
                query_str = 'mimeType != \'application/vnd.google-apps.folder\' and '
            else:
                query_str = ''
            for folder_resource_i in range(len(folder_resources)):
                folder_resource = folder_resources[folder_resource_i]
                if folder_resource_i == 0:
                    query_str = query_str + str('( \'%s\' in parents'%(folder_resource.get('id')))
                else:
                    query_str = query_str + str(' or \'%s\' in parents'%(folder_resource.get('id')))
            query_str = query_str + ' )'
            if verbose:
                print('Query string: %s'%(query_str))
            # 
            token = None
            while True:
                try:
                    time.sleep(0.25) # Google Drive has a limit of 10 query per second per user
                    query = self.service.files().list(
                                                        q=query_str, 
                                                        supportsTeamDrives=True, 
                                                        includeTeamDriveItems=True, 
                                                        teamDriveId=self.team_drive['id'], 
                                                        corpora='teamDrive', 
                                                        fields='nextPageToken, files(id, name, size, mimeType, parents, md5Checksum)', 
                                                        pageSize=100, 
                                                        pageToken=token, 
                                                        quotaUser=self.quota_user
                                                    ).execute()
                    #print(query)
                    for item in query.get('files'):
                        if verbose:
                            print('Found item: "%s" (Id: %s, MimeType: %s)' % (item.get('name'), item.get('id'), item.get('mimeType')))
                        file_resources.append(item)
                    # 
                    token = query.get('nextPageToken')
                    if not token:
                        break
                except errors.HttpError as error:
                    print('An error occurred: %s'%(error))
                    break
                token = query.get('nextPageToken', None)
            # 
        return file_resources
    # 
    def download_files(self, file_resources, output_directory='', output_directories=None, verbose=False):
        # Download
        # -- https://developers.google.com/drive/v3/web/manage-downloads
        if self.service and self.team_drive:
            # check input
            if file_resources is None:
                return
            # check the input output_directories
            if output_directories is not None:
                if len(output_directories) != len(file_resources):
                    raise Exception('Error! The input \"output_directories\" and \"file_resources\" do not have the same length!')
            else:
                # check the input output_directory
                if output_directory != '':
                    if not output_directory.endswith(os.sep):
                        output_directory = output_directory + os.sep
                    if not os.path.isdir(output_directory):
                        os.makedirs(output_directory)
                else:
                    raise Exception('Please input either \"output_directory\" (no subfolder structure) or \"output_directories\" (parent folder for each input file_resource)!')
            # check input file_resources
            if type(file_resources) is not list:
                file_resources = [file_resources]
            # loop file resources
            for i, file_resource in enumerate(file_resources):
                # check output_directory
                if output_directories is not None:
                    output_directory = output_directories[i]
                    if not output_directory.endswith(os.sep):
                        output_directory = output_directory + os.sep
                    if not os.path.isdir(output_directory):
                        os.makedirs(output_directory)
                # verbose
                if verbose:
                    print('Downloading file "%s" into the folder "%s"' %(file_resource.get('name'), output_directory ) )
                # check file format <TODO> we could not download google document
                if file_resource.get('mimeType') == 'application/vnd.google-apps.document':
                    print('Warning! File "%s" is a google document! We will not download it into the folder "%s"' %(file_resource.get('name'), output_directory ) )
                    continue
                # download
                file_id = file_resource.get('id')
                time.sleep(0.15) # Google Drive has a limit of 10 query per second per user
                request = self.service.files().get_media(fileId=file_id, quotaUser=self.quota_user)
                #<DEBUG><20171108># print('Requesting "%s"'%(request.to_json()))
                #<BytesIO># fh = io.BytesIO()
                output_file_path = output_directory + file_resource.get('name')
                # 
                # check file existence
                has_existence_file = False
                if os.path.isfile(output_file_path):
                    if verbose:
                        print('Found existing file "%s", hashing md5 info...'%(output_file_path))
                    hash_md5 = hashlib.md5()
                    with open(output_file_path, "rb") as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hash_md5.update(chunk)
                    hash_md5_result = hash_md5.hexdigest()
                    #print(file_resource.get('md5Checksum'), type(file_resource.get('md5Checksum')))
                    #print(hash_md5_result, type(hash_md5_result))
                    if file_resource.get('md5Checksum') == hash_md5_result:
                        print('Found existing file "%s" with matched md5 checksum.'%(output_file_path))
                        has_existence_file = True
                # 
                # check FAILED file mark
                if os.path.isfile(output_file_path+'.FAILED'):
                    os.remove(output_file_path+'.FAILED')
                # 
                if not has_existence_file:
                    retry_counter = 0
                    while retry_counter >= 0 and retry_counter < 3:
                        fh = io.FileIO(output_file_path, mode='wb')
                        downloader = MediaIoBaseDownload(fh, request, chunksize=5*1024*1024)
                        done = False
                        while not done:
                            status, done = downloader.next_chunk()
                            print('Downloading "%s" (Id: %s, Md5: %s) (%.0f%%)' % (output_file_path, file_resource.get('id'), file_resource.get('md5Checksum'), status.progress()*100.0))
                            #time.sleep(0.25) # Google Drive has a limit of 10 query per second per user
                        #<BytesIO># # 
                        #<BytesIO># # write to file, if we use "fh = io.BytesIO()"
                        #<BytesIO># fp = open(file_resource.get('name'), 'wb')
                        #<BytesIO># fp.write(fh.getvalue())
                        # 
                        # verify downloaded file
                        if done:
                            file_size = file_resource.get('size')
                            file_size_downloaded = os.path.getsize(output_file_path)
                            print('Checking file size %s and downloaded size %s'%(file_size, file_size_downloaded))
                            if long(file_size_downloaded) != long(file_size):
                                print('Error! File size %s is different from the downloaded size %s! Deleting the failed download and re-trying!'%(file_size, file_size_downloaded))
                                os.remove(output_file_path)
                                retry_counter += 1
                            else:
                                print('OK!')
                                retry_counter = -99
                    # 
                    if retry_counter > 0:
                        print('Error occurred! Failed to download the file.')
                        with open(output_file_path+'.FAILED', 'w') as fp:
                            fp.write(datetime.today().strftime('%Y-%m-%d %Hh%Mm%Ss') + '\n')
                            fp.write('Failed to download file "%s" into the folder "%s"\n' %(file_resource.get('name'), output_directory ) )
                            fp.write('File Id: %s, Md5: %s\n' % (file_resource.get('id'), file_resource.get('md5Checksum') ) )
                            fp.write('')
                # 
                # end of looping file_resources
            # 
            # end of if valid
        # 
        # end of function
    # 
    def download_folders(self, folder_resources, output_directory='', verbose=False):
        # Recursively download a folder
        if self.service and self.team_drive:
            # check the input output_directory
            if output_directory != '':
                if not output_directory.endswith(os.sep):
                    output_directory = output_directory + os.sep
                if not os.path.isdir(output_directory):
                    os.makedirs(output_directory)
            # check input
            if folder_resources == None:
                return
            if type(folder_resources) is not list and type(folder_resources) is not tuple:
                folder_resources = [folder_resources]
            # loop folder resources
            for folder_resource in folder_resources:
                child_resources = self.get_files_and_folders_in_a_folder_resource(folder_resource, verbose=verbose)
                child_is_folder = self.is_folder_resource(child_resources)
                child_files = [t for t,k in zip(child_resources,child_is_folder) if not k]
                child_folders = [t for t,k in zip(child_resources,child_is_folder) if k]
                # prepare output directory
                if output_directory != '':
                    output_directory2 = output_directory + folder_resource.get('name')
                else:
                    output_directory2 = folder_resource.get('name')
                # verbose
                if verbose:
                    print('')
                    print('Prepare to download %d files and %d folders under the folder "%s"' %(len(child_files), len(child_folders), output_directory2) )
                # check existence
                downloading_files = []
                for child_file in child_files:
                    # get remote file size
                    remote_file_size = child_file.get('size')
                    if remote_file_size is not None:
                        remote_file_size = long(remote_file_size)
                    else:
                        remote_file_size = 0
                    # print verbose info
                    if verbose:
                        print('Checking file "%s" existence.' % (output_directory2 + os.sep + child_file.get('name') ) )
                    # if local file exists
                    if os.path.isfile(output_directory2 + os.sep + child_file.get('name')):
                        # get local file size
                        local_file_size = os.path.getsize(output_directory2 + os.sep + child_file.get('name'))
                        if local_file_size is not None:
                            local_file_size = long(local_file_size)
                        else:
                            local_file_size = -1
                        # print verbose info
                        if verbose:
                            print('Checking file "%s" size %d vs remote size %d.' % (output_directory2 + os.sep + child_file.get('name'), 
                                                                                     local_file_size, 
                                                                                     remote_file_size ) )
                        # compare remote and local file size, if they equal, skip this file for downloading
                        if os.path.getsize(output_directory2 + os.sep + child_file.get('name')) == remote_file_size:
                            if verbose:
                                print('Skipping file "%s" which has already been fully downloaded.' % (output_directory2 + os.sep + child_file.get('name') ) )
                            continue
                    else:
                        # dealing with zero remote size files which could not be properly downloaded with google API for now, see -- https://stackoverflow.com/questions/40830787/http-error-416-requested-range-not-satisfiable-using-google-drive-rest-api-on-a
                        if child_file.get('mimeType') == 'application/vnd.google-apps.document':
                            if verbose:
                                print('Skipping file "%s" which is a google document.' % (output_directory2 + os.sep + child_file.get('name') ) )
                            continue
                        elif remote_file_size == 0:
                            if verbose:
                                print('Touching file "%s" which has a zero size.' % (output_directory2 + os.sep + child_file.get('name') ) )
                            if not os.path.isdir(output_directory2): 
                                os.makedirs(output_directory2)
                            open(output_directory2 + os.sep + child_file.get('name'), 'a').close()
                            continue
                    # add the rest remote files into the list for downloading
                    downloading_files.append(child_file)
                # download files into the folder
                self.download_files(downloading_files, output_directory2, verbose=verbose)
                # go into child folders
                self.download_folders(child_folders, output_directory2, verbose=verbose)
                










