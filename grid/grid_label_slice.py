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

from raster_util import read_label_data, write_slice_array
from raster_util import write_numpy_array, load_numpy_array

warnings.filterwarnings('ignore')
os.environ['CPL_ZIP_ENCODING'] = 'UTF-8'
os.environ['PROJ_LIB'] = r'D:\develop-envi\anaconda3\envs\py38\Lib\site-packages\pyproj\proj_dir\share\proj'
gdal.UseExceptions()


class GridLabelSlice(object):
    def __init__(self, label_folder, result_folder, patch_size=32, min_pixel_percent=0.01):
        self.label_folder = label_folder
        self.result_folder = result_folder

        self.patch_size = patch_size
        self.min_pixel_percent = min_pixel_percent

        self.grid_code_list = []

    def list_grid_codes(self, filter_ext='.npy'):

        # fast version
        item_list = os.listdir(self.label_folder)
        for path in item_list:
            self.grid_code_list.append(path[:-4])
        self.grid_code_list.sort()

        # item_list = os.listdir(self.label_folder)
        # for path in item_list:
        #     abs_path = os.path.join(self.label_folder, path)
        #     name, ext = os.path.splitext(path)
        #     if os.path.isfile(abs_path) and (ext == filter_ext):
        #         # print(path)
        #         self.grid_code_list.append(path)
        # self.grid_code_list.sort()

        return self.grid_code_list

    @staticmethod
    def _slice_label(label_data, min_pixel_percent, grid_code, folder):
        print(f'Slicing types for {grid_code} ...')
        patch_size2 = label_data.size

        # 1. the number of types in parcel_data, and their values
        unique, counts = np.unique(label_data, return_counts=True, axis=None)

        # 2. for each type in parcel_data
        for vv, num in zip(unique, counts):

            if (vv != 0) and (num / patch_size2 > min_pixel_percent):

                slice_path = os.path.join(folder, '{:0>2d}_00000000_{}'.format(vv, grid_code))
                print(f'generating sample on {slice_path}')
                label_data_current = label_data.copy()

                # mask non-target values
                label_mask = label_data_current != vv
                label_data_current[label_mask] = 0

                # save to disk
                write_slice_array(vv, label_data_current, slice_path)
            # if
        # for
        return grid_code

    def slice_label_grid(self):
        print('### Slicing grid by labels...')

        combine_folder = os.path.join(self.result_folder, 'label_slice')
        if not os.path.exists(combine_folder):
            os.makedirs(combine_folder)

        # combine grid data
        num_grid = len(self.grid_code_list)
        for gg, code in tqdm(enumerate(self.grid_code_list)):
            print(f'Grid {code}')

            # target folder
            if num_grid > 10000:
                sub = gg // 10000
                write_folder = os.path.join(combine_folder, '{:0>2d}'.format(sub))
                if gg % 10000 == 0 and not os.path.exists(write_folder):
                    os.makedirs(write_folder)
            else:
                write_folder = combine_folder

            # load label grid data
            label_grid_path = os.path.join(self.label_folder, code + '.npy')
            label_grid_data = load_numpy_array(label_grid_path)

            # slice grid label by type
            self._slice_label(label_grid_data, self.min_pixel_percent, code, write_folder)
        # for

        print('### Combining grid samples complete!')
        return combine_folder


def main():
    print("##################################################################")
    print("###                                      #########################")
    print("##################################################################")

    #######################################################
    # cmd line
    min_pixel_percent = 0.01
    patch_size = 32
    result_folder = r'K:\FF\application_dataset\2020-france-agri-grid\s2_l2a_tif_masked\slice_label_32'
    label_folder = r'K:\FF\application_dataset\2020-france-agri-grid\parcel_dirong\polygon_rasterize\parcel_dirong_label40'

    #######################################################
    # do
    gls = GridLabelSlice(label_folder, result_folder, patch_size, min_pixel_percent)
    gls.list_grid_codes()
    gls.slice_label_grid()

    #######################################################
    # close

    print('### Task complete !')


if __name__ == '__main__':
    main()
