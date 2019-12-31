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

import os, sys, io, re, copy, json
import numpy as np

script_dir = os.path.dirname(__file__)
if not script_dir in sys.path:
    sys.path.append(script_dir)

from phangs_alma_gsearch import phangs_alma_gsearch

from phangs_alma_gdio import CAAP_Google_Drive_Operator






# 
# phangs_alma_gdownload
# 
def phangs_alma_data_downloader(input_galaxies = None, 
                                cubes = False, 
                                maps = False, 
                                cube_types = None, 
                                map_types = None, 
                                map_resolutions = None, 
                                array_configs = None, 
                                dry_run = False, 
                                update = False, 
                                verbose = False):
    # 
    # Set data release
    #data_root_dir = '/Archive/ALMA/'
    #data_release_folder = 'delivery_v3p4'
    # 
    # Search all moment maps for current data release
    moment_maps_cache = None
    cache_file = os.path.join(script_dir, 'cache_broad_maps_all_fits.json')
    if not os.path.isfile(cache_file) and not update:
        phangs_alma_gsearch("/Archive/ALMA/delivery_v3p4/broad_maps/*.fits", cache_file)
    if not os.path.isfile(cache_file):
        raise Exception('Error! Could not run \'phangs_alma_gsearch\' and write the cache file "%s"!'%(cache_file))
    with open(cache_file, 'r') as fp:
        moment_maps_cache = json.load(fp)
        print('Loaded %d moment maps in Google Drive'%(len(moment_maps_cache)))
    # 
    # Search all data cubes for current data release 
    data_cubes_cache = None
    cache_file = os.path.join(script_dir, 'cache_data_cubes_all_fits.json')
    if not os.path.isfile(cache_file) and not update:
        phangs_alma_gsearch("/Archive/ALMA/delivery_v3p4/cubes/*.fits", cache_file)
    if not os.path.isfile(cache_file):
        raise Exception('Error! Could not run \'phangs_alma_gsearch\' and write the cache file "%s"!'%(cache_file))
    with open(cache_file, 'r') as fp:
        data_cubes_cache = json.load(fp)
        print('Loaded %d data cubes in Google Drive'%(len(data_cubes_cache)))
    # 
    # find out all map resolutions
    if maps:
        moment_maps_resolutions = [re.sub(r'^.*_([0-9]+pc)\.fits$', r'\1', t['name'], re.IGNORECASE) for t in moment_maps_cache if re.match(r'^.*_([0-9]+pc)\.fits$', t['name'], re.IGNORECASE)]
        moment_maps_resolutions = sorted(list(set(moment_maps_resolutions)))
        moment_maps_resolutions.insert(0, '')
        print('All available map resolutions (%d): %s'%(len(moment_maps_resolutions), str(moment_maps_resolutions)))
    # 
    # find out all galaxy names
    all_galaxy_names = []
    if maps:
        moment_maps_galaxy_names = [re.sub(r'^([a-zA-Z0-9]+)_.*\.fits$', r'\1', t['name'], re.IGNORECASE) for t in moment_maps_cache]
        moment_maps_galaxy_names = sorted(list(set(moment_maps_galaxy_names)))
        all_galaxy_names.extend(moment_maps_galaxy_names)
        #print('All available galaxy names (%d): %s'%(len(moment_maps_galaxy_names), str(moment_maps_galaxy_names)))
    if cubes:
        data_cubes_galaxy_names = [re.sub(r'^([a-zA-Z0-9]+)_.*\.fits$', r'\1', t['name'], re.IGNORECASE) for t in data_cubes_cache]
        data_cubes_galaxy_names = sorted(list(set(data_cubes_galaxy_names)))
        all_galaxy_names.extend(data_cubes_galaxy_names)
        #print('All available galaxy names (%d): %s'%(len(data_cubes_galaxy_names), str(data_cubes_galaxy_names)))
    if len(all_galaxy_names) > 0:
        all_galaxy_names = sorted(list(set(all_galaxy_names)))
        print('All available galaxy names (%d): %s'%(len(all_galaxy_names), str(all_galaxy_names)))
    # 
    # print dry-run message
    if dry_run:
        print('Dry run mode! Will not actually download the data!')
    # 
    # check user input list
    if map_resolutions is not None:
        if type(map_resolutions) is str:
            map_resolutions = [map_resolutions]
    # 
    # check user input list
    if cube_types is not None:
        if type(cube_types) is str:
            cube_types = [cube_types]
    # 
    # check user input list
    if map_types is not None:
        if type(map_types) is str:
            map_types = [map_types]
    # 
    # check user input list
    if array_configs is not None:
        if type(array_configs) is str:
            array_configs = [array_configs]
    # 
    # check user input list
    if input_galaxies is not None:
        if type(input_galaxies) is str:
            input_galaxies = [input_galaxies]
    # 
    if len(input_galaxies) > 0:
        loop_list = copy.copy(input_galaxies)
        print('Selecting galaxies (%d): %s'%(len(loop_list), str(loop_list)))
    else:
        loop_list = ['.*']
        print('Downloading all galaxies (%d).'%(len(all_galaxy_names)))
    # 
    # init gdio
    gdo = CAAP_Google_Drive_Operator()
    print('Team Drive: %s' % (gdo.team_drive_name))
    # 
    has_found_cubes = False
    has_found_maps = False
    for galaxy_name in loop_list:
        if cubes == True:
            found_indices = [k for k in range(len(data_cubes_cache)) if re.match(r'^%s_.*_pbcorr_round_k\.fits$'%(galaxy_name), data_cubes_cache[k]['name'], re.IGNORECASE)]
            if array_configs is not None:
                if len(array_configs) > 0:
                    found_indices = [k for k in found_indices if re.match(r'^.*_(%s)_.*$'%('|'.join(array_configs).replace('+',r'\+')), data_cubes_cache[k]['name'], re.IGNORECASE)]
            if len(found_indices) > 0:
                has_found_cubes = True
                print('Found data cubes:')
                for k in found_indices:
                    print('  %s ("%s")'%(data_cubes_cache[k]['name'], data_cubes_cache[k]['abspath']))
                    # download
                    if not dry_run:
                        output_directory = 'delivery_v3p4/cubes'
                        gdo.download_files(data_cubes_cache[k], 
                                           output_directory = output_directory, 
                                           verbose = verbose) # the input is google drive file resource class
        # 
        if maps == True:
            found_indices = [k for k in range(len(moment_maps_cache)) if re.match(r'^%s_.*\.fits$'%(galaxy_name), moment_maps_cache[k]['name'], re.IGNORECASE)]
            # selecting map resolutions
            has_resolution_selection = False
            if map_resolutions is not None:
                if len(map_resolutions) > 0:
                    found_indices = [k for k in found_indices if re.match(r'^%s_.*_(%s)\.fits$'%(galaxy_name, '|'.join(map_resolutions)), moment_maps_cache[k]['name'], re.IGNORECASE)]
                    has_resolution_selection = True
            if not has_resolution_selection:
                found_indices = [k for k in found_indices if ( not re.match(r'^%s_.*_([0-9]+pc)\.fits$'%(galaxy_name), moment_maps_cache[k]['name'], re.IGNORECASE) ) ]
            # selecting array configs
            if array_configs is not None:
                if len(array_configs) > 0:
                    found_indices = [k for k in found_indices if re.match(r'^.*_(%s)_.*$'%('|'.join(array_configs).replace('+',r'\+')), moment_maps_cache[k]['name'], re.IGNORECASE)]
            # selecting map types
            if map_types is not None:
                if len(map_types) > 0:
                    found_indices = [k for k in found_indices if re.match(r'^.*[^a-zA-Z0-9](%s)[^a-zA-Z0-9].*$'%('|'.join(map_types)), moment_maps_cache[k]['name'], re.IGNORECASE)]
            if len(found_indices) > 0:
                has_found_maps = True
                print('Found moment maps:')
                for k in found_indices:
                    print('  %s ("%s")'%(moment_maps_cache[k]['name'], moment_maps_cache[k]['abspath']))
                    # download
                    if not dry_run:
                        output_directory = 'delivery_v3p4/broad_maps'
                        gdo.download_files(moment_maps_cache[k], 
                                           output_directory = output_directory, 
                                           verbose = verbose) # the input is google drive file resource class
    # 
    if (not has_found_cubes) and (not has_found_maps):
        print('Nothing found! Please check your input!')



