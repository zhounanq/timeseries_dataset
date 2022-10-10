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


# can be implemented using Geopandas
