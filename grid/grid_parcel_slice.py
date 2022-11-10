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


class GridParcelSlice(object):
    """
    对地块栅格数据切片，按照地块ID不同，进行分层。
    输入：32*32大小的切片，可能含有多个地块的像元；
    处理：根据像元ID不同，生成每个ID对应的切片，该切片中仅保留该ID像元的值，其余像元值=0；
    输出：多个32*32切片，每个切片只有一种像元值。
    """
    def __init__(self, parcel_folder, result_folder, patch_size=32, min_pixel_percent=0.01):
        self.parcel_folder = parcel_folder
        self.result_folder = result_folder

        self.patch_size = patch_size
        self.min_pixel_percent = min_pixel_percent

        self.grid_code_list = []

    def list_grid_codes(self, filter_ext='.npy'):
        """

        :param filter_ext:
        :return:
        """
        # fast version
        item_list = os.listdir(self.parcel_folder)
        for path in item_list:
            self.grid_code_list.append(path[:-4])
        self.grid_code_list.sort()

        # item_list = os.listdir(self.label_folder)
        # for path in item_list:
        #     abs_path = os.path.join(self.label_folder, path)
        #     name, ext = os.path.splitext(path)
        #     if os.path.isfile(abs_path) and (ext == filter_ext):
        #         self.grid_code_list.append(path)
        # self.grid_code_list.sort()

        return self.grid_code_list

    @staticmethod
    def _slice_parcel(parcel_data, min_pixel_percent, grid_code, folder):
        """
        对切片进行分层
        :param parcel_data: 输入切片数据
        :param min_pixel_percent: 类别的最小像元个数比例
        :param grid_code: 切片编码
        :param folder: 输出目录
        :return:
        """
        print(f'Slicing types for {grid_code} ...')
        patch_size2 = parcel_data.size

        # 1. the number of parcel in parcel_data, and their values
        unique, counts = np.unique(parcel_data, return_counts=True, axis=None)

        # 2. for each type in parcel_data
        for vv, num in zip(unique, counts):
            # check not background pixels, and percent of target pixel is enough
            if (vv != 0) and (num / patch_size2 > min_pixel_percent):
                # path for the slice of this grid
                slice_path = os.path.join(folder, '00_{:0>8d}_{}'.format(vv, grid_code))
                print(f'generating sample on {slice_path}')
                # make a data copy.
                parcel_data_current = parcel_data.copy()
                # mask non-target values
                label_mask = parcel_data_current != vv
                parcel_data_current[label_mask] = 0
                # save to disk
                write_slice_array(vv, parcel_data_current, slice_path)
            # if
        # for
        return grid_code

    def slice_parcel_grid(self):
        """

        :return:
        """
        print('### Slicing grid by parcels...')

        # make result folder
        combine_folder = os.path.join(self.result_folder, 'parcel_slice')
        if not os.path.exists(combine_folder):
            os.makedirs(combine_folder)

        # combine grid data
        num_grid = len(self.grid_code_list)
        for gg, code in tqdm(enumerate(self.grid_code_list)):
            print(f'Grid {code}')

            # target folder for too many grid.
            if num_grid > 10000:
                sub = gg // 10000
                write_folder = os.path.join(combine_folder, '{:0>2d}'.format(sub))
                if gg % 10000 == 0 and not os.path.exists(write_folder):
                    os.makedirs(write_folder)
            else:
                write_folder = combine_folder

            # load parcel grid data
            parcel_grid_path = os.path.join(self.parcel_folder, code + '.npy')
            parcel_grid_data = load_numpy_array(parcel_grid_path)

            # slice grid parcel by type
            self._slice_parcel(parcel_grid_data, self.min_pixel_percent, code, write_folder)
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
    result_folder = r'K:\FF\application_dataset\2020-france-agri-grid\s2_l2a_tif_masked\slice_parcel_32'
    parcel_folder = r'K:\FF\application_dataset\2020-france-agri-grid\parcel_dirong\polygon_rasterize\parcel_dirong_polygon'

    #######################################################
    # do
    gps = GridParcelSlice(parcel_folder, result_folder, patch_size, min_pixel_percent)
    gps.list_grid_codes()
    gps.slice_parcel_grid()

    #######################################################
    # close

    print('### Task complete !')


if __name__ == '__main__':
    main()
