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

from raster_util import read_label_data
from raster_util import write_numpy_array

warnings.filterwarnings('ignore')
os.environ['CPL_ZIP_ENCODING'] = 'UTF-8'
os.environ['PROJ_LIB'] = r'D:\develop-envi\anaconda3\envs\py38\Lib\site-packages\pyproj\proj_dir\share\proj'
gdal.UseExceptions()


class LabelDatasetSplit(object):
    def __init__(self, label_path, result_folder, patch_size=32):
        """

        :param label_path:
        :param result_folder:
        :param patch_size:
        """
        self.label_path = label_path
        self.result_folder = result_folder

        self.label_data = None
        self.grid_code = None
        self.label_rows, self.label_cols = 0, 0

        self.patch_size = patch_size

    def prepare_data(self):
        # todo check the list of raster

        self.label_data = read_label_data(self.label_path)
        self.label_rows = self.label_data.shape[0]
        self.label_cols = self.label_data.shape[1]

    def generate_grid_code(self):
        print("### Generating grid codes for study area...")
        assert (self.label_rows > 0 and self.label_cols > 0)

        rows_patch = self.label_rows // self.patch_size
        cols_patch = self.label_cols // self.patch_size
        self.grid_code = np.zeros((rows_patch * cols_patch, 4), dtype=np.int)
        for rr in range(rows_patch):
            row_start = rr * self.patch_size
            row_end = (rr + 1) * self.patch_size
            for cc in range(cols_patch):
                col_start = cc * self.patch_size
                col_end = (cc + 1) * self.patch_size
                self.grid_code[rr * cols_patch + cc, :] = (row_start, row_end, col_start, col_end)
            # for
        # for

        print(f'{self.grid_code.shape[0]} patch searched')
        return self.grid_code

    def split_grid_label(self):
        print('### Splitting label data into grids...')
        assert self.label_data

        # create folder for grid data
        if not os.path.exists(self.result_folder):
            os.makedirs(self.result_folder)

        # split raster and write
        num_grid = self.grid_code.shape[0]
        for gg in tqdm(range(num_grid), desc='Splitting label datasets ...'):

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
            grid_label_data = self.label_data[r_s:r_e, c_s:c_e]

            # save to disk
            write_path = os.path.join(write_folder, grid_name)
            write_numpy_array(grid_label_data, write_path)
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
    label_path = r''

    #######################################################
    # do
    lds = LabelDatasetSplit(label_path, result_folder, patch_size)
    lds.prepare_data()
    lds.generate_grid_code()
    lds.split_grid_label()

    #######################################################
    # close

    print('### Task complete !')


if __name__ == '__main__':
    main()
