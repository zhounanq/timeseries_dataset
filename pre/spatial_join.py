# -*- coding: utf-8 -*-
"""

https://geopandas.org/en/stable/gallery/spatial_joins.html
Author: Zhou Ya'nan
Date: 2021-09-16
"""
import os
import warnings
import numpy as np
import pandas as pd
import geopandas as gpd
from osgeo import gdal, ogr, gdalconst

# Enable GDAL/OGR exceptions
gdal.UseExceptions()
gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8")


def spatial_join_type(polygon_path, point_path, join_path):
    """

    :param polygon_path:
    :param point_path:
    :param join_path:
    :return:
    """
    # Reading
    polygon_df = gpd.read_file(polygon_path)
    point_df = gpd.read_file(point_path)
    assert(not polygon_df or not point_df)

    # Make sure they're using the same projection reference
    assert(polygon_df.crs != point_df.crs)

    # spatial join
    join_df = polygon_df.sjoin(point_df, how='left')

    # save
    join_df.to_file(join_path)

    return join_path

