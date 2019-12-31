# phangs-alma-gdrive-io
PHANGS-ALMA Google Drive I/O


# README


### Files:

    phangs_alma_gsearch.py      -- Search for galaxy name and products (not required to run this before gdownload) 
    phangs_alma_gdownload.py    -- Download products 

### Python package dependency:

    google-api-python-client
    httplib2
    oauth2client
    hashlib


### TODOs: 

#### 1. Will prepare scripts to batch download products with certain version. 


### Examples: 
    
#### 1. Download one file

```
(In Terminal)
/path/to/phangs_alma_gdownload.py "/Archive/ALMA/delivery_v3p3/broad_maps/ngc3627_12m+7m+tp_co21_broad_mom0.fits"
# This will download into a subfolder "./Archive/ALMA/delivery_v3p3/broad_maps/"
```

#### 2. Download all moment maps for one galaxy

```
(In Terminal)
/path/to/phangs_alma_gdownload.py "/Archive/ALMA/delivery_v3p3/broad_maps/ngc3627_*_co21_broad_mom0.fits"
# This will download all files into the subfolder "./Archive/ALMA/delivery_v3p3/broad_maps/"
```

#### 3. Download all moment maps for all galaxies

```
(In Terminal)
/path/to/phangs_alma_gdownload.py "/Archive/ALMA/delivery_v3p3/broad_maps/*_12m+7m+tp_co21_broad_mom0.fits"
# This will download all files into the subfolder "./Archive/ALMA/delivery_v3p3/broad_maps/"
```

#### 4. Download cubes for one galaxy

```
(In Terminal)
/path/to/phangs_alma_gdownload.py "/Archive/ALMA/delivery_v3p3/cubes/ngc3627_12m+7m+tp_co21_pbcorr_round_k.fits"
# This will download all files into the subfolder "./Archive/ALMA/delivery_v3p3/cubes/"
```




### Last update:

    2019-12-06 Init

        
        
        
        





