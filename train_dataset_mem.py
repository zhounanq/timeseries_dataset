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

from raster_util import read_raster_list, read_label_raster, write_patch_sample

warnings.filterwarnings('ignore')
os.environ['CPL_ZIP_ENCODING'] = 'UTF-8'
os.environ['PROJ_LIB'] = r'D:\develop-envi\anaconda3\envs\py38\Lib\site-packages\pyproj\proj_dir\share\proj'
gdal.UseExceptions()


class TrainDatasetMem(object):

    def __init__(self, label_path, raster_list, result_folder, patch_size=32, min_pixel_percent=0.01):
        self.label_raster_path = label_path
        self.raster_path_list = raster_list
        self.result_folder = result_folder

        self.label_data = None
        self.raster_data = None

        self.patch_size = patch_size
        self.min_pixel_percent = min_pixel_percent

        pass

    def _grid_to_sample(self, label_data, raster_data, grid_code):
        print(f'Slicing types for {grid_code} ...')

        patch_size2 = label_data.size
        min_pixel_percent = self.min_pixel_percent
        num_band = raster_data.shape[0]

        # 1. the number of types in parcel_data, and their values
        unique, counts = np.unique(label_data, return_counts=True, axis=None)

        # 2. for each type in parcel_data
        for vv, num in zip(unique, counts):
            if (vv != 0) and (num / patch_size2 > min_pixel_percent):
                sample_path = os.path.join(self.result_folder, 'npy', '{:0>2d}_{}'.format(vv, grid_code))
                print(f'generating sample on {sample_path}')
                label_data_current = label_data.copy()
                raster_data_current = raster_data.copy()

                label_mask = label_data_current != vv
                # label_data_current[label_mask] = 0
                raster_mask = label_mask[np.newaxis, :]
                raster_mask = np.repeat(raster_mask, repeats=num_band, axis=0)
                raster_data_current[raster_mask] = 0

                # save to disk
                write_patch_sample(vv, raster_data_current, sample_path)
            # if
        # for
        pass

    def _split_grid_raster(self, label_data, raster_data):
        print('### Spliting raster and label data into grids...')

        src_rows, src_cols = label_data.shape
        patch_size = self.patch_size

        if src_rows % patch_size > patch_size * 0.6:
            self.pad_rows = int((src_rows // patch_size + 1) * patch_size)
        else:
            self.pad_rows = int((src_rows // patch_size) * patch_size)

        if src_cols % patch_size > patch_size * 0.6:
            self.pad_cols = int((src_cols // patch_size + 1) * patch_size)
        else:
            self.pad_cols = int((src_cols // patch_size) * patch_size)

        pad_rows_num = (self.pad_rows - src_rows) if (self.pad_rows > src_rows) else 0
        pad_cols_num = (self.pad_cols - src_cols) if (self.pad_cols > src_cols) else 0
        raster_data = np.pad(raster_data, ((0, 0), (0, pad_rows_num), (0, pad_cols_num)), 'constant')
        label_data = np.pad(label_data, ((0, pad_rows_num), (0, pad_cols_num)), 'constant')

        # for each grid
        rows_grid = self.pad_rows // patch_size
        cols_grid = self.pad_cols // patch_size
        for rr in range(rows_grid):
            row_start = rr * patch_size
            row_end = rr * patch_size + patch_size
            for cc in range(cols_grid):
                col_start = cc * patch_size
                col_end = cc * patch_size + patch_size

                grid_name = '{:0>5d}_{:0>5d}_{:0>5d}_{:0>5d}'.format(row_start, row_end, col_start, col_end)
                patch_raster_data = raster_data[:, row_start: row_end, col_start: col_end]
                patch_label_data = label_data[row_start: row_end, col_start: col_end]
                print(f'Grid {grid_name}')

                self._grid_to_sample(patch_label_data, patch_raster_data)
            # for
        # for

        pass

    def prepare_data(self):
        assert(os.path.exists(self.label_raster_path))
        # todo check the list of raster

        self.label_data = read_label_raster(self.label_raster_path)
        self.raster_data = read_raster_list(self.raster_path_list)
        pass

    def generate(self):

        self._split_grid_raster(self.label_data, self.raster_data)

        pass
