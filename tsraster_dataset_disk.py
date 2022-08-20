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

from raster_util import read_raster, read_label_raster, write_patch_sample
from raster_util import load_numpy_array, write_numpy_array

warnings.filterwarnings('ignore')
os.environ['CPL_ZIP_ENCODING'] = 'UTF-8'
os.environ['PROJ_LIB'] = r'D:\develop-envi\anaconda3\envs\py38\Lib\site-packages\pyproj\proj_dir\share\proj'
gdal.UseExceptions()


class TSRasterDatasetDisk(object):

    def __init__(self, label_path, raster_list, result_folder, patch_size=32, min_pixel_percent=0.01):
        self.label_raster_path = label_path
        self.raster_path_list = raster_list
        self.result_folder = result_folder

        self.pad_rows, self.pad_cols = 0, 0
        self.grid_code = None

        self.patch_size = patch_size
        self.min_pixel_percent = min_pixel_percent

        pass

    def _generate_grid_code(self):
        print("### Generating grid codes for study area...")

        label_data = read_label_raster(self.label_raster_path)
        src_rows, src_cols = label_data.shape
        patch_size = self.patch_size

        rows_patch = src_rows // patch_size
        cols_patch = src_cols // patch_size
        self.grid_code = np.zeros((rows_patch*cols_patch, 4), dtype=np.int)
        for rr in range(rows_patch):
            row_start = rr * patch_size
            row_end = rr * patch_size + patch_size
            for cc in range(cols_patch):
                col_start = cc * patch_size
                col_end = cc * patch_size + patch_size
                self.grid_code[rr*cols_patch + cc, :] = (row_start, row_end, col_start, col_end)
            # for
        # for

        print(f'{self.grid_code.shape[0]} patch searched')
        pass

    def _split_label_data(self):
        print('### Split label data ...')

        # create folder for grid data
        (grid_folder, ext) = os.path.splitext(self.label_raster_path)
        if not os.path.exists(grid_folder):
            os.makedirs(grid_folder)

        # read and pad raster
        label_data = read_label_raster(self.label_raster_path)
        src_rows, src_cols = label_data.shape

        # split raster and write
        num_grid = self.grid_code.shape[0]
        for gg in range(num_grid):
            r_s, r_e, c_s, c_e = self.grid_code[gg, :]
            grid_name = '{:0>5d}_{:0>5d}_{:0>5d}_{:0>5d}'.format(r_s, r_e, c_s, c_e)
            grid_path = os.path.join(grid_folder, grid_name)

            grid_label_data = label_data[r_s:r_e, c_s:c_e]
            write_numpy_array(grid_label_data, grid_path)
        # for

        pass

    def _split_raster_data(self):
        print('### Split multi-temporal raster data ...')

        for path in self.raster_path_list:
            print(f'### Split raster data {path}')

            # create folder for grid data
            (grid_folder, ext) = os.path.splitext(path)
            if not os.path.exists(grid_folder):
                os.makedirs(grid_folder)

            # read and pad raster
            raster_data = read_raster(path)
            src_band, src_rows, src_cols = raster_data.shape

            # split raster and write
            num_grid = self.grid_code.shape[0]
            for gg in range(num_grid):
                r_s, r_e, c_s, c_e = self.grid_code[gg, :]
                grid_name = '{:0>5d}_{:0>5d}_{:0>5d}_{:0>5d}'.format(r_s, r_e, c_s, c_e)
                grid_path = os.path.join(grid_folder, grid_name)

                grid_raster_data = raster_data[:, r_s:r_e, c_s:c_e]
                write_numpy_array(grid_raster_data, grid_path)
            # for
        # for

        print('### Split multi-temporal raster data complete!')
        pass

    def _combine_label_raster_data(self):
        print('### Generating grid samples...')

        # path for grid data
        raster_grid_folder_list = []
        for path in self.raster_path_list:
            (raster_grid_folder, ext) = os.path.splitext(path)
            raster_grid_folder_list.append(raster_grid_folder)
        (label_grid_folder, ext) = os.path.splitext(self.label_raster_path)

        # combine grid data
        num_grid = self.grid_code.shape[0]
        for gg in range(num_grid):
            r_s, r_e, c_s, c_e = self.grid_code[gg, :]
            grid_name = '{:0>5d}_{:0>5d}_{:0>5d}_{:0>5d}'.format(r_s, r_e, c_s, c_e)
            print(f'Grid {grid_name}')

            raster_grid_data_list = []
            for folder in raster_grid_folder_list:
                raster_grid_path = os.path.join(folder, grid_name+'.npy')
                raster_grid_data = load_numpy_array(raster_grid_path)
                raster_grid_data_list.append(raster_grid_data)
            # for
            all_raster_grid_data = np.concatenate(raster_grid_data_list, axis=0)

            label_grid_path = os.path.join(label_grid_folder, grid_name+'.npy')
            label_grid_data = load_numpy_array(label_grid_path)

            self._grid_to_sample(label_grid_data, all_raster_grid_data, grid_name)
        # for

        print('### Generating grid samples complete!')
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

                # mask non-target values
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

    def prepare_data(self):
        assert(os.path.exists(self.label_raster_path))
        # todo check the list of raster data

        self._generate_grid_code()
        self._split_label_data()
        self._split_raster_data()
        pass

    def generate(self):
        assert(self.grid_code is not None)

        self._combine_label_raster_data()
        pass
