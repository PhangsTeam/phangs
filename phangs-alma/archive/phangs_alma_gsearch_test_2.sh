#!/bin/bash
# 

$(dirname ${BASH_SOURCE[0]})/phangs_alma_gsearch.py "ngc3627_12m+7m+tp_*_mom0.fits" -verbose | tee phangs_alma_gsearch_test_2.log

