# -*- coding: utf-8 -*-

"""
Functions for time-series dataset

Author: Zhou Ya'nan
Date: 2021-09-16
"""
import os, sys, time
import numpy as np
import warnings
from osgeo import gdal, ogr, gdalconst

# Enable GDAL/OGR exceptions
gdal.UseExceptions()
gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8")


def add_field_rasterize(polygon_path, field_name='RSTIZE_ID'):
    """
    为输入矢量，添加序列ID，ID从1开始。
    :param polygon_path:
    :param field_name:
    :return:
    """
    # 1. load shpfile
    polygon_dataset = ogr.Open(polygon_path, gdal.OF_VECTOR | gdal.OF_UPDATE)
    if polygon_dataset is None:
        print(f"### ERROR: could not open {polygon_path}")
        return None
    polygon_layer = polygon_dataset.GetLayer(0)

    # 2. create field
    layer_definition = polygon_layer.GetLayerDefn()
    # if exits, delete it first.
    polygon_layer.DeleteField(layer_definition.GetFieldIndex(field_name))
    # Add a new field
    new_field = ogr.FieldDefn(field_name, field_type=ogr.OFTInteger64)
    polygon_layer.CreateField(new_field)

    # 3. write attributes
    rstize_id = 1
    for feat in polygon_layer:
        feat.SetField(field_name, int(rstize_id))
        polygon_layer.SetFeature(feat)
        rstize_id = rstize_id + 1

    # 4. close
    polygon_layer = None
    polygon_dataset = None
    return polygon_path


def polygon_rasterize_id(polygon_path, dst_raster_path, reference_raster_path, format='GTiff'):
    """
    Rasterize a polygon layer, using ref_raster_path as a reference.
    :param polygon_path:
    :param dst_raster_path:
    :param reference_raster_path:
    :param format:
    :return:
    """

    # read polygon file and reference raster file
    reference_dataset = gdal.Open(reference_raster_path, gdalconst.GA_ReadOnly)
    if not reference_dataset:
        print("Unable to open image {}".format(reference_raster_path))
        return None
    x_size, y_size = reference_dataset.RasterXSize, reference_dataset.RasterYSize
    # meta of raster, resolution, projection, geo transformation
    projection = reference_dataset.GetProjection()
    geo_transform = reference_dataset.GetGeoTransform()

    polygon_dataset = ogr.Open(polygon_path)
    if not polygon_dataset:
        print("Unable to open polygon file {}".format(polygon_path))
        return None
    polygon_layer = polygon_dataset.GetLayer()
    # common regions of polygon and raster

    # create result raster
    raster_driver = gdal.GetDriverByName(format)
    raster_dataset = raster_driver.Create(dst_raster_path, xsize=x_size, ysize=y_size, bands=1, eType=gdal.GDT_UInt32)
    if not raster_dataset:
        print("Unable to create image {} with driver {}".format(dst_raster_path, format))
        return None
    raster_dataset.SetGeoTransform(geo_transform)
    raster_dataset.SetProjection(projection)
    raster_band = raster_dataset.GetRasterBand(1)

    # rasterize
    nodata_value = 0
    raster_band.SetNoDataValue(nodata_value)
    raster_band.FlushCache()
    return_value = gdal.RasterizeLayer(raster_dataset, [1], polygon_layer, options=["ATTRIBUTE=RSTIZE_ID"])

    # close
    raster_dataset = None
    reference_dataset = None
    polygon_layer = None
    polygon_dataset = None
    return dst_raster_path


def polygon_rasterize_type(polygon_path, dst_raster_path, reference_raster_path, burn_field='type', format='GTiff'):
    """
    Rasterize a polygon layer, using ref_raster_path as a reference.
    :param polygon_path:
    :param dst_raster_path:
    :param reference_raster_path:
    :param burn_field:
    :param format:
    :return:
    """

    # read polygon file and reference raster file
    reference_dataset = gdal.Open(reference_raster_path, gdalconst.GA_ReadOnly)
    if not reference_dataset:
        print("Unable to open image {}".format(reference_raster_path))
        return None
    # meta of raster, resolution, projection, geo transformation
    x_size, y_size = reference_dataset.RasterXSize, reference_dataset.RasterYSize
    projection = reference_dataset.GetProjection()
    geo_transform = reference_dataset.GetGeoTransform()

    polygon_dataset = ogr.Open(polygon_path)
    if not polygon_dataset:
        print("Unable to open polygon file {}".format(polygon_path))
        return None
    polygon_layer = polygon_dataset.GetLayer()
    # common regions of polygon and raster

    # create result raster
    raster_driver = gdal.GetDriverByName(format)
    raster_dataset = raster_driver.Create(dst_raster_path, xsize=x_size, ysize=y_size, bands=1, eType=gdal.GDT_UInt32)
    if not raster_dataset:
        print("Unable to create image {} with driver {}".format(dst_raster_path, format))
        return None
    raster_dataset.SetGeoTransform(geo_transform)
    raster_dataset.SetProjection(projection)

    # rasterize
    nodata_value = 0
    raster_band = raster_dataset.GetRasterBand(1)
    raster_band.SetNoDataValue(nodata_value)
    raster_band.FlushCache()
    option_list = "ATTRIBUTE={}".format(burn_field)
    return_value = gdal.RasterizeLayer(raster_dataset, [1], polygon_layer, options=[option_list])

    # close
    raster_dataset = None
    reference_dataset = None
    polygon_layer = None
    polygon_dataset = None
    return dst_raster_path


def main():
    print("##########################################################")
    print("###  #####################################################")
    print("##########################################################")

    polygon_path = r'G:\FF\application_dataset\2020-france-agri-grid\parcel_dirong\polygon\parcel_dirong_maincrop_removesmall_utm_randomselection\parcel_dirong_maincrop_removesmall_utm.shp'
    dst_raster_path = r'G:\FF\application_dataset\2020-france-agri-grid\parcel_dirong\polygon\parcel_dirong_maincrop_removesmall_utm_polygon.tif'
    reference_raster_path = r'G:\FF\application_dataset\2020-france-agri\s2_l2a_tif_masked\10m\L1C_T31TFN_20190103_masked_10m.tif'

    add_field_rasterize(polygon_path)

    polygon_rasterize_id(polygon_path, dst_raster_path, reference_raster_path)

    print("### Complete! #############################################")


if __name__ == "__main__":
    main()
