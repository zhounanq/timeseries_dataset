# -*- coding: utf-8 -*-

"""
Functions for time-series dataset

Author: Zhou Ya'nan
Date: 2021-09-16
"""
import os
import numpy as np
import warnings
from tqdm import tqdm
from osgeo import gdal

from raster_util import read_raster_list, read_label_data, write_patch_sample
from raster_util import load_numpy_array, write_numpy_array

warnings.filterwarnings('ignore')
os.environ['CPL_ZIP_ENCODING'] = 'UTF-8'
os.environ['PROJ_LIB'] = r'D:\develop-envi\anaconda3\envs\py38\Lib\site-packages\pyproj\proj_dir\share\proj'
gdal.UseExceptions()


class RasterDatasetsSplit(object):
    def __init__(self, raster_list, result_folder, patch_size=32):
        """

        :param raster_list:
        :param result_folder:
        :param patch_size:
        """
        self.raster_path_list = raster_list
        self.result_folder = result_folder

        self.raster_data = None
        self.grid_code = None
        self.raster_rows, self.raster_cols = 0, 0

        self.patch_size = patch_size

    def prepare_data(self):
        # todo check the list of raster

        self.raster_data = read_raster_list(self.raster_path_list)
        self.raster_rows = self.raster_data.shape[1]
        self.raster_cols = self.raster_data.shape[2]

    def generate_grid_code(self):
        print("### Generating grid codes for study area...")
        assert (self.raster_rows > 0 and self.raster_cols > 0)

        rows_patch = self.raster_rows // self.patch_size
        cols_patch = self.raster_cols // self.patch_size
        self.grid_code = np.zeros((rows_patch*cols_patch, 4), dtype=np.int)
        for rr in range(rows_patch):
            row_start = rr * self.patch_size
            row_end = (rr+1) * self.patch_size
            for cc in range(cols_patch):
                col_start = cc * self.patch_size
                col_end = (cc+1) * self.patch_size
                self.grid_code[rr*cols_patch + cc, :] = (row_start, row_end, col_start, col_end)
            # for
        # for

        print(f'{self.grid_code.shape[0]} patch searched')
        return self.grid_code

    def split_grid_raster(self):
        print('### Splitting raster data into grids...')
        assert self.raster_data

        # create folder for grid data
        if not os.path.exists(self.result_folder):
            os.makedirs(self.result_folder)

        # split raster and write
        num_grid = self.grid_code.shape[0]
        for gg in tqdm(range(num_grid), desc='Splitting raster datasets ...'):

            # folder
            if num_grid > 10000:
                sub = gg // 10000
                write_folder = os.path.join(self.result_folder, '{:0>2d}'.format(sub))
                if gg % 10000 == 0 and not os.path.exists(write_folder):
                    os.makedirs(write_folder)
            else:
                write_folder = self.result_folder

            # data
            r_s, r_e, c_s, c_e = self.grid_code[gg, :]
            grid_name = '{:0>5d}_{:0>5d}_{:0>5d}_{:0>5d}'.format(r_s, r_e, c_s, c_e)
            grid_raster_data = self.raster_data[:, r_s:r_e, c_s:c_e]

            # save to disk
            write_path = os.path.join(write_folder, grid_name)
            write_numpy_array(grid_raster_data, write_path)
        # for

        return self.result_folder


def main():
    print("##################################################################")
    print("###                                      #########################")
    print("##################################################################")

    #######################################################
    # cmd line
    patch_size = 32
    result_folder = r''
    raster_list = [
        r'',
        r'',

    ]

    #######################################################
    # do
    rds = RasterDatasetsSplit(raster_list, result_folder, patch_size)
    rds.prepare_data()
    rds.generate_grid_code()
    rds.split_grid_raster()

    #######################################################
    # close

    print('### Task complete !')


if __name__ == '__main__':
    main()