# 
# Main Code
# 
if __name__ == '__main__':
    if len(sys.argv)>1:
        input_filenames = []
        input_galaxies = []
        update_cache = False
        download_cubes = False
        download_maps = False
        array_configs = []
        cube_types = []
        map_types = []
        map_resolutions = []
        dry_run = False
        verbose = False
        argmode = ''
        i = 1
        while i < len(sys.argv):
            argstr = sys.argv[i].lower().replace('--','-')
            if argstr == '-verbose':
                verbose = True
                argmode = ''
                i = i + 1
                continue
            elif argstr == '-update' or argstr == '-update-cache':
                update_cache = True
                argmode = ''
                i = i + 1
                continue
            elif argstr == '-cube' or argstr == '-cubes':
                download_cubes = True
                argmode = ''
                i = i + 1
                continue
            elif argstr == '-map' or argstr == '-maps':
                download_maps = True
                argmode = ''
                i = i + 1
                continue
            elif argstr == '-mom0':
                download_maps = True
                map_types.append('mom0')
                argmode = ''
                i = i + 1
                continue
            elif argstr == '-mom1':
                download_maps = True
                map_types.append('mom1')
                argmode = ''
                i = i + 1
                continue
            elif argstr == '-mom2':
                download_maps = True
                map_types.append('mom2')
                argmode = ''
                i = i + 1
                continue
            elif argstr == '-emom0':
                download_maps = True
                map_types.append('emom0')
                argmode = ''
                i = i + 1
                continue
            elif argstr == '-emom1':
                download_maps = True
                map_types.append('emom1')
                argmode = ''
                i = i + 1
                continue
            elif argstr == '-emom2':
                download_maps = True
                map_types.append('emom2')
                argmode = ''
                i = i + 1
                continue
            elif argstr == '-dry-run':
                dry_run = True
                argmode = ''
                i = i + 1
                continue
            elif argstr == '-array' or argstr == '-arrays':
                argmode = 'array'
                i = i + 1
                continue
            elif argstr == '-galaxy' or argstr == '-galaxies':
                argmode = 'galaxy'
                i = i + 1
                continue
            elif argstr == '-resolution' or argstr == '-resolutions' or argstr == '-res':
                argmode = 'resolution'
                i = i + 1
                continue
            elif argstr.startswith('-'):
                raise Exception('Error! Unrecognized input argument "%s"!'%(sys.argv[i]))
            # 
            if argmode == 'galaxy':
                input_galaxies.append(sys.argv[i])
            elif argmode == 'array':
                array_configs.append(sys.argv[i])
            elif argmode == 'resolution':
                map_resolutions.append(sys.argv[i])
            # 
            i = i + 1
        # 
        # 
        phangs_alma_data_downloader(input_galaxies, 
                                    cubes = download_cubes, 
                                    maps = download_maps, 
                                    cube_types = cube_types, 
                                    map_types = map_types, 
                                    map_resolutions = map_resolutions, 
                                    array_configs = array_configs, 
                                    dry_run = dry_run, 
                                    update = update_cache, 
                                    verbose = verbose)
    else:
        print('Usage: ')
        print('    /path/to/phangs_alma_data_downloader.py -cubes # download all data cubes')
        print('    /path/to/phangs_alma_data_downloader.py -maps # download all moment maps')
        print('    /path/to/phangs_alma_data_downloader.py -cubes -maps -galaxy NGC3627 # download cube and map for NGC3627')
        print('Options: ')
        print('    -cubes means downloading cubes.')
        print('    -maps means downloading maps.')
        print('    -galaxy or -galaxies followed by galaxy name(s) (case-insensitive) means selecting by galaxy name(s).')
        print('    -array or -arrays followed by array config(s) (case-insensitive) means selecting by array config(s).')
        print('    -resolution or -resolutions followed by resolution string(s) (e.g., \'500pc\') means selecting by resolution(s).')
        print('    -mom0 means selecting moment0 maps.')
        print('    -mom1 means selecting moment1 maps.')
        print('    -mom2 means selecting moment2 maps.')
        print('    -emom0 means selecting moment0 error maps.')
        print('    -emom1 means selecting moment1 error maps.')
        print('    -emom2 means selecting moment2 error maps. These -mom options are incremental.')
        print('    -dry-run means do not actually download the data.')
        print('    -verbose is for debugging use.')
        print('    -update is for next data releases. Do not use it.')
        print('    These options can either be starting with -- or -. Unrecognized options will cause Exception.')
    





