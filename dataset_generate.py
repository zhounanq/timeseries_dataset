# -*- coding: utf-8 -*-

"""
Functions for time-series dataset

Author: Zhou Ya'nan
Date: 2021-09-16
"""
import os, sys, time
import datetime
import argparse
import numpy as np
import warnings
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
from osgeo import gdal, osr

warnings.filterwarnings('ignore')
os.environ['CPL_ZIP_ENCODING'] = 'UTF-8'
os.environ['PROJ_LIB'] = r'D:\develop-envi\anaconda3\envs\py38\Lib\site-packages\pyproj\proj_dir\share\proj'
gdal.UseExceptions()


def patch2sample(parcal_data, raster_data, min_pixel_percent):

    patch_size = parcal_data.shape[0]

    # 1. the number of types in parcel_data, and their values

    value_list = []
    num_list = []

    # 2. for each type in parcel_data
    for vv, num in zip(value_list, num_list):
        if float(num/patch_size/patch_size) > min_pixel_percent:
            parcel_data_current = parcal_data
            raster_data_current = raster_data

            parcel_data_current[parcel_data_current == vv] = 0
            raster_data_current[parcel_data_current == vv] = 0




    pass


def grid_clip_raster(parcal_data, raster_data, patch_size=32):
    (bb, rows, cols) = raster_data.shape

    if rows % patch_size != 0:
        rows = (rows / patch_size + 1) * patch_size
    if cols % patch_size != 0:
        cols = (cols / patch_size + 1) * patch_size

    raster_data = np.pad(raster_data, ((0, 0), (0, rows - raster_data.shape[1]), (0, cols - raster_data.shape[2])),
                         'constant')
    parcal_data = np.pad(parcal_data, ((0, rows - raster_data.shape[1]), (0, cols - raster_data.shape[2])), 'constant')

    rows_patch = rows / patch_size
    cols_patch = cols / patch_size

    for rr in range(rows_patch):
        row_start = rr * patch_size
        row_end = rr * patch_size + patch_size
        for cc in range(cols_patch):
            col_start = cc * patch_size
            col_end = cc * patch_size + patch_size
            patch_raster_data = raster_data[:, row_start: row_end, col_start:col_end]
            patch_parcel_data = parcal_data[row_start: row_end, col_start:col_end]

            pass

    pass
