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


def grid_folder_meta_csv(grid_folder, csv_path):

    pass


def metacsv_to_typecsv(metacsv_path, typecsv_path):


    pass


def typecsv_updata_polygon(typecsv_path, polygon_path):


    pass

