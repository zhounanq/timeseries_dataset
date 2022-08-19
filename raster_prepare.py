# -*- coding: utf-8 -*-

"""
Functions for time-series dataset

Author: Zhou Ya'nan
Date: 2021-09-16
"""
import os, sys, time
import numpy as np
import warnings

from osgeo import gdal

warnings.filterwarnings('ignore')
os.environ['CPL_ZIP_ENCODING'] = 'UTF-8'
os.environ['PROJ_LIB'] = r'D:\develop-envi\anaconda3\envs\py38\Lib\site-packages\pyproj\proj_dir\share\proj'
gdal.UseExceptions()


def read_raster(raster_path, print_info=False):
    print("### Reading raster image {}".format(raster_path))

    # 1. open source data
    raster_ds = gdal.Open(raster_path, gdal.GA_ReadOnly)
    if not raster_ds:
        print('Unable to open image {}'.format(raster_path))
        sys.exit(1)

    if print_info:
        raster_proj = raster_ds.GetProjection()
        print(f'Project: {raster_proj}')
        raster_geotransform = raster_ds.GetGeoTransform()
        print(f'GeoTransform: {raster_geotransform}')
        raster_datatype = raster_ds.GetRasterBand(1).DataType
        print(f'DataType: {raster_datatype}')
        raster_shape = (raster_ds.RasterXSize, raster_ds.RasterYSize, raster_ds.RasterCount)
        print(f'Raster Shape: {raster_shape}')

    # 2. get data
    raster_array = raster_ds.ReadAsArray()
    # np.nan has type float
    no_data = raster_ds.GetRasterBand(1).GetNoDataValue()
    raster_array = raster_array.astype(np.float32)
    raster_array[raster_array == no_data] = np.nan

    print(f'Array shape: {raster_array.shape}')
    if raster_array.ndim != 3:
        print('Only multi-spectral raster supported')
        sys.exit(1)

    # 3. return
    return raster_array


def prepare_raster_list(raster_list):
    print("### Reading reference raster {}".format(raster_list))

    raster_data_list = []
    num_reference = len(raster_list)
    for rr in range(num_reference):
        path = raster_list[rr]
        raster_data = read_raster(path, (True if rr == 0 else False))

        if rr == 0:
            num_band = raster_data.shape[0]
        else:
            assert (num_band == raster_data.shape[0])

        raster_data_list.append(raster_data)
    # for
    all_data = np.concatenate(raster_data_list, axis=0)

    return all_data


def prepare_parcel_raster(parcel_raster):
    print("### Reading target raster {}".format(parcel_raster))

    # 1. open source data
    raster_ds = gdal.Open(parcel_raster, gdal.GA_ReadOnly)
    if not raster_ds:
        print('Unable to open image {}'.format(parcel_raster))
        sys.exit(1)

    if 0 > 1:
        raster_proj = raster_ds.GetProjection()
        print(f'Project: {raster_proj}')
        raster_geotransform = raster_ds.GetGeoTransform()
        print(f'GeoTransform: {raster_geotransform}')
        raster_datatype = raster_ds.GetRasterBand(1).DataType
        print(f'DataType: {raster_datatype}')
        raster_shape = (raster_ds.RasterXSize, raster_ds.RasterYSize, raster_ds.RasterCount)
        print(f'Raster Shape: {raster_shape}')

    # 2. get data
    raster_array = raster_ds.ReadAsArray()
    print(f'Array shape: {raster_array.shape}')

    # 3. close
    del raster_ds
    return raster_array


def write_patch_sample():

    pass

