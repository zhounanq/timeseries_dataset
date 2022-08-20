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

from raster_util import read_raster, read_label_raster, write_raster_ref

warnings.filterwarnings('ignore')
os.environ['CPL_ZIP_ENCODING'] = 'UTF-8'
os.environ['PROJ_LIB'] = r'D:\develop-envi\anaconda3\envs\py38\Lib\site-packages\pyproj\proj_dir\share\proj'
gdal.UseExceptions()


class ResultDataset(object):

    def __init__(self, result_grid_folder, label_raster_path):

        self.label_raster_path = label_raster_path
        self.result_grid_folder = result_grid_folder

        self.label_raster_data = None
        self.result_grid_list = []

        pass

    def _prepare_data(self):

        for path in os.listdir(self.result_grid_folder):
            if os.path.isfile(path):
                self.result_grid_list.append(path)

        self.label_raster_data = read_label_raster(self.label_raster_path)

        pass

    def _update_type_to_label(self, type, label, row_start, row_end, col_start, col_end):

        grid_label = self.label_raster_data[row_start:row_end, col_start:col_end]
        grid_label[grid_label == label] = type
        self.label_raster_data[row_start:row_end, col_start:col_end] = grid_label

        pass

    def merge_grid_label(self):

        for path in self.result_grid_list:
            (file_name_ext, folder) = os.path.split(path)
            (file_name, ext) = os.path.splitext(file_name_ext)
            sub_strs = file_name.split(sep='_')

            result_type, label_id = sub_strs[0], sub_strs[1]
            grid_r_s, grid_r_e, grid_c_s, grid_c_e = sub_strs[2], sub_strs[3], sub_strs[4], sub_strs[5]
            self._update_type_to_label(result_type, label_id, grid_r_s, grid_r_e, grid_c_s, grid_c_e)
        # for
        pass

    def save_result_data(self, result_path):
        print("Saving result data to: ", result_path)

        result_folder = os.path.dirname(result_path)
        if not os.path.exists(result_folder):
            os.makedirs(result_folder)

        write_raster_ref(self.label_raster_data, result_path, self.label_raster_path)
        pass
