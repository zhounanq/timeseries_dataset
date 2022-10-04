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
        raster_transform = raster_ds.GetGeoTransform()
        print(f'GeoTransform: {raster_transform}')
        raster_datatype = raster_ds.GetRasterBand(1).DataType
        print(f'DataType: {raster_datatype}')
        raster_shape = (raster_ds.RasterXSize, raster_ds.RasterYSize, raster_ds.RasterCount)
        print(f'XSize, YSize, BandCount: {raster_shape}')

    # 2. get data
    raster_array = raster_ds.ReadAsArray()
    # np.nan has type float
    no_data = raster_ds.GetRasterBand(1).GetNoDataValue()
    raster_array = raster_array.astype(np.float32)
    raster_array[raster_array == no_data] = np.nan

    print(f'Array shape: {raster_array.shape}')
    if raster_array.ndim != 3:
        print('Only multi-spectral raster supported')
        raster_array = raster_array[np.newaxis, :]
        sys.exit(1)

    # 3. return
    return raster_array


def read_raster_list(raster_list):
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


def read_label_data(label_path):
    print("### Reading label raster {}".format(label_path))

    # 1. open source data
    raster_ds = gdal.Open(label_path, gdal.GA_ReadOnly)
    if not raster_ds:
        print('Unable to open image {}'.format(label_path))
        sys.exit(1)
    print(f'Project: {raster_ds.GetProjection()}')
    print(f'GeoTransform: {raster_ds.GetGeoTransform()}')
    print(f'DataType: {raster_ds.GetRasterBand(1).DataType}')

    # 2. get data
    raster_array = raster_ds.ReadAsArray()
    print(f'Array shape: {raster_array.shape}')
    no_data = raster_ds.GetRasterBand(1).GetNoDataValue()
    raster_array[raster_array == no_data] = 0

    # 3. close
    del raster_ds
    return raster_array


def write_raster_ref(raster_array, result_path, ref_path, format='GTiff'):
    print('### Writing result image...')

    #################################################################
    # 1. open source data
    ref_ds = gdal.Open(ref_path, gdal.GA_ReadOnly)
    if not ref_ds:
        print('Unable to open image {}'.format(ref_path))
        sys.exit(1)
    ref_proj = ref_ds.GetProjection()
    ref_transform = ref_ds.GetGeoTransform()
    ref_datatype = ref_ds.GetRasterBand(1).DataType
    ref_shape = (ref_ds.RasterCount, ref_ds.RasterYSize, ref_ds.RasterXSize)

    assert(ref_shape[0] == raster_array[0] and ref_shape[1] == raster_array[1])

    #################################################################
    # 3. write image
    raster_driver = gdal.GetDriverByName(format)
    raster_ds = raster_driver.Create(result_path, xsize=ref_shape[2], ysize=ref_shape[1], bands=ref_shape[0], eType=ref_datatype)
    if not raster_ds:
        print("Unable to create image {} with driver {}".format(result_path, format))
        sys.exit(1)

    raster_ds.SetGeoTransform(ref_transform)
    raster_ds.SetProjection(ref_proj)
    # dst_ds.GetRasterBand(1).SetNoDataValue(nodata_value)
    raster_ds.WriteRaster(0, 0, ref_shape[2], ref_shape[1], raster_array.tobytes())

    #################################################################
    # 4. close
    raster_ds.FlushCache()
    del raster_ds, ref_ds

    print("### Success @ write_raster_with_ref() ##################")


def write_patch_sample(class_type, raster_data, target_path):
    print(f'Saving for type {class_type} on {target_path}')

    parent_dir = os.path.dirname(target_path)
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)

    np.save(target_path, raster_data)
    pass


def write_numpy_array(numpy_array, target_path):

    parent_dir = os.path.dirname(target_path)
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)

    np.save(target_path, numpy_array)
    pass


def load_numpy_array(array_path):
    return np.load(array_path)
